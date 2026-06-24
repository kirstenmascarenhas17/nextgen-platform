import os
import re
import resend
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
import json
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
    important_notice: str = ""  # ✨ NEW FIELD
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

    # ✨ UPGRADED: Premium Corporate Email Template (Now with Bulletproof PNG)
    html_content = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #334155; line-height: 1.6; max-width: 600px; margin: 0 auto; background-color: #f8fafc; padding: 20px;">
            <div style="background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <div style="text-align: center; padding: 30px 20px; border-bottom: 3px solid #0ea5e9;">
                    <img src="https://i.postimg.cc/MHSrKGLX/logo2.png" alt="NextGen Consultancy" width="240" style="width: 240px; max-width: 100%; height: auto; display: block; margin: 0 auto;" />
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #0f172a; margin-top: 0;">Welcome, {candidate_name}!</h2>
                    <p>Thank you for registering your profile with us. Our placement team has successfully received your details and secured your spot in our global database.</p>
                    <p>We are currently reviewing placement opportunities across our verified network in <strong>Europe, the UK, Israel, and Scandinavia</strong>.</p>
                    <p>Our advisory team will reach out to you directly via phone or email as soon as a suitable role matches your specific expertise.</p>
                    <br>
                    <p style="margin-bottom: 5px;">Best Regards,</p>
                    <p style="margin: 0; font-weight: bold; color: #0ea5e9;">The NextGen Placement Team</p>
                    <p style="font-size: 0.85em; color: #94a3b8; margin-top: 5px;">Adding Value to Lives!</p>
                </div>
                <div style="background-color: #0f172a; color: #94a3b8; text-align: center; padding: 20px; font-size: 0.85em;">
                    &copy; 2026 NextGen Consultancy. All rights reserved.
                </div>
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

# 7. The Route that handles new chat messages (Upgraded with Live Job Awareness)
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

        # ✨ NEW: 2. Fetch LIVE Active Jobs from the database
        live_jobs_context = "Current Active Job Openings:\n"
        if conn:
            cursor.execute("SELECT title, country, salary FROM job_postings WHERE expiry_date > NOW()")
            active_jobs = cursor.fetchall()
            if active_jobs:
                for job in active_jobs:
                    # Index 0=title, 1=country, 2=salary
                    live_jobs_context += f"- Role: {job[0]} | Location: {job[1]} | Salary: {job[2]}\n"
            else:
                live_jobs_context += "There are currently no active job openings. Please check back later.\n"

        # 3. Load the NextGen Knowledge Base
        try:
            with open("knowledge_base.txt", "r") as file:
                company_knowledge = file.read()
        except FileNotFoundError:
            company_knowledge = "NextGen Consultancy is a global placement agency."

        # ✨ UPGRADED: 4. The Master System Prompt (Now with Live DB Knowledge)
        system_prompt = f"""
        You are an expert Career Placement Advisor for NextGen Consultancy.
        Your goal is to be helpful, professional, and guide candidates toward registering with us.

        CRITICAL RULES:
        1. Base your answers on the 'Company Knowledge' and 'Live Job Data' provided below. 
        2. If a candidate asks about currently available jobs, use the 'Live Job Data' to tell them exactly what is open right now!
        3. If a candidate asks about salaries, fees, or timelines NOT listed in the live data, do not make up numbers. Tell them politely that it varies and will be discussed after registration.
        4. Keep your answers short, friendly, and under 4 sentences. Encourage them to use the "Candidate Registration" button.

        --- COMPANY KNOWLEDGE ---
        {company_knowledge}
        
        --- LIVE JOB DATA (FROM DATABASE) ---
        {live_jobs_context}
        -------------------------
        
        Candidate message: {payload.message}
        """
        
        # 5. Generate the AI Response
        response = ai_model.generate_content(system_prompt)
        ai_reply = response.text
        
        # 6. Save the AI's reply to MySQL
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

#10.
# ==========================================
# PHASE 7: JOB BOARD ROUTES (FINAL FIX)
# ==========================================

@app.get("/jobs")
def get_active_jobs():
    conn = get_db_connection() # Use 'conn' instead of 'db'
    if not conn: return {"jobs": []}
    try:
        cursor = conn.cursor()
        sql = "SELECT * FROM job_postings WHERE expiry_date > NOW() ORDER BY expiry_date ASC"
        cursor.execute(sql)
        
        columns = [column[0] for column in cursor.description]
        jobs = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"jobs": jobs}
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return {"jobs": []}


@app.post("/admin/jobs")
def create_job_posting(job: JobPostingModel, secret: str):
    if secret != "NextGenAdmin2026":
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    conn = get_db_connection() 
    if not conn: raise HTTPException(status_code=500, detail="DB connection failed")
    try:
        cursor = conn.cursor()
        # ✨ UPGRADED: Added important_notice to the INSERT query
        sql = """INSERT INTO job_postings (title, country, salary, details, eligibility, important_notice, expiry_date) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                 
        formatted_date = job.expiry_date.strftime('%Y-%m-%d %H:%M:%S')
        values = (job.title, job.country, job.salary, job.details, job.eligibility, job.important_notice, formatted_date)
        
        cursor.execute(sql, values)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Job successfully posted!"}
    except Exception as e:
        print(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/admin/jobs/{job_id}")
def delete_job_posting(job_id: int, secret: str):
    if secret != "NextGenAdmin2026":
        raise HTTPException(status_code=401, detail="Unauthorized")

    conn = get_db_connection() # Use 'conn'
    if not conn: raise HTTPException(status_code=500, detail="DB connection failed")
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM job_postings WHERE id = %s"
        cursor.execute(sql, (job_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Job successfully deleted!"}
    except Exception as e:
        print(f"Error deleting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

    #11. ✨ PHASE 8: AI Poster Parsing Route
@app.post("/admin/parse-poster")
async def parse_poster(secret: str = Form(...), file: UploadFile = File(...)):
    if secret != "NextGenAdmin2026":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        image_bytes = await file.read()
        
        # Give Gemini strict instructions to format the output as JSON and use newlines
        prompt = """
        You are an expert data extractor. Read this recruitment poster and extract the information into a strict JSON format. 
        Do not include markdown blocks like ```json or ```, just return the raw JSON.
        CRITICAL: For the "details" and "eligibility" fields, use actual newline characters (\\n) to separate different points so they appear as a clean list.
        {
            "title": "Exact job title",
            "country": "Country name",
            "salary": "Salary listed (or 'Salary Discussed on Interview' if none)",
            "details": "Job details and benefits. Use \\n to separate each point.",
            "eligibility": "Eligibility criteria. Use \\n to separate each point.",
            "important_notice": "Any urgent or highlighted notices (leave blank if none)"
        }
        """
        
        image_parts = [{"mime_type": file.content_type, "data": image_bytes}]
        response = ai_model.generate_content([prompt, image_parts[0]])
        
        # Clean the response and parse it into real JSON
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        extracted_data = json.loads(raw_text)
        
        return extracted_data
    except Exception as e:
        print(f"AI Extraction Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse poster.")