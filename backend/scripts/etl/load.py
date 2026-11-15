"""
Bước 4 (Load): Nạp dữ liệu đã chuẩn hóa vào Database của App (SQLite hoặc PostgreSQL)
thông qua SQLAlchemy ORM (`init_db()` + `SessionLocal`).
"""

from typing import Any, Type

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, init_db
from app.models import Exercise, Food


def _bulk_upsert_foods(
    db: Session,
    records: list[dict[str, Any]],
    *,
    replace: bool = True,
) -> tuple[int, int]:
    """Upsert danh sách thực phẩm theo cột `code`."""
    if not records:
        return 0, 0

    existing_map: dict[str, Food] = {
        obj.code: obj
        for obj in db.query(Food).all()
        if obj.code
    }
    new_codes: set[str] = set()
    created = 0
    updated = 0

    for item in records:
        code = item.get("code")
        if not code:
            continue
        clean_fields = {
            k: v for k, v in item.items()
            if hasattr(Food, k) and k not in ("id", "code")
        }
        obj = existing_map.get(code)
        if obj is None:
            obj = Food(code=code, **clean_fields)
            db.add(obj)
            existing_map[code] = obj
            new_codes.add(code)
            created += 1
        elif replace:
            for k, v in clean_fields.items():
                setattr(obj, k, v)
            if code not in new_codes:
                updated += 1

    return created, updated


def _bulk_upsert_exercises(
    db: Session,
    records: list[dict[str, Any]],
    *,
    replace: bool = True,
) -> tuple[int, int]:
    """Upsert danh sách bài tập theo cột `name_en`."""
    if not records:
        return 0, 0

    existing_map: dict[str, Exercise] = {
        obj.name_en: obj
        for obj in db.query(Exercise).all()
        if obj.name_en
    }
    created = 0
    updated = 0

    for item in records:
        name_en = item.get("name_en")
        if not name_en:
            continue
        clean_fields = {
            k: v for k, v in item.items()
            if hasattr(Exercise, k) and k != "id"
        }
        obj = existing_map.get(name_en)
        if obj is None:
            obj = Exercise(**clean_fields)
            db.add(obj)
            existing_map[name_en] = obj
            created += 1
        elif replace:
            for k, v in clean_fields.items():
                setattr(obj, k, v)
            updated += 1

    return created, updated


def load_exercises(records: list[dict[str, Any]], *, replace: bool = True) -> tuple[int, int]:
    """Sinh bảng nếu chưa có và nạp danh sách bài tập đã chuẩn hóa vào DB qua ORM."""
    init_db()
    db = SessionLocal()
    try:
        created, updated = _bulk_upsert_exercises(db, records, replace=replace)
        db.commit()
        return created, updated
    finally:
        db.close()


def load_foods(records: list[dict[str, Any]], *, replace: bool = True) -> tuple[int, int]:
    """Sinh bảng nếu chưa có và nạp danh sách thực phẩm đã chuẩn hóa vào DB qua ORM."""
    init_db()
    db = SessionLocal()
    try:
        created, updated = _bulk_upsert_foods(db, records, replace=replace)
        db.commit()
        return created, updated
    finally:
        db.close()
