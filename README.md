# Fitness & Nutrition

Ứng dụng web lập kế hoạch tập luyện, thực đơn dinh dưỡng cá nhân hóa và theo dõi năng lượng hằng ngày.

- **Backend:** FastAPI + SQLAlchemy + SQLite (`backend/`)
- **Frontend:** React + Vite (`frontend/`)

---

## 1. Cài đặt & Seed Database (Backend)

Đứng tại thư mục `backend/`:

```bash
cd backend

# Tạo file .env nếu chưa có
cp .env.example .env

# Tạo & kích hoạt virtual environment (nếu chưa có .venv thì chạy: python3 -m venv .venv)
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1

# Cài dependencies (lần đầu)
pip install -r requirements.txt
```

Nạp dữ liệu thực phẩm (`data/vietnam_foods_curated.json`) và bài tập (`data/exercises_65.json`) vào `fitness_app.db`:

```bash
# Xóa dữ liệu catalog/lịch/log cũ (giữ lại tài khoản users) và nạp mới từ 2 file JSON
# Tự động tạo fitness_app.db và toàn bộ bảng nếu file DB chưa tồn tại
python -m scripts.import_curated_json

# Xóa luôn toàn bộ tài khoản users khi reset
python -m scripts.import_curated_json --reset-users
```

> Nếu muốn reset trắng từ file DB mới hoàn toàn: xóa `backend/fitness_app.db` rồi chạy lại `python -m scripts.import_curated_json`.

---

## 2. Khởi động Backend

Đứng tại thư mục `backend/` (đã kích hoạt `.venv`):

```bash
uvicorn app.main:app --reload
```

- API server: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

---

## 3. Khởi động Frontend

Mở terminal mới, đứng tại thư mục `frontend/`:

```bash
cd frontend
npm install   # chỉ cần chạy lần đầu hoặc khi cập nhật package
npm run dev
```

- Web app: `http://localhost:5173`
