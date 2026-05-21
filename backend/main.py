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
    allow_origins=["*"],  # Allows literally any website to connect
    allow_credentials=False, # ✨ Turning this OFF stops the browser from panicking
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
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# 5. The Route that saves the form data
@app.post("/register")
async def create_candidate(candidate: CandidateModel):
    # Connect to the cloud using the helper function!
    db = get_db_connection()
    if not db:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = db.cursor()
        
        # Write the data into the cloud vault
        sql = "INSERT INTO candidates (full_name, email, phone_number, preferred_country) VALUES (%s, %s, %s, %s)"
        values = (candidate.full_name, candidate.email, candidate.phone_number, candidate.preferred_country)
        
        cursor.execute(sql, values)
        db.commit()
        
        return {"message": "Candidate profile successfully uploaded to the cloud!"}
        
    except Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save to database.")
        
    finally:
        # Always close the vault doors when finished
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals() and db.is_connected():
            db.close()