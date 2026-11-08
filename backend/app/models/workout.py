from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False)
    logged_date = Column(String, nullable=False, index=True)
    user_weight_kg = Column(Float, nullable=False)
    met_applied = Column(Float, nullable=False)
    sets = Column(Integer, default=1, nullable=False)
    duration_per_set_sec = Column(Float, nullable=False)
    rest_between_sets_sec = Column(Float, default=0.0)
    total_duration_minutes = Column(Float, nullable=False)
    calories_burned = Column(Float, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
