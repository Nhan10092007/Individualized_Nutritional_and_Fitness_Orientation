"""
fetch_and_seed_from_urls.py
=============================================================================
SCRIPT TỰ ĐỘNG NẠP DATASET TRỰC TIẾP TỪ CÁC ĐƯỜNG DẪN URL TRÊN INTERNET:
1. GitHub Compendium (Raw CSV): Tải tự động 800+ hoạt động từ Ainsworth 2011.
   URL: https://raw.githubusercontent.com/andyreagan/compendium-of-physical-activity/master/compendiumofphysicalactivities.csv
2. USDA FoodData Central (REST API): Gọi API trực tiếp từ USDA lấy dinh dưỡng 100g.
   Endpoint: https://api.nal.usda.gov/fdc/v1/foods/search
3. FAO Vietnamese Food Composition (PDF): Tải file PDF chính thức từ FAO về thư mục data/
   URL: https://www.fao.org/fileadmin/templates/food_composition/documents/pdf/VTN_FCT_2007.pdf
4. Kaggle Exercise Dataset: Hỗ trợ nạp file exercise_dataset.csv hoặc tải từ mirror.
=============================================================================
"""

import os
import sys
import csv
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "fitness_nutrition.db"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 1. Các URL nguồn chính thống
GITHUB_COMPENDIUM_RAW_URL = "https://raw.githubusercontent.com/andyreagan/compendium-of-physical-activity/master/compendiumofphysicalactivities.csv"
FAO_VIETNAM_PDF_URL = "https://www.fao.org/fileadmin/templates/food_composition/documents/pdf/VTN_FCT_2007.pdf"
USDA_API_ENDPOINT = "https://api.nal.usda.gov/fdc/v1/foods/search"
USDA_API_KEY = "DEMO_KEY"  # Key dùng thử chính thức do USDA cấp công khai


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# =============================================================================
# A. TẢI VÀ NẠP TOÀN BỘ 800+ BÀI TẬP TỪ GITHUB COMPENDIUM RAW URL
# =============================================================================
def fetch_and_seed_compendium_from_github():
    print("\n[1/4] Đang kết nối tới GitHub Compendium Raw URL...")
    print(f"      URL: {GITHUB_COMPENDIUM_RAW_URL}")
    local_csv = DATA_DIR / "compendium_github.csv"
    
    try:
        req = urllib.request.Request(
            GITHUB_COMPENDIUM_RAW_URL, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=15) as response, open(local_csv, "wb") as out_file:
            out_file.write(response.read())
        print(f"      [✓] Đã tải xong file CSV về: {local_csv}")
    except Exception as e:
        print(f"      [!] Lỗi khi tải từ GitHub URL: {e}")
        print("      (Nếu chạy offline hoặc không có mạng, script sẽ bỏ qua bước này).")
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0

    with open(local_csv, mode="r", encoding="utf-8-sig", errors="ignore") as f:
        # File compendium của repo dùng delimiter là dấu gạch đứng '|'
        reader = csv.reader(f, delimiter="|")
        header = next(reader, None)
        
        for row in reader:
            if len(row) < 4:
                continue
            
            code = row[0].strip()
            met_str = row[1].strip()
            major_heading = row[2].strip()
            specific_activity = row[3].strip()

            try:
                met = float(met_str)
            except ValueError:
                continue

            if met <= 0 or not specific_activity:
                continue

            # Phân loại cường độ
            if met < 3.0:
                intensity = "Light"
            elif met < 6.0:
                intensity = "Moderate"
            else:
                intensity = "Vigorous"

            name_en = specific_activity
            name_vi = f"{specific_activity} ({major_heading})"

            cursor.execute("""
                INSERT OR REPLACE INTO exercises (
                    code, category, name_vi, name_en, met_value, intensity_level, description, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'GitHub Ainsworth 2011')
            """, (code, major_heading, name_vi, name_en, met, intensity, f"Compendium Code {code} - {major_heading}"))
            count += 1

    conn.commit()
    conn.close()
    print(f"      [✓] Đã nạp thành công {count} bài tập tự động từ GitHub vào SQLite Database!")
    return count


# =============================================================================
# B. TẢI VÀ NẠP DỮ LIỆU THỰC PHẨM TRỰC TIẾP TỪ REST API CỦA USDA
# =============================================================================
def fetch_and_seed_usda_from_api(food_queries=None):
    if food_queries is None:
        food_queries = [
            "Chicken breast raw", "Beef tenderloin raw", "Salmon raw", 
            "Egg whole raw", "Rolled oats", "Brown rice raw", 
            "Broccoli raw", "Avocado raw", "Almonds", "Sweet potato raw"
        ]

    print("\n[2/4] Đang gọi trực tiếp REST API của USDA FoodData Central...")
    conn = get_db_connection()
    cursor = conn.cursor()
    count = 0

    for query in food_queries:
        params = urllib.parse.urlencode({
            "api_key": USDA_API_KEY,
            "query": query,
            "dataType": "Foundation,SR Legacy",
            "pageSize": 1
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
                name_vi = f"{query} (Chuẩn USDA FDC)"
                category = item.get("foodCategory", "Thực phẩm quốc tế")

                # Trích xuất 4 chỉ số Macro & Calo trên 100g từ foodNutrients
                cal_100g, protein_100g, fat_100g, carbs_100g, fiber_100g = 0.0, 0.0, 0.0, 0.0, 0.0
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

                cursor.execute("""
                    INSERT OR REPLACE INTO foods (
                        code, name_vi, name_en, category, source, serving_unit,
                        serving_weight_g, calories_100g, protein_100g, fat_100g,
                        carbs_100g, fiber_100g, estimated_price_vnd, diet_type, notes
                    ) VALUES (?, ?, ?, ?, 'USDA', '100g', 100.0, ?, ?, ?, ?, ?, 20000.0, 'all', 'Dữ liệu trực tiếp từ USDA REST API')
                """, (fdc_id, name_vi, name_en, category, cal_100g, protein_100g, fat_100g, carbs_100g, fiber_100g))
                count += 1
                print(f"      [✓] Đã nạp từ USDA: {name_en} ({cal_100g} kcal/100g, P:{protein_100g}g, F:{fat_100g}g, C:{carbs_100g}g)")
        except Exception as e:
            print(f"      [!] Lỗi khi gọi API cho '{query}': {e}")

    conn.commit()
    conn.close()
    print(f"      [✓] Hoàn tất nạp {count} thực phẩm trực tiếp từ USDA FoodData Central API!")
    return count


# =============================================================================
# C. TẢI FILE GỐC FAO VIỆT NAM (VTN_FCT_2007.pdf) TỪ URL CHÍNH THỐNG
# =============================================================================
def download_fao_vietnam_fct_pdf():
    print("\n[3/4] Đang tải file gốc Bảng thành phần thực phẩm Việt Nam từ FAO...")
    print(f"      URL: {FAO_VIETNAM_PDF_URL}")
    local_pdf = DATA_DIR / "VTN_FCT_2007.pdf"

    if local_pdf.exists():
        print(f"      [i] File PDF đã tồn tại sẵn tại: {local_pdf}")
        return True

    try:
        req = urllib.request.Request(
            FAO_VIETNAM_PDF_URL, 
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response, open(local_pdf, "wb") as out_file:
            out_file.write(response.read())
        print(f"      [✓] Tải thành công file PDF Viện Dinh Dưỡng/FAO ({os.path.getsize(local_pdf) // 1024} KB) về thư mục data/.")
        return True
    except Exception as e:
        print(f"      [!] Không thể tải PDF từ FAO: {e}")
        return False


# =============================================================================
# D. NẠP DỮ LIỆU TỪ KAGGLE EXERCISE DATASET (NẾU CÓ FILE TRONG DATA/)
# =============================================================================
def seed_from_kaggle_csv():
    print("\n[4/4] Kiểm tra file Kaggle 'exercise_dataset.csv'...")
    local_kaggle = DATA_DIR / "exercise_dataset.csv"
    if not local_kaggle.exists():
        print("      [i] File 'exercise_dataset.csv' chưa có trong thư mục backend/data/.")
        print("          (Kaggle bắt buộc đăng nhập tài khoản để tải; nếu bạn đã tải về máy, hãy chép file vào backend/data/)")
        return 0

    from scripts.import_kaggle_github import import_kaggle_exercise_csv
    import_kaggle_exercise_csv(str(local_kaggle))
    return 1


if __name__ == "__main__":
    print("=" * 70)
    print(" BẮT ĐẦU QUY TRÌNH NẠP DỮ LIỆU TỰ ĐỘNG TỪ CÁC LINK URL TRỰC TUYẾN")
    print("=" * 70)
    
    # 1. Kéo 800+ bài tập từ GitHub Raw
    fetch_and_seed_compendium_from_github()
    
    # 2. Gọi REST API USDA lấy thực phẩm
    fetch_and_seed_usda_from_api()
    
    # 3. Tải PDF FAO
    download_fao_vietnam_fct_pdf()
    
    # 4. Kiểm tra Kaggle file
    seed_from_kaggle_csv()

    print("\n" + "=" * 70)
    print(" TỔNG KẾT HOÀN TẤT QUY TRÌNH TỰ ĐỘNG NẠP QUA URL!")
    print("=" * 70)
