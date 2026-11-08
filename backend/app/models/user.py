from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    gender = Column(String, nullable=False, default="male")
    age = Column(Integer, nullable=False)
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    fitness_goal = Column(String, default="maintain")
    activity_level = Column(String, default="moderate")
    daily_budget_vnd = Column(Float, default=50000.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
