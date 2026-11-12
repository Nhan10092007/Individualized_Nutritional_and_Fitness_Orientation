"""
common.py
Tiện ích dùng chung cho các script nạp dữ liệu (seed) bằng SQLAlchemy ORM.

Chạy các script từ thư mục backend/ dưới dạng module, ví dụ:
    python -m scripts.seed_database
"""

from typing import Type, TypeVar

from sqlalchemy.orm import Session

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def upsert_by_code(db: Session, model: Type[ModelT], code: str, *, replace: bool = True, **fields) -> ModelT:
    """
    Tương đương INSERT OR REPLACE / INSERT OR IGNORE theo cột `code`:
    - Chưa có bản ghi với code này  -> tạo mới.
    - Đã có và replace=True         -> cập nhật các trường (INSERT OR REPLACE).
    - Đã có và replace=False        -> giữ nguyên (INSERT OR IGNORE).
    """
    obj = db.query(model).filter_by(code=code).one_or_none()
    if obj is None:
        obj = model(code=code, **fields)
        db.add(obj)
        db.flush()
    elif replace:
        for key, value in fields.items():
            setattr(obj, key, value)
    return obj
