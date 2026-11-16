from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from app.algorithms.workout_generator import is_exercise_safe
from app.database import get_db
from app.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.user import User

router = APIRouter(prefix="/api/exercises", tags=["Exercises"])


def _serialize_exercise(ex: Exercise, medical_conditions: List[str]) -> Dict[str, Any]:
    """Serialize an Exercise ORM object with user medical safety status."""
    banned_for = ex.banned_for or []
    is_safe = is_exercise_safe({"banned_for": banned_for}, medical_conditions)
    return {
        "id": ex.id,
        "name_en": ex.name_en,
        "name_vi": ex.name_vi,
        "category": ex.category,
        "target_muscle": ex.target_muscle,
        "secondary_muscle": ex.secondary_muscle or [],
        "intensity_level": ex.intensity_level,
        "description": ex.description,
        "equipment": ex.equipment,
        "instructions": ex.instructions or [],
        "common_mistakes": ex.common_mistakes or [],
        "image": ex.image,
        "video_url": ex.video_url,
        "banned_for": banned_for,
        "clinical_reasons": ex.clinical_reasons,
        "source": ex.source,
        "is_safe_for_user": is_safe,
    }


@router.get("", summary="Tra cứu danh sách và bộ lọc kho bài tập")
def list_exercises(
    q: Optional[str] = Query(default=None, description="Từ khóa tìm kiếm theo tên hoặc mô tả"),
    target_muscle: Optional[str] = Query(default=None, description="Lọc theo nhóm cơ chính"),
    intensity_level: Optional[str] = Query(default=None, description="Light | Moderate | Vigorous"),
    safe_only: bool = Query(default=False, description="Chỉ lấy bài an toàn với bệnh nền của người dùng"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    query = db.query(Exercise).filter(Exercise.target_muscle.isnot(None))

    if target_muscle and target_muscle.upper() != "ALL":
        query = query.filter(Exercise.target_muscle.ilike(target_muscle.strip()))

    if intensity_level and intensity_level.upper() != "ALL":
        query = query.filter(Exercise.intensity_level.ilike(intensity_level.strip()))

    if q and q.strip():
        pattern = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Exercise.name_en.ilike(pattern),
                Exercise.name_vi.ilike(pattern),
                Exercise.category.ilike(pattern),
                Exercise.target_muscle.ilike(pattern),
                Exercise.equipment.ilike(pattern),
                Exercise.description.ilike(pattern),
            )
        )

    rows = query.order_by(Exercise.target_muscle.asc(), Exercise.id.asc()).all()
    conditions = current_user.medical_conditions or []

    items = [_serialize_exercise(ex, conditions) for ex in rows]
    if safe_only:
        items = [item for item in items if item["is_safe_for_user"]]

    muscles = sorted(
        {
            r[0]
            for r in db.query(Exercise.target_muscle)
            .filter(Exercise.target_muscle.isnot(None))
            .distinct()
            .all()
            if r[0]
        }
    )

    return {
        "total": len(items),
        "muscles": muscles,
        "exercises": items,
    }


@router.get("/{exercise_id}", summary="Xem chi tiết một bài tập theo ID")
def get_exercise_detail(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bài tập yêu cầu.",
        )
    conditions = current_user.medical_conditions or []
    return _serialize_exercise(ex, conditions)
