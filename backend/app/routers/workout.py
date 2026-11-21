"""
    Router: workout.py
    Manage APIs for workout-related operations: Generate automatically plan(A3+A4), swap exercises, and save workout logs.
    """

    from copy import deepcopy
    from typing import Any, Dict, Optional

    from fastapi import APIRouter, Depends, HTTPException, status
    from pydantic import BaseModel, Field
    from sqlalchemy.orm import Session
    from sqlalchemy.orm.attributes import flag_modified

    from app.algorithms.workout_generator import (
        generate_weekly_workout_schedule,
        is_exercise_safe,
    )
    from app.database import get_db
    from app.dependencies import get_current_user
    from app.models.exercise import Exercise
    from app.models.user import User
    from app.models.workout import WorkoutPlan

    router = APIRouter(prefix="/api/workout", tags=["Workout"])


    class SwapExerciseRequest(BaseModel):
        day: str = Field(..., description="Ngày trong tuần, ví dụ: Mon, Tue, Wed...")
        exercise_index: int = Field(..., ge=0, description="Vị trí (index) bài tập trong buổi cần thay đổi")
        new_exercise_id: int = Field(..., gt=0, description="ID bài tập mới muốn thay thế")


    def _compute_intensity_warning(
        fitness_level: Optional[str],
        intensity_level: Optional[str],
    ) -> Optional[Dict[str, str]]:
        """
        Evaluate intensity mismatch warning when a user swaps an exercise:
        - beginner + Vigorous -> red warning ("danger")
        - experienced / advanced + Light -> green notice ("easy")
        """
        level = (fitness_level or "beginner").strip().lower()
        intensity = (intensity_level or "Moderate").strip().lower()

        if level == "beginner" and intensity == "vigorous":
            return {
                "type": "danger",
                "label": "Cảnh báo: Cường độ cao",
                "message": "Bài tập cường độ cao (Vigorous) có thể quá sức với người mới. Hãy ưu tiên mức tạ nhẹ và giữ chuẩn kỹ thuật.",
            }

        if level in ("experienced", "advanced") and intensity == "light":
            return {
                "type": "easy",
                "label": "Cường độ nhẹ",
                "message": "Bài tập cường độ nhẹ (Light) so với trình độ hiện tại. Phù hợp để phục hồi hoặc tăng số lần lặp.",
            }

        return None


    def _enrich_schedule_intensity(
        schedule: Any,
        db: Session,
    ) -> Any:
        """Backfill intensity_level from Exercise table for legacy saved plans."""
        if not isinstance(schedule, list) or not schedule:
            return schedule

        missing_ids = set()
        for session in schedule:
            for ex in session.get("exercises", []):
                if not ex.get("intensity_level") and ex.get("exercise_id") is not None:
                    try:
                        missing_ids.add(int(ex["exercise_id"]))
                    except (TypeError, ValueError):
                        pass

        if not missing_ids:
            return schedule

        intensity_map = {
            str(row.id): (row.intensity_level or "Moderate")
            for row in db.query(Exercise.id, Exercise.intensity_level)
            .filter(Exercise.id.in_(missing_ids))
            .all()
        }

        enriched = deepcopy(schedule)
        for session in enriched:
            for ex in session.get("exercises", []):
                if not ex.get("intensity_level"):
                    ex_id = str(ex.get("exercise_id", ""))
                    ex["intensity_level"] = intensity_map.get(ex_id, "Moderate")
        return enriched


    # API_01: POST
    @router.post("/generate", summary="Automaticly generate personalized weekly plan")
    def generate_workout_plan(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Dict[str, Any]:

        # 1. Onboarding check thong tin nguoi dung
        available_days = current_user.available_days or ["Mon", "Wed", "Fri"]
        duration_mins = current_user.session_duration_mins or 45
        goal = current_user.fitness_goal or "general_fitness"
        level = current_user.fitness_level or "beginner"
        conditions = current_user.medical_conditions or []

        # Validate chặt chẽ số ngày tập theo chu kỳ phục hồi sinh lý (chỉ chấp nhận 3, 4 hoặc 6 ngày)
        if len(available_days) not in [3, 4, 6]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Số ngày tập không hợp lệ ({len(available_days)} ngày). Hệ thống chỉ hỗ trợ 3 ngày (Full Body), 4 ngày (Upper/Lower) hoặc 6 ngày
                (Push/Pull/Legs).",
            )

        # 2. Truy van ex tu db
        exercise_in_db = db.query(Exercise).all()
        if not exercise_in_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kho bài tập rỗng. Vui lòng chạy seed_database.py trước",
            )

        # Chuyen tu SQLAlchemy object sang Dict de chay thuat toan
        exercise_pool = []
        for ex in exercise_in_db:
            if ex.target_muscle:
                exercise_pool.append({
                    "id": str(ex.id),
                    "name": ex.name_vi or ex.name_en,
                    "target_muscle": ex.target_muscle,
                    "intensity_level": ex.intensity_level or "Moderate",
                    "secondary_muscles": ex.secondary_muscle or [],
                    "banned_for": ex.banned_for or [],
                    "clinical_reason": ex.clinical_reasons or "",
                })

        # 3. A3_algorithms
        safe_pool = [ex for ex in exercise_pool if is_exercise_safe(ex, conditions)]
        if not safe_pool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tìm thấy bài tập nào an toàn với tình trạng sức khỏe hiện tại.",
            )

        # 4. A4_algorithms
        plan_data = generate_weekly_workout_schedule(
            available_days=available_days,
            session_duration_mins=duration_mins,
            safe_pool=safe_pool,
            fitness_goal=goal,
            fitness_level=level,
        )

        if "error" in plan_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=plan_data["error"],
            )

        # 5. Luu vao db
        existing_plan = (
            db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).first()
        )
        if existing_plan:
            existing_plan.split_type = plan_data["split_type"]
            existing_plan.schedule_json = plan_data["weekly_schedule"]
            flag_modified(existing_plan, "schedule_json")
        else:
            new_plan = WorkoutPlan(
                user_id=current_user.id,
                split_type=plan_data["split_type"],
                schedule_json=plan_data["weekly_schedule"],
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
                "medical_conditions": conditions,
            },
            "workout_plan": plan_data,
        }
    
    
    # API_02: GET
    @router.get("/plan", summary="Lấy lịch tập hiện hành của người dùng")
    def get_user_workout_plan(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Dict[str, Any]:
        """
        Frontend gọi API này khi người dùng vào trang lịch tập
        """
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).first()
    
        if not plan:
            return {
                "has_plan": False,
                "message": "Người dùng chưa tạo lịch tập. Hãy bấm 'Sinh lịch tập' để bắt đầu.",
                "workout_plan": None,
            }
    
        weekly_schedule = _enrich_schedule_intensity(plan.schedule_json or [], db)
    
        return {
            "has_plan": True,
            "split_type": plan.split_type,
            "created_at": plan.updated_at or plan.created_at,
            "workout_plan": {
                "split_type": plan.split_type,
                "total_sessions": len(weekly_schedule),
                "weekly_schedule": weekly_schedule,
            },
        }
    
    
    # API_03: PATCH
    @router.patch(
        "/plan/swap-exercise",
        summary="Thay đổi một bài tập trong lịch tập theo nhóm cơ chính",
    )
    def swap_workout_exercise(
        payload: SwapExerciseRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> Dict[str, Any]:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == current_user.id).first()
        if not plan or not plan.schedule_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chưa có lịch tập để chỉnh sửa. Vui lòng tạo lịch tập trước.",
            )
    
        schedule = deepcopy(plan.schedule_json)
        target_session = next(
            (s for s in schedule if str(s.get("day", "")).lower() == payload.day.strip().lower()),
            None,
        )
        if not target_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy buổi tập vào ngày '{payload.day}'.",
            )
    
        exercises_in_session = target_session.get("exercises") or []
        if payload.exercise_index < 0 or payload.exercise_index >= len(exercises_in_session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vị trí bài tập cần thay đổi không hợp lệ.",
            )
    
        old_entry = exercises_in_session[payload.exercise_index]
        new_ex = db.query(Exercise).filter(Exercise.id == payload.new_exercise_id).first()
        if not new_ex:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy bài tập thay thế trong kho dữ liệu.",
            )
    
        old_muscle = (old_entry.get("target_muscle") or "").strip().lower()
        new_muscle = (new_ex.target_muscle or "").strip().lower()
        if old_muscle and new_muscle != old_muscle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bài tập thay thế phải tác động vào cùng nhóm cơ chính với bài tập hiện tại.",
            )
    
        conditions = current_user.medical_conditions or []
        if not is_exercise_safe({"banned_for": new_ex.banned_for or []}, conditions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bài tập này không an toàn với tình trạng bệnh nền của bạn.",
            )
    
        new_id_str = str(new_ex.id)
        for idx, item in enumerate(exercises_in_session):
            if idx != payload.exercise_index and str(item.get("exercise_id")) == new_id_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Bài tập này đã tồn tại trong buổi tập hôm nay.",
                )
    
        new_intensity = new_ex.intensity_level or "Moderate"
        warning = _compute_intensity_warning(current_user.fitness_level, new_intensity)

        updated_entry = {
            **old_entry,
            "exercise_id": new_id_str,
            "name": new_ex.name_vi or new_ex.name_en,
            "target_muscle": new_ex.target_muscle or old_entry.get("target_muscle"),
            "intensity_level": new_intensity,
            "is_swapped": True,
            "intensity_warning": warning,
        }
        exercises_in_session[payload.exercise_index] = updated_entry
        target_session["exercises"] = exercises_in_session

        plan.schedule_json = schedule
        flag_modified(plan, "schedule_json")
        db.commit()
        db.refresh(plan)

        return {
            "status": "success",
            "message": "Đã thay đổi bài tập thành công!",
            "swapped_exercise": updated_entry,
            "workout_plan": {
                "split_type": plan.split_type,
                "total_sessions": len(schedule),
                "weekly_schedule": schedule,
            },
        }