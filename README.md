# 🌍 NextGen Consultancy Platform

![NextGen Consultancy](https://i.postimg.cc/MHSrKGLX/logo2.png)

**Live Demo:** [https://www.nextgen-consultancy.net](https://www.nextgen-consultancy.net)  
**Backend API:** [https://nextgen-api-11jg.onrender.com](https://nextgen-api-11jg.onrender.com)

An enterprise-grade, full-stack recruitment platform built to streamline global placement operations. This application features a fully responsive React frontend, a secure Python FastAPI backend, a comprehensive MySQL relational database, and deep integration with Google's Gemini AI for dynamic data extraction and automated workflows.

---

## ✨ Key Features

### 🤖 AI-Powered Automation
* **Vision AI Poster Parsing:** Administrators can upload recruitment flyers, and the integrated Gemini AI Vision model will automatically extract job details, formatting them into structured JSON to instantly auto-fill job posting forms.
* **Context-Aware Chatbot:** A live customer support widget powered by Gemini AI that dynamically reads real-time active job data from the MySQL database to pitch relevant positions to candidates.

### 💼 Comprehensive Admin Suite
* **Command Center Analytics:** A live dashboard displaying real-time metrics for total candidates, active jobs, pipeline flow, and successful placements.
* **Kanban Pipeline Tracking:** Interactive candidate status management allowing administrators to move applicants through stages (Registered → Interviewing → Visa Processing → Placed).
* **Instant Data Export:** One-click clipboard exports for seamlessly transferring candidate data into Excel or CRM tools.

### 🌐 Scalable Frontend & Communications
* **Dynamic Job Board:** Features real-time countdown timers for job expirations and live database-driven alerts.
* **Automated Corporate Emailing:** Integrated with the Resend API to automatically dispatch professional, branded welcome emails upon candidate registration.
* **Responsive UI/UX:** A premium, shadow-lifted corporate aesthetic that adapts flawlessly across all mobile and desktop devices.

---

## 🛠️ Tech Stack

**Frontend Framework:** React.js, Vite  
**Backend API:** Python, FastAPI  
**Database:** MySQL (Relational structure with automated schema enforcement)  
**AI Integration:** Google Generative AI (Gemini Flash & Vision models)  
**Communications:** Resend Email API, WhatsApp Click-to-Chat  
**Deployment:** Vercel (Frontend) & Render (Backend Web Service)  

---

## 🚀 Local Development Setup

To run this project locally, you will need Node.js, Python 3.9+, and a local MySQL server instance.

### 1. Database Setup
1. Open MySQL Workbench and create a new database.
2. The backend application will automatically create the required `candidates`, `job_postings`, and `user_chats` tables upon startup.

### 2. Backend (FastAPI) Setup
```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

### 3. Frontend (React) Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

---

## 🔐 Environment Variables

To run this application, you must configure the following environment variables in your secure hosting environments or local `.env` files:

*   `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
*   `GEMINI_API_KEY`
*   `RESEND_API_KEY`

---

*This project was developed as a comprehensive portfolio piece demonstrating modern Full-Stack web architecture and live LLM integration techniques.*