import os
import re
import resend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai

from datetime import datetime
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
    preferred_job: str # ✨ NEW FIELD

    @field_validator('phone_number')
    @classmethod
    def validate_indian_phone(cls, value: str) -> str:
        clean_number = re.sub(r'[\s\-+]', '', value)
        if clean_number.startswith('91') and len(clean_number) > 10:
            clean_number = clean_number[2:]
        if not re.match(r'^[6-9]\d{9}$', clean_number):
            raise ValueError('Invalid phone number. Must be a valid 10-digit Indian mobile number.')
        return clean_number

class JobPostingModel(BaseModel):
    title: str
    country: str
    salary: str
    details: str
    eligibility: str
    expiry_date: datetime

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
        
        r = resend.Emails.send({
            # ✨ UPDATED: Sending from the official NextGen Domain
            "from": "NextGen Careers <careers@nextgen-consultancy.net>",
            "to": [candidate_email],
            "subject": "Welcome to NextGen Consultancy - Global Placement",
            "html": html_content
        })
        
        print(f"✅ API Email dispatched! Resend ID: {r['id']}", flush=True)
    except Exception as e:
        print(f"⚠️ API Email blocked (likely due to free-tier restrictions): {e}", flush=True)
            
# 5. The Route that saves the form data
@app.post("/register")
@limiter.limit("5/minute")
async def create_candidate(request: Request, candidate: CandidateModel): 
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = db.cursor()
        # ✨ UPDATED SQL QUERY
        sql = "INSERT INTO candidates (full_name, email, phone_number, preferred_country, preferred_job) VALUES (%s, %s, %s, %s, %s)"
        values = (candidate.full_name, candidate.email, candidate.phone_number, candidate.preferred_country, candidate.preferred_job)
        
        cursor.execute(sql, values)
        db.commit()
        
        # This will now run, and if Resend blocks it, it just prints a warning and keeps going!
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

# 7. The Route that handles new chat messages (Upgraded with Knowledge Injection)
@app.post("/chat")
@limiter.limit("10/minute") 
async def chat_with_ai(request: Request, payload: ChatRequest):
    try:
        # 1. Save the user's message to MySQL
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_chats (session_id, sender, message) VALUES (%s, %s, %s)", 
                (payload.session_id, "user", payload.message)
            )
            conn.commit()

        # 2. Load the NextGen Knowledge Base
        try:
            with open("knowledge_base.txt", "r") as file:
                company_knowledge = file.read()
        except FileNotFoundError:
            company_knowledge = "NextGen Consultancy is a global placement agency. (Knowledge base file missing)."

        # 3. The Master System Prompt
        system_prompt = f"""
        You are an expert Career Placement Advisor for NextGen Consultancy.
        Your goal is to be helpful, professional, and guide candidates toward registering with us.

        CRITICAL RULES:
        1. Base all your answers ONLY on the 'Company Knowledge' provided below. 
        2. If a candidate asks about salaries, fees, processing timelines, or specific open jobs today, YOU MUST NOT make up numbers. Tell them politely that those details vary and they will be discussed personally with a placement officer once they register.
        3. Keep your answers short, friendly, and under 4 sentences.

        --- COMPANY KNOWLEDGE ---
        {company_knowledge}
        -------------------------
        
        Candidate message: {payload.message}
        """
        
        # 4. Generate the AI Response
        response = ai_model.generate_content(system_prompt)
        ai_reply = response.text
        
        # 5. Save the AI's reply to MySQL
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
        # If Google tells us we hit the 5-message limit, show a clean user-friendly response
        if "429" in str(e) or "quota" in str(e).lower():
            return {"reply": "NextGen AI is receiving a lot of queries right now! Please wait a few seconds and try sending your message again."}
    
        return {"reply": "Our AI assistant is temporarily offline. Please try again shortly."}
        

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

# 9. ✨ NEW: The Admin Dashboard Route
@app.get("/admin/candidates")
async def get_all_candidates(request: Request, secret: str = ""):
    # Simple security lock (Change this PIN to whatever you want!)
    if secret != "NextGenAdmin2026":
        raise HTTPException(status_code=401, detail="Unauthorized Access")
        
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
    try:
        cursor = db.cursor(dictionary=True)
        # Fetch all candidates
        cursor.execute("SELECT * FROM candidates")
        candidates = cursor.fetchall()
        # Reverse the list so the newest registrations are at the top
        candidates.reverse() 
        return {"candidates": candidates}
    except Exception as e:
        print(f"🚨 ADMIN ROUTE FAILED: {str(e)}", flush=True)
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()

# ==========================================
# PHASE 7: JOB BOARD ROUTES
# ==========================================

@app.get("/jobs")
def get_active_jobs():
    try:
        db.ping(reconnect=True, attempts=3, delay=2) # ✨ Wake up DB if it went to sleep!
        cursor = db.cursor()
        sql = "SELECT * FROM job_postings WHERE expiry_date > NOW() ORDER BY expiry_date ASC"
        cursor.execute(sql)
        
        columns = [column[0] for column in cursor.description]
        jobs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {"jobs": jobs}
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return {"jobs": []}


@app.post("/admin/jobs")
def create_job_posting(job: JobPostingModel, secret: str):
    try:
        db.ping(reconnect=True)
        cursor = db.cursor()
        sql = """INSERT INTO job_postings (title, country, salary, details, eligibility, expiry_date) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
                 
        # ✨ Safely convert Python datetime into a MySQL timestamp string
        formatted_date = job.expiry_date.strftime('%Y-%m-%d %H:%M:%S')
        values = (job.title, job.country, job.salary, job.details, job.eligibility, formatted_date)
        
        cursor.execute(sql, values)
        db.commit()
        return {"message": "Job successfully posted!"}
    except Exception as e:
        print(f"Error creating job: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/jobs/{job_id}")
def delete_job_posting(job_id: int, secret: str):
    try:
        db.ping(reconnect=True, attempts=3, delay=2) # ✨ Wake up DB
        cursor = db.cursor()
        sql = "DELETE FROM job_postings WHERE id = %s"
        cursor.execute(sql, (job_id,))
        db.commit()
        return {"message": "Job successfully deleted!"}
    except Exception as e:
        print(f"Error deleting job: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))