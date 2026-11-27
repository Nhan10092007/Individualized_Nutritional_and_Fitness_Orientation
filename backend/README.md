# Backend - Fitness & Nutrition API

Hệ thống API backend xây dựng bằng **FastAPI**, **SQLAlchemy ORM** và **PostgreSQL**, hỗ trợ tính toán dinh dưỡng, phân tích năng lượng và cá nhân hóa lịch tập.

---

## 1. Cài đặt môi trường Python

Từ thư mục `backend/`:

**Linux / macOS / WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

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

---

## 2. Khởi tạo PostgreSQL Server & Cấu hình `.env`

### Bước 2.1: Bật PostgreSQL và tạo User + Database (Ubuntu / WSL)

```bash
# 1. Khởi động PostgreSQL Server (port mặc định: 5432)
sudo service postgresql start

# 2. Tạo user PostgreSQL mới (thay <ten_user> và <mat_khau> bằng thông tin của bạn, hoặc dùng user postgres có sẵn)
sudo -u postgres psql -c "CREATE USER <ten_user> WITH PASSWORD '<mat_khau>' CREATEDB SUPERUSER;"

# (Nếu muốn đổi lại mật khẩu cho user đã có):
# sudo -u postgres psql -c "ALTER USER <ten_user> WITH PASSWORD '<mat_khau>';"

# 3. Tạo database fitness_app
sudo -u postgres psql -c "CREATE DATABASE fitness_app OWNER <ten_user>;"
```

### Bước 2.2: Cấu hình `DATABASE_URL` trong `backend/.env`

Tạo hoặc mở file `backend/.env` và khai báo chuỗi kết nối (dùng prefix `postgresql+psycopg://` cho thư viện `psycopg` v3 trong `requirements.txt`):

```env
DATABASE_URL=postgresql+psycopg://<ten_user>:<mat_khau>@localhost:5432/fitness_app
```

---

## 3. Khởi tạo Bảng & Nạp dữ liệu vào PostgreSQL (SQLAlchemy ORM)

Hệ thống dùng **SQLAlchemy ORM** (`app/models/`) để tự động sinh cấu trúc bảng (`Base.metadata.create_all`) và nạp dữ liệu chuẩn hóa:
- **Thực phẩm (Calo IN):** Danh mục thực phẩm quen thuộc từ `backend/data/vietnam_foods_curated.json`.
- **Bài tập (Calo BURN):** 65 bài tập chuẩn hóa từ `backend/data/exercises_65.json`.

Từ thư mục `backend/` (sau khi đã kích hoạt `.venv` và bật PostgreSQL):

```bash
# Tự động tạo bảng (nếu chưa có) và nạp mới danh mục thực phẩm + bài tập
python -m scripts.import_curated_json

# Nếu muốn xóa luôn toàn bộ dữ liệu bảng users khi reset:
python -m scripts.import_curated_json --reset-users
```

Hoặc chạy script seed kèm tài khoản mẫu (`vanan24@gmail.com` / `123456`):

```bash
python -m scripts.seed_database
```

---

## 4. Xem dữ liệu PostgreSQL bằng Extension hoặc Terminal

### Cách 1: Dùng Extension **PostgreSQL** trên VS Code / IDE
1. Mở tab **Extensions** (`Ctrl + Shift + X`), tìm và cài extension **PostgreSQL** (hoặc **Database Client**).
2. Bấm vào biểu tượng **PostgreSQL** ở thanh bên trái $\rightarrow$ bấm **`+` (Add Connection)** và nhập:
   - **Server name / Hostname:** `localhost`
   - **User name:** `<ten_user>` (user PostgreSQL của bạn, hoặc `postgres`)
   - **Password:** `<mat_khau>` (mật khẩu tương ứng)
   - **Port:** `5432`
   - **Connection type / SSL:** Chọn **`Standard Connection`** hoặc **`Disable`**
   - **Database name:** `fitness_app`
   - **Display name:** `fitness_app`
3. Mở nhánh: `fitness_app` $\rightarrow$ **`Schemas`** $\rightarrow$ **`public`** $\rightarrow$ **`Tables`**.
4. Click chuột phải vào bảng cần xem (`foods`, `exercises`, `users`, `food_logs`, `workout_logs`, `meal_plans`, `workout_plans`) $\rightarrow$ chọn **`Select Top 1000`** (hoặc **`View Data`**).

### Cách 2: Xem trực tiếp trên Terminal bằng `psql`

```bash
# Xem danh sách các bảng trong fitness_app
psql "postgresql://<ten_user>:<mat_khau>@localhost:5432/fitness_app" -c "\dt"

# Xem thử 10 món ăn đầu tiên
psql "postgresql://<ten_user>:<mat_khau>@localhost:5432/fitness_app" -c "SELECT id, code, name_vi, calories_100g, estimated_price_vnd FROM foods LIMIT 10;"

# Xem thử 10 bài tập đầu tiên
psql "postgresql://<ten_user>:<mat_khau>@localhost:5432/fitness_app" -c "SELECT id, category, name_vi, intensity_level, target_muscle FROM exercises LIMIT 10;"
```

---

## 5. Chạy API Server

```bash
uvicorn app.main:app --reload
# Hoặc:
fastapi dev app/main.py
```

- API Server: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
