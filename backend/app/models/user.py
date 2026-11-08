from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON
from app.database import Base


class User(Base):
    """
    Mô hình người dùng: Lưu tài khoản đăng nhập và hồ sơ sinh trắc học cá nhân hóa (A1).
    """
    __tablename__ = "users"

    # Thông tin tài khoản xác thực (Auth)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Thông tin thu thập ban đầu từ Onboarding (A1 Raw Input)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)               # "male" | "female"
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    fitness_goal = Column(String(30), nullable=True)         # "fat_loss" | "muscle_gain" | "maintain"
    fitness_level = Column(Integer, default=1)               # 1 (Beginner) -> 5 (Advanced)
    available_days = Column(JSON, default=list)              # ["Mon", "Wed", "Fri"]
    session_duration_mins = Column(Integer, default=45)      # 15 - 120 phút
    medical_conditions = Column(JSON, default=list)          # ["knee_osteoarthritis", "hypertension"]
    dietary_preference = Column(String(30), default="normal") # "normal" | "vegetarian"
    daily_budget_vnd = Column(Float, default=50000.0)

    # Các chỉ số chuyển hóa & Ràng buộc do Phân hệ A1 tính toán & dựng ra
    bmi = Column(Float, nullable=True)                       # Chỉ số khối cơ thể
    ibw_kg = Column(Float, nullable=True)                    # Cân nặng lý tưởng (Devine)
    bmr_kcal = Column(Float, nullable=True)                  # Calo trao đổi chất cơ bản
    tdee_kcal = Column(Float, nullable=True)                 # Tổng tiêu hao năng lượng hàng ngày
    target_calorie_kcal = Column(Float, nullable=True)       # Calo mục tiêu (đã áp dụng sàn an toàn)
    protein_g = Column(Integer, nullable=True)
    carb_g = Column(Integer, nullable=True)
    fat_g = Column(Integer, nullable=True)
    budget_tier = Column(String(30), nullable=True)          # tier_1_under_50k, tier_2_50k_to_100k, tier_3_over_100k
    banned_exercise_tags = Column(JSON, default=list)        # Nhãn cấm bài tập cho A3
