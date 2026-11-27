# Fitness & Nutrition

Ứng dụng web lập kế hoạch tập luyện, thực đơn dinh dưỡng cá nhân hóa và theo dõi năng lượng hằng ngày.

- **Backend:** FastAPI + SQLAlchemy ORM + PostgreSQL (`backend/`)
- **Frontend:** React + Vite (`frontend/`)

---

## 1. Thiết lập PostgreSQL (Local / Ubuntu / WSL)

### Bước 1.1: Khởi động PostgreSQL Server & Tạo User / Database

Mở Terminal và chạy các lệnh sau:

```bash
# 1. Bật PostgreSQL service (trên WSL/Ubuntu mỗi lần mở lại máy cần bật lại)
sudo service postgresql start

# 2. Kiểm tra trạng thái (đảm bảo hiện port 5432: online)
service postgresql status

# 3. Tạo user riêng (thay <ten_user> và <mat_khau> bằng tên & mật khẩu của bạn)
#    Hoặc có thể dùng luôn user mặc định 'postgres'
sudo -u postgres psql -c "CREATE USER <ten_user> WITH PASSWORD '<mat_khau>' CREATEDB SUPERUSER;"
# (Nếu muốn đặt/đổi mật khẩu cho user 'postgres' hoặc user đã tồn tại):
# sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '<mat_khau>';"

# 4. Tạo database fitness_app thuộc quyền sở hữu của user vừa tạo
sudo -u postgres psql -c "CREATE DATABASE fitness_app OWNER <ten_user>;"
```

### Bước 1.2: Các lệnh `psql` tra cứu nhanh trên Terminal

```bash
# Xem danh sách toàn bộ Database
sudo -u postgres psql -c "\l"

# Xem danh sách toàn bộ User (Role)
sudo -u postgres psql -c "\du"

# Xem danh sách các bảng (Tables) trong database fitness_app
psql "postgresql://<ten_user>:<mat_khau>@localhost:5432/fitness_app" -c "\dt"
```

*(Nếu đang ở bên trong giao diện `postgres=#`: dùng `\l` xem DB, `\du` xem user, `\c fitness_app` để chuyển vào DB, `\dt` xem bảng, `q` để thoát danh sách dài, `\q` để thoát `psql`).*

---

## 2. Cài đặt & Seed Database (Backend)

Đứng tại thư mục `backend/`:

```bash
cd backend

# Tạo file .env nếu chưa có
cp .env.example .env
```

Mở file `backend/.env` và cấu hình `DATABASE_URL` trỏ tới PostgreSQL vừa tạo (lưu ý dùng prefix `postgresql+psycopg://` vì project sử dụng driver **Psycopg 3**):

```env
DATABASE_URL=postgresql+psycopg://<ten_user>:<mat_khau>@localhost:5432/fitness_app
```

Kích hoạt môi trường ảo và nạp dữ liệu thực phẩm (`data/vietnam_foods_curated.json`) + bài tập (`data/exercises_65.json`) vào PostgreSQL:

```bash
# Tạo & kích hoạt virtual environment (nếu chưa có .venv thì chạy: python3 -m venv .venv)
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1

# Cài dependencies (lần đầu)
pip install -r requirements.txt

# Tự động sinh toàn bộ bảng trên PostgreSQL và nạp dữ liệu chuẩn từ 2 file JSON
# (Giữ lại bảng users hiện có, chỉ làm mới danh mục món ăn, bài tập và lịch/log phụ thuộc)
python -m scripts.import_curated_json

# Hoặc xóa luôn toàn bộ tài khoản users khi reset
python -m scripts.import_curated_json --reset-users
```

---

## 3. Xem dữ liệu PostgreSQL bằng Extension trên VS Code / IDE

Để xem và chỉnh sửa các bảng dữ liệu trực quan giống như Excel ngay trong IDE:

1. Mở mục **Extensions** (`Ctrl + Shift + X`), tìm và cài đặt extension **PostgreSQL** (hoặc **Database Client**).
2. Mở biểu tượng **PostgreSQL** ở thanh công cụ bên trái $\rightarrow$ bấm dấu **`+` (Add Connection)** và điền lần lượt:
   - **Server name / Hostname:** `localhost` (hoặc `127.0.0.1`)
   - **User name:** `<ten_user>` (tên user PostgreSQL bạn đã tạo ở Bước 1, hoặc `postgres`)
   - **Password:** `<mat_khau>` (mật khẩu bạn đã đặt, tích chọn *Save Password*)
   - **Port:** `5432`
   - **Connection type / SSL:** Chọn **`Standard Connection`** hoặc **`Disable`** (chạy local không cần SSL)
   - **Database name:** `fitness_app`
   - **Display name / Profile name:** `fitness_app`
3. Sau khi kết nối thành công, mở cây thư mục bên trái theo đường dẫn:
   `fitness_app` $\rightarrow$ **`Schemas`** $\rightarrow$ **`public`** $\rightarrow$ **`Tables`**
4. Bạn sẽ thấy đầy đủ các bảng (`users`, `foods`, `exercises`, `food_logs`, `workout_logs`, `meal_plans`, ` meal_plan_items`, `workout_plans`).
   - **Click chuột phải** vào bảng muốn xem $\rightarrow$ chọn **`Select Top 1000`** (hoặc **`View Data`**) để xem bảng dữ liệu chi tiết.

---

## 4. Khởi động Backend

Đứng tại thư mục `backend/` (đã kích hoạt `.venv`):

```bash
uvicorn app.main:app --reload
```

- API server: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

---

## 5. Khởi động Frontend

Mở terminal mới, đứng tại thư mục `frontend/`:

```bash
cd frontend
npm install   # chỉ cần chạy lần đầu hoặc khi cập nhật package
npm run dev
```

- Web app: `http://localhost:5173`
