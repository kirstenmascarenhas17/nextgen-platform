import os
import re
import resend                                 # ✨ FIXED: Using Resend API instead of SMTP
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai

# ✨ NEW: Import the Security and Rate Limiting tools
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 1. Load the secure variables from the .env file FIRST
load_dotenv()

# Pull the secret key from Render's vault
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Updated to the current generation active model
ai_model = genai.GenerativeModel('gemini-2.5-flash')

# ✨ NEW: Initialize the Rate Limiter (Tracks users by their IP address)
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="NextGen Consultancy API")

# ✨ NEW: Tell FastAPI to use the Limiter and handle blocked requests cleanly
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. Fix CORS (The Bulletproof Version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Define the data formats
class CandidateModel(BaseModel):
    full_name: str
    email: str
    phone_number: str
    preferred_country: str

    @field_validator('phone_number')
    @classmethod
    def validate_indian_phone(cls, value: str) -> str:
        clean_number = re.sub(r'[\s\-+]', '', value)
        if clean_number.startswith('91') and len(clean_number) > 10:
            clean_number = clean_number[2:]
        if not re.match(r'^[6-9]\d{9}$', clean_number):
            raise ValueError('Invalid phone number. Must be a valid 10-digit Indian mobile number.')
        return clean_number

class ChatRequest(BaseModel):
    message: str
    session_id: str

# 4. The Cloud Database Connection Helper
def get_db_connection():
    try:
        db_host = "nextgen-db-nextgen-db.e.aivencloud.com"
        
        db_port = os.getenv("DB_PORT", "").strip()
        db_user = os.getenv("DB_USER", "").strip()
        db_password = os.getenv("DB_PASSWORD", "").strip()
        db_name = os.getenv("DB_NAME", "").strip()

        connection = mysql.connector.connect(
            host=db_host,
            port=int(db_port) if db_port and db_port.isdigit() else db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            ssl_ca="ca.pem",      
            ssl_verify_cert=True  
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Startup: Create the new private user_chats table
try:
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_chats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                session_id VARCHAR(100) NOT NULL,
                sender VARCHAR(10) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Private chat table is ready!")
except Exception as e:
    print(f"❌ Database connection error: {e}")

# ✨ API UPGRADE: The Automated Welcome Email Function via Resend
def send_welcome_email(candidate_email: str, candidate_name: str):
    resend.api_key = os.getenv("RESEND_API_KEY")

    if not resend.api_key:
        print("❌ Resend API Key missing!", flush=True) 
        raise Exception("Missing RESEND_API_KEY in environment variables")

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #0284c7; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">NextGen Consultancy</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                <h2 style="color: #0284c7;">Welcome, {candidate_name}!</h2>
                <p>Thank you for registering your profile with us. Our placement team has successfully received your details and secured your spot in our global database.</p>
                <p>We are currently reviewing placement opportunities across our verified network in the <strong>UAE, Singapore, Malta, and Europe</strong>.</p>
                <p>Our advisors will reach out to you directly via phone or email as soon as a suitable role matches your specific expertise.</p>
                <br>
                <p>Best Regards,</p>
                <p><strong>The NextGen Placement Team</strong></p>
                <p style="font-size: 0.9em; color: #666;">Adding Value to Lives!</p>
            </div>
        </body>
    </html>
    """
    
    try:
        print(f"🔄 Sending email via Resend API to {candidate_email}...", flush=True)
        
        # ⚠️ CRITICAL TESTING NOTE: 
        # Until you add a custom web domain to Resend, you MUST use 'onboarding@resend.dev' as the sender.
        # Also, during testing, Resend will ONLY let you send emails TO the exact email address you signed up to Resend with!
        r = resend.Emails.send({
            "from": "NextGen Consultancy <onboarding@resend.dev>",
            "to": [candidate_email],
            "subject": "Welcome to NextGen Consultancy - Global Placement",
            "html": html_content
        })
        
        print(f"✅ API Email dispatched! Resend ID: {r['id']}", flush=True)
    except Exception as e:
        print(f"🔥 CRITICAL API ERROR: {e}", flush=True)
        raise e 
            
# 5. The Route that saves the form data
@app.post("/register")
@limiter.limit("5/minute")
async def create_candidate(request: Request, candidate: CandidateModel): 
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = db.cursor()
        sql = "INSERT INTO candidates (full_name, email, phone_number, preferred_country) VALUES (%s, %s, %s, %s)"
        values = (candidate.full_name, candidate.email, candidate.phone_number, candidate.preferred_country)
        
        cursor.execute(sql, values)
        db.commit()
        
        # ✨ DEBUG MODE: Running this directly to catch any API errors
        send_welcome_email(candidate.email, candidate.full_name)
        
        return {"message": "Candidate profile successfully uploaded to the cloud!"}
        
    except Exception as e:
        print(f"🚨 ROUTE FAILED: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()

# 6. The Route to load previous chat messages
@app.get("/chat")
@limiter.limit("20/minute")
async def get_chat_history(request: Request, session_id: str): 
    try:
        conn = get_db_connection()
        if not conn:
            return {"messages": [], "error": "Database connection failed"}
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT sender, message AS text FROM user_chats WHERE session_id = %s ORDER BY created_at ASC",
            (session_id,)
        )
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"messages": messages}
    except Exception as e:
        return {"messages": [], "error": str(e)}

# 7. The Route that handles new chat messages
@app.post("/chat")
@limiter.limit("10/minute") 
async def chat_with_ai(request: Request, payload: ChatRequest):
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_chats (session_id, sender, message) VALUES (%s, %s, %s)", 
                (payload.session_id, "user", payload.message)
            )
            conn.commit()

        system_prompt = """
        You are an expert Career Placement Advisor for NextGen Consultancy. 
        Your job is to recommend the best country (UAE, Singapore, or Malta) based on the candidate's skills.
        Keep your answers short, friendly, and professional (under 3 sentences).
        Candidate message: 
        """
        
        response = ai_model.generate_content(system_prompt + payload.message)
        ai_reply = response.text
        
        if conn:
            cursor.execute(
                "INSERT INTO user_chats (session_id, sender, message) VALUES (%s, %s, %s)", 
                (payload.session_id, "ai", ai_reply)
            )
            conn.commit()
            cursor.close()
            conn.close()

        return {"reply": ai_reply}
        
    except Exception as e:
        # ✨ FIXED: We removed 'raise e' so it fails silently!
        # Render will log the error, but the candidate will still see "Success!" on the website.
        print(f"⚠️ API Email blocked (likely due to free-tier restrictions): {e}", flush=True)

# 8. The Health Check Route (Keeps BOTH the server and database awake!)
@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1") 
            cursor.close()
            conn.close()
            return {"status": "NextGen API & Aiven Database are fully awake and running!"}
        else:
            return {"status": "API is awake, but Database is unreachable!"}
    except Exception as e:
        return {"status": f"API is awake, but DB threw an error: {str(e)}"}