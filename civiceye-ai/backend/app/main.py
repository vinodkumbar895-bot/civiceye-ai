import os
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Complaint
from .ai_service import analyze_image

load_dotenv()
Base.metadata.create_all(bind=engine)
UPLOADS = Path("uploads")
UPLOADS.mkdir(exist_ok=True)
LIMIT = int(os.getenv("MAX_UPLOAD_MB", "5"))
ALLOWED = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title="CivicEye AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"), "http://127.0.0.1:5173"],
    allow_methods=["*"], allow_headers=["*"], allow_credentials=True,
)
app.mount("/uploads", StaticFiles(directory=str(UPLOADS)), name="uploads")

def output(c):
    return {
        "id": c.id, "title": c.title, "description": c.description, "location": c.location,
        "category": c.category, "severity": c.severity, "ai_summary": c.ai_summary,
        "department": c.department, "status": c.status,
        "image_url": f"/uploads/{c.image_path}" if c.image_path else None,
        "created_at": c.created_at,
    }

@app.get("/")
def home():
    return {"message": "CivicEye AI API is running"}

@app.get("/api/complaints")
def list_complaints(db: Session = Depends(get_db)):
    return [output(c) for c in db.query(Complaint).order_by(Complaint.created_at.desc()).all()]

@app.post("/api/complaints")
async def create_complaint(
    title: str = Form(...), description: str = Form(...), location: str = Form(...),
    image: UploadFile = File(...), db: Session = Depends(get_db)
):
    if not title.strip() or not description.strip() or not location.strip():
        raise HTTPException(400, "Title, description and location are required.")
    if image.content_type not in ALLOWED:
        raise HTTPException(415, "Upload JPG, PNG or WEBP.")
    data = await image.read()
    if not data or len(data) > LIMIT * 1024 * 1024:
        raise HTTPException(413, f"Image must be non-empty and smaller than {LIMIT} MB.")
    try:
        ai = analyze_image(data, image.content_type)
    except Exception as e:
        raise HTTPException(502, f"AI analysis failed: {str(e)[:220]}")
    ext = Path(image.filename or "photo.jpg").suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}: ext = ".jpg"
    name = uuid4().hex + ext
    (UPLOADS / name).write_bytes(data)
    c = Complaint(title=title.strip(), description=description.strip(), location=location.strip(),
        category=ai["category"], severity=ai["severity"], ai_summary=ai["summary"],
        department=ai["department"], image_path=name)
    db.add(c); db.commit(); db.refresh(c)
    return output(c)

@app.patch("/api/complaints/{cid}/status")
def update_status(cid: int, payload: dict, db: Session = Depends(get_db)):
    status = payload.get("status")
    if status not in {"Pending", "In Progress", "Resolved"}:
        raise HTTPException(400, "Invalid status.")
    c = db.query(Complaint).filter(Complaint.id == cid).first()
    if not c: raise HTTPException(404, "Complaint not found.")
    c.status = status; db.commit(); db.refresh(c)
    return output(c)
