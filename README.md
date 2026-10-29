# Fitness & Nutrition

Web application hỗ trợ người dùng xây dựng kế hoạch tập luyện và dinh dưỡng cá nhân hóa, theo dõi tiến độ và điều chỉnh kế hoạch theo thời gian.

## Tech stack

- **Frontend:** React + Vite
- **Backend:** FastAPI + Python
- **Database:** PostgreSQL
- **API communication:** HTTP/JSON
- **Version control:** Git + GitHub

> Dự án đang trong giai đoạn khởi tạo. Một số tính năng và cấu hình có thể được bổ sung khi phát triển.

---

## Mục lục

- [Yêu cầu cài đặt](#yêu-cầu-cài-đặt)
- [Clone dự án](#1-clone-dự-án)
- [Frontend: React + Vite](#2-frontend-react--vite)
- [Backend: Fastapi](#3-backend-fastapi)
- [PostgreSQL](#4-postgresql)
- [Biến môi trường](#5-biến-môi-trường)
- [Chạy toàn bộ dự án](#6-chạy-toàn-bộ-dự-án)
- [Các lệnh thường dùng](#7-các-lệnh-thường-dùng)
- [Quy trình Git khi làm việc nhóm](#8-quy-trình-git-khi-làm-việc-nhóm)
- [Xử lý lỗi thường gặp](#9-xử-lý-lỗi-thường-gặp)
- [Quy tắc an toàn](#10-quy-tắc-an-toàn)

---

## Yêu cầu cài đặt

Cài các công cụ sau trước khi bắt đầu:

1. **Git** – quản lý source code.
2. **Node.js và npm** – chạy frontend React/Vite. Nên dùng phiên bản Node.js được Vite hiện tại hỗ trợ; kiểm tra yêu cầu tại [Vite Guide](https://vite.dev/guide/).
3. **Python 3** – chạy backend FastAPI. Nên thống nhất cùng một phiên bản Python trong team.
4. **PostgreSQL** – database.
5. **Visual Studio Code** – editor được khuyến nghị.

Kiểm tra phiên bản sau khi cài:

```bash
git --version
node --version
npm --version
python --version
```

Trên một số hệ thống Linux, dùng `python3 --version` thay cho `python --version`.

---

## 1. Clone dự án

Mở terminal tại thư mục muốn lưu source code:

```bash
git clone <GITHUB_REPOSITORY_URL>
cd fitness-nutrition
```

Thay `<GITHUB_REPOSITORY_URL>` bằng URL repository thật của team.

Cấu trúc thư mục dự kiến:

```text
fitness-nutrition/
├── frontend/             # React + Vite
├── backend/              # FastAPI
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

Tên file hoặc thư mục có thể thay đổi theo cấu trúc thực tế của repository.

---

## 2. Frontend: React + Vite

### Cài dependencies

Chạy các lệnh trong thư mục `frontend`.

**Windows PowerShell:**

```powershell
cd frontend
npm install
```

**Linux / Ubuntu / WSL:**

```bash
cd frontend
npm install
```

`npm install` đọc `package.json` và cài các package cần thiết. Nếu repository có `package-lock.json`, npm sẽ dùng file lock để giữ phiên bản dependencies nhất quán hơn giữa các thành viên.

Các thư viện dự kiến dùng:

- `react` và `react-dom`: xây dựng giao diện.
- `vite`: development server và build.
- `react-router-dom`: điều hướng giữa các trang.
- `axios`: gọi API backend.
- `lucide-react`: icon.
- `recharts`: biểu đồ tiến độ.

Khi cần thêm package mới, đứng trong `frontend` và chạy:

```bash
npm install <package-name>
```

Ví dụ:

```bash
npm install axios
```

Sau khi cài package mới, commit cả `package.json` và `package-lock.json` để các thành viên khác cài được cùng dependency.

### Chạy frontend ở chế độ development

```bash
npm run dev
```

Vite sẽ in địa chỉ local, thường là `http://localhost:5173`. Mở địa chỉ đó trong trình duyệt.

Dừng server bằng `Ctrl + C`.

### Các lệnh frontend thường dùng

```bash
npm run dev       # Chạy development server
npm run build     # Build bản production vào thư mục dist/
npm run preview   # Xem thử bản build local
npm install       # Cài dependencies của dự án
npm install <pkg> # Thêm package
npm uninstall <pkg> # Gỡ package
```

Không commit `node_modules/` hoặc `dist/`.

---

## 3. Backend: FastAPI

### Tạo virtual environment

Virtual environment (`.venv`) là môi trường Python riêng cho backend, giúp tránh xung đột dependencies giữa các dự án. Mỗi thành viên tự tạo `.venv` trên máy của mình; không commit thư mục này lên Git.

#### Windows PowerShell

Từ thư mục gốc repository:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Nếu lệnh `py` không có, thử:

```powershell
python -m venv .venv
```

Nếu PowerShell chặn script activation, có thể cho phép trong phiên terminal hiện tại rồi kích hoạt lại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Thiết lập này chỉ áp dụng cho tiến trình PowerShell hiện tại.

#### Linux / Ubuntu / WSL

Từ thư mục gốc repository:

```bash
cd backend
```

Trên Ubuntu/Debian, nếu chưa có module `venv`:

```bash
sudo apt update
sudo apt install -y python3-venv python3-full
```

Tạo và kích hoạt môi trường:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Khi kích hoạt thành công, terminal thường hiện tiền tố `(.venv)`.

### Cài dependencies backend

Đảm bảo đã kích hoạt `.venv`, sau đó chạy trên cả Windows và Linux:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Nếu repository chưa có `requirements.txt` và team đang sử dụng các package dưới đây, có thể cài bộ khởi tạo một lần:

```bash
python -m pip install "fastapi[standard]" sqlalchemy "psycopg[binary]" alembic pydantic-settings "PyJWT[crypto]" "pwdlib[argon2]" python-multipart email-validator
python -m pip freeze > requirements.txt
```

Các package này phục vụ:
- `fastapi[standard]`: API framework và lệnh chạy development server.
- `sqlalchemy`: ORM để làm việc với database.
- `psycopg[binary]`: PostgreSQL driver.
- `alembic`: quản lý database migrations.
- `pydantic-settings`: đọc cấu hình từ environment.
- `PyJWT`: hỗ trợ JWT.
- `pwdlib[argon2]`: hash mật khẩu.
- `python-multipart`: nhận form/file upload.
- `email-validator`: kiểm tra định dạng email.

> Chỉ chạy lệnh cài bộ khởi tạo nếu team chưa có `requirements.txt`. Khi file này đã được quản lý trong repository, ưu tiên `pip install -r requirements.txt`. Sau khi chủ động thêm/gỡ package, cập nhật lại `requirements.txt` và commit thay đổi.

### Chạy backend

Từ thư mục `backend`, sau khi kích hoạt `.venv`:

```bash
fastapi dev app/main.py
```

Mặc định API thường chạy tại `http://127.0.0.1:8000`.

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

Dừng server bằng `Ctrl + C`. Thoát virtual environment bằng:

```bash
deactivate
```

`deactivate` chỉ thoát môi trường ảo, không xóa `.venv` và không thay thế `Ctrl + C` để dừng server.

### Các lệnh Python thường dùng

```bash
python --version
python -m pip list
python -m pip show fastapi
python -m pip install <package-name>
python -m pip uninstall <package-name>
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
```

Trên Linux, nếu đang ở ngoài `.venv` và lệnh `python` không tồn tại, dùng `python3` để tạo/kích hoạt môi trường. Sau khi `.venv` được kích hoạt, dùng `python` như các ví dụ ở trên.

---

## 4. PostgreSQL

PostgreSQL là database dùng để lưu tài khoản, hồ sơ, bài tập, món ăn, kế hoạch và dữ liệu tiến độ.

Mỗi thành viên cần có PostgreSQL đang chạy và một database dùng cho dự án. Thống nhất tên database và các biến cấu hình với team, nhưng **không chia sẻ mật khẩu database qua GitHub**.

### Kiểm tra công cụ PostgreSQL

```bash
psql --version
```

Nếu `psql` đã được cài và database server đang chạy, có thể kết nối bằng:

```bash
psql -h localhost -U <DB_USER> -d <DB_NAME>
```

Nhập mật khẩu khi được yêu cầu. Thoát `psql` bằng:

```sql
\q
```

### Một số lệnh SQL cơ bản

```sql
-- Liệt kê database trong psql
\l

-- Kết nối tới database khác
\c database_name

-- Liệt kê bảng
\dt

-- Xem cấu trúc bảng
\d table_name
```

Các lệnh bắt đầu bằng dấu `\` là lệnh của công cụ `psql`, không phải SQL chuẩn.

> Tạo database, migration và schema cụ thể cần làm theo cấu hình thực tế của backend. Chưa chạy migration nếu team chưa thiết lập Alembic hoặc chưa thống nhất cách quản lý schema.

---

## 5. Biến môi trường

Không commit mật khẩu, JWT secret, API key hoặc thông tin nhạy cảm.

Khi backend cần cấu hình, tạo file `backend/.env` trên máy cá nhân theo mẫu do team thống nhất. Có thể commit `backend/.env.example` với các giá trị minh họa, ví dụ:

```dotenv
# Example only — replace values in your local .env
DATABASE_URL=postgresql+psycopg://<DB_USER>:<DB_PASSWORD>@localhost:5432/<DB_NAME>
JWT_SECRET_KEY=replace-with-a-long-random-secret
```

Đây chỉ là ví dụ tên biến. Tên biến và cách đọc chúng phải khớp với code cấu hình backend. Không dùng các giá trị placeholder này để chạy ứng dụng.

Nếu frontend cần URL backend, có thể tạo `frontend/.env.local`:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Vite chỉ đưa biến có tiền tố `VITE_` vào frontend bundle. **Không bao giờ đặt secret, mật khẩu hoặc private API key trong biến `VITE_`**, vì chúng có thể bị người dùng xem trong trình duyệt.

Sau khi đổi biến môi trường, khởi động lại development server nếu cần.

---

## 6. Chạy toàn bộ dự án

Cần chạy frontend và backend ở **hai terminal riêng biệt**.

### Terminal 1 — Backend

**Windows PowerShell**, từ thư mục gốc:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
fastapi dev app/main.py
```

**Linux / Ubuntu / WSL**, từ thư mục gốc:

```bash
cd backend
source .venv/bin/activate
fastapi dev app/main.py
```

### Terminal 2 — Frontend

Từ thư mục gốc, trên Windows PowerShell hoặc Linux:

```bash
cd frontend
npm run dev
```

Mở địa chỉ frontend được Vite hiển thị, thường là `http://localhost:5173`. Kiểm tra backend tại `http://127.0.0.1:8000/docs`.

### CORS

Khi frontend gọi backend từ một origin khác, backend cần cấu hình CORS cho origin frontend đang sử dụng, ví dụ `http://localhost:5173`. Nếu Vite chạy trên port khác, cập nhật cấu hình tương ứng. Không nên mở CORS cho mọi origin trong production.

---

## 7. Các lệnh thường dùng

### Git

```bash
git status                         # Xem thay đổi
git pull                           # Lấy thay đổi từ upstream branch đã cấu hình
git add .                          # Đưa thay đổi vào staging
git add <file-path>                # Chỉ stage file cụ thể
git commit -m "Describe changes"   # Tạo commit
git push                           # Đẩy commit lên remote
git log --oneline -5               # Xem 5 commit gần nhất
git diff                           # Xem thay đổi chưa stage
git diff --staged                  # Xem thay đổi đã stage
```

### Frontend

```bash
npm install
npm run dev
npm run build
npm run preview
```

### Backend

```bash
# Kích hoạt môi trường trước khi chạy các lệnh Python
source .venv/bin/activate          # Linux / WSL
# .\.venv\Scripts\Activate.ps1     # Windows PowerShell

fastapi dev app/main.py
python -m pip install -r requirements.txt
deactivate
```

---

## 8. Quy trình Git khi làm việc nhóm

Khuyến nghị mỗi thành viên làm việc trên branch riêng, thay vì tất cả cùng commit trực tiếp vào `main`.

### Bắt đầu một task

```bash
git switch main
git pull
git switch -c feature/<short-task-name>
```

Ví dụ:

```bash
git switch -c feature/workout-plan
```

### Trong quá trình làm

```bash
git status
git add <file-path>
git commit -m "Add workout plan endpoint"
git push -u origin feature/workout-plan
```

Sau đó tạo Pull Request trên GitHub để team review và merge.

### Cập nhật branch theo main

Cách đơn giản cho người mới là commit/stash thay đổi đang làm, rồi lấy `main` mới nhất và tích hợp theo quy ước team:

```bash
git fetch origin
git status
```

Nếu branch của bạn cần cập nhật theo `main`, làm theo quy ước nhóm về merge hoặc rebase. Tránh rebase branch đã được nhiều người cùng sử dụng nếu chưa thống nhất.

### Lưu ý khi có thay đổi dependencies

- Frontend: commit `package.json` và `package-lock.json`.
- Backend: commit `requirements.txt`.
- Không commit `node_modules/`, `.venv/`, file `.env` hoặc secret.
- Nếu gặp conflict, đừng xóa hoặc ghi đè thay đổi của đồng đội khi chưa hiểu nội dung conflict.

---

## 9. Xử lý lỗi thường gặp

### `npm` hoặc `node` không được nhận diện

Cài Node.js phiên bản được Vite hỗ trợ, đóng và mở lại terminal, rồi kiểm tra:

```bash
node --version
npm --version
```

### PowerShell không cho chạy Activate.ps1

Trong phiên PowerShell hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Linux báo `externally-managed-environment`

Không cài package vào Python hệ thống bằng `pip`. Tạo và kích hoạt virtual environment trong backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Nếu thiếu `venv`, Ubuntu/Debian có thể cần:

```bash
sudo apt install -y python3-venv python3-full
```

### `fastapi: command not found`

Kiểm tra `.venv` đã được kích hoạt và dependencies đã được cài:

```bash
python -m pip install -r requirements.txt
python -m pip show fastapi
```

Có thể chạy bằng module CLI nếu môi trường đã cài FastAPI:

```bash
python -m fastapi dev app/main.py
```

### Port đang được sử dụng

Dừng server cũ bằng `Ctrl + C`, hoặc cấu hình port khác. Với Vite có thể dùng `npm run dev -- --port 5174`. Nếu đổi port, cập nhật CORS/backend URL cho phù hợp.

### Frontend không gọi được backend

Kiểm tra:
1. Backend có đang chạy không.
2. API URL có đúng không.
3. CORS có cho phép origin frontend không.
4. Endpoint có đúng path không.
5. Backend có trả lỗi trong terminal hoặc `/docs` không.

### Thiếu package sau khi pull code mới

Frontend:

```bash
cd frontend
npm install
```

Backend:

```bash
cd backend
# Kích hoạt .venv trước
python -m pip install -r requirements.txt
```

---

## 10. Quy tắc an toàn

- Không commit `.env`, mật khẩu, JWT secret, API key hoặc dữ liệu cá nhân.
- Không đặt secret trong biến frontend có tiền tố `VITE_`.
- Không commit `node_modules/`, `.venv/`, cache hoặc file build.
- Không đưa dữ liệu người dùng thật vào repository công khai.
- Chỉ dùng dữ liệu mẫu/đã được phép chia sẻ trong môi trường phát triển.
- Kiểm tra `git status` trước mỗi commit.
- Khi thay đổi dependencies hoặc cấu hình chạy dự án, cập nhật README để thành viên khác làm theo được.
