from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class Food(Base):
    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True)
    name_vi = Column(String, nullable=False, index=True)
    name_en = Column(String)
    category = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False)  # 'USDA' | 'VN_FCT' | 'CUSTOM'
    serving_unit = Column(String, default="100g")
    serving_weight_g = Column(Float, default=100.0)
    calories_100g = Column(Float, nullable=False)
    protein_100g = Column(Float, default=0.0)
    fat_100g = Column(Float, default=0.0)
    carbs_100g = Column(Float, default=0.0)
    fiber_100g = Column(Float, default=0.0)
    estimated_price_vnd = Column(Float, default=0.0)
    diet_type = Column(String, default="all")
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
