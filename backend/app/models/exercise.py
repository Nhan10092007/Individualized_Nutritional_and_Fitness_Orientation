from sqlalchemy import Column, Integer, String, Float, CheckConstraint, JSON
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        CheckConstraint(
            "intensity_level IN ('Light', 'Moderate', 'Vigorous')",
            name="ck_exercises_intensity",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String, nullable=False, index=True)
    name_vi = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    intensity_level = Column(String, nullable=False, default="Moderate")  # 'Light' | 'Moderate' | 'Vigorous'
    description = Column(String)
    equipment = Column(String(100), nullable=True)
    instructions = Column(JSON, default=list)
    common_mistakes = Column(JSON, default=list)
    image = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    #add 4 more fields for ex: target, secondary, banned for, clinical reasons
    target_muscle = Column(String(50), nullable=True, index=True)
    secondary_muscle = Column(JSON, default=list)
    banned_for = Column(JSON, default=list)
    clinical_reasons = Column(String, nullable=True)
    source = Column(String, default="Compendium 2011")
