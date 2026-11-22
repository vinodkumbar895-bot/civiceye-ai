from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text
from .database import Base

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(240), nullable=False)
    category = Column(String(80), default="Other", nullable=False)
    severity = Column(String(20), default="Medium", nullable=False)
    ai_summary = Column(Text, default="", nullable=False)
    department = Column(String(100), default="Municipal Corporation", nullable=False)
    status = Column(String(30), default="Pending", nullable=False)
    image_path = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
