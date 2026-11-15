"""
Package ETL chuẩn 4 bước:
1. Extract (extract.py): Tải file raw từ GitHub/URL hoặc đọc từ backend/data/raw/
2. Asset Handling (asset_handler.py): Tải & ánh xạ Ảnh/GIF/Video lên S3 / Cloudinary / CDN
3. Transform & Map MET (transform.py): Chuẩn hóa theo Schema Exercise ORM + gắn chỉ số MET & nhãn A3
4. Load (load.py): Nạp vào Database (SQLite / PostgreSQL) thông qua SQLAlchemy ORM
"""

from scripts.etl.asset_handler import AssetHandler
from scripts.etl.extract import (
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
    VIETNAM_FCT_2017_PDF_NAME,
    VIETNAM_FCT_2017_PDF_PATH,
    check_vietnam_fct_2017_pdf,
    download_file,
    extract_compendium_csv,
    extract_exercises_json,
    extract_kaggle_exercise_csv,
    extract_megagym_csv,
)
from scripts.etl.load import load_exercises, load_foods
from scripts.etl.transform import (
    infer_clinical_tags,
    intensity_from_met,
    map_met_for_exercise,
    transform_compendium_rows,
    transform_exercises_json,
    transform_kaggle_rows,
    transform_megagym_rows,
)

__all__ = [
    "RAW_DATA_DIR",
    "PROCESSED_DATA_DIR",
    "VIETNAM_FCT_2017_PDF_NAME",
    "VIETNAM_FCT_2017_PDF_PATH",
    "check_vietnam_fct_2017_pdf",
    "AssetHandler",
    "download_file",
    "extract_compendium_csv",
    "extract_exercises_json",
    "extract_kaggle_exercise_csv",
    "extract_megagym_csv",
    "infer_clinical_tags",
    "intensity_from_met",
    "map_met_for_exercise",
    "transform_compendium_rows",
    "transform_exercises_json",
    "transform_kaggle_rows",
    "transform_megagym_rows",
    "load_exercises",
    "load_foods",
]
