from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, ForeignKey, CheckConstraint, Index,
)

from app.database import Base, utcnow


class FoodLog(Base):
    """Nhật ký ăn uống (Calo IN)."""
    __tablename__ = "food_logs"
    __table_args__ = (
        CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')",
            name="ck_food_logs_meal_type",
        ),
        CheckConstraint("actual_weight_g >= 0", name="ck_food_logs_weight_non_negative"),
        Index("idx_food_logs_user_date", "user_id", "logged_date"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False)
    logged_date = Column(Date, nullable=False, index=True)
    meal_type = Column(String, nullable=False)  # 'breakfast', 'lunch', 'dinner', 'snack'
    serving_count = Column(Float, nullable=False, default=1.0)
    actual_weight_g = Column(Float, nullable=False)
    calculated_calories = Column(Float, nullable=False)
    calculated_protein = Column(Float, nullable=False, default=0.0)
    calculated_fat = Column(Float, nullable=False, default=0.0)
    calculated_carbs = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
