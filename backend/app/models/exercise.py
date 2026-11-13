from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, CheckConstraint

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
    code = Column(String, unique=True, index=True)          # Mã Compendium ('02050'), 'EXDB_...', 'KAGGLE_0001'
    category = Column(String, nullable=False, index=True)
    name_vi = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    met_value = Column(Float, nullable=False, index=True)
    intensity_level = Column(String, nullable=False, default="Moderate")  # 'Light' | 'Moderate' | 'Vigorous'
    description = Column(String)
    source = Column(String, default="Compendium 2011")

    # Thuộc tính mở rộng từ GitHub ExerciseDB / MegaGym (Step 2 Asset Handling + Step 3 Transform & A3)
    primary_muscles = Column(JSON, default=list)            # ['quadriceps']
    secondary_muscles = Column(JSON, default=list)          # ['glutes', 'hamstrings']
    equipment = Column(String, index=True)                  # 'body only' | 'barbell' | 'dumbbell' ...
    level = Column(String, index=True)                      # 'beginner' | 'intermediate' | 'expert'
    instructions = Column(JSON, default=list)               # Các bước hướng dẫn tập
    image_urls = Column(JSON, default=list)                 # URL ảnh/GIF đã qua bước Asset Handling (S3/Cloudinary/CDN)
    thumbnail_url = Column(String)                          # Ảnh/GIF đại diện
    video_url = Column(String)                              # Video hướng dẫn (nếu có)
    banned_for = Column(JSON, default=list)                 # ['knee_osteoarthritis', 'hypertension'] phục vụ A3
    clinical_reason = Column(String)                        # Lý do chống chỉ định y khoa (A3)

    created_at = Column(DateTime(timezone=True), default=utcnow)
