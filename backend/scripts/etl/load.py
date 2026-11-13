"""
Bước 4 (Load): Nạp dữ liệu đã chuẩn hóa vào Database của App (SQLite hoặc PostgreSQL)
thông qua SQLAlchemy ORM (`init_db()` + `SessionLocal`).
"""

from typing import Any, Type

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, init_db
from app.models import Exercise, Food


def _bulk_upsert_by_code(
    db: Session,
    model: Type[Base],
    records: list[dict[str, Any]],
    *,
    replace: bool = True,
) -> tuple[int, int]:
    """Upsert hàng loạt theo cột `code`, trả về (số_tạo_mới, số_cập_nhật)."""
    if not records:
        return 0, 0

    existing_map: dict[str, Any] = {
        code: obj
        for obj in db.query(model).all()
        if (code := getattr(obj, "code", None))
    }
    new_codes: set[str] = set()
    created = 0
    updated = 0

    for item in records:
        code = item.get("code")
        if not code:
            continue
        fields = {k: v for k, v in item.items() if k != "code"}
        obj = existing_map.get(code)
        if obj is None:
            obj = model(code=code, **fields)
            db.add(obj)
            existing_map[code] = obj
            new_codes.add(code)
            created += 1
        elif replace:
            for k, v in fields.items():
                setattr(obj, k, v)
            if code not in new_codes:
                updated += 1

    return created, updated


def load_exercises(records: list[dict[str, Any]], *, replace: bool = True) -> tuple[int, int]:
    """Sinh bảng nếu chưa có và nạp danh sách bài tập đã chuẩn hóa vào DB qua ORM."""
    init_db()
    db = SessionLocal()
    try:
        created, updated = _bulk_upsert_by_code(db, Exercise, records, replace=replace)
        db.commit()
        return created, updated
    finally:
        db.close()


def load_foods(records: list[dict[str, Any]], *, replace: bool = True) -> tuple[int, int]:
    """Sinh bảng nếu chưa có và nạp danh sách thực phẩm đã chuẩn hóa vào DB qua ORM."""
    init_db()
    db = SessionLocal()
    try:
        created, updated = _bulk_upsert_by_code(db, Food, records, replace=replace)
        db.commit()
        return created, updated
    finally:
        db.close()

