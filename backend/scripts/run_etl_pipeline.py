"""
run_etl_pipeline.py
=============================================================================
Pipeline ETL chuẩn 4 bước đồng bộ với kiến trúc SQLAlchemy ORM:
  (1. Extract)         Đọc / tải file raw từ backend/data/raw/ hoặc GitHub
  (2. Asset Handling)  Xử lý URL Ảnh/GIF/Video (CDN mặc định, hoặc upload S3 / Cloudinary)
  (3. Transform & MET) Chuẩn hóa Schema Exercise + map chỉ số MET + gắn nhãn A3
  (4. Load)            Sinh bảng từ ORM Models và nạp vào DB (SQLite / PostgreSQL)

Cách chạy (từ thư mục backend/):
  python -m scripts.run_etl_pipeline
  python -m scripts.run_etl_pipeline --upload-assets --provider cloudinary
  python -m scripts.run_etl_pipeline --include-megagym --download-missing
=============================================================================
"""

import argparse

from app.database import DATABASE_URL, SessionLocal, init_db
from scripts.etl import (
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
from scripts.seed_database import seed_foods, seed_sample_user_and_logs


def run_pipeline(
    *,
    download_missing: bool = False,
    upload_assets: bool = False,
    provider: str | None = None,
    include_megagym: bool = False,
    seed_core: bool = True,
) -> None:
    print("=" * 72)
    print(" CHẠY ETL PIPELINE 4 BƯỚC (EXTRACT -> ASSET -> TRANSFORM & MET -> LOAD)")
    print(f" Target Database: {DATABASE_URL}")
    print("=" * 72)

    if seed_core:
        init_db()
        db = SessionLocal()
        try:
            seed_foods(db)
        finally:
            db.close()

    print("\n[1/4] EXTRACT: Đọc dữ liệu thô từ backend/data/raw/...")
    raw_exdb = extract_exercises_json(download_if_missing=download_missing)
    raw_compendium = extract_compendium_csv(download_if_missing=download_missing)
    raw_kaggle = extract_kaggle_exercise_csv()
    raw_megagym = extract_megagym_csv() if include_megagym else []
    print(
        f"      -> exercises.json: {len(raw_exdb)} | compendium: {len(raw_compendium)} "
        f"| kaggle: {len(raw_kaggle)} | megagym: {len(raw_megagym)}"
    )

    asset_handler = AssetHandler(provider=provider, upload_enabled=upload_assets)
    print(
        f"\n[2/4] ASSET HANDLING: provider='{asset_handler.provider}' "
        f"(upload={'ON' if upload_assets else 'URL-mapping'})"
    )
    print("[3/4] TRANSFORM & MAP MET: Chuẩn hóa Schema ORM + gán MET + nhãn y khoa A3...")

    transformed_records = []
    transformed_records.extend(transform_exercises_json(raw_exdb, asset_handler=asset_handler))
    transformed_records.extend(transform_compendium_rows(raw_compendium))
    transformed_records.extend(transform_kaggle_rows(raw_kaggle))
    if include_megagym:
        transformed_records.extend(transform_megagym_rows(raw_megagym))
    print(f"      -> Tổng số bản ghi bài tập sau Transform: {len(transformed_records)}")

    print("\n[4/4] LOAD: Ghi dữ liệu vào Database qua SQLAlchemy ORM...")
    created, updated = load_exercises(transformed_records, replace=True)
    print(f"      -> Bài tập: tạo mới {created}, cập nhật {updated}")

    if seed_core:
        db = SessionLocal()
        try:
            seed_sample_user_and_logs(db)
        finally:
            db.close()

    print("\n" + "=" * 72)
    print(" HOÀN TẤT ETL PIPELINE 4 BƯỚC!")
    print("=" * 72)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chạy ETL Pipeline 4 bước vào SQLAlchemy ORM Database.")
    parser.add_argument("--download-missing", action="store_true", help="Tải từ GitHub nếu thiếu file raw local")
    parser.add_argument("--upload-assets", action="store_true", help="Upload ảnh/GIF/video lên S3/Cloudinary")
    parser.add_argument("--provider", choices=["github_cdn", "cloudinary", "s3"], default=None, help="Nơi lưu asset")
    parser.add_argument("--include-megagym", action="store_true", help="Nạp thêm megaGymDataset.csv (2900+ dòng)")
    parser.add_argument("--skip-core-seed", action="store_true", help="Bỏ qua nạp thực phẩm & user mẫu")
    args = parser.parse_args()

    run_pipeline(
        download_missing=args.download_missing,
        upload_assets=args.upload_assets,
        provider=args.provider,
        include_megagym=args.include_megagym,
        seed_core=not args.skip_core_seed,
    )


if __name__ == "__main__":
    main()
