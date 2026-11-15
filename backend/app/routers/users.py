from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db, utcnow
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import OnboardingRequest, OnboardingResponse
from app.algorithms.input_validator import InputValidator

router = APIRouter(prefix = "/api/users", tags = ["Users"])

# API khảo sát và validate dữ liệu người dùng
@router.post("/onboarding", response_model = OnboardingResponse, status_code = status.HTTP_200_OK)
def submit_onboarding(payload: OnboardingRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = InputValidator.validate_and_construct(payload)
    clean_data = result["clean_data"]

    for field, value in clean_data.items():
        setattr(current_user, field, value)

    current_user.onboarded_at = utcnow()

    db.commit()
    db.refresh(current_user)

    return result["response"]

# API trả về thông tin profile
@router.get("/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_onboarded": current_user.is_onboarded,
        "biometrics": {
            "gender": current_user.gender,
            "age": current_user.age,
            "height_cm": current_user.height_cm,
            "weight_kg": current_user.weight_kg,
            "bmi": current_user.bmi,
            "ibw_kg": current_user.ibw_kg
        },
        "plan_targets": {
            "fitness_goal": current_user.fitness_goal,
            "fitness_level": current_user.fitness_level,
            "available_days": current_user.available_days,
            "session_duration_mins": current_user.session_duration_mins,
            "bmr_kcal": current_user.bmr_kcal,
            "tdee_kcal": current_user.tdee_kcal,
            "target_calorie_kcal": current_user.target_calorie_kcal,
            "macro_split": {
                "protein_g": current_user.protein_g,
                "carb_g": current_user.carb_g,
                "fat_g": current_user.fat_g
            }
        },
        "constraints": {
            "daily_budget_vnd": current_user.daily_budget_vnd,
            "budget_tier": current_user.budget_tier,
            "banned_exercise_tags": current_user.banned_exercise_tags,
            "medical_conditions": current_user.medical_conditions
        }
    }