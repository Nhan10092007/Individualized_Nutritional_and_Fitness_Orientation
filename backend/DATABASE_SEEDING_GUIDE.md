# Hướng Dẫn Khởi Tạo Database (SQLAlchemy ORM) & Nạp Dữ Liệu Local

> **Lưu ý quan trọng cho cả nhóm:**  
> Database của dự án là **local trên từng máy** (file `*.db` và `.env` được ignore trong `.gitignore`, không chia sẻ trực tiếp qua Git). Mỗi thành viên sau khi pull code mới cần tự chạy lệnh để **sinh cấu trúc bảng từ SQLAlchemy Models** và **nạp dữ liệu khởi tạo** về máy của mình.

---

## 1. Kiến trúc Database hiện tại: SQLAlchemy ORM (Không dùng file `.sql`)

Dự án đã chuyển hoàn toàn từ cách tạo bảng bằng SQL thuần (`schema.sql` / `sqlite3`) sang **SQLAlchemy ORM (`2.x`)**:

* Toàn bộ cấu trúc bảng được định nghĩa dưới dạng Python class trong `backend/app/models/`:
  * `app/models/user.py` → bảng `users` (tài khoản đăng nhập + thông tin onboarding A1 + các chỉ số BMI, IBW, BMR, TDEE, Macro, `banned_exercise_tags`)
  * `app/models/food.py` → bảng `foods` (dữ liệu dinh dưỡng trên 100g, khẩu phần, giá ước tính VNĐ, `diet_type`, nguồn `USDA` / `VN_FCT` / `CUSTOM`)
  * `app/models/exercise.py` → bảng `exercises` (50 bài tập chuẩn hóa gồm `id`, `category`, `name_vi`, `name_en`, `met_value`, `intensity_level`, `description`, `equipment`, `instructions`, `common_mistakes`, `image`, `video_url`, `target_muscle`, `secondary_muscle`, `banned_for`, `clinical_reasons`, `source`)
  * `app/models/meal.py` → bảng `food_logs` (nhật ký ăn uống – Calo IN, khóa ngoại tới `users.id` và `foods.id`)
  * `app/models/workout.py` → bảng `workout_logs` (nhật ký tập luyện – Calo BURN, khóa ngoại tới `users.id` và `exercises.id`)
  * `app/models/__init__.py` → gom và đăng ký tất cả model vào `Base.metadata`.
* File `backend/app/database.py` cung cấp hàm `init_db()` gọi `Base.metadata.create_all(bind=engine)` để **tự động sinh toàn bộ bảng, khóa ngoại, `CHECK` constraints và index** tương thích với cả **SQLite** lẫn **PostgreSQL**.
* Các script trong `backend/scripts/` đều ghi dữ liệu thông qua `SessionLocal()` và các ORM model, sử dụng cơ chế upsert theo cột `code` để chạy lại nhiều lần không bị trùng dữ liệu.
* Tổng hợp cân bằng năng lượng hằng ngày (`get_daily_energy_balance`) được thực hiện bằng truy vấn SQLAlchemy trong `app/services/progress_service.py` (thay thế cho SQL `VIEW` trước đây).

---

## 2. Kiến trúc Pipeline ETL & Dữ liệu Chuẩn hóa

Dữ liệu được xử lý tự động và nạp vào DB theo đúng yêu cầu:

1. **Thực phẩm (Calo IN) & Giá cả Bách Hóa Xanh (VND)**:
   * **Lọc danh mục thực phẩm quen thuộc**: Chuẩn hóa chính xác 80 nguyên liệu và món ăn quen thuộc hàng ngày (Gạo, ức gà, thịt heo, thịt bò, trứng, cá hồi, rau muống, đậu phụ, phở, bún bò, cơm tấm...) loại bỏ hoàn toàn các loại củ/thịt thú rừng hiếm gặp.
   * **Dinh dưỡng chuẩn**: Định lượng Calories, Protein, Lipid, Glucid, Xơ từ **Viện Dinh Dưỡng Quốc Gia 2017** và **USDA FoodData Central**.
   * **Crawl giá thị trường**: Script Python `scripts/etl/crawl_bhx_prices.py` tự động crawl giá niêm yết từ siêu thị **Bách Hóa Xanh** (`bachhoaxanh.com`) và tính toán đơn giá theo 100g/khẩu phần (`estimated_price_vnd`) hỗ trợ thuật toán tối ưu chi phí A5.
2. **Bài tập (Calo BURN)**: Trích xuất **đúng 50 bài tập nền tảng** từ `backend/data/raw/exercises.json` phủ đều 11 nhóm cơ chính (`Chest`, `Back`, `Shoulders`, `Rear Delts`, `Biceps`, `Triceps`, `Quadriceps`, `Hamstrings`, `Glutes`, `Calves`, `Abs`) phục vụ hoàn hảo cho thuật toán sinh lịch tập A4 và bộ lọc chống chỉ định bệnh lý A3 (`banned_for`, `clinical_reasons`).
3. **Asset Handling**: Gắn link ảnh minh họa bài tập phân giải cao trực tiếp từ CDN GitHub (`https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/...`) không cần cấu hình key cloud.
4. **Load vào DB**: Gọi `init_db()` sinh bảng từ SQLAlchemy ORM models và nạp dữ liệu an toàn (upsert theo code / tên) vào SQLite hoặc PostgreSQL.

---

## 3. Chuẩn bị môi trường Backend

Mở terminal và di chuyển vào thư mục `backend/`:

```bash
cd backend
```

### 3.1. Tạo và kích hoạt Virtual Environment (`.venv`)

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

*(Nếu PowerShell báo chặn script, chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` rồi kích hoạt lại).*

**Windows (Git Bash / MINGW64):**

```bash
py -m venv .venv
source .venv/Scripts/activate
```

**Linux / macOS / WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3.2. Cài đặt thư viện phụ thuộc

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 4. Cấu hình Database Local & Asset Storage (`.env`)

Tạo file `backend/.env` (copy từ `backend/.env.example`) và chọn **1 trong 2** cấu hình database dưới đây:

### Lựa chọn A — SQLite local (Mặc định, nhanh nhất, không cần cài DB server)

```dotenv
DATABASE_URL=sqlite:///./fitness_app.db
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
GEMINI_API_KEY=

# Step 2 Asset Handling (mặc định dùng CDN GitHub không cần key)
ASSET_STORAGE_PROVIDER=github_cdn
ASSET_BASE_URL=https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises
```

* Đường dẫn tương đối `sqlite:///./fitness_app.db` được `app/database.py` tự động quy đổi về `backend/fitness_app.db`.
* Khi dùng SQLite, `app/database.py` tự bật `PRAGMA foreign_keys=ON` để kiểm tra khóa ngoại.
* *(Lưu ý: Nếu trong `backend/` còn file `fitness_nutrition.db` từ phiên bản SQL cũ trước đây, hãy xóa hoặc bỏ qua — cấu hình hiện tại dùng `fitness_app.db`).*

### Lựa chọn B — PostgreSQL local (Theo tech stack chung của dự án)

1. Đảm bảo PostgreSQL đang chạy trên máy và tạo sẵn một database trống (ví dụ `fitness_app`):
   ```sql
   CREATE DATABASE fitness_app;
   ```
2. Trong `backend/.env`, đổi `DATABASE_URL` sang chuỗi kết nối PostgreSQL (`psycopg` driver đã có sẵn trong `requirements.txt`):
   ```dotenv
   DATABASE_URL=postgresql+psycopg://<DB_USER>:<DB_PASSWORD>@localhost:5432/fitness_app
   ```
3. Không cần chạy file `.sql` tạo bảng — bước chạy script ở Mục 5 sẽ gọi `init_db()` để SQLAlchemy ORM tự sinh toàn bộ bảng trên PostgreSQL.

*(Tùy chọn Asset Handling lên Cloud: Nếu muốn upload ảnh thật lên Cloudinary hoặc AWS S3, đổi `ASSET_STORAGE_PROVIDER=cloudinary` hoặc `s3` và điền các biến tương ứng trong `.env.example`, sau đó chạy kèm cờ `--upload-assets`).*

---

## 5. Các lệnh khởi tạo bảng & nạp dữ liệu

> **Quy tắc chạy lệnh:** Luôn đứng ở thư mục gốc `backend/` (khi `.venv` đã được kích hoạt) và chạy bằng `python -m scripts.<ten_script>`.

### Cách 1 (Khuyên dùng — Chạy lệnh nạp cơ sở dữ liệu nhanh & đầy đủ)

```bash
python -m scripts.seed_database
```

Lệnh này thực hiện tự động toàn bộ quy trình:
1. Sinh đủ 5 bảng từ SQLAlchemy ORM models (`init_db()`).
2. Nạp **590+ thực phẩm** từ Bảng thành phần dinh dưỡng thực phẩm VN 2017 (file PDF) cùng các thực phẩm thô USDA và món ăn hàng ngày.
3. Nạp **đúng 50 bài tập chọn lọc** từ `backend/data/raw/exercises.json` phủ đều 10 nhóm cơ lớn, khớp 100% các cột (`category`, `name_vi`, `name_en`, `met_value`, `intensity_level`, `instructions`, `common_mistakes`, `image`, `target_muscle`, `secondary_muscle`, `banned_for`, `clinical_reasons`).
4. Tạo **1 tài khoản mẫu** (`username`: `vanan24@gmail.com`, `password`: `123456`) kèm `food_logs` và `workout_logs` mẫu cho ngày hôm nay để xem ngay Dashboard.

### Cách 2 (Chạy pipeline ETL trích xuất lại từ đầu)

```bash
python -m scripts.run_etl_pipeline
```

# Tự tải lại từ GitHub nếu thư mục backend/data/raw/ bị thiếu file
python -m scripts.run_etl_pipeline --download-missing
```

### Cách 2 (Tối giản — Chỉ nạp dữ liệu mẫu gọn nhẹ để test nhanh)

```bash
python -m scripts.seed_database
```

Chỉ nạp **39 thực phẩm** + **38 bài tập cốt lõi** + **1 user mẫu (`vanan24` / `123456`)** và in báo cáo cân bằng năng lượng.

### Cách 3 (Tùy chọn khi có mạng — Kéo thêm từ USDA API & kiểm tra file PDF 2017)

```bash
python -m scripts.fetch_and_seed_from_urls
```

---

## 6. Kiểm tra nhanh Database sau khi nạp

Đứng tại thư mục `backend/` (đã kích hoạt `.venv`), chạy lệnh Python sau để kiểm tra số bản ghi trực tiếp qua SQLAlchemy ORM (dùng giống nhau cho cả SQLite và PostgreSQL):

```bash
python -c "from app.database import SessionLocal; from app.models import User, Food, Exercise, FoodLog, WorkoutLog; db = SessionLocal(); print('users:', db.query(User).count(), '| foods:', db.query(Food).count(), '| exercises:', db.query(Exercise).count(), '| food_logs:', db.query(FoodLog).count(), '| workout_logs:', db.query(WorkoutLog).count()); db.close()"
```

Sau khi chạy `python -m scripts.run_etl_pipeline`, bạn sẽ thấy:
* `users: 1`
* `foods: 39`
* `exercises: ~1900+` (gộp từ `exercises.json`, `compendium_github.csv`, `exercise_dataset.csv`)
* `food_logs: 3`, `workout_logs: 2`

---

## 7. Cách làm mới (Reset) Database khi Models thay đổi

Vì dự án dùng `Base.metadata.create_all()` (chưa chạy Alembic `ALTER TABLE` tự động khi thêm cột mới vào models):

* **Nếu dùng SQLite:** Xóa file `backend/fitness_app.db`, sau đó chạy lại:
  ```bash
  python -m scripts.run_etl_pipeline
  ```
* **Nếu dùng PostgreSQL:** Drop và tạo lại database (hoặc drop toàn bộ bảng), sau đó chạy lại:
  ```bash
  python -m scripts.run_etl_pipeline
  ```
