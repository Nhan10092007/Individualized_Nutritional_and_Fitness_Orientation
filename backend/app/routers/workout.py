"""
Router: workout.py
Manage APIs for workout-related operations: Generate automatically plan(A3+A4) and save workout logs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Set, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.exercise import Exercise
from app.models.workout import WorkoutPlan
from app.algorithms.workout_generator import is_exercise_safe, generate_weekly_workout_schedule

router = APIRouter(prefix="/api/workout", tags=["Workout"])
#API_01: POST
@router.post("/generate", summary="Automaticly generate personalized weekly plan")
def generate_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:

    #1. Onboarding check thong tin nguoi dung
    available_days = current_user.available_days or ["Mon", "Wed", "Fri"]
    duration_mins = current_user.session_duration_mins or 45
    goal = current_user.fitness_goal or "general_fitness"
    level = current_user.fitness_level or "beginner"
    conditions = current_user.medical_conditions or []

    #2. Truy van ex tu db
    exercise_in_db = db.query(Exercise).all()
    if not exercise_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Kho bài tập rỗng. Vui lòng chạy seed_database.py trước"
        )   

    # Chuyen tu SQLAchemy object sang Dict de chay thuat toan
    exercise_pool = []
    for ex in exercise_in_db:
        if ex.target_muscle:
            exercise_pool.append({
                "id": str(ex.id),
                "name": ex.name_vi or ex.name_en,
                "target_muscle": ex.target_muscle,
                "secondary_muscles": ex.secondary_muscle or [],
                "banned_for": ex.banned_for or [],
                "clinical_reason": ex.clinical_reasons or ""
            })
    #3 A3_algorithms
    safe_pool = [ex for ex in exercise_pool if is_exercise_safe(ex, conditions)]
    if not safe_pool:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, detail = "Không tìm thấy bài tập nào an toàn với tình trạng sức khỏe hiện tại."
        )
    #4 A4_algorithms
    plan_data = generate_weekly_workout_schedule(
        available_days = available_days,
        session_duration_mins = duration_mins,
        safe_pool = safe_pool,
        fitness_goal = goal,
        fitness_level=  level
    )

    if "error" in plan_data:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST, detail = plan_data["error"]

        )
    #5 Luu vao db
    existing_plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).first()
    if existing_plan:
        existing_plan.split_type = plan_data["split_type"]
        existing_plan.schedule_json = plan_data["weekly_schedule"]
    else:
        new_plan = WorkoutPlan(
            user_id = current_user.id,
            split_type = plan_data["split_type"],
            schedule_json = plan_data["weekly_schedule"]
        )
        db.add(new_plan)
    db.commit()

    return {
        "status": "success",
        "message": "Đã tạo và lưu lịch tập thành công!",
        "user_profile": {
            "email": current_user.email,
            "fitness_level": level,
            "fitness_goal": goal,
            "medical_conditions": conditions
        },
        "workout_plan": plan_data
    }

#API_02: GET
@router.get("/plan", summary="Lấy lịch tập hiện hành của người dùng")
def get_user_workout_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Frontend gọi API này khi người dùng vào trang lịch tập
    """
    plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).first()

    if not plan:
        return {
            "has_plan": False,
            "message": "Người dùng chưa tạo lịch tập. Hãy bấm 'Sinh lịch tập' để bắt đầu.",
            "workout_plan": None
        }

    return {
        "has_plan": True,
        "split_type": plan.split_type,
        "created_at": plan.created_at,
        "workout_plan": {
            "split_type": plan.split_type,
            "total_sessions": len(plan.schedule_json or []),
            "weekly_schedule": plan.schedule_json
        }
    }