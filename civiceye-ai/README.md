# CivicEye AI — IDEA//FORGE MVP

## Stack
React + Vite frontend, FastAPI backend, SQLite database, Gemini image analysis API.

## Run on Windows
### Backend (Terminal 1)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Add your Gemini API key to `backend/.env`, then:
```powershell
uvicorn app.main:app --reload
```
API: http://127.0.0.1:8000/docs

### Frontend (Terminal 2)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open http://localhost:5173

Get a Gemini API key at https://aistudio.google.com/app/apikey.
The key belongs only in backend/.env, never in frontend code.

## MVP flow
Citizen enters title, description and location, uploads an image; Gemini suggests category, severity and department; FastAPI saves the complaint to SQLite; admin demo dashboard lists complaints and updates status.

AI classification is a suggestion, not an official inspection. This MVP does not submit complaints to a real municipality. Add authentication, authorization, rate limits, privacy notice and secure file storage before public launch.
