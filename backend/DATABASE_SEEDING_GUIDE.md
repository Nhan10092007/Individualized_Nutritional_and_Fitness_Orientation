# Hướng Dẫn Khởi Tạo Database (SQLAlchemy ORM) & Nạp Dữ Liệu Local

> **Lưu ý quan trọng cho cả nhóm:**  
> Database của dự án là **local trên từng máy** (file `*.db` và `.env` được ignore trong `.gitignore`, không chia sẻ trực tiếp qua Git). Mỗi thành viên sau khi pull code mới cần tự chạy lệnh để **sinh cấu trúc bảng từ SQLAlchemy Models** và **nạp dữ liệu khởi tạo** về máy của mình.

---

## 1. Kiến trúc Database hiện tại: SQLAlchemy ORM (Không dùng file `.sql`)

Dự án đã chuyển hoàn toàn từ cách tạo bảng bằng SQL thuần (`schema.sql` / `sqlite3`) sang **SQLAlchemy ORM (`2.x`)**:

* Toàn bộ cấu trúc bảng được định nghĩa dưới dạng Python class trong `backend/app/models/`:
  * `app/models/user.py` → bảng `users` (tài khoản đăng nhập + thông tin onboarding A1 + các chỉ số BMI, IBW, BMR, TDEE, Macro, `banned_exercise_tags`)
  * `app/models/food.py` → bảng `foods` (dữ liệu dinh dưỡng trên 100g, khẩu phần, giá ước tính VNĐ, `diet_type`, nguồn `USDA` / `VN_FCT` / `CUSTOM`)
  * `app/models/exercise.py` → bảng `exercises` (bài tập kèm `met_value`, `intensity_level`, nhóm cơ `primary_muscles`/`secondary_muscles`, `equipment`, `level`, `instructions`, URL media `image_urls`/`thumbnail_url`/`video_url`, và nhãn chống chỉ định A3 `banned_for`/`clinical_reason`)
  * `app/models/meal.py` → bảng `food_logs` (nhật ký ăn uống – Calo IN, khóa ngoại tới `users.id` và `foods.id`)
  * `app/models/workout.py` → bảng `workout_logs` (nhật ký tập luyện – Calo BURN, khóa ngoại tới `users.id` và `exercises.id`)
  * `app/models/__init__.py` → gom và đăng ký tất cả model vào `Base.metadata`.
* File `backend/app/database.py` cung cấp hàm `init_db()` gọi `Base.metadata.create_all(bind=engine)` để **tự động sinh toàn bộ bảng, khóa ngoại, `CHECK` constraints và index** tương thích với cả **SQLite** lẫn **PostgreSQL**.
* Các script trong `backend/scripts/` đều ghi dữ liệu thông qua `SessionLocal()` và các ORM model, sử dụng cơ chế upsert theo cột `code` để chạy lại nhiều lần không bị trùng dữ liệu.
* Tổng hợp cân bằng năng lượng hằng ngày (`get_daily_energy_balance`) được thực hiện bằng truy vấn SQLAlchemy trong `app/services/progress_service.py` (thay thế cho SQL `VIEW` trước đây).

---

## 2. Kiến trúc Pipeline ETL 4 bước (`backend/scripts/etl/`)

Dữ liệu bài tập từ các nguồn GitHub/Kaggle được xử lý đúng theo 4 bước:

1. **Bước 1 — Extract (`scripts/etl/extract.py`)**: Đọc các file raw trong `backend/data/raw/` (`exercises.json`, `compendium_github.csv`, `exercise_dataset.csv`, `megaGymDataset.csv`) hoặc tự tải từ GitHub nếu thiếu (`--download-missing`).
2. **Bước 2 — Asset Handling (`scripts/etl/asset_handler.py`)**: Chuẩn hóa/tải Ảnh, GIF, Video theo biến `ASSET_STORAGE_PROVIDER` trong `.env`:
   * `github_cdn` *(mặc định local)*: ánh xạ sang `ASSET_BASE_URL` (không cần tài khoản cloud).
   * `cloudinary`: upload media qua Cloudinary REST API và cache ánh xạ vào `backend/data/processed/asset_manifest.json`.
   * `s3`: upload media lên AWS S3 bucket (cần cài thêm `boto3`).
3. **Bước 3 — Transform & Map MET (`scripts/etl/transform.py`)**: Chuẩn hóa schema khớp với model `Exercise`, tự động map chỉ số `met_value` + `intensity_level` theo chuẩn Ainsworth 2011, và suy luận `banned_for` / `clinical_reason` cho thuật toán A3.
4. **Bước 4 — Load (`scripts/etl/load.py`)**: Gọi `init_db()` sinh bảng từ SQLAlchemy models và nạp hàng loạt qua `SessionLocal()` vào **SQLite** hoặc **PostgreSQL**.

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

### Cách 1 (Khuyên dùng — Chạy trọn bộ ETL 4 bước + dữ liệu cốt lõi)

```bash
python -m scripts.run_etl_pipeline
```

Lệnh này thực hiện tự động toàn bộ quy trình:
1. Sinh đủ 5 bảng từ SQLAlchemy ORM models (`init_db()`).
2. Nạp **39 thực phẩm chuẩn hóa** (16 từ USDA + 23 từ Bảng thành phần dinh dưỡng thực phẩm VN 2017 kèm giá tiền và `diet_type`).
3. **Extract + Asset Handling + Transform & Map MET + Load** toàn bộ các bộ dữ liệu bài tập trong `backend/data/raw/`:
   * `exercises.json` (876 bài tập có ảnh, nhóm cơ, thiết bị, hướng dẫn)
   * `compendium_github.csv` (820 hoạt động chuẩn Ainsworth 2011)
   * `exercise_dataset.csv` (248 hoạt động Kaggle quy đổi MET từ calo/giờ @ 155 lb)
4. Tạo **1 tài khoản mẫu** (`username`: `vanan24`, `password`: `123456`) kèm `food_logs` và `workout_logs` mẫu cho ngày hôm nay.

**Các tùy chọn mở rộng của `run_etl_pipeline`:**

```bash
# Nạp thêm megaGymDataset.csv (2.918 bài tập)
python -m scripts.run_etl_pipeline --include-megagym

# Upload ảnh thật lên Cloudinary / S3 (cần điền credentials trong .env)
python -m scripts.run_etl_pipeline --upload-assets --provider cloudinary

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
