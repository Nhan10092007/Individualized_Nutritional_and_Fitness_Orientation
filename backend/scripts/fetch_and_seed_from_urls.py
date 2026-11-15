"""
fetch_and_seed_from_urls.py
=============================================================================
SCRIPT TỰ ĐỘNG TẢI RAW DATASET TỪ INTERNET VỀ backend/data/raw/ VÀ CHẠY ETL ORM:
1. GitHub free-exercise-db (`exercises.json`) + ánh xạ Asset URLs (Step 2)
2. GitHub Compendium (`compendium_github.csv`) - Ainsworth 2011 (Step 1 + 3 + 4)
3. USDA FoodData Central REST API - lấy dinh dưỡng chuẩn 100g
4. Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2017 (PDF Viện Dinh Dưỡng - Bộ Y Tế)
5. Kaggle `exercise_dataset.csv` (nếu đã đặt trong `backend/data/raw/`)

Cách chạy (từ thư mục backend/):  python -m scripts.fetch_and_seed_from_urls
=============================================================================
"""

import json
import os
import urllib.parse
import urllib.request

from scripts.etl import (
    RAW_DATA_DIR,
    AssetHandler,
    download_file,
    extract_compendium_csv,
    extract_exercises_json,
    extract_kaggle_exercise_csv,
    load_exercises,
    load_foods,
    transform_compendium_rows,
    transform_exercises_json,
    transform_kaggle_rows,
    VIETNAM_FCT_2017_PDF_NAME,
    check_vietnam_fct_2017_pdf,
)

USDA_API_ENDPOINT = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "DEMO_KEY"


def fetch_and_seed_exercises_json_from_github() -> int:
    print("\n[1/5] Extract & Transform GitHub free-exercise-db (exercises.json)...")
    raw_items = extract_exercises_json(download_if_missing=True)
    if not raw_items:
        print("      [!] Không lấy được exercises.json.")
        return 0
    records = transform_exercises_json(raw_items, asset_handler=AssetHandler())
    created, updated = load_exercises(records, replace=True)
    print(f"      [✓] exercises.json: tạo mới {created}, cập nhật {updated} bài tập.")
    return created + updated


def fetch_and_seed_compendium_from_github() -> int:
    print("\n[2/5] Extract & Transform GitHub Compendium (compendium_github.csv)...")
    raw_rows = extract_compendium_csv(download_if_missing=True)
    if not raw_rows:
        print("      [!] Không lấy được compendium_github.csv.")
        return 0
    records = transform_compendium_rows(raw_rows)
    created, updated = load_exercises(records, replace=True)
    print(f"      [✓] Compendium 2011: tạo mới {created}, cập nhật {updated} bài tập.")
    return created + updated


def fetch_and_seed_usda_from_api(food_queries: list[str] | None = None) -> int:
    if food_queries is None:
        food_queries = [
            "Chicken breast raw", "Beef tenderloin raw", "Salmon raw",
            "Egg whole raw", "Rolled oats", "Brown rice raw",
            "Broccoli raw", "Avocado raw", "Almonds", "Sweet potato raw",
        ]

    print("\n[3/5] Đang gọi REST API của USDA FoodData Central...")
    food_records: list[dict] = []

    for query in food_queries:
        params = urllib.parse.urlencode({
            "api_key": USDA_API_KEY,
            "query": query,
            "dataType": "Foundation,SR Legacy",
            "pageSize": 1,
        })
        url = f"{USDA_API_ENDPOINT}?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "FitnessNutritionApp/1.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            foods = data.get("foods", [])
            if not foods:
                continue

            item = foods[0]
            fdc_id = f"USDA_{item.get('fdcId')}"
            name_en = item.get("description", query)
            category = item.get("foodCategory", "Thực phẩm quốc tế")

            cal_100g = protein_100g = fat_100g = carbs_100g = fiber_100g = 0.0
            for n in item.get("foodNutrients", []):
                name = n.get("nutrientName", "").lower()
                val = float(n.get("value", 0.0))
                if "energy" in name and (n.get("unitName") == "KCAL" or val < 1000):
                    cal_100g = val
                elif "protein" in name:
                    protein_100g = val
                elif "total lipid" in name or "fat" in name:
                    fat_100g = val
                elif "carbohydrate" in name:
                    carbs_100g = val
                elif "fiber" in name:
                    fiber_100g = val

            food_records.append({
                "code": fdc_id,
                "name_vi": f"{query} (Chuẩn USDA FDC)",
                "name_en": name_en,
                "category": category,
                "source": "USDA",
                "serving_unit": "100g",
                "serving_weight_g": 100.0,
                "calories_100g": cal_100g,
                "protein_100g": protein_100g,
                "fat_100g": fat_100g,
                "carbs_100g": carbs_100g,
                "fiber_100g": fiber_100g,
                "estimated_price_vnd": 20000.0,
                "diet_type": "all",
                "notes": "Dữ liệu trực tiếp từ USDA REST API",
            })
        except Exception as exc:
            print(f"      [!] Lỗi khi gọi API cho '{query}': {exc}")

    created, updated = load_foods(food_records, replace=True)
    print(f"      [✓] USDA API: tạo mới {created}, cập nhật {updated} thực phẩm.")
    return created + updated


def verify_vietnam_fct_pdf() -> bool:
    print("\n[4/5] Kiểm tra file Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2017 (PDF)...")
    local_pdf = check_vietnam_fct_2017_pdf()
    if local_pdf:
        size_kb = os.path.getsize(local_pdf) // 1024
        print(f"      [✓] Đã có sẵn file PDF chuẩn 2017: {local_pdf.name} ({size_kb} KB)")
        return True
    print(f"      [!] Chưa tìm thấy file '{VIETNAM_FCT_2017_PDF_NAME}' trong {RAW_DATA_DIR}")
    return False


def seed_from_kaggle_csv() -> int:
    print("\n[5/5] Kiểm tra Kaggle 'exercise_dataset.csv' trong backend/data/raw/...")
    raw_rows = extract_kaggle_exercise_csv()
    if not raw_rows:
        print("      [i] Chưa có 'backend/data/raw/exercise_dataset.csv'.")
        return 0
    records = transform_kaggle_rows(raw_rows)
    created, updated = load_exercises(records, replace=False)
    print(f"      [✓] Kaggle CSV: tạo mới {created}, bỏ qua trùng/cập nhật {updated} bài tập.")
    return created + updated


if __name__ == "__main__":
    print("=" * 70)
    print(" BẮT ĐẦU QUY TRÌNH EXTRACT & SEED TỰ ĐỘNG (SQLAlchemy ORM)")
    print("=" * 70)

    fetch_and_seed_exercises_json_from_github()
    fetch_and_seed_compendium_from_github()
    fetch_and_seed_usda_from_api()
    verify_vietnam_fct_pdf()
    seed_from_kaggle_csv()

    print("\n" + "=" * 70)
    print(" TỔNG KẾT HOÀN TẤT QUY TRÌNH!")
    print("=" * 70)
