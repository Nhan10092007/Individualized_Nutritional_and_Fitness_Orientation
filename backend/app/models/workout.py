from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, CheckConstraint, Index,
)

from app.database import Base, utcnow


class WorkoutLog(Base):
    """
    Nhật ký tập luyện (Calo BURN).
    Cal/min = MET * 3.5 * Body_Weight / 200
    T (phút) = [(sets * duration_per_set_sec) + ((sets - 1) * rest_between_sets_sec)] / 60
    Total Calo = Cal/min * T
    """
    __tablename__ = "workout_logs"
    __table_args__ = (
        CheckConstraint("sets >= 1", name="ck_workout_logs_sets"),
        CheckConstraint("duration_per_set_sec > 0", name="ck_workout_logs_duration"),
        CheckConstraint("rest_between_sets_sec >= 0", name="ck_workout_logs_rest"),
        Index("idx_workout_logs_user_date", "user_id", "logged_date"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False)
    logged_date = Column(Date, nullable=False, index=True)
    user_weight_kg = Column(Float, nullable=False)
    met_applied = Column(Float, nullable=False)
    sets = Column(Integer, default=1, nullable=False)
    duration_per_set_sec = Column(Float, nullable=False)
    rest_between_sets_sec = Column(Float, nullable=False, default=0.0)
    total_duration_minutes = Column(Float, nullable=False)
    calories_burned = Column(Float, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)
