from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from database import Base
from datetime import datetime

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    due_date = Column(String, nullable=False)
    estimated_hours = Column(Float, nullable=False)
    importance = Column(Integer, nullable=False)
    dependencies = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
