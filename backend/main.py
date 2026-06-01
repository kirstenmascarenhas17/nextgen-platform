import os
import re
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

# 5. The Route that saves the form data
@app.post("/register")
@limiter.limit("5/minute") # ✨ NEW: Max 5 submissions per minute per IP
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
        return {"message": "Candidate profile successfully uploaded to the cloud!"}
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Failed to save to database.")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()

# 6. The Route to load previous chat messages
@app.get("/chat")
@limiter.limit("20/minute") # ✨ NEW: Rate limit for loading history
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
@limiter.limit("10/minute") # ✨ NEW: Protects Gemini API from spam
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
        return {"reply": f"AI connection error: {str(e)}"}

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