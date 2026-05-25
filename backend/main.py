import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import os
import google.generativeai as genai
import pydantic
from pydantic import BaseModel, Field

# Pull the secret key from Render's vault
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Changed to the most stable, globally available model string
ai_model = genai.GenerativeModel('gemini-pro')

# Define what an incoming chat message from React looks like
class ChatRequest(BaseModel):
    message: str

# 1. Load the secure variables from the .env file
load_dotenv()

app = FastAPI(title="NextGen Consultancy API")

# 2. Fix CORS (The Bulletproof Version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Define the data format coming from the frontend
class CandidateModel(pydantic.BaseModel):
    full_name: str
    email: str
    phone_number: str
    preferred_country: str

# 4. The Cloud Database Connection Helper
def get_db_connection():
    try:
        # ✨ THE IP BYPASS: Skipping Render's broken DNS entirely
        db_host = "64.227.186.189"
        
        db_port = os.getenv("DB_PORT", "").strip()
        db_user = os.getenv("DB_USER", "").strip()
        db_password = os.getenv("DB_PASSWORD", "").strip()
        db_name = os.getenv("DB_NAME", "").strip()

        print(f"Attempting to connect to hardcoded host: {db_host}")

        connection = mysql.connector.connect(
            host=db_host,
            port=int(db_port) if db_port.isdigit() else db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            ssl_disabled=False  # ✨ AIVEN SECURITY OVERRIDE
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# 5. The Route that saves the form data
@app.post("/register")
async def create_candidate(candidate: CandidateModel):
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
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save to database.")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()

# 6. The Route that handles the chat messages
@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # Give the AI its NextGen Internship personality
        system_prompt = """
        You are an expert Career Placement Advisor for NextGen Consultancy. 
        Your job is to recommend the best country (UAE, Singapore, or Malta) based on the candidate's skills.
        Keep your answers short, friendly, and professional (under 3 sentences).
        Candidate message: 
        """
        
        # Send the personality instructions + the user's message to Gemini
        response = ai_model.generate_content(system_prompt + request.message)
        
        # Send the AI's answer back to the React frontend
        return {"reply": response.text}
        
    except Exception as e:
        return {"reply": f"AI connection error: {str(e)}"}