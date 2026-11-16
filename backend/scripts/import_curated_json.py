"""
import_curated_json.py
Xóa sạch dữ liệu thực phẩm, bài tập và các kế hoạch/nhật ký phụ thuộc cũ,
sau đó nạp mới toàn bộ từ:
- backend/data/vietnam_foods_curated.json
- backend/data/exercises_65.json

Cách chạy (từ thư mục backend/):
    .venv/bin/python -m scripts.import_curated_json
    .venv/bin/python -m scripts.import_curated_json --reset-users   # nếu muốn xóa cả bảng users
"""

import argparse
import json
from pathlib import Path

from sqlalchemy import text

from app.database import DATABASE_URL, SessionLocal, init_db
from app.models.exercise import Exercise
from app.models.food import Food
from app.models.meal import FoodLog, MealPlan, MealPlanItem
from app.models.user import User
from app.models.workout import WorkoutLog, WorkoutPlan

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FOODS_JSON = DATA_DIR / "vietnam_foods_curated.json"
EXERCISES_JSON = DATA_DIR / "exercises_65.json"


def reset_and_import(reset_users: bool = False) -> None:
    """Clear old catalog/plan/log rows and seed foods & exercises from curated JSON files."""
    if not FOODS_JSON.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {FOODS_JSON}")
    if not EXERCISES_JSON.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {EXERCISES_JSON}")

    foods_data = json.loads(FOODS_JSON.read_text(encoding="utf-8"))
    exercises_data = json.loads(EXERCISES_JSON.read_text(encoding="utf-8"))

    init_db()
    db = SessionLocal()
    try:
        # Xóa bảng phụ thuộc trước để không vướng khóa ngoại RESTRICT
        db.query(MealPlanItem).delete()
        db.query(MealPlan).delete()
        db.query(FoodLog).delete()
        db.query(WorkoutLog).delete()
        db.query(WorkoutPlan).delete()
        db.query(Food).delete()
        db.query(Exercise).delete()

        reset_tables = [
            "meal_plan_items",
            "meal_plans",
            "food_logs",
            "workout_logs",
            "workout_plans",
            "foods",
            "exercises",
        ]
        if reset_users:
            db.query(User).delete()
            reset_tables.append("users")

        db.flush()

        # Đặt lại bộ đếm autoincrement trên SQLite (nếu bảng sqlite_sequence tồn tại)
        if DATABASE_URL.startswith("sqlite"):
            placeholders = ", ".join(f"'{name}'" for name in reset_tables)
            try:
                db.execute(text(f"DELETE FROM sqlite_sequence WHERE name IN ({placeholders})"))
            except Exception:
                pass

        for item in foods_data:
            db.add(Food(**item))

        for item in exercises_data:
            fields = dict(item)
            fields.pop("id", None)
            fields.pop("met_value", None)
            db.add(Exercise(**fields))

        db.commit()

        food_count = db.query(Food).count()
        exercise_count = db.query(Exercise).count()
        user_count = db.query(User).count()
        print(f"[SUCCESS] Đã reset dữ liệu cũ tại: {DATABASE_URL}")
        print(f"  - foods: {food_count} bản ghi")
        print(f"  - exercises: {exercise_count} bản ghi")
        print(f"  - users giữ lại: {user_count} tài khoản")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset catalog & import curated JSON datasets.")
    parser.add_argument(
        "--reset-users",
        action="store_true",
        help="Xóa luôn toàn bộ dữ liệu trong bảng users.",
    )
    args = parser.parse_args()
    reset_and_import(reset_users=args.reset_users)
