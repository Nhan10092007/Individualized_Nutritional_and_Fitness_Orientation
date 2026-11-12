from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

# Định nghĩa các lựa chọn khi người dùng đăng nhập. Ví dụ: giới tính thì ta chọn nam hoặc nữ

# Giới tính
class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"

# Fitness Goal
class FitnessGoalEnum(str, Enum):
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTAIN = "maintain"

# Fitness Level
class FitnessLevelEnum(str, Enum):
    BEGINNER = "beginner"
    EXPERIENCED = "experienced"
    ADVANCED = "advanced"

# Dữ liệu Client gửi lên khi hoàn thành Form Onboarding (dữ liệu nhập)
class OnboardingRequest(BaseModel):
    gender: GenderEnum = Field(..., description = "Biological gender ('male' or 'female')")
    age: int = Field(..., ge = 10, le = 70, description = "Age (from 10 to 70)")
    height_cm: float = Field(..., ge = 125.0, le = 200.0, description = "Height (cm)")
    weight_kg: float = Field(..., ge = 35.0, le = 150.0, description = "Weight (kg)")
    fitness_goal: FitnessGoalEnum = Field(..., description = "Fitness goal (fat loss, muscle gain, maintain)")
    fitness_level: FitnessLevelEnum = Field(..., description = "Fitness level (beginner, experienced, advanced)")
    available_days: List[str] = Field(..., min_length = 2, max_length = 6, description = "Days in week that you are available to workout (2 to 6 days)")
    session_duration_mins: int = Field(45, ge = 30, le = 120, description = "Session duration time (30 - 120 minutes)")
    medical_conditions: List[str] = Field(default_factory = list, description = "Underlying medical condition: 'knee_osteoarthritis' and 'hypertension'")
    daily_budget_vnd: float = Field(50000.0, ge = 50000.0, description = "Daily budget for food (at least 50,000 VND)")

# Cấu trúc chia nhỏ Macro
class MacroSplit(BaseModel):
    protein_g: int
    carb_g: int
    fat_g: int

# Dữ liệu trả về cho client sau khi tính toán các chỉ số và lưu vào database
class OnboardingResponse(BaseModel):
    message: str
    is_valid: bool
    validation_warnings: List[str] = Field(default_factory = list, description = "An alert is issued if a user enters data that exceeds safe medical thresholds, and the system has automatically made adjustments.")
    bmi: float
    ibw_kg: float
    bmr_kcal: float
    tdee_kcal: float
    target_calorie_kcal: float
    is_safety_floor_triggered: bool = Field(..., description="True if the target calorie count hit the medical lower limit and the system automatically increased it.")
    macro_split: MacroSplit
    budget_tier: str
    banned_exercise_tags: List[str]
