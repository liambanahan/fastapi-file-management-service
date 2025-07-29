from infrastructure.db.mysql import mysql as db
from sqlalchemy import Column, String, DateTime, VARCHAR
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime


class Appointment(db.Base):
    __tablename__ = "appointments"
    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    files = relationship("File", back_populates="appointment") 