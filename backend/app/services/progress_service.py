"""
progress_service.py
Các truy vấn tổng hợp tiến độ.

get_daily_energy_balance() thay thế cho VIEW `v_daily_energy_balance` trước đây trong schema.sql
(ORM không tạo VIEW, nên tổng hợp bằng truy vấn SQLAlchemy + ghép kết quả bằng Python).
"""

from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Query, Session

from app.models import FoodLog, WorkoutLog


def _apply_filters(q: Query, model, user_id, start_date, end_date) -> Query:
    if user_id is not None:
        q = q.filter(model.user_id == user_id)
    if start_date is not None:
        q = q.filter(model.logged_date >= start_date)
    if end_date is not None:
        q = q.filter(model.logged_date <= end_date)
    return q.group_by(model.user_id, model.logged_date)


def get_daily_energy_balance(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[dict]:
    """Tổng hợp Calo IN / Calo BURN / Net Calo theo (user_id, ngày)."""
    food_q = _apply_filters(
        db.query(
            FoodLog.user_id,
            FoodLog.logged_date,
            func.sum(FoodLog.calculated_calories),
            func.sum(FoodLog.calculated_protein),
            func.sum(FoodLog.calculated_fat),
            func.sum(FoodLog.calculated_carbs),
        ),
        FoodLog, user_id, start_date, end_date,
    )
    workout_q = _apply_filters(
        db.query(
            WorkoutLog.user_id,
            WorkoutLog.logged_date,
            func.sum(WorkoutLog.calories_burned),
            func.sum(WorkoutLog.total_duration_minutes),
        ),
        WorkoutLog, user_id, start_date, end_date,
    )

    balance: dict[tuple[int, date], dict] = {}

    def _row(uid: int, d: date) -> dict:
        return balance.setdefault((uid, d), {
            "user_id": uid,
            "log_date": d,
            "total_calories_in": 0.0,
            "total_protein_g": 0.0,
            "total_fat_g": 0.0,
            "total_carbs_g": 0.0,
            "total_calories_burned": 0.0,
            "total_workout_minutes": 0.0,
        })

    for uid, d, cal, protein, fat, carbs in food_q.all():
        r = _row(uid, d)
        r["total_calories_in"] = round(cal or 0.0, 2)
        r["total_protein_g"] = round(protein or 0.0, 2)
        r["total_fat_g"] = round(fat or 0.0, 2)
        r["total_carbs_g"] = round(carbs or 0.0, 2)

    for uid, d, burned, minutes in workout_q.all():
        r = _row(uid, d)
        r["total_calories_burned"] = round(burned or 0.0, 2)
        r["total_workout_minutes"] = round(minutes or 0.0, 2)

    result = sorted(balance.values(), key=lambda r: (r["user_id"], r["log_date"]))
    for r in result:
        r["net_calories"] = round(r["total_calories_in"] - r["total_calories_burned"], 2)
    return result
