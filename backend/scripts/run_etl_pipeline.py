"""
run_etl_pipeline.py
=============================================================================
Pipeline ETL chuẩn 4 bước đồng bộ với kiến trúc SQLAlchemy ORM:
  (1. Extract)         Trích xuất PDF dinh dưỡng 2017 & đúng 65 bài tập từ exercises.json
  (2. Asset Handling)  Xử lý URL Ảnh/GIF/Video (CDN mặc định, hoặc upload S3 / Cloudinary)
  (3. Transform & MET) Chuẩn hóa Schema Exercise đúng hình thiết kế + gán MET + nhãn A3
  (4. Load)            Sinh bảng từ ORM Models và nạp vào DB (SQLite / PostgreSQL)

Cách chạy (từ thư mục backend/):
  python -m scripts.run_etl_pipeline
=============================================================================
"""

import argparse
import json

from app.database import DATABASE_URL, SessionLocal, init_db
from app.models import Exercise, Food
from scripts.etl.build_65_exercises import build_65_exercises
from scripts.etl.build_curated_foods import build_curated_foods
from scripts.etl.crawl_bhx_prices import crawl_bhx_food_prices
from scripts.etl.extract_pdf_foods import extract_pdf_foods
from scripts.seed_database import seed_exercises, seed_foods, seed_sample_user_and_logs


def run_pipeline(
    *,
    download_missing: bool = False,
    upload_assets: bool = False,
    provider: str | None = None,
    seed_core: bool = True,
) -> None:
    print("=" * 72)
    print(" CHẠY ETL PIPELINE (PDF 2017 FOODS + 65 BÀI TẬP TỪ EXERCISES.JSON)")
    print(f" Target Database: {DATABASE_URL}")
    print("=" * 72)

    init_db()
    db = SessionLocal()
    try:
        print("\n[1/4] EXTRACT & CRAWL:")
        print("      -> Crawl giá thực tế từ Bách Hóa Xanh (bachhoaxanh.com)...")
        crawl_bhx_food_prices()
        print("      -> Chuẩn hóa danh mục thực phẩm quen thuộc (Viện Dinh Dưỡng 2017 + USDA + Giá BHX)...")
        curated_foods = build_curated_foods()
        print(f"         + Đã chuẩn hóa {len(curated_foods)} thực phẩm quen thuộc kèm giá Bách Hóa Xanh.")

        print("      -> Trích xuất 65 bài tập chọn lọc từ backend/data/raw/exercises.json...")
        exercises_65 = build_65_exercises()
        print(f"         + Đã trích xuất và chuẩn hóa đúng {len(exercises_65)} bài tập.")

        print("\n[2/4] ASSET HANDLING:")
        print("      -> Gắn URL ảnh bài tập trực tiếp từ CDN GitHub (không cần key cloud).")

        print("\n[3/4] TRANSFORM & MAP MET:")
        print("      -> Ánh xạ đầy đủ nhóm cơ (Chest, Back, Shoulders, Biceps, Triceps, Quads, Hamstrings, Glutes, Calves, Abs).")
        print("      -> Gán nhãn y khoa A3 (banned_for, clinical_reasons) và chỉ số MET chuẩn hóa.")

        print("\n[4/4] LOAD: Nạp vào Database qua SQLAlchemy ORM...")
        food_count = seed_foods(db)
        ex_count = seed_exercises(db)

        if seed_core:
            seed_sample_user_and_logs(db)

        print("\n" + "=" * 72)
        print(f" HOÀN TẤT ETL PIPELINE! ({food_count} thực phẩm, {ex_count} bài tập trong DB)")
        print("=" * 72)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Chạy ETL Pipeline vào SQLAlchemy ORM Database.")
    parser.add_argument("--download-missing", action="store_true", help="Tải từ GitHub nếu thiếu file raw")
    parser.add_argument("--upload-assets", action="store_true", help="Upload ảnh lên S3/Cloudinary")
    parser.add_argument("--provider", type=str, default="github_cdn", help="github_cdn | cloudinary | s3")
    args = parser.parse_args()

    run_pipeline(
        download_missing=args.download_missing,
        upload_assets=args.upload_assets,
        provider=args.provider,
    )


if __name__ == "__main__":
    main()
