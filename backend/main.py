from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error

app = FastAPI(title="NextGen Consultancy API")

# We add CORS so your React frontend is allowed to talk to this backend securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Database Connection Helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='nextgen_db',
            user='root', # Change if your MySQL username is different
            password='12345' # <-- CHANGE THIS!
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# 2. Data Validation Model (What we expect to receive from React)
class Candidate(BaseModel):
    full_name: str
    email: str
    phone_number: str
    preferred_country: str

# 3. A simple health-check route
@app.get("/")
def read_root():
    return {"message": "NextGen API is running and ready!"}

# 4. The Registration Endpoint
@app.post("/register")
def register_candidate(candidate: Candidate):
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Database connection failed")

    cursor = conn.cursor()
    try:
        # Securely insert the data to prevent SQL injection
        sql = """INSERT INTO candidates (full_name, email, phone_number, preferred_country) 
                 VALUES (%s, %s, %s, %s)"""
        val = (candidate.full_name, candidate.email, candidate.phone_number, candidate.preferred_country)
        cursor.execute(sql, val)
        conn.commit()
        return {"message": "Candidate registered successfully!", "id": cursor.lastrowid}
        
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="This email is already registered.")
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()