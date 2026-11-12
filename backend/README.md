# Backend - Fitness & Nutrition API

Hệ thống API backend xây dựng bằng **FastAPI** và **SQLAlchemy (SQLite)**, hỗ trợ tính toán dinh dưỡng, phân tích năng lượng và cá nhân hóa lịch tập.

---

## 1. Cài đặt môi trường

Từ thư mục gốc `backend/`:

```bash
# Kích hoạt môi trường ảo (nếu chưa kích hoạt)
source .venv/bin/activate

# Tắt môi trường ảo:
deactivate

# Bật server backend:
uvicorn app.main:app --reload

# Cài đặt các thư viện cần thiết (nếu có cập nhật mới)
pip install -r requirements.txt
```

---

## 2. Khởi tạo & Nạp dữ liệu vào Database (SQLite)

Hệ thống sử dụng **SQLAlchemy ORM** để tự động sinh cấu trúc bảng và nạp dữ liệu mẫu vào file `fitness_app.db`.

### 📌 Lệnh chính: Tạo database & nạp dữ liệu chuẩn hóa
Chạy lệnh sau từ thư mục `backend/`:

```bash
python -m scripts.seed_database
```

Lệnh này sẽ tự động:
1. Tạo file CSDL `fitness_app.db` và toàn bộ các bảng (`users`, `foods`, `exercises`, `food_logs`, `workout_logs`).
2. Nạp **39 thực phẩm** (Chuẩn USDA và Viện Dinh Dưỡng VN kèm giá tiền ước tính).
3. Nạp **38 bài tập thể lực** (Chuẩn Ainsworth Compendium 2011 có chỉ số MET).
4. Tạo sẵn **1 tài khoản mẫu** kèm nhật ký ăn uống & tập luyện mẫu để kiểm tra.