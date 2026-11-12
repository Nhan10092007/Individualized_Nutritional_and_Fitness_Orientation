from sqlalchemy import Column, Integer, String, Float, DateTime, CheckConstraint

from app.database import Base, utcnow


class Food(Base):
    __tablename__ = "foods"
    __table_args__ = (
        CheckConstraint("source IN ('USDA', 'VN_FCT', 'CUSTOM')", name="ck_foods_source"),
        CheckConstraint("calories_100g >= 0", name="ck_foods_calories_non_negative"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True)          # 'USDA_171077' | 'VN_01001'
    name_vi = Column(String, nullable=False, index=True)
    name_en = Column(String)
    category = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False, index=True)     # 'USDA' | 'VN_FCT' | 'CUSTOM'
    serving_unit = Column(String, nullable=False, default="100g")
    serving_weight_g = Column(Float, nullable=False, default=100.0)
    calories_100g = Column(Float, nullable=False)
    protein_100g = Column(Float, nullable=False, default=0.0)
    fat_100g = Column(Float, nullable=False, default=0.0)
    carbs_100g = Column(Float, nullable=False, default=0.0)
    fiber_100g = Column(Float, default=0.0)
    estimated_price_vnd = Column(Float, default=0.0)        # Hỗ trợ A5 (ngân sách)
    diet_type = Column(String, default="all")               # 'all' | 'vegetarian' | 'vegan'
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)
