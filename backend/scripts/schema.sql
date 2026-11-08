-- ==============================================================================
-- DATABASE SCHEMA: FITNESS & NUTRITION (SQLite)
-- Chuẩn 3NF, hỗ trợ Calo In (USDA + VN_FCT) và Calo Burn (MET Compendium)
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. Bảng Người dùng (User Profile - lưu thông số sinh trắc học để tính Calo tiêu thụ cá nhân)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    gender TEXT CHECK(gender IN ('male', 'female', 'other')) NOT NULL DEFAULT 'male',
    age INTEGER CHECK(age > 0 AND age < 120) NOT NULL,
    height_cm REAL CHECK(height_cm > 50 AND height_cm < 250) NOT NULL,
    weight_kg REAL CHECK(weight_kg > 20 AND weight_kg < 300) NOT NULL,
    fitness_goal TEXT CHECK(fitness_goal IN ('fat_loss', 'muscle_gain', 'maintain')) DEFAULT 'maintain',
    activity_level TEXT CHECK(activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')) DEFAULT 'moderate',
    daily_budget_vnd REAL DEFAULT 50000.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Bảng Danh mục Thực phẩm (Foods - Calo IN: USDA 100g & Khẩu phần Việt Nam)
CREATE TABLE IF NOT EXISTS foods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,                       -- Mã USDA FDC ID (vd: 'USDA_171077') hoặc Mã Viện Dinh Dưỡng (vd: 'VN_01001')
    name_vi TEXT NOT NULL,                  -- Tên tiếng Việt (vd: Ức gà phi lê, Cơm trắng, Phở bò)
    name_en TEXT,                           -- Tên tiếng Anh (vd: Chicken breast fillet, White cooked rice)
    category TEXT NOT NULL,                 -- Nhóm: Ngũ cốc, Thịt/Gia cầm, Thủy hải sản, Rau củ, Món chế biến sẵn...
    source TEXT CHECK(source IN ('USDA', 'VN_FCT', 'CUSTOM')) NOT NULL, -- Nguồn dữ liệu
    serving_unit TEXT NOT NULL DEFAULT '100g', -- Đơn vị khẩu phần thông dụng (vd: '100g', '1 bát (150g)', '1 quả (50g)', '1 tô (450g)')
    serving_weight_g REAL NOT NULL DEFAULT 100.0, -- Trọng lượng tương ứng với 1 serving_unit (tính bằng gam)
    calories_100g REAL NOT NULL,            -- Năng lượng trên 100g (kcal)
    protein_100g REAL NOT NULL DEFAULT 0.0, -- Đạm trên 100g (g)
    fat_100g REAL NOT NULL DEFAULT 0.0,     -- Béo trên 100g (g)
    carbs_100g REAL NOT NULL DEFAULT 0.0,   -- Tinh bột trên 100g (g)
    fiber_100g REAL DEFAULT 0.0,            -- Chất xơ trên 100g (g)
    estimated_price_vnd REAL DEFAULT 0.0,   -- Giá tiền ước tính / 100g hoặc / khẩu phần (hỗ trợ phân hệ A5 ngân sách)
    diet_type TEXT DEFAULT 'all',           -- 'all', 'vegetarian', 'vegan'
    notes TEXT,                             -- Ghi chú thêm (vd: tỷ lệ phần ăn được 80%...)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng Danh mục Bài tập / Hoạt động Thể chất (Exercises - Calo BURN: Compendium of Physical Activities)
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT,                              -- Mã 5 chữ số trong Ainsworth Compendium 2011 (vd: '02050', '12020')
    category TEXT NOT NULL,                 -- Nhóm: Conditioning, Running, Cycling, Sports, Walking, Water Activities...
    name_vi TEXT NOT NULL,                  -- Tên tiếng Việt (vd: Hít đất, Chạy bộ 8km/h, Nâng tạ tự do)
    name_en TEXT NOT NULL,                  -- Tên tiếng Anh (vd: Calisthenics, Running 5 mph, Weight lifting)
    met_value REAL NOT NULL CHECK(met_value > 0), -- Chỉ số MET khoa học (1 MET = 3.5 ml O2/kg/min)
    intensity_level TEXT CHECK(intensity_level IN ('Light', 'Moderate', 'Vigorous')) NOT NULL DEFAULT 'Moderate',
    description TEXT,                       -- Chi tiết kỹ thuật / tốc độ / tải trọng
    source TEXT DEFAULT 'Compendium 2011',  -- Nguồn: 'Compendium 2011', 'Kaggle', 'Custom'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bảng Nhật ký Ăn uống (Food Intake Log - Calo IN)
CREATE TABLE IF NOT EXISTS food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    food_id INTEGER NOT NULL,
    logged_date DATE NOT NULL,              -- Ngày ăn (YYYY-MM-DD)
    meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')) NOT NULL,
    serving_count REAL NOT NULL DEFAULT 1.0, -- Số lượng khẩu phần (vd: 1.5 bát cơm, 2 quả trứng)
    actual_weight_g REAL NOT NULL,          -- Khối lượng thực tế nạp vào (gam)
    calculated_calories REAL NOT NULL,      -- Calo nạp vào = (actual_weight_g / 100.0) * calories_100g
    calculated_protein REAL NOT NULL,       -- Protein nạp vào (g)
    calculated_fat REAL NOT NULL,           -- Fat nạp vào (g)
    calculated_carbs REAL NOT NULL,         -- Carbs nạp vào (g)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES foods(id) ON DELETE RESTRICT
);

-- 5. Bảng Nhật ký Tập luyện (Workout Log - Calo BURN)
-- Tính theo chuẩn: Cal/min = MET * 3.5 * Body_Weight / 200
-- T (phút) = [(sets * duration_per_set_sec) + ((sets - 1) * rest_between_sets_sec)] / 60
-- Total Calo = Cal/min * T
CREATE TABLE IF NOT EXISTS workout_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    logged_date DATE NOT NULL,              -- Ngày tập (YYYY-MM-DD)
    user_weight_kg REAL NOT NULL,           -- Cân nặng người dùng tại thời điểm tập
    met_applied REAL NOT NULL,              -- Giá trị MET áp dụng
    sets INTEGER NOT NULL DEFAULT 1 CHECK(sets >= 1), -- Số set tập
    duration_per_set_sec REAL NOT NULL CHECK(duration_per_set_sec > 0), -- Thời gian 1 set (giây)
    rest_between_sets_sec REAL NOT NULL DEFAULT 0.0 CHECK(rest_between_sets_sec >= 0), -- Thời gian nghỉ giữa các set (giây)
    total_duration_minutes REAL NOT NULL,   -- Tổng thời gian T (phút)
    calories_burned REAL NOT NULL,          -- Tổng calo tiêu thụ (kcal)
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE RESTRICT
);

-- ==============================================================================
-- INDEXES & PERFORMANCE OPTIMIZATIONS
-- ==============================================================================
CREATE INDEX IF NOT EXISTS idx_foods_name_vi ON foods(name_vi);
CREATE INDEX IF NOT EXISTS idx_foods_category ON foods(category);
CREATE INDEX IF NOT EXISTS idx_foods_source ON foods(source);

CREATE INDEX IF NOT EXISTS idx_exercises_category ON exercises(category);
CREATE INDEX IF NOT EXISTS idx_exercises_met ON exercises(met_value);

CREATE INDEX IF NOT EXISTS idx_food_logs_user_date ON food_logs(user_id, logged_date);
CREATE INDEX IF NOT EXISTS idx_workout_logs_user_date ON workout_logs(user_id, logged_date);

-- ==============================================================================
-- VIEW: TỔNG HỢP CÂN BẰNG NĂNG LƯỢNG HÀNG NGÀY (DAILY ENERGY BALANCE VIEW)
-- Calo In vs Calo Burned & Net Calo
-- ==============================================================================
CREATE VIEW IF NOT EXISTS v_daily_energy_balance AS
SELECT 
    COALESCE(fl.user_id, wl.user_id) AS user_id,
    COALESCE(fl.logged_date, wl.logged_date) AS log_date,
    COALESCE(fl.total_cal_in, 0.0) AS total_calories_in,
    COALESCE(fl.total_protein_g, 0.0) AS total_protein_g,
    COALESCE(fl.total_fat_g, 0.0) AS total_fat_g,
    COALESCE(fl.total_carbs_g, 0.0) AS total_carbs_g,
    COALESCE(wl.total_cal_burn, 0.0) AS total_calories_burned,
    COALESCE(wl.total_workout_minutes, 0.0) AS total_workout_minutes,
    (COALESCE(fl.total_cal_in, 0.0) - COALESCE(wl.total_cal_burn, 0.0)) AS net_calories
FROM (
    SELECT 
        user_id, 
        logged_date,
        ROUND(SUM(calculated_calories), 2) AS total_cal_in,
        ROUND(SUM(calculated_protein), 2) AS total_protein_g,
        ROUND(SUM(calculated_fat), 2) AS total_fat_g,
        ROUND(SUM(calculated_carbs), 2) AS total_carbs_g
    FROM food_logs
    GROUP BY user_id, logged_date
) fl
FULL OUTER JOIN (
    SELECT 
        user_id, 
        logged_date,
        ROUND(SUM(calories_burned), 2) AS total_cal_burn,
        ROUND(SUM(total_duration_minutes), 2) AS total_workout_minutes
    FROM workout_logs
    GROUP BY user_id, logged_date
) wl ON fl.user_id = wl.user_id AND fl.logged_date = wl.logged_date;
