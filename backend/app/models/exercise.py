from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, index=True)
    category = Column(String, nullable=False, index=True)
    name_vi = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    met_value = Column(Float, nullable=False, index=True)
    intensity_level = Column(String, default="Moderate")  # 'Light' | 'Moderate' | 'Vigorous'
    description = Column(String)
    source = Column(String, default="Compendium 2011")
    created_at = Column(DateTime, default=datetime.utcnow)
