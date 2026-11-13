# Backend - Fitness & Nutrition API

Hệ thống API backend xây dựng bằng **FastAPI** và **SQLAlchemy ORM** (hỗ trợ **SQLite** local mặc định và **PostgreSQL**), hỗ trợ tính toán dinh dưỡng, phân tích năng lượng và cá nhân hóa lịch tập.

---

## 1. Cài đặt môi trường

Từ thư mục `backend/`:

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Windows (Git Bash / MINGW64):**

```bash
py -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

**Linux / macOS / WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

---

## 2. Khởi tạo & Nạp dữ liệu vào Database (SQLAlchemy ORM)

Hệ thống dùng **SQLAlchemy ORM** (`app/models/`) để tự động sinh cấu trúc bảng (không dùng file `.sql`) và chạy **Pipeline ETL 4 bước** (`Extract -> Asset Handling -> Transform & Map MET -> Load`).

### Lệnh chính: Chạy Pipeline ETL 4 bước đầy đủ

Từ thư mục `backend/` (sau khi kích hoạt `.venv`):

```bash
python -m scripts.run_etl_pipeline
```

Lệnh này sẽ tự động:
1. Sinh toàn bộ các bảng (`users`, `foods`, `exercises`, `food_logs`, `workout_logs`) trong `fitness_app.db` (hoặc PostgreSQL nếu cấu hình `DATABASE_URL` trong `.env`).
2. Nạp **39 thực phẩm chuẩn hóa** (USDA và Bảng thành phần dinh dưỡng thực phẩm VN 2017 kèm giá tiền ước tính).
3. Chạy 4 bước ETL trên `backend/data/raw/` (`exercises.json`, `compendium_github.csv`, `exercise_dataset.csv`) để chuẩn hóa schema, ánh xạ URL ảnh/asset, gắn chỉ số **MET** và nhãn chống chỉ định **A3**.
4. Tạo sẵn **1 tài khoản mẫu** (`vanan24` / `123456`) kèm nhật ký ăn uống & tập luyện mẫu.

### Lệnh rút gọn (chỉ nạp bộ dữ liệu mẫu gọn nhẹ)

```bash
python -m scripts.seed_database
```

Xem hướng dẫn chi tiết (cấu hình SQLite/PostgreSQL, Cloudinary/S3, kiểm tra dữ liệu và reset DB) tại [DATABASE_SEEDING_GUIDE.md](./DATABASE_SEEDING_GUIDE.md).

---

## 3. Chạy API Server

```bash
fastapi dev app/main.py
```

Swagger UI: `http://127.0.0.1:8000/docs`
