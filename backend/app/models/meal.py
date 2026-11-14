from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base, utcnow

class FoodLog(Base):
    """Nhật ký ăn uống (Calo IN)."""
    __tablename__ = "food_logs"
    __table_args__ = (
        CheckConstraint(
            "meal_type IN ('breakfast', 'lunch', 'dinner')",
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


class MealPlan(Base):
    """Bảng lưu trữ thông tin tổng quan của 1 lần sinh thực đơn."""
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    generated_date = Column(Date, nullable=False, default=utcnow)
    
    total_calories = Column(Float, nullable=False)
    total_protein = Column(Float, nullable=False)
    total_carbs = Column(Float, nullable=False)
    total_fat = Column(Float, nullable=False)
    total_cost_vnd = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=utcnow)

    # Quan hệ 1-n với MealPlanItem
    items = relationship("MealPlanItem", back_populates="plan", cascade="all, delete-orphan")


class MealPlanItem(Base):
    """Bảng lưu chi tiết từng món ăn trong 1 thực đơn (chia theo bữa)."""
    __tablename__ = "meal_plan_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id", ondelete="RESTRICT"), nullable=False)
    
    meal_type = Column(String, nullable=False) # 'Bữa Sáng', 'Bữa Trưa', 'Bữa Tối'
    grams = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, nullable=False)
    carbs_g = Column(Float, nullable=False)
    fat_g = Column(Float, nullable=False)
    cost_vnd = Column(Float, nullable=False)

    plan = relationship("MealPlan", back_populates="items")

