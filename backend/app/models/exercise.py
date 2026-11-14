from sqlalchemy import Column, Integer, String, Float, DateTime, CheckConstraint, JSON

from app.database import Base, utcnow


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint("met_value > 0", name="ck_exercises_met_positive"),
        CheckConstraint(
            "intensity_level IN ('Light', 'Moderate', 'Vigorous')",
            name="ck_exercises_intensity",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True)          # Mã Compendium (vd: '02050') hoặc 'KAGGLE_0001'
    category = Column(String, nullable=False, index=True)
    name_vi = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    met_value = Column(Float, nullable=False, index=True)
    intensity_level = Column(String, nullable=False, default="Moderate")  # 'Light' | 'Moderate' | 'Vigorous'
    description = Column(String)
    #add 4 more fields for ex: target, secondary, banned for, clinical reasons
    target_muscle = Column(String(50), nullable=True, index=True)
    secondary_muscle = Column(JSON, default=list)
    banned_for = Column(JSON, default=list)
    clinical_reasons = Column(String, nullable=True)
    source = Column(String, default="Compendium 2011")
    created_at = Column(DateTime(timezone=True), default=utcnow)
