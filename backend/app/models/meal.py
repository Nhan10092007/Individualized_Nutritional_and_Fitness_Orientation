from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False)
    logged_date = Column(String, nullable=False, index=True)
    meal_type = Column(String, nullable=False)  # 'breakfast', 'lunch', 'dinner', 'snack'
    serving_count = Column(Float, default=1.0)
    actual_weight_g = Column(Float, nullable=False)
    calculated_calories = Column(Float, nullable=False)
    calculated_protein = Column(Float, default=0.0)
    calculated_fat = Column(Float, default=0.0)
    calculated_carbs = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
