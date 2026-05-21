import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

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
class CandidateModel(BaseModel):
    full_name: str
    email: str
    phone_number: str
    preferred_country: str

# 4. The Cloud Database Connection Helper
def get_db_connection():
    try:
        # ✨ THE OVERRIDE: We are hardcoding the host to completely bypass Render's environment variables
        db_host = "nextgen-db-nextgen-db.a.aivencloud.com"
        
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