"""
import_kaggle_github.py
ETL Tool: Nhập khẩu dữ liệu bài tập từ các file raw (CSV/JSON) trong backend/data/raw/:
1. GitHub free-exercise-db (`exercises.json`)
2. GitHub Compendium of Physical Activities (`compendium_github.csv`)
3. Kaggle `exercise_dataset.csv`
4. Kaggle `megaGymDataset.csv` (tùy chọn)

Cách chạy (từ thư mục backend/):  python -m scripts.import_kaggle_github
Dữ liệu được chuẩn hóa và ghi qua SQLAlchemy ORM (`scripts.etl`).
"""

from scripts.etl import (
    RAW_DATA_DIR,
    AssetHandler,
    extract_compendium_csv,
    extract_exercises_json,
    extract_kaggle_exercise_csv,
    extract_megagym_csv,
    load_exercises,
    transform_compendium_rows,
    transform_exercises_json,
    transform_kaggle_rows,
    transform_megagym_rows,
)


def import_github_exercises_json(json_path: str | None = None, *, replace: bool = True) -> tuple[int, int]:
    """Extract -> Asset Handling -> Transform & Map MET -> Load cho exercises.json."""
    raw_items = extract_exercises_json(json_path)
    records = transform_exercises_json(raw_items, asset_handler=AssetHandler())
    created, updated = load_exercises(records, replace=replace)
    print(f"[+] exercises.json: tạo mới {created}, cập nhật {updated} bản ghi.")
    return created, updated


def import_github_compendium_csv(csv_path: str | None = None, *, replace: bool = False) -> tuple[int, int]:
    """Extract -> Transform -> Load cho compendium_github.csv (hỗ trợ delimiter '|')."""
    raw_rows = extract_compendium_csv(csv_path)
    records = transform_compendium_rows(raw_rows)
    created, updated = load_exercises(records, replace=replace)
    print(f"[+] Compendium CSV: tạo mới {created}, cập nhật {updated} bản ghi.")
    return created, updated


def import_kaggle_exercise_csv(csv_path: str | None = None, *, replace: bool = False) -> tuple[int, int]:
    """Extract -> Transform & Map MET -> Load cho Kaggle exercise_dataset.csv."""
    raw_rows = extract_kaggle_exercise_csv(csv_path)
    records = transform_kaggle_rows(raw_rows)
    created, updated = load_exercises(records, replace=replace)
    print(f"[+] Kaggle exercise_dataset.csv: tạo mới {created}, cập nhật {updated} bản ghi.")
    return created, updated


def import_megagym_csv(csv_path: str | None = None, *, replace: bool = False) -> tuple[int, int]:
    """Extract -> Transform & Map MET -> Load cho Kaggle megaGymDataset.csv."""
    raw_rows = extract_megagym_csv(csv_path)
    records = transform_megagym_rows(raw_rows)
    created, updated = load_exercises(records, replace=replace)
    print(f"[+] Kaggle megaGymDataset.csv: tạo mới {created}, cập nhật {updated} bản ghi.")
    return created, updated


if __name__ == "__main__":
    print(f"[*] Nạp dữ liệu bài tập từ thư mục raw: {RAW_DATA_DIR}")
    import_github_exercises_json()
    import_github_compendium_csv()
    import_kaggle_exercise_csv()
