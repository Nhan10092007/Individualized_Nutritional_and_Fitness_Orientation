"""
seed_database.py
=============================================================================
Script khởi tạo database (SQLite mặc định hoặc PostgreSQL) và nạp dữ liệu:
1. Thực phẩm (Calo IN):
   - Bảng Thành Phần Dinh Dưỡng Thực Phẩm Việt Nam 2017 (Viện Dinh Dưỡng Quốc Gia)
     trích xuất từ PDF (bang-thanh-phan-dinh-duong-thuc-pham-vn-2017-27-4-17.pdf).
   - Nền tảng thực phẩm thô USDA FoodData Central & 10 món ăn hàng ngày thông dụng.
2. Bài tập (Calo BURN):
   - ĐÚNG 50 BÀI TẬP chuẩn hóa trích xuất từ backend/data/raw/exercises.json.
   - Khớp 100% với schema ORM `Exercise`:
     id, category, name_vi, name_en, met_value, intensity_level, description,
     equipment, instructions, common_mistakes, image, video_url,
     target_muscle, secondary_muscle, banned_for, clinical_reasons, source.
3. Người dùng mẫu & Logs:
   - Tài khoản `vanan24@gmail.com` / `123456`.
   - Nhật ký ăn uống & tập luyện mẫu trong ngày.

Toàn bộ database được tạo và quản trị thông qua SQLAlchemy ORM (Base.metadata.create_all),
tuyệt đối KHÔNG sử dụng file .sql thô.
=============================================================================
"""

import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import BACKEND_DIR
from app.database import DATABASE_URL, SessionLocal, init_db
from app.models import Exercise, Food, FoodLog, User, WorkoutLog
from app.services.progress_service import get_daily_energy_balance
from app.utils.security import hash_password
from scripts.etl.build_65_exercises import PROCESSED_65_PATH, build_65_exercises
from scripts.etl.build_curated_foods import CURATED_FOODS_PATH, build_curated_foods
from scripts.etl.load import _bulk_upsert_exercises, _bulk_upsert_foods

# Danh sách thực phẩm bổ trợ cơ bản (USDA & Món ăn gia đình thông dụng)
CORE_ADDITIONAL_FOODS = [
    # --- USDA Thô chuẩn 100g ---
    {
        "code": "USDA_171077",
        "name_vi": "Ức gà không da (sống)",
        "name_en": "Chicken Breast, raw, skinless",
        "category": "Thịt & Gia cầm",
        "source": "USDA",
        "serving_unit": "100g",
        "serving_weight_g": 100.0,
        "calories_100g": 120.0,
        "protein_100g": 22.5,
        "fat_100g": 2.6,
        "carbs_100g": 0.0,
        "fiber_100g": 0.0,
        "estimated_price_vnd": 16000.0,
        "diet_type": "all",
        "notes": "Nguồn đạm nạc cao cấp, giàu leucine",
    },
    {
        "code": "USDA_173686",
        "name_vi": "Ức gà luộc/áp chảo",
        "name_en": "Chicken Breast, cooked",
        "category": "Thịt & Gia cầm",
        "source": "USDA",
        "serving_unit": "100g",
        "serving_weight_g": 100.0,
        "calories_100g": 165.0,
        "protein_100g": 31.0,
        "fat_100g": 3.6,
        "carbs_100g": 0.0,
        "fiber_100g": 0.0,
        "estimated_price_vnd": 18000.0,
        "diet_type": "all",
        "notes": "Đã qua nấu chín, protein cô đặc",
    },
    {
        "code": "USDA_170567",
        "name_vi": "Thịt bò thăn nạc (sống)",
        "name_en": "Beef Tenderloin, raw",
        "category": "Thịt & Gia cầm",
        "source": "USDA",
        "serving_unit": "100g",
        "serving_weight_g": 100.0,
        "calories_100g": 143.0,
        "protein_100g": 21.6,
        "fat_100g": 5.7,
        "carbs_100g": 0.0,
        "fiber_100g": 0.0,
        "estimated_price_vnd": 35000.0,
        "diet_type": "all",
        "notes": "Giàu sắt heme và kẽm",
    },
    {
        "code": "USDA_175167",
        "name_vi": "Cá hồi phi lê tươi",
        "name_en": "Atlantic Salmon, raw",
        "category": "Thủy hải sản",
        "source": "USDA",
        "serving_unit": "100g",
        "serving_weight_g": 100.0,
        "calories_100g": 208.0,
        "protein_100g": 20.4,
        "fat_100g": 13.4,
        "carbs_100g": 0.0,
        "fiber_100g": 0.0,
        "estimated_price_vnd": 55000.0,
        "diet_type": "all",
        "notes": "Giàu Omega-3 (EPA/DHA) và vitamin D",
    },
    {
        "code": "USDA_171287",
        "name_vi": "Trứng gà tươi nguyên quả",
        "name_en": "Egg, whole, raw, fresh",
        "category": "Trứng & Sản phẩm",
        "source": "USDA",
        "serving_unit": "1 quả (50g)",
        "serving_weight_g": 50.0,
        "calories_100g": 143.0,
        "protein_100g": 12.6,
        "fat_100g": 9.5,
        "carbs_100g": 0.7,
        "fiber_100g": 0.0,
        "estimated_price_vnd": 4000.0,
        "diet_type": "vegetarian",
        "notes": "1 quả ~72 kcal, P: 6.3g",
    },
    # --- Món chế biến ăn sẵn thông dụng Việt Nam ---
    {
        "code": "VN_MEAL_01",
        "name_vi": "Phở bò chín (bát tiêu chuẩn)",
        "name_en": "Beef Noodle Soup (Pho)",
        "category": "Món chế biến sẵn",
        "source": "VN_FCT",
        "serving_unit": "1 bát (450g)",
        "serving_weight_g": 450.0,
        "calories_100g": 84.4,
        "protein_100g": 4.1,
        "fat_100g": 1.9,
        "carbs_100g": 12.7,
        "fiber_100g": 0.4,
        "estimated_price_vnd": 45000.0,
        "diet_type": "all",
        "notes": "1 bát 450g: ~380 kcal, P: 18.5g, F: 8.6g, C: 57.2g",
    },
    {
        "code": "VN_MEAL_02",
        "name_vi": "Bún bò Huế (tô đầy đủ)",
        "name_en": "Hue Beef Noodle Soup",
        "category": "Món chế biến sẵn",
        "source": "VN_FCT",
        "serving_unit": "1 tô (500g)",
        "serving_weight_g": 500.0,
        "calories_100g": 96.0,
        "protein_100g": 4.8,
        "fat_100g": 2.8,
        "carbs_100g": 12.8,
        "fiber_100g": 0.8,
        "estimated_price_vnd": 50000.0,
        "diet_type": "all",
        "notes": "1 tô 500g: ~480 kcal, P: 24g, F: 14g, C: 64g",
    },
    {
        "code": "VN_MEAL_03",
        "name_vi": "Bánh mì kẹp thịt chả pate",
        "name_en": "Vietnamese Baguette Sandwich",
        "category": "Món chế biến sẵn",
        "source": "VN_FCT",
        "serving_unit": "1 cái (130g)",
        "serving_weight_g": 130.0,
        "calories_100g": 300.0,
        "protein_100g": 11.5,
        "fat_100g": 9.2,
        "carbs_100g": 42.3,
        "fiber_100g": 2.1,
        "estimated_price_vnd": 25000.0,
        "diet_type": "all",
        "notes": "1 ổ 130g: ~390 kcal, P: 15g, F: 12g, C: 55g",
    },
    {
        "code": "VN_MEAL_04",
        "name_vi": "Cơm tấm sườn nướng",
        "name_en": "Broken Rice with Grilled Pork Chop",
        "category": "Món chế biến sẵn",
        "source": "VN_FCT",
        "serving_unit": "1 đĩa (350g)",
        "serving_weight_g": 350.0,
        "calories_100g": 170.0,
        "protein_100g": 7.5,
        "fat_100g": 6.0,
        "carbs_100g": 21.0,
        "fiber_100g": 0.9,
        "estimated_price_vnd": 45000.0,
        "diet_type": "all",
        "notes": "1 đĩa 350g: ~595 kcal, P: 26g, F: 21g, C: 73g",
    },
]


def seed_foods(db: Session, *, clean: bool = True) -> int:
    """Nạp danh mục thực phẩm quen thuộc chuẩn hóa (kèm giá Bách Hóa Xanh)."""
    print("[*] Đang nạp dữ liệu Thực phẩm quen thuộc (VN 2017 + USDA + Giá Bách Hóa Xanh)...")

    if not CURATED_FOODS_PATH.exists():
        print("    -> Đang xây dựng danh mục thực phẩm quen thuộc và crawl giá Bách Hóa Xanh...")
        all_foods = build_curated_foods()
    else:
        with open(CURATED_FOODS_PATH, mode="r", encoding="utf-8") as f:
            all_foods = json.load(f)

    if clean:
        valid_codes = {f["code"] for f in all_foods}
        # Xóa các thực phẩm lạ không thuộc danh mục quen thuộc
        deleted = db.query(Food).filter(~Food.code.in_(valid_codes)).delete(synchronize_session=False)
        if deleted > 0:
            print(f"    -> Đã loại bỏ {deleted} món ăn/nguyên liệu lạ không thuộc danh mục quen thuộc.")
        db.commit()

    created, updated = _bulk_upsert_foods(db, all_foods, replace=True)
    db.commit()

    total = db.query(Food).count()
    print(f"[+] Hoàn tất nạp Thực phẩm: tạo mới {created}, cập nhật {updated} (Tổng cộng trong DB: {total} món quen thuộc).")
    return total


def seed_exercises(db: Session) -> int:
    """Nạp đúng 65 bài tập chuẩn hóa từ backend/data/raw/exercises.json."""
    print("[*] Đang nạp đúng 65 bài tập chuẩn hóa từ exercises.json...")

    if not PROCESSED_65_PATH.exists():
        print("    -> Đang chuẩn hóa 65 bài tập từ exercises.json...")
        exercises_65 = build_65_exercises()
    else:
        with open(PROCESSED_65_PATH, mode="r", encoding="utf-8") as f:
            exercises_65 = json.load(f)

    # Dọn dẹp các bài tập cũ (như bài giãn cơ/khởi động) không nằm trong danh mục 65 bài thực thụ
    valid_names = {item.get("name_en") for item in exercises_65 if item.get("name_en")}
    db.query(Exercise).filter(~Exercise.name_en.in_(valid_names)).delete(synchronize_session=False)

    created, updated = _bulk_upsert_exercises(db, exercises_65, replace=True)
    db.commit()

    total = db.query(Exercise).count()
    print(f"[+] Hoàn tất nạp Bài tập: tạo mới {created}, cập nhật {updated} (Tổng cộng trong DB: {total} bài).")
    return total


def seed_sample_user_and_logs(db: Session) -> None:
    """Tạo tài khoản mẫu Nguyễn Văn An (vanan24) và logs mẫu hôm nay."""
    print("[*] Đang nạp tài khoản mẫu và nhật ký dinh dưỡng / tập luyện...")

    user = db.query(User).filter_by(email="vanan24@gmail.com").first()
    if user is None:
        user = User(
            email="vanan24@gmail.com",
            hashed_password=hash_password("123456"),
            full_name="Nguyễn Văn An",
            gender="male",
            age=24,
            height_cm=172.0,
            weight_kg=70.0,
            fitness_goal="fat_loss",
            fitness_level="beginner",
            daily_budget_vnd=80000.0,
            available_days=["Mon", "Wed", "Fri"],
            session_duration_mins=45,
            medical_conditions=[],
            banned_exercise_tags=[],
        )
        db.add(user)
        db.flush()

    today = date.today()

    # Kiểm tra nếu đã có logs hôm nay thì không tạo lặp
    already_has_food_logs = db.query(FoodLog).filter_by(user_id=user.id, logged_date=today).first() is not None
    if not already_has_food_logs:
        # Lấy một số món từ DB
        pho_food = db.query(Food).filter(Food.code == "VN_MEAL_01").first()
        rice_food = db.query(Food).filter(Food.code == "VN_01004").first() or db.query(Food).filter(Food.code == "VN_01001").first()
        chicken_food = db.query(Food).filter(Food.code == "USDA_173686").first()

        if pho_food:
            db.add(FoodLog(
                user_id=user.id,
                food_id=pho_food.id,
                logged_date=today,
                meal_type="breakfast",
                serving_count=1.0,
                actual_weight_g=450.0,
                calculated_calories=380.0,
                calculated_protein=18.5,
                calculated_fat=8.6,
                calculated_carbs=57.2,
            ))
        if rice_food:
            db.add(FoodLog(
                user_id=user.id,
                food_id=rice_food.id,
                logged_date=today,
                meal_type="lunch",
                serving_count=2.0,
                actual_weight_g=200.0,
                calculated_calories=260.0,
                calculated_protein=5.2,
                calculated_fat=0.6,
                calculated_carbs=56.4,
            ))
        if chicken_food:
            db.add(FoodLog(
                user_id=user.id,
                food_id=chicken_food.id,
                logged_date=today,
                meal_type="lunch",
                serving_count=1.5,
                actual_weight_g=150.0,
                calculated_calories=247.5,
                calculated_protein=46.5,
                calculated_fat=5.4,
                calculated_carbs=0.0,
            ))

    already_has_workout_logs = db.query(WorkoutLog).filter_by(user_id=user.id, logged_date=today).first() is not None
    if not already_has_workout_logs:
        pushup_ex = db.query(Exercise).filter(Exercise.name_en.ilike("%pushup%")).first()
        squat_ex = db.query(Exercise).filter(Exercise.name_en.ilike("%squat%")).first()

        if pushup_ex:
            # Cal/min = MET * 3.5 * weight / 200 = 4.5 * 3.5 * 70 / 200 = 5.51 kcal/min
            # 4 hiệp x 45s + 3 nghỉ x 60s = 6 phút -> 33 kcal
            db.add(WorkoutLog(
                user_id=user.id,
                exercise_id=pushup_ex.id,
                logged_date=today,
                user_weight_kg=70.0,
                met_applied=pushup_ex.met_value,
                sets=4,
                duration_per_set_sec=45.0,
                rest_between_sets_sec=60.0,
                total_duration_minutes=6.0,
                calories_burned=33.1,
                notes="Hít đất 4 hiệp x 15 reps buổi sáng",
            ))

        if squat_ex:
            db.add(WorkoutLog(
                user_id=user.id,
                exercise_id=squat_ex.id,
                logged_date=today,
                user_weight_kg=70.0,
                met_applied=squat_ex.met_value,
                sets=4,
                duration_per_set_sec=45.0,
                rest_between_sets_sec=90.0,
                total_duration_minutes=7.5,
                calories_burned=59.9,
                notes="Gánh tạ đòn 4 hiệp x 10 reps",
            ))

    db.commit()
    print("[+] Hoàn tất nạp người dùng mẫu & logs thành công.")


def main() -> None:
    print("=" * 72)
    print(" KHỞI TẠO VÀ NẠP DỮ LIỆU DATABASE (SQLAlchemy ORM)")
    print(f" Database URL: {DATABASE_URL}")
    print("=" * 72)

    init_db()
    print("[+] Đã sinh cấu trúc bảng thành công qua SQLAlchemy ORM.")

    db = SessionLocal()
    try:
        seed_foods(db)
        seed_exercises(db)
        seed_sample_user_and_logs(db)

        print("\n--- BÁO CÁO CÂN BẰNG NĂNG LƯỢNG MẪU (HÔM NAY) ---")
        for row in get_daily_energy_balance(db):
            print(
                f"User: {row['user_id']} | Ngày: {row['log_date']} | "
                f"Calo nạp: {row['total_calories_in']:.1f} kcal | "
                f"Calo đốt: {row['total_calories_burned']:.1f} kcal ({row['total_workout_minutes']:.0f} phút tập) | "
                f"Net Balance: {row['net_calories']:.1f} kcal"
            )
        print("--------------------------------------------------\n")
        print(f"[SUCCESS] Toàn bộ dữ liệu đã sẵn sàng trong database: {DATABASE_URL}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
