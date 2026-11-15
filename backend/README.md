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
# Tắt môi trường ảo:
deactivate

# Bật server backend:
uvicorn app.main:app --reload

# Tắt môi trường ảo:
deactivate

# Bật server backend:
uvicorn app.main:app --reload

# Cài đặt các thư viện cần thiết (nếu có cập nhật mới)
pip install -r requirements.txt
```

---

## 2. Khởi tạo & Nạp dữ liệu vào Database (SQLAlchemy ORM)

Hệ thống dùng **SQLAlchemy ORM** (`app/models/`) để tự động sinh cấu trúc bảng (không dùng bất kỳ file `.sql` nào) và nạp dữ liệu chuẩn hóa:
- **Thực phẩm (Calo IN)**: Trích xuất 590+ thực phẩm thuần Việt từ Bảng thành phần dinh dưỡng thực phẩm VN 2017 (`bang-thanh-phan-dinh-duong-thuc-pham-vn-2017-27-4-17.pdf`) cùng các thực phẩm thô USDA và món ăn hàng ngày.
- **Bài tập (Calo BURN)**: Trích xuất **đúng 50 bài tập nền tảng** từ `backend/data/raw/exercises.json` phủ đều 10 nhóm cơ lớn, chuẩn hóa theo schema ORM `Exercise` (`category`, `name_vi`, `name_en`, `met_value`, `intensity_level`, `description`, `equipment`, `instructions`, `common_mistakes`, `image`, `video_url`, `target_muscle`, `secondary_muscle`, `banned_for`, `clinical_reasons`, `source`).

### Lệnh chính: Nạp dữ liệu vào Database

Từ thư mục `backend/` (sau khi kích hoạt `.venv`):

```bash
python -m scripts.seed_database
```

Lệnh này sẽ tự động:
1. Gọi `init_db()` để sinh toàn bộ các bảng (`users`, `foods`, `exercises`, `food_logs`, `workout_logs`) trong `fitness_app.db` (hoặc PostgreSQL nếu cấu hình `DATABASE_URL` trong `.env`).
2. Nạp **590+ thực phẩm** từ Bảng thành phần dinh dưỡng thực phẩm Việt Nam 2017.
3. Nạp **đúng 50 bài tập chọn lọc** từ `exercises.json` kèm ảnh CDN, hướng dẫn, lỗi thường gặp, và nhãn chống chỉ định bệnh lý A3.
4. Tạo sẵn **1 tài khoản mẫu** (`vanan24@gmail.com` / `123456`) kèm nhật ký ăn uống & tập luyện mẫu cho ngày hôm nay.

Hoặc chạy lại toàn bộ Pipeline trích xuất từ raw data:
```bash
python -m scripts.run_etl_pipeline
```

Xem hướng dẫn chi tiết (cấu hình SQLite/PostgreSQL, Cloudinary/S3, kiểm tra dữ liệu và reset DB) tại [DATABASE_SEEDING_GUIDE.md](./DATABASE_SEEDING_GUIDE.md).

---

## 3. Chạy API Server

```bash
fastapi dev app/main.py
```

Swagger UI: `http://127.0.0.1:8000/docs`
