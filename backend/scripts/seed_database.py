"""
seed_database.py
Script khởi tạo database SQLite và nạp bộ dữ liệu chuẩn hóa:
1. Thức ăn (Calo IN):
   - Chuẩn USDA FoodData Central (trên 100g)
   - Bảng Thành Phần Thực Phẩm Việt Nam VTN_FCT 2007 (Viện Dinh Dưỡng Quốc Gia / FAO) với định lượng khẩu phần thông dụng
2. Bài tập (Calo BURN):
   - 2011 Compendium of Physical Activities (Ainsworth et al. / ACSM)
   - Kaggle Exercise Dataset

Cách chạy (từ thư mục backend/):
    python -m scripts.seed_database

Bảng được tạo từ SQLAlchemy models (Base.metadata.create_all), KHÔNG dùng file .sql.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.database import DATABASE_URL, SessionLocal, init_db
from app.models import Exercise, Food, FoodLog, User, WorkoutLog
from app.services.progress_service import get_daily_energy_balance
from app.utils.security import hash_password
from scripts.common import upsert_by_code

FOOD_FIELDS = (
    "code", "name_vi", "name_en", "category", "source", "serving_unit",
    "serving_weight_g", "calories_100g", "protein_100g", "fat_100g",
    "carbs_100g", "fiber_100g", "estimated_price_vnd", "diet_type", "notes",
)
EXERCISE_FIELDS = (
    "code", "category", "name_vi", "name_en", "met_value", "intensity_level", "description", "source",
)


def seed_foods(db: Session):
    print("[*] Bắt đầu nạp dữ liệu Thực phẩm (USDA + VTN_FCT 2007)...")
    
    # Danh sách dữ liệu thực phẩm chuẩn
    # (code, name_vi, name_en, category, source, serving_unit, serving_weight_g, cal_100g, p_100g, f_100g, c_100g, fiber_100g, price_vnd, diet_type, notes)
    foods_data = [
        # --- THỰC PHẨM QUỐC TẾ (USDA FoodData Central - Nền tảng nguyên liệu thô 100g) ---
        (
            "USDA_171077", "Ức gà không da (sống)", "Chicken Breast, raw, skinless",
            "Thịt & Gia cầm", "USDA", "100g", 100.0,
            120.0, 22.5, 2.6, 0.0, 0.0, 16000.0, "all", "Nguồn đạm nạc cao cấp, giàu leucine"
        ),
        (
            "USDA_173686", "Ức gà luộc/áp chảo", "Chicken Breast, cooked",
            "Thịt & Gia cầm", "USDA", "100g", 100.0,
            165.0, 31.0, 3.6, 0.0, 0.0, 18000.0, "all", "Đã qua nấu chín, protein cô đặc"
        ),
        (
            "USDA_170567", "Thịt bò thăn nạc (sống)", "Beef Tenderloin, raw",
            "Thịt & Gia cầm", "USDA", "100g", 100.0,
            143.0, 21.6, 5.7, 0.0, 0.0, 35000.0, "all", "Giàu sắt heme và kẽm"
        ),
        (
            "USDA_175167", "Cá hồi Đại Tây Dương (sống)", "Atlantic Salmon, raw",
            "Thủy hải sản", "USDA", "100g", 100.0,
            208.0, 20.4, 13.4, 0.0, 0.0, 55000.0, "all", "Nguồn Axit béo Omega-3 (EPA, DHA)"
        ),
        (
            "USDA_171287", "Trứng gà công nghiệp (nguyên quả)", "Egg, whole, raw",
            "Trứng & Sản phẩm sữa", "USDA", "1 quả (50g)", 50.0,
            143.0, 12.6, 9.5, 0.7, 0.0, 3500.0, "vegetarian", "1 quả khoảng 50g chứa ~72 kcal"
        ),
        (
            "USDA_171288", "Lòng trắng trứng gà", "Egg white, raw",
            "Trứng & Sản phẩm sữa", "USDA", "100g", 100.0,
            52.0, 10.9, 0.2, 0.7, 0.0, 4000.0, "vegetarian", "Đạm tinh khiết, gần như không béo"
        ),
        (
            "USDA_169704", "Yến mạch cán dẹt", "Rolled Oats, raw",
            "Ngũ cốc", "USDA", "100g", 100.0,
            389.0, 16.9, 6.9, 66.3, 10.6, 12000.0, "vegan", "Giàu chất xơ hòa tan Beta-Glucan"
        ),
        (
            "USDA_168878", "Gạo lứt (sống)", "Brown Rice, raw",
            "Ngũ cốc", "USDA", "100g", 100.0,
            370.0, 7.9, 2.9, 77.2, 3.5, 4500.0, "vegan", "Chỉ số GI trung bình thấp"
        ),
        (
            "USDA_171705", "Quả Bơ sáp", "Avocado, raw",
            "Trái cây & Hạt", "USDA", "100g", 100.0,
            160.0, 2.0, 14.7, 8.5, 6.7, 10000.0, "vegan", "Chất béo không bão hòa đơn (MUFA)"
        ),
        (
            "USDA_170567b", "Hạt Hạnh nhân", "Almonds, raw",
            "Trái cây & Hạt", "USDA", "100g", 100.0,
            579.0, 21.2, 49.9, 21.6, 12.5, 30000.0, "vegan", "Giàu Vitamin E và Magie"
        ),
        (
            "USDA_170379", "Bông cải xanh (Broccoli, sống)", "Broccoli, raw",
            "Rau củ", "USDA", "100g", 100.0,
            34.0, 2.8, 0.4, 6.6, 2.6, 6000.0, "vegan", "Giàu Sulforaphane và Vitamin C"
        ),
        (
            "USDA_171413", "Dầu Ô-liu nguyên chất", "Olive Oil, extra virgin",
            "Dầu mỡ & Bơ", "USDA", "1 thìa canh (14g)", 14.0,
            884.0, 0.0, 100.0, 0.0, 0.0, 6000.0, "vegan", "Chất béo đơn kháng viêm"
        ),
        (
            "USDA_173944", "Chuối chín", "Banana, raw",
            "Trái cây & Hạt", "USDA", "1 quả vừa (118g)", 118.0,
            89.0, 1.1, 0.3, 22.8, 2.6, 4000.0, "vegan", "Giàu Kali, bổ sung năng lượng nhanh"
        ),
        (
            "USDA_171265", "Khoai lang ruột vàng (sống)", "Sweet Potato, raw",
            "Củ & Tinh bột", "USDA", "100g", 100.0,
            86.0, 1.6, 0.1, 20.1, 3.0, 3000.0, "vegan", "Carb chuyển hóa chậm"
        ),
        (
            "USDA_173430", "Sữa tươi không đường tiệt trùng", "Cow Milk, whole, unsweetened",
            "Trứng & Sản phẩm sữa", "USDA", "1 hộp (220ml)", 220.0,
            61.0, 3.2, 3.3, 4.8, 0.0, 8500.0, "vegetarian", "Giàu Canxi và vitamin D"
        ),
        (
            "USDA_WHEY", "Bột Whey Protein Isolate", "Whey Protein Powder",
            "Thực phẩm bổ sung", "USDA", "1 muỗng (30g)", 30.0,
            370.0, 83.3, 1.5, 3.3, 0.0, 25000.0, "vegetarian", "Đạm hấp thu siêu nhanh"
        ),

        # --- DỮ LIỆU ĐẶC THÙ VIỆT NAM (VTN_FCT 2007 - Viện Dinh Dưỡng & Khẩu phần thực tế) ---
        (
            "VN_01001", "Gạo tẻ giã/máy (hạt khô)", "White Rice, raw",
            "Ngũ cốc", "VN_FCT", "100g", 100.0,
            344.0, 7.6, 1.0, 76.2, 0.4, 2500.0, "vegan", "Lương thực chính của người Việt"
        ),
        (
            "VN_01002", "Cơm trắng nấu chín", "Cooked White Rice",
            "Món chế biến sẵn", "VN_FCT", "1 bát (150g)", 150.0,
            130.0, 2.6, 0.3, 28.2, 0.3, 3000.0, "vegan", "1 bát cơm gạt chuẩn 150g = ~195 kcal"
        ),
        (
            "VN_02015", "Thịt lợn nạc (sống)", "Pork, lean, raw",
            "Thịt & Gia cầm", "VN_FCT", "100g", 100.0,
            145.0, 19.0, 7.0, 0.0, 0.0, 14000.0, "all", "Thịt nạc thăn hoặc mông lợn"
        ),
        (
            "VN_02016", "Thịt lợn ba chỉ (sống)", "Pork, belly, raw",
            "Thịt & Gia cầm", "VN_FCT", "100g", 100.0,
            260.0, 16.5, 21.5, 0.0, 0.0, 15000.0, "all", "Nhiều mỡ, calo cao"
        ),
        (
            "VN_02025", "Đậu phụ mơ (đậu hũ trắng)", "Tofu, firm",
            "Đậu & Sản phẩm họ đậu", "VN_FCT", "1 bìa (100g)", 100.0,
            95.0, 10.9, 5.4, 0.7, 0.5, 4000.0, "vegan", "Nguồn đạm thực vật giá rẻ, dễ tiêu"
        ),
        (
            "VN_03010", "Cá rô đồng (thịt cá sống)", "Climbing Perch Fish, raw",
            "Thủy hải sản", "VN_FCT", "100g", 100.0,
            104.0, 19.1, 3.0, 0.0, 0.0, 12000.0, "all", "Cá nước ngọt, đạm lành tính"
        ),
        (
            "VN_03045", "Tôm đồng (bỏ vỏ)", "Freshwater Shrimp, raw",
            "Thủy hải sản", "VN_FCT", "100g", 100.0,
            90.0, 18.4, 1.8, 0.0, 0.0, 20000.0, "all", "Giàu canxi và kẽm"
        ),
        (
            "VN_04001", "Rau muống (sống)", "Water Spinach, raw",
            "Rau củ", "VN_FCT", "100g", 100.0,
            23.0, 3.2, 0.4, 2.1, 1.0, 2500.0, "vegan", "Rau quốc dân, calo thấp, giàu chất xơ"
        ),
        (
            "VN_04015", "Rau ngót (sống)", "Sweet Leaf bush, raw",
            "Rau củ", "VN_FCT", "100g", 100.0,
            35.0, 5.3, 0.5, 3.4, 2.5, 4000.0, "vegan", "Lượng đạm thực vật cao trong nhóm rau"
        ),
        (
            "VN_04020", "Rau cải thìa / Cải ngọt", "Bok Choy, raw",
            "Rau củ", "VN_FCT", "100g", 100.0,
            16.0, 1.5, 0.2, 2.2, 1.0, 3000.0, "vegan", "Rau lá xanh mát, vitamin K dồi dào"
        ),
        (
            "VN_04055", "Khoai lang luộc chín", "Boiled Sweet Potato",
            "Củ & Tinh bột", "VN_FCT", "1 củ vừa (150g)", 150.0,
            90.0, 1.3, 0.2, 21.0, 2.8, 5000.0, "vegan", "Thực phẩm giảm cân thông dụng"
        ),
        (
            "VN_05001", "Bánh phở tươi", "Fresh Rice Noodles",
            "Ngũ cốc", "VN_FCT", "100g", 100.0,
            143.0, 2.4, 0.3, 32.7, 0.2, 3000.0, "vegan", "Bánh phở mềm ẩm"
        ),
        (
            "VN_05002", "Bún tươi", "Rice Vermicelli, fresh",
            "Ngũ cốc", "VN_FCT", "100g", 100.0,
            110.0, 1.7, 0.0, 25.7, 0.3, 2500.0, "vegan", "Dùng cho bún chả, bún bò, bún riêu"
        ),
        
        # --- CÁC MÓN ĂN VIỆT CHẾ BIẾN SẴN (Định lượng khẩu phần theo bữa thực tế) ---
        (
            "VN_MEAL_01", "Phở bò chín (tô vừa)", "Beef Pho, cooked bowl",
            "Món chế biến sẵn", "VN_FCT", "1 tô (450g)", 450.0,
            84.4, 4.1, 1.9, 12.7, 0.6, 45000.0, "all", "1 tô 450g: ~380 kcal, P: 18.5g, F: 8.5g, C: 57g"
        ),
        (
            "VN_MEAL_02", "Bún bò Huế (tô đầy đủ)", "Hue Beef Noodle Soup",
            "Món chế biến sẵn", "VN_FCT", "1 tô (500g)", 500.0,
            96.0, 4.8, 2.8, 12.8, 0.8, 50000.0, "all", "1 tô 500g: ~480 kcal, P: 24g, F: 14g, C: 64g"
        ),
        (
            "VN_MEAL_03", "Bánh mì kẹp thịt chả pate", "Vietnamese Baguette Sandwich",
            "Món chế biến sẵn", "VN_FCT", "1 cái (130g)", 130.0,
            300.0, 11.5, 9.2, 42.3, 2.1, 25000.0, "all", "1 ổ 130g: ~390 kcal, P: 15g, F: 12g, C: 55g"
        ),
        (
            "VN_MEAL_04", "Trứng chiên / ốp la (1 quả)", "Fried Egg",
            "Món chế biến sẵn", "VN_FCT", "1 quả (55g)", 55.0,
            200.0, 12.7, 15.5, 1.5, 0.0, 7000.0, "vegetarian", "1 quả chiên dầu mỡ: ~110 kcal"
        ),
        (
            "VN_MEAL_05", "Thịt kho tàu nước dừa", "Braised Pork with Eggs",
            "Món chế biến sẵn", "VN_FCT", "1 đĩa nhỏ (120g)", 120.0,
            267.0, 15.0, 18.3, 6.7, 0.0, 30000.0, "all", "Thịt ba chỉ kho trứng: ~320 kcal / khẩu phần"
        ),
        (
            "VN_MEAL_06", "Rau muống xào tỏi", "Stir-fried Morning Glory with Garlic",
            "Món chế biến sẵn", "VN_FCT", "1 đĩa (150g)", 150.0,
            73.3, 2.3, 4.7, 5.3, 1.8, 15000.0, "vegan", "1 đĩa 150g xào dầu ăn: ~110 kcal"
        ),
        (
            "VN_MEAL_07", "Canh chua cá lóc", "Sour Fish Soup",
            "Món chế biến sẵn", "VN_FCT", "1 bát (250g)", 250.0,
            48.0, 4.8, 1.4, 4.0, 1.2, 25000.0, "all", "1 bát canh thanh đạm: ~120 kcal, P: 12g"
        ),
        (
            "VN_MEAL_08", "Đậu phụ sốt cà chua", "Tofu with Tomato Sauce",
            "Món chế biến sẵn", "VN_FCT", "1 đĩa (180g)", 180.0,
            105.5, 7.8, 6.1, 4.7, 1.5, 18000.0, "vegan", "1 đĩa 180g: ~190 kcal, P: 14g"
        ),
        (
            "VN_MEAL_09", "Gà xào sả ớt (ức gà)", "Stir-fried Lemongrass Chicken",
            "Món chế biến sẵn", "VN_FCT", "1 đĩa (150g)", 150.0,
            160.0, 18.7, 7.3, 4.0, 0.8, 30000.0, "all", "1 đĩa 150g: ~240 kcal, P: 28g"
        ),
        (
            "VN_MEAL_10", "Canh bí đao nấu thịt nạc", "Winter Melon Soup with Minced Pork",
            "Món chế biến sẵn", "VN_FCT", "1 bát (250g)", 250.0,
            36.0, 3.2, 1.2, 3.2, 1.0, 15000.0, "all", "1 bát thanh nhiệt: ~90 kcal"
        )
    ]
    
    # Tương đương INSERT OR REPLACE theo cột code
    for row in foods_data:
        fields = dict(zip(FOOD_FIELDS, row))
        upsert_by_code(db, Food, fields.pop("code"), **fields)

    db.commit()
    print(f"[+] Đã nạp thành công {len(foods_data)} thực phẩm chuẩn hóa.")


def seed_exercises(db: Session):
    print("[*] Bắt đầu nạp dữ liệu Bài tập (Ainsworth 2011 Compendium of Physical Activities & Kaggle)...")
    
    # Dữ liệu bài tập chuẩn hóa:
    # (code, category, name_vi, name_en, met_value, intensity_level, description, source)
    exercises_data = [
        # --- CONDITIONING EXERCISE (Gym, Calisthenics, Kháng lực) ---
        (
            "02050", "Conditioning Exercise", "Calisthenics cường độ nặng (Hít đất, kéo xà, gập bụng liên tục)",
            "Calisthenics (e.g., pushups, pullups, situps), vigorous effort",
            8.0, "Vigorous", "Bài tập thể trọng cường độ cao, đốt calo và phát triển sức bền cơ bắp", "Compendium 2011"
        ),
        (
            "02040", "Conditioning Exercise", "Calisthenics cường độ nhẹ đến vừa",
            "Calisthenics, light or moderate effort",
            3.8, "Moderate", "Bài tập thể trọng nhịp độ vừa phải, giãn cơ, chống đẩy nhẹ nhàng", "Compendium 2011"
        ),
        (
            "02020", "Conditioning Exercise", "Tập Tạ / Kháng lực cường độ nặng (Free Weights, Deadlift, Squat nặng)",
            "Resistance (weight) training, free weights, vigorous effort",
            6.0, "Vigorous", "Nâng tạ tự do, cường độ tạ nặng, nghỉ ngắn giữa các hiệp", "Compendium 2011"
        ),
        (
            "02030", "Conditioning Exercise", "Tập Tạ / Máy tạ cường độ nhẹ hoặc trung bình",
            "Weight lifting, light or moderate effort",
            3.5, "Moderate", "Tập máy kháng lực, tạ đơn nhẹ nhịp độ duy trì", "Compendium 2011"
        ),
        (
            "02011", "Conditioning Exercise", "Tập Circuit Training / HIIT cường độ cao",
            "Circuit training, including kettlebells, vigorous effort",
            8.0, "Vigorous", "Tập xoay vòng liên tục nhiều bài tập, nhịp tim cao", "Compendium 2011"
        ),
        (
            "02010", "Conditioning Exercise", "Circuit training cường độ trung bình",
            "Circuit training, moderate effort",
            4.3, "Moderate", "Tập xoay vòng có thời gian nghỉ hợp lý", "Compendium 2011"
        ),
        (
            "02065", "Conditioning Exercise", "Burpees cường độ cao",
            "Burpees, vigorous effort",
            8.0, "Vigorous", "Bật nhảy phối hợp toàn thân, đốt mỡ tối đa", "Compendium 2011"
        ),
        (
            "02080", "Conditioning Exercise", "Jumping Jacks (Nhảy vung tay chân)",
            "Jumping jacks, vigorous effort",
            8.0, "Vigorous", "Khởi động hoặc Cardio ngắt quãng", "Compendium 2011"
        ),
        (
            "02070", "Conditioning Exercise", "Plank (Gồng cơ lõi)",
            "Plank, core isometric hold",
            3.8, "Moderate", "Gồng giữ thắt lưng và cơ bụng đẳng trường", "Compendium 2011"
        ),
        (
            "02060", "Conditioning Exercise", "Bodyweight Squat / Lunges (Ngồi xổm tay không)",
            "Squats / lunges, bodyweight",
            5.0, "Moderate", "Tập cơ mông đùi không tạ", "Compendium 2011"
        ),
        (
            "02105", "Conditioning Exercise", "Pilates thảm",
            "Pilates, mat, intermediate",
            3.5, "Moderate", "Cải thiện tư thế và săn chắc cơ lõi", "Compendium 2011"
        ),
        (
            "10110", "Conditioning Exercise", "Yoga (Hatha Yoga nhẹ nhàng)",
            "Yoga, Hatha",
            2.5, "Light", "Giãn cơ, hít thở và giải tỏa căng thẳng", "Compendium 2011"
        ),
        (
            "10120", "Conditioning Exercise", "Power Yoga / Vinyasa Yoga",
            "Yoga, Power / Vinyasa",
            4.0, "Moderate", "Chuỗi động tác yoga liên hoàn đòi hỏi sức mạnh", "Compendium 2011"
        ),

        # --- RUNNING & JOGGING (Chạy bộ) ---
        (
            "12020", "Running", "Chạy bộ 8.0 km/h (Pace 7:30 min/km)",
            "Running, 5 mph (12 min/mile)",
            8.3, "Vigorous", "Chạy bền tốc độ vừa phải trên đường bằng", "Compendium 2011"
        ),
        (
            "12030", "Running", "Chạy bộ 9.7 km/h (Pace 6:13 min/km)",
            "Running, 6 mph (10 min/mile)",
            9.8, "Vigorous", "Chạy nhịp độ cao, rèn luyện hệ hô hấp tim mạch", "Compendium 2011"
        ),
        (
            "12050", "Running", "Chạy bộ 11.3 km/h (Pace 5:19 min/km)",
            "Running, 7 mph (8.5 min/mile)",
            11.0, "Vigorous", "Chạy tốc độ nhanh", "Compendium 2011"
        ),
        (
            "12070", "Running", "Chạy bộ 12.9 km/h (Pace 4:39 min/km)",
            "Running, 8 mph (7.5 min/mile)",
            11.8, "Vigorous", "Chạy nước rút hoặc cự ly trung bình nhanh", "Compendium 2011"
        ),
        (
            "12010", "Running", "Chạy bước nhỏ tại chỗ / Jogging nhẹ",
            "Jogging, general",
            7.0, "Vigorous", "Chạy thư giãn phục hồi", "Compendium 2011"
        ),

        # --- WALKING (Đi bộ) ---
        (
            "17150", "Walking", "Đi bộ tốc độ vừa phải 4.8 km/h",
            "Walking, 3.0 mph, moderate pace",
            3.5, "Moderate", "Đi bộ đường bằng hàng ngày", "Compendium 2011"
        ),
        (
            "17170", "Walking", "Đi bộ nhanh 5.6 km/h",
            "Walking, 3.5 mph, brisk pace",
            4.3, "Moderate", "Đi bộ nhanh rèn luyện thể chất", "Compendium 2011"
        ),
        (
            "17080", "Walking", "Leo cầu thang bộ",
            "Stair climbing, slow pace",
            4.0, "Moderate", "Đi lên từng bậc cầu thang", "Compendium 2011"
        ),
        (
            "17082", "Walking", "Leo cầu thang bộ nhanh",
            "Stair climbing, fast pace",
            8.8, "Vigorous", "Chạy leo cầu thang đốt mỡ thần tốc", "Compendium 2011"
        ),

        # --- BICYCLING (Đạp xe) ---
        (
            "01015", "Cycling", "Đạp xe máy tập tại chỗ (nhẹ, 50W)",
            "Bicycling, stationary, light effort (50 watts)",
            3.5, "Moderate", "Khởi động làm nóng trên xe đạp tập", "Compendium 2011"
        ),
        (
            "01020", "Cycling", "Đạp xe dạo phố thư giãn 15 km/h",
            "Bicycling, leisure 9.4 mph",
            5.8, "Moderate", "Đạp xe dạo phố ngoài trời", "Compendium 2011"
        ),
        (
            "01030", "Cycling", "Đạp xe tốc độ trung bình 20 km/h",
            "Bicycling, moderate 12-13.9 mph",
            8.0, "Vigorous", "Đạp xe đường trường thể thao", "Compendium 2011"
        ),
        (
            "01050", "Cycling", "Spinning / Đạp xe nhịp điệu trên máy tập",
            "Bicycling, stationary, vigorous (150-200 watts)",
            8.8, "Vigorous", "Lớp học đạp xe RPM / Spinning", "Compendium 2011"
        ),

        # --- SPORTS & WATER ACTIVITIES (Các môn thể thao phổ biến) ---
        (
            "15040", "Sports", "Cầu lông thi đấu",
            "Badminton, competitive match play",
            7.0, "Vigorous", "Đánh cầu lông cường độ cao, di chuyển nhiều", "Compendium 2011"
        ),
        (
            "15050", "Sports", "Cầu lông giao lưu thư giãn",
            "Badminton, social singles and doubles",
            4.5, "Moderate", "Đánh cầu lông ngoài công viên hoặc giao lưu nhẹ", "Compendium 2011"
        ),
        (
            "15610", "Sports", "Bóng đá thi đấu sân lớn",
            "Football / Soccer, competitive",
            10.0, "Vigorous", "Chạy liên tục và tranh chấp bóng", "Compendium 2011"
        ),
        (
            "15620", "Sports", "Bóng đá mini / Giao hữu sân cỏ nhân tạo",
            "Football / Soccer, casual",
            7.0, "Vigorous", "Đá bóng phong trào 7 người hoặc 5 người", "Compendium 2011"
        ),
        (
            "15080", "Sports", "Bóng rổ thi đấu",
            "Basketball, match play",
            8.0, "Vigorous", "Bật nhảy và tranh bóng liên tục", "Compendium 2011"
        ),
        (
            "15470", "Sports", "Bóng bàn (Ping pong)",
            "Table tennis / Ping pong",
            4.0, "Moderate", "Phản xạ nhanh, di chuyển ngắn", "Compendium 2011"
        ),
        (
            "18310", "Water Activities", "Bơi ếch nhịp độ vừa",
            "Swimming, breaststroke, recreational",
            5.3, "Moderate", "Bơi thư giãn đều đặn", "Compendium 2011"
        ),
        (
            "18320", "Water Activities", "Bơi sải tự do cường độ nhanh",
            "Swimming laps, freestyle, vigorous effort",
            9.8, "Vigorous", "Bơi tốc độ cao, tiêu hao năng lượng lớn", "Compendium 2011"
        ),
        (
            "15580", "Conditioning Exercise", "Nhảy dây tốc độ trung bình (< 100 lần/phút)",
            "Rope skipping, moderate pace (< 100 skips/min)",
            10.0, "Vigorous", "Đốt calo cực kỳ hiệu quả", "Compendium 2011"
        ),
        (
            "15590", "Conditioning Exercise", "Nhảy dây tốc độ nhanh (120-140 lần/phút)",
            "Rope skipping, fast pace (120-140 skips/min)",
            12.3, "Vigorous", "Bài tập HIIT đốt mỡ đỉnh cao", "Compendium 2011"
        ),
        (
            "05040", "Sports", "Boxing / Đấm bao cát",
            "Boxing, punching bag",
            5.5, "Moderate", "Rèn luyện sức mạnh tay và vai", "Compendium 2011"
        ),
        (
            "05050", "Sports", "Boxing đối kháng / Sparring",
            "Boxing, in ring, sparring",
            7.8, "Vigorous", "Tập luyện võ thuật đối kháng", "Compendium 2011"
        )
    ]
    
    # Tương đương INSERT OR REPLACE theo cột code
    for row in exercises_data:
        fields = dict(zip(EXERCISE_FIELDS, row))
        upsert_by_code(db, Exercise, fields.pop("code"), **fields)

    db.commit()
    print(f"[+] Đã nạp thành công {len(exercises_data)} bài tập thể chất chuẩn hóa.")


def seed_sample_user_and_logs(db: Session):
    print("[*] Nạp người dùng mẫu và logs thực hành...")

    # 1. Thêm user mẫu (Nguyễn Văn An, 24 tuổi, 70kg, mục tiêu fat_loss) - tương đương INSERT OR IGNORE
    #    Đăng nhập thử bằng: username = vanan24 / password = 123456
    user = db.query(User).filter_by(username="vanan24").one_or_none()
    if user is None:
        user = User(
            username="vanan24",
            hashed_password=hash_password("123456"),
            full_name="Nguyễn Văn An",
            gender="male",
            age=24,
            height_cm=172.0,
            weight_kg=70.0,
            fitness_goal="fat_loss",
            daily_budget_vnd=80000.0,
        )
        db.add(user)
        db.flush()

    today = date.today()
    foods = {f.code: f for f in db.query(Food).filter(Food.code.in_(["VN_MEAL_01", "VN_01002", "USDA_173686"]))}
    exercises = {e.code: e for e in db.query(Exercise).filter(Exercise.code.in_(["02050", "12020"]))}

    # Tránh nạp trùng log nếu chạy script nhiều lần trong cùng một ngày
    already_seeded = db.query(FoodLog).filter_by(user_id=user.id, logged_date=today).first() is not None
    if already_seeded:
        db.commit()
        print("[i] Logs mẫu của hôm nay đã tồn tại, bỏ qua.")
        return

    # 2. Thêm food log mẫu cho hôm nay:
    # Bữa sáng: 1 bát phở bò (450g) = ~380 kcal
    # Bữa trưa: 1.5 bát cơm trắng (225g) + 150g ức gà áp chảo
    food_logs = [
        ("VN_MEAL_01", "breakfast", 1.0, 450.0, 379.8, 18.5, 8.55, 57.15),
        ("VN_01002", "lunch", 1.5, 225.0, 130.0 * 2.25, 2.6 * 2.25, 0.3 * 2.25, 28.2 * 2.25),
        ("USDA_173686", "lunch", 1.5, 150.0, 165.0 * 1.5, 31.0 * 1.5, 3.6 * 1.5, 0.0),
    ]
    for code, meal_type, servings, weight_g, cal, protein, fat, carbs in food_logs:
        if code not in foods:
            continue
        db.add(FoodLog(
            user_id=user.id, food_id=foods[code].id, logged_date=today, meal_type=meal_type,
            serving_count=servings, actual_weight_g=weight_g, calculated_calories=cal,
            calculated_protein=protein, calculated_fat=fat, calculated_carbs=carbs,
        ))

    # 3. Thêm workout log mẫu theo đúng công thức:
    # Bài 1: Calisthenics (Hít đất) - MET = 8.0, Cân nặng = 70kg
    # 4 sets, mỗi set 45 giây, nghỉ 60 giây giữa các hiệp
    # Cal/min = 8.0 * 3.5 * 70 / 200 = 9.8 kcal/min
    # T = [(4 * 45) + ((4 - 1) * 60)] / 60 = (180 + 180) / 60 = 6.0 phút
    # Total Calo Burned = 9.8 * 6.0 = 58.8 kcal
    #
    # Bài 2: Chạy bộ 8 km/h - MET = 8.3, 70kg, chạy liên tục 30 phút (1 set = 1800 giây, rest = 0)
    # Cal/min = 8.3 * 3.5 * 70 / 200 = 10.1675 kcal/min
    # Total Calo Burned = 10.1675 * 30.0 = 305.03 kcal
    workout_logs = [
        ("02050", 8.0, 4, 45.0, 60.0, 6.0, 58.8, "Hít đất 4 hiệp x 15 reps"),
        ("12020", 8.3, 1, 1800.0, 0.0, 30.0, 305.03, "Chạy bộ ngoài trời buổi chiều"),
    ]
    for code, met, sets, dur, rest, total_min, burned, notes in workout_logs:
        if code not in exercises:
            continue
        db.add(WorkoutLog(
            user_id=user.id, exercise_id=exercises[code].id, logged_date=today,
            user_weight_kg=70.0, met_applied=met, sets=sets, duration_per_set_sec=dur,
            rest_between_sets_sec=rest, total_duration_minutes=total_min,
            calories_burned=burned, notes=notes,
        ))

    db.commit()
    print("[+] Đã nạp thành công user mẫu và workout/food logs.")


def main():
    print(f"[*] Khởi tạo SQLite Database tại: {DATABASE_URL}")
    init_db()  # Tạo bảng từ models (thay cho schema.sql)
    print("[+] Đã tạo các bảng và indexes thành công.")

    db = SessionLocal()
    try:
        seed_foods(db)
        seed_exercises(db)
        seed_sample_user_and_logs(db)

        # In kiểm tra Cân Bằng Năng Lượng (thay cho VIEW v_daily_energy_balance)
        print("\n--- BÁO CÁO CÂN BẰNG NĂNG LƯỢNG MẪU ---")
        for row in get_daily_energy_balance(db):
            print(
                f"User ID: {row['user_id']} | Ngày: {row['log_date']} | "
                f"Calo nạp: {row['total_calories_in']} kcal | "
                f"Calo đốt: {row['total_calories_burned']} kcal (Tập {row['total_workout_minutes']} phút) | "
                f"Net: {row['net_calories']} kcal"
            )
        print("---------------------------------------------------------------------\n")
        print(f"[SUCCESS] Cơ sở dữ liệu SQLite đã sẵn sàng tại: {DATABASE_URL}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
