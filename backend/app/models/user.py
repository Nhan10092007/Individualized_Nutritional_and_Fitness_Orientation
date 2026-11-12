from sqlalchemy import Column, Integer, String, Float, DateTime, JSON

from app.database import Base, utcnow


class User(Base):
    """
    Người dùng: tài khoản đăng nhập + hồ sơ sinh trắc học (A1 input) + kết quả tính toán của A1.

    Các trường sinh trắc học để nullable=True vì lúc đăng ký chưa có;
    chúng được điền sau khi người dùng hoàn thành bước Onboarding (A1).
    Việc kiểm tra miền giá trị (tuổi, chiều cao, cân nặng...) do Pydantic schema + thuật toán A1 đảm nhận.
    """
    __tablename__ = "users"

    # --- 1. Tài khoản (Auth) ---
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))

    # --- 2. Dữ liệu thu thập từ Onboarding (A1 Raw Input) ---
    gender = Column(String(10))                               # 'male' | 'female'
    age = Column(Integer)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    fitness_goal = Column(String(20))                         # 'fat_loss' | 'muscle_gain' | 'maintain'
    fitness_level = Column(Integer)                           # 1 (mới tập) -> 5 (nâng cao)
    available_days = Column(JSON, default=list)               # ['Mon', 'Wed', 'Fri']
    session_duration_mins = Column(Integer)                   # 15 -> 120 phút
    medical_conditions = Column(JSON, default=list)           # ['knee_osteoarthritis', 'hypertension']
    daily_budget_vnd = Column(Float)                          # >= 15,000 VNĐ

    # --- 3. Kết quả do thuật toán A1 tính ra (A1 Output) ---
    bmi = Column(Float)
    ibw_kg = Column(Float)                                    # Cân nặng lý tưởng (Devine)
    bmr_kcal = Column(Float)                                  # Mifflin - St Jeor
    tdee_kcal = Column(Float)
    target_calorie_kcal = Column(Float)                       # Đã áp dụng sàn an toàn y tế
    protein_g = Column(Integer)
    carb_g = Column(Integer)
    fat_g = Column(Integer)
    budget_tier = Column(String(30))                          # 'tier_1_under_50k' | 'tier_2_50k_to_100k' | 'tier_3_over_100k'
    banned_exercise_tags = Column(JSON, default=list)         # Nhãn cấm bài tập dùng cho A3
    onboarded_at = Column(DateTime(timezone=True))            # NULL = chưa hoàn thành onboarding

    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    @property
    def is_onboarded(self) -> bool:
        return self.onboarded_at is not None
