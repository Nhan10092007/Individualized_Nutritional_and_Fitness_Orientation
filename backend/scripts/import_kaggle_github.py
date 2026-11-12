"""
import_kaggle_github.py
ETL Tool: Tự động nhập khẩu dữ liệu bài tập và thực phẩm từ các file CSV tải về từ:
1. Kaggle: 'calories-burned-during-exercise-and-activities' (exercise_dataset.csv)
2. GitHub: 'compendium-of-physical-activity' (compendium_data.csv)
3. USDA FoodData Central (food.csv & food_nutrient.csv)

Cách chạy (từ thư mục backend/):  python -m scripts.import_kaggle_github
Dữ liệu được ghi qua SQLAlchemy ORM (SessionLocal), không dùng sqlite3 thuần.
"""

import csv
from pathlib import Path

from app.database import SessionLocal, init_db
from app.models import Exercise
from scripts.common import upsert_by_code


def _intensity(met: float) -> str:
    if met < 3.0:
        return "Light"
    if met < 6.0:
        return "Moderate"
    return "Vigorous"


def import_github_compendium_csv(csv_path: str):
    """
    Nạp dữ liệu từ repo GitHub: https://github.com/andyreagan/compendium-of-physical-activity
    File thường có cột: Activity Code, METs, Specific Activity Description, Category...
    """
    path = Path(csv_path)
    if not path.exists():
        print(f"[!] Không tìm thấy file: {csv_path}")
        return

    init_db()
    db = SessionLocal()
    inserted = 0

    try:
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Linh hoạt nhận diện tên cột
                code = row.get("code") or row.get("Activity Code") or row.get("CODE") or ""
                met_str = row.get("met") or row.get("METs") or row.get("MET") or "0"
                desc = row.get("description") or row.get("Specific Activity Description") or row.get("activity") or ""
                category = row.get("category") or row.get("Heading") or "General Activity"

                try:
                    met = float(met_str.strip())
                except ValueError:
                    continue

                if met <= 0 or not desc or not code.strip():
                    continue

                name_en = desc.strip()
                # Tương đương INSERT OR IGNORE theo cột code
                upsert_by_code(
                    db, Exercise, code.strip(), replace=False,
                    category=category.strip(), name_vi=f"{name_en} (Compendium {code})", name_en=name_en,
                    met_value=met, intensity_level=_intensity(met), description=desc.strip(),
                    source="GitHub Compendium",
                )
                inserted += 1
        db.commit()
    finally:
        db.close()
    print(f"[+] Đã import thành công {inserted} dòng từ GitHub Compendium CSV.")


def import_kaggle_exercise_csv(csv_path: str):
    """
    Nạp dữ liệu từ Kaggle dataset: 
    https://www.kaggle.com/datasets/aadhavvignesh/calories-burned-during-exercise-and-activities
    File exercise_dataset.csv có các cột:
    ['Activity, Exercise or Sport (1 hour)', '130 lb', '155 lb', '180 lb', '205 lb']
    
    Quy đổi Calo 1 hour của 155 lb (70.3 kg) thành MET:
    Formula: Cal/1h = (MET * 3.5 * 70.3068 / 200) * 60 = MET * 73.822
    => MET = (Cal/1h @ 155 lb) / 73.822
    """
    path = Path(csv_path)
    if not path.exists():
        print(f"[!] Không tìm thấy file: {csv_path}")
        return

    init_db()
    db = SessionLocal()
    inserted = 0

    try:
        with open(path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                activity_name = row.get("Activity, Exercise or Sport (1 hour)") or row.get("Activity") or ""
                cal_155 = row.get("155 lb") or row.get("155")

                if not activity_name or not cal_155:
                    continue

                try:
                    cal_val = float(str(cal_155).replace(",", "").strip())
                    # Tính MET từ mức cân 155 lb (70.3 kg) trong 60 phút
                    met_approx = round(cal_val / 73.822, 1)
                except ValueError:
                    continue

                if met_approx <= 0:
                    continue

                # Phân loại category
                category = "Fitness & Sports"
                lower_name = activity_name.lower()
                if any(w in lower_name for w in ["run", "jog"]):
                    category = "Running"
                elif any(w in lower_name for w in ["cycl", "bicycl", "bike"]):
                    category = "Cycling"
                elif any(w in lower_name for w in ["walk", "hike"]):
                    category = "Walking"
                elif any(w in lower_name for w in ["swim", "water"]):
                    category = "Water Activities"

                # Tương đương INSERT OR IGNORE theo cột code
                upsert_by_code(
                    db, Exercise, f"KAGGLE_{inserted + 1:04d}", replace=False,
                    category=category, name_vi=activity_name.strip(), name_en=activity_name.strip(),
                    met_value=met_approx, intensity_level=_intensity(met_approx),
                    description=f"Kaggle activity, cal/hour @ 155lb = {cal_val}",
                    source="Kaggle Dataset",
                )
                inserted += 1
        db.commit()
    finally:
        db.close()
    print(f"[+] Đã import thành công {inserted} bài tập từ Kaggle Exercise CSV.")


if __name__ == "__main__":
    print("[*] Sẵn sàng import dữ liệu bổ sung từ Kaggle / GitHub / USDA.")
    print("Ví dụ sử dụng (từ thư mục backend/):")
    print("  python -m scripts.import_kaggle_github")
    print("Gọi import_kaggle_exercise_csv('data/exercise_dataset.csv') hoặc import_github_compendium_csv('compendium.csv')")
