# EduStaff — Hệ Thống Quản Lý Giảng Viên Đại Học

> Phần mềm quản lý giảng viên dành cho các trường đại học, được xây dựng theo kiến trúc tách service với Backend REST API và Frontend Desktop Application.

---

## Mục Lục

- [Tổng Quan](#tổng-quan)
- [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
- [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Thiết Kế Database](#thiết-kế-database)
- [Phân Quyền Hệ Thống](#phân-quyền-hệ-thống)
- [API Endpoints](#api-endpoints)
- [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
- [Hướng Dẫn Chạy](#hướng-dẫn-chạy)
- [Tài Khoản Mặc Định](#tài-khoản-mặc-định)
- [Tính Năng Nâng Cao](#tính-năng-nâng-cao)

---

## Tổng Quan

**EduStaff** là hệ thống phần mềm quản lý giảng viên trong trường đại học, hỗ trợ các nghiệp vụ:

- **Quản lý giảng viên**: Thêm, sửa, xóa, tìm kiếm thông tin giảng viên
- **Quản lý khoa/bộ môn**: Tổ chức giảng viên theo khoa
- **Quản lý lịch giảng dạy**: Phân công lịch dạy theo học kỳ, kiểm tra trùng lịch
- **Quản lý tài khoản**: Tạo, phân quyền, khóa/mở tài khoản người dùng
- **Phân quyền người dùng**: Admin và Nhân sự (Staff)
- **Thống kê & báo cáo**: Thống kê theo khoa, học vị, chức vụ
- **Xuất báo cáo**: Export danh sách giảng viên ra Excel và PDF
- **Nhật ký hệ thống**: Ghi log đăng nhập, chỉnh sửa, xóa dữ liệu
- **Sao lưu dữ liệu**: Backup/Restore database
- **Dashboard**: Tổng quan thống kê nhanh

### Đặc điểm nổi bật

| Tính năng | Mô tả |
|-----------|--------|
| Bảo mật | JWT Authentication + bcrypt password hashing |
| Phân quyền | Role-based Access Control (Admin / Staff) |
| Giao diện | Desktop app hiện đại với dark theme |
| Báo cáo | Export Excel + PDF danh sách giảng viên |
| Thống kê | Thống kê GV theo khoa, học vị, chức vụ |
| Nhật ký | Audit logs ghi lịch sử login/edit/delete |
| Logging | Ghi log hệ thống cho debug và giám sát |
| Backup | Sao lưu và phục hồi database |
| Docker | Hỗ trợ Docker cho backend + MySQL |

---

## Kiến Trúc Hệ Thống

Hệ thống được tách thành **2 service độc lập**, giao tiếp qua HTTP/JSON:

```
┌─────────────────────────┐         HTTP/JSON         ┌─────────────────────────┐
│                         │ ◄──────────────────────►   │                         │
│   Frontend (PySide6)    │                            │   Backend (FastAPI)     │
│   Desktop Application   │    POST /api/auth/login    │   REST API Server      │
│                         │    GET  /api/lecturers     │                         │
│  ┌───────────────────┐  │    POST /api/lecturers     │  ┌───────────────────┐  │
│  │   Login Screen    │  │    PUT  /api/lecturers/1   │  │   Routers         │  │
│  │   Dashboard       │  │    DELETE /api/lecturers/1 │  │   Services        │  │
│  │   Lecturer Mgmt   │  │    GET  /api/stats/*       │  │   Models          │  │
│  │   Department Mgmt │  │    GET  /api/audit-logs    │  │   Schemas         │  │
│  │   Schedule Mgmt   │  │    POST /api/backup/*      │  └───────┬───────────┘  │
│  │   Account Mgmt    │  │    ...                     │          │              │
│  │   Audit Logs      │  │                            │          ▼              │
│  └───────────────────┘  │                            │  ┌───────────────────┐  │
│                         │                            │  │   MySQL Database  │  │
└─────────────────────────┘                            │  └───────────────────┘  │
                                                       └─────────────────────────┘
```

### Nguyên tắc thiết kế

1. **Tách biệt Frontend/Backend**: Frontend không truy cập trực tiếp database
2. **RESTful API**: Giao tiếp hoàn toàn qua HTTP JSON
3. **Stateless Authentication**: JWT token, không lưu session trên server
4. **Tách logic khỏi UI**: Frontend tách rõ lớp API client, UI components, và screens
5. **Module hóa Backend**: Routers → Services → Models, dễ mở rộng
6. **Audit Trail**: Mọi thao tác quan trọng đều được ghi log

---

## Công Nghệ Sử Dụng

### Backend

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| Framework | FastAPI | 0.110+ |
| ORM | SQLAlchemy | 2.0+ |
| Database | MySQL | 8.0+ |
| DB Driver | PyMySQL | 1.1+ |
| Auth | python-jose (JWT) | 3.3+ |
| Password Hash | passlib + bcrypt | 1.7+ |
| Validation | Pydantic | 2.0+ |
| Server | Uvicorn | 0.29+ |
| Excel Export | openpyxl | 3.1+ |
| PDF Export | reportlab | 4.1+ |

### Frontend

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| UI Framework | PySide6 (Qt6) | 6.6+ |
| HTTP Client | requests | 2.31+ |

---

## Cấu Trúc Dự Án

```
EduStaff/
│
├── backend/                        # ── Backend Service (FastAPI REST API) ──
│   ├── main.py                     # Entry point: khởi tạo app, middleware, router
│   ├── config.py                   # Cấu hình (DB URL, JWT secret, ...)
│   ├── database.py                 # SQLAlchemy engine, session, Base
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Docker image cho backend
│   ├── .env                        # Biến môi trường (không commit)
│   ├── .env.example                # Template biến môi trường
│   │
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── account.py              # Bảng accounts (tài khoản đăng nhập)
│   │   ├── department.py           # Bảng departments (khoa/bộ môn)
│   │   ├── lecturer.py             # Bảng lecturers (giảng viên)
│   │   ├── teaching_schedule.py    # Bảng teaching_schedule (lịch dạy)
│   │   └── audit_log.py            # Bảng audit_logs (nhật ký hệ thống)
│   │
│   ├── schemas/                    # Pydantic Schemas (validate request/response)
│   │   ├── __init__.py
│   │   ├── auth.py                 # LoginRequest, TokenResponse
│   │   ├── department.py           # DepartmentCreate, DepartmentUpdate, ...
│   │   ├── lecturer.py             # LecturerCreate, LecturerUpdate, ...
│   │   ├── schedule.py             # ScheduleCreate, ScheduleUpdate, ...
│   │   ├── account.py              # AccountCreate, AccountUpdate, ...
│   │   ├── stats.py                # StatsOverview, StatsByDepartment, ...
│   │   └── audit_log.py            # AuditLogResponse, AuditLogFilter
│   │
│   ├── routers/                    # API Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py                 # POST /login, GET /me
│   │   ├── departments.py          # CRUD /departments
│   │   ├── lecturers.py            # CRUD /lecturers + export excel/pdf
│   │   ├── schedules.py            # CRUD /schedules
│   │   ├── accounts.py             # CRUD /accounts + toggle active
│   │   ├── stats.py                # GET /stats/*
│   │   ├── audit_logs.py           # GET /audit-logs
│   │   └── backup.py               # POST /backup/create, /backup/restore
│   │
│   └── services/                   # Business Logic Layer
│       ├── __init__.py
│       ├── auth_service.py         # JWT, password hashing, authentication
│       ├── department_service.py   # CRUD logic cho departments
│       ├── lecturer_service.py     # CRUD logic cho lecturers + excel/pdf export
│       ├── schedule_service.py     # CRUD logic cho schedules + conflict check
│       ├── account_service.py      # CRUD logic cho accounts + toggle active
│       ├── stats_service.py        # Thống kê theo khoa, học vị, chức vụ
│       ├── audit_service.py        # Ghi và truy vấn audit logs
│       └── backup_service.py       # mysqldump backup + restore
│
├── frontend/                       # ── Frontend Service (PySide6 Desktop) ──
│   ├── main.py                     # Entry point: QApplication, theme, window
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── api/                        # HTTP API Client Layer
│   │   ├── __init__.py
│   │   ├── client.py               # Base HTTP client (requests wrapper + JWT)
│   │   ├── auth_api.py             # Login, get current user
│   │   ├── department_api.py       # CRUD departments
│   │   ├── lecturer_api.py         # CRUD lecturers
│   │   ├── schedule_api.py         # CRUD schedules
│   │   ├── account_api.py          # CRUD accounts
│   │   ├── stats_api.py            # Thống kê
│   │   └── audit_api.py            # Audit logs
│   │
│   ├── ui/                         # UI Utilities & Theme
│   │   ├── __init__.py
│   │   ├── styles.py               # QSS dark theme stylesheet
│   │   └── components.py           # Reusable widgets (buttons, tables, inputs...)
│   │
│   └── screens/                    # Application Screens
│       ├── __init__.py
│       ├── login_screen.py         # Màn hình đăng nhập
│       ├── main_window.py          # Main window + sidebar navigation
│       ├── dashboard_screen.py     # Dashboard thống kê
│       ├── lecturer_screen.py      # Quản lý giảng viên
│       ├── department_screen.py    # Quản lý khoa
│       ├── schedule_screen.py      # Quản lý lịch giảng dạy
│       ├── account_screen.py       # Quản lý tài khoản (admin only)
│       └── audit_log_screen.py     # Xem nhật ký hệ thống (admin only)
│
├── docker-compose.yml              # Docker: MySQL + Backend
└── README.md                       # Tài liệu dự án
```

---

## Thiết Kế Database

### Sơ đồ quan hệ (ERD)

```
┌──────────────────┐       ┌──────────────────────────┐       ┌──────────────────────────┐
│   departments    │       │       lecturers           │       │   teaching_schedule      │
├──────────────────┤       ├──────────────────────────┤       ├──────────────────────────┤
│ id          PK   │───┐   │ id              PK       │───┐   │ id              PK       │
│ name        UQ   │   │   │ employee_code   UQ       │   │   │ lecturer_id     FK       │
│ code        UQ   │   └──►│ full_name                │   └──►│ subject_name             │
│ description      │       │ email           UQ       │       │ subject_code             │
│ created_at       │       │ phone                    │       │ room                     │
│ updated_at       │       │ gender                   │       │ day_of_week              │
└──────────────────┘       │ date_of_birth            │       │ start_time               │
                           │ degree                   │       │ end_time                 │
┌──────────────────┐       │ position                 │       │ semester                 │
│    accounts      │       │ department_id   FK       │       │ academic_year            │
├──────────────────┤       │ hire_date                │       │ created_at               │
│ id          PK   │       │ status                   │       │ updated_at               │
│ username    UQ   │       │ created_at               │       └──────────────────────────┘
│ password_hash    │       │ updated_at               │
│ full_name        │       └──────────────────────────┘
│ role             │                                          ┌──────────────────────────┐
│ is_active        │                                          │     audit_logs           │
│ created_at       │                                          ├──────────────────────────┤
│ updated_at       │                                          │ id              PK       │
└──────────────────┘                                          │ user_id         FK       │
                                                              │ action                   │
                                                              │ entity_type              │
                                                              │ entity_id                │
                                                              │ details                  │
                                                              │ ip_address               │
                                                              │ created_at               │
                                                              └──────────────────────────┘
```

### Chi tiết bảng

#### `departments` — Khoa / Bộ môn

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã khoa |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Tên khoa |
| code | VARCHAR(20) | NOT NULL, UNIQUE | Mã viết tắt (VD: CNTT, DTVT) |
| description | TEXT | NULLABLE | Mô tả |
| created_at | DATETIME | DEFAULT NOW | Ngày tạo |
| updated_at | DATETIME | ON UPDATE NOW | Ngày cập nhật |

#### `accounts` — Tài khoản đăng nhập

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã tài khoản |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Tên đăng nhập |
| password_hash | VARCHAR(255) | NOT NULL | Mật khẩu đã hash (bcrypt) |
| full_name | VARCHAR(100) | NOT NULL | Họ tên người dùng |
| role | ENUM('admin','staff') | NOT NULL, DEFAULT 'staff' | Vai trò |
| is_active | BOOLEAN | DEFAULT TRUE | Trạng thái hoạt động |
| created_at | DATETIME | DEFAULT NOW | Ngày tạo |
| updated_at | DATETIME | ON UPDATE NOW | Ngày cập nhật |

#### `lecturers` — Giảng viên

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã GV |
| employee_code | VARCHAR(20) | NOT NULL, UNIQUE | Mã nhân viên (VD: GV001) |
| full_name | VARCHAR(100) | NOT NULL | Họ tên |
| email | VARCHAR(100) | NOT NULL, UNIQUE | Email |
| phone | VARCHAR(15) | NULLABLE | Số điện thoại |
| gender | ENUM('male','female','other') | NOT NULL | Giới tính |
| date_of_birth | DATE | NULLABLE | Ngày sinh |
| degree | VARCHAR(20) | NOT NULL | Học vị (ThS, TS, PGS, GS) |
| position | VARCHAR(50) | NULLABLE | Chức vụ (Trưởng khoa, Phó khoa, GV...) |
| department_id | INT | FK → departments.id | Khoa |
| hire_date | DATE | NOT NULL | Ngày vào làm |
| status | ENUM('active','inactive','on_leave') | DEFAULT 'active' | Trạng thái |
| created_at | DATETIME | DEFAULT NOW | Ngày tạo |
| updated_at | DATETIME | ON UPDATE NOW | Ngày cập nhật |

#### `teaching_schedule` — Lịch giảng dạy

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã lịch |
| lecturer_id | INT | FK → lecturers.id | Giảng viên |
| subject_name | VARCHAR(100) | NOT NULL | Tên môn học |
| subject_code | VARCHAR(20) | NOT NULL | Mã môn học |
| room | VARCHAR(20) | NOT NULL | Phòng học |
| day_of_week | ENUM('Mon','Tue','Wed','Thu','Fri','Sat','Sun') | NOT NULL | Thứ |
| start_time | TIME | NOT NULL | Giờ bắt đầu |
| end_time | TIME | NOT NULL | Giờ kết thúc |
| semester | VARCHAR(20) | NOT NULL | Học kỳ (VD: HK1, HK2) |
| academic_year | INT | NOT NULL | Năm học (VD: 2025) |
| created_at | DATETIME | DEFAULT NOW | Ngày tạo |
| updated_at | DATETIME | ON UPDATE NOW | Ngày cập nhật |

#### `audit_logs` — Nhật ký hệ thống

| Cột | Kiểu | Ràng buộc | Mô tả |
|-----|------|-----------|-------|
| id | INT | PK, AUTO_INCREMENT | Mã log |
| user_id | INT | FK → accounts.id | Ai thực hiện |
| action | VARCHAR(20) | NOT NULL | login, create, update, delete |
| entity_type | VARCHAR(50) | NULLABLE | lecturer, department, schedule, account |
| entity_id | INT | NULLABLE | ID đối tượng bị tác động |
| details | TEXT | NULLABLE | JSON mô tả chi tiết thay đổi |
| ip_address | VARCHAR(45) | NULLABLE | IP client |
| created_at | DATETIME | DEFAULT NOW | Thời điểm |

---

## Phân Quyền Hệ Thống

### 2 Vai trò (Roles)

| Role | Mô tả | Đối tượng sử dụng |
|------|--------|-------------------|
| `admin` | Quản trị viên — toàn quyền | Quản trị viên hệ thống |
| `staff` | Nhân sự — xem và xuất báo cáo | Phòng nhân sự, Ban giám hiệu |

### Ma trận phân quyền chi tiết

| Chức năng | admin | staff |
|-----------|-------|-------|
| CRUD giảng viên | ✅ | ❌ |
| CRUD khoa | ✅ | ❌ |
| CRUD lịch giảng dạy | ✅ | ❌ |
| CRUD tài khoản | ✅ | ❌ |
| Xem danh sách GV, khoa, lịch | ✅ | ✅ |
| Export Excel / PDF | ✅ | ✅ |
| Xem thống kê | ✅ | ✅ |
| Xem audit logs | ✅ | ❌ |
| Backup / Restore | ✅ | ❌ |
| Khóa/mở tài khoản | ✅ | ❌ |

---

## API Endpoints

### Authentication — Xác thực

| Method | Endpoint | Auth | Mô tả |
|--------|----------|------|--------|
| POST | `/api/auth/login` | ❌ | Đăng nhập, trả JWT token |
| GET | `/api/auth/me` | ✅ all | Lấy thông tin user hiện tại |

### Departments — Khoa

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| GET | `/api/departments` | staff+ | Danh sách khoa |
| GET | `/api/departments/{id}` | staff+ | Chi tiết khoa |
| POST | `/api/departments` | admin | Thêm khoa mới |
| PUT | `/api/departments/{id}` | admin | Cập nhật khoa |
| DELETE | `/api/departments/{id}` | admin | Xóa khoa |

### Lecturers — Giảng viên

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| GET | `/api/lecturers` | staff+ | Danh sách GV (search, filter, paginate) |
| GET | `/api/lecturers/{id}` | staff+ | Chi tiết GV |
| POST | `/api/lecturers` | admin | Thêm GV mới |
| PUT | `/api/lecturers/{id}` | admin | Cập nhật GV |
| DELETE | `/api/lecturers/{id}` | admin | Xóa GV |
| GET | `/api/lecturers/export/excel` | staff+ | Export danh sách ra Excel |
| GET | `/api/lecturers/export/pdf` | staff+ | Export danh sách ra PDF |

Filter params: `?search=&department_id=&degree=&position=&status=&page=&size=`

### Teaching Schedule — Lịch giảng dạy

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| GET | `/api/schedules` | staff+ | Danh sách lịch dạy |
| GET | `/api/schedules/{id}` | staff+ | Chi tiết lịch |
| POST | `/api/schedules` | admin | Thêm lịch dạy |
| PUT | `/api/schedules/{id}` | admin | Cập nhật lịch |
| DELETE | `/api/schedules/{id}` | admin | Xóa lịch |

### Accounts — Quản lý tài khoản

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| GET | `/api/accounts` | admin | Danh sách tài khoản |
| GET | `/api/accounts/{id}` | admin | Chi tiết tài khoản |
| POST | `/api/accounts` | admin | Tạo tài khoản mới |
| PUT | `/api/accounts/{id}` | admin | Cập nhật tài khoản |
| PATCH | `/api/accounts/{id}/toggle-active` | admin | Khóa/mở tài khoản |
| DELETE | `/api/accounts/{id}` | admin | Xóa tài khoản |

### Stats — Thống kê

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| GET | `/api/stats/overview` | staff+ | Tổng quan (tổng GV, khoa, lịch) |
| GET | `/api/stats/by-department` | staff+ | Số GV theo từng khoa |
| GET | `/api/stats/by-degree` | staff+ | Số GV theo học vị |
| GET | `/api/stats/by-position` | staff+ | Số GV theo chức vụ |

### Audit Logs — Nhật ký hệ thống

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| GET | `/api/audit-logs` | admin | Danh sách log (filter, paginate) |

### Backup — Sao lưu

| Method | Endpoint | Role | Mô tả |
|--------|----------|------|--------|
| POST | `/api/backup/create` | admin | Tạo backup (mysqldump) |
| GET | `/api/backup/list` | admin | Danh sách file backup |
| POST | `/api/backup/restore` | admin | Restore từ file backup |

### Response Format

**Thành công:**
```json
{
  "id": 1,
  "employee_code": "GV001",
  "full_name": "Nguyễn Văn A",
  "email": "nguyenvana@university.edu.vn",
  "position": "Trưởng bộ môn",
  "department": {
    "id": 1,
    "name": "Công nghệ Thông tin"
  }
}
```

**Lỗi:**
```json
{
  "detail": "Không tìm thấy giảng viên với ID: 99"
}
```

---

## Hướng Dẫn Cài Đặt

### Yêu cầu hệ thống

- Python 3.10+
- MySQL 8.0+
- Git

### 1. Clone project

```bash
git clone https://github.com/imxyanua/EduStaff.git
cd EduStaff
```

### 2. Tạo database MySQL

```sql
CREATE DATABASE edustaff CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'edustaff'@'localhost' IDENTIFIED BY 'edustaff_password';
GRANT ALL PRIVILEGES ON edustaff.* TO 'edustaff'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Cài đặt Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

Cấu hình file `.env`:
```env
DATABASE_URL=mysql+pymysql://edustaff:edustaff_password@localhost:3306/edustaff
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=480
```

### 4. Cài đặt Frontend

```bash
cd frontend
python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

---

## Hướng Dẫn Chạy

### Chạy Backend

```bash
cd backend
# Activate venv
venv\Scripts\activate

# Chạy server (development)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Truy cập Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

### Chạy Frontend

```bash
cd frontend
# Activate venv
venv\Scripts\activate

# Chạy ứng dụng
python main.py
```

### Chạy bằng Docker (Backend + MySQL)

```bash
docker-compose up -d
```

---

## Tài Khoản Mặc Định

Hệ thống tự tạo tài khoản khi khởi động lần đầu:

| Vai trò | Username | Password | Quyền hạn |
|---------|----------|----------|-----------|
| Admin | `admin` | `admin123` | Toàn quyền |
| Staff | `staff` | `staff123` | Xem + export |

> **Lưu ý**: Đổi mật khẩu mặc định khi triển khai production!

### Dữ liệu mẫu (seed data)

Khi khởi động lần đầu, hệ thống tự tạo dữ liệu test:

- **2 Tài khoản**: admin, staff
- **3 Khoa**: Công nghệ Thông tin, Điện tử Viễn thông, Quản trị Kinh doanh
- **5 Giảng viên**: Phân bổ trong các khoa (có chức vụ)
- **10 Lịch giảng dạy**: Lịch mẫu cho học kỳ HK1 - 2025

---

## Tính Năng Nâng Cao

| Tính năng | Trạng thái | Mô tả |
|-----------|-----------|-------|
| JWT Auth | Có | Xác thực bằng JSON Web Token |
| RBAC (2 roles) | Có | Phân quyền Admin / Staff |
| Logging | Có | Ghi log hệ thống (file + console) |
| Audit Logs | Có | Lịch sử đăng nhập/chỉnh sửa/xóa |
| Export Excel | Có | Xuất danh sách GV ra .xlsx |
| Export PDF | Có | Xuất danh sách GV ra .pdf |
| Thống kê | Có | Theo khoa, học vị, chức vụ |
| Quản lý TK | Có | CRUD + khóa/mở tài khoản |
| Backup/Restore | Có | Sao lưu/phục hồi database |
| Docker | Có | docker-compose cho backend + MySQL |
| Seed Data | Có | Dữ liệu mẫu tự động |
| Search & Filter | Có | Tìm kiếm, lọc theo khoa/học vị/chức vụ |
| Pagination | Có | Phân trang danh sách |

---

## Đối Tượng Sử Dụng

| Đối tượng | Role | Mô tả |
|-----------|------|-------|
| Quản trị viên hệ thống | admin | Quản lý toàn bộ hệ thống |
| Phòng nhân sự | staff | Xem thông tin, xuất báo cáo |
| Ban giám hiệu | staff | Xem thống kê, báo cáo |

---

## Ghi Chú Phát Triển

### Quy tắc code

- Tất cả code có **comment tiếng Việt** rõ ràng
- Backend: tách rõ Router → Service → Model
- Frontend: tách rõ Screen → API Client → UI Component
- Validate dữ liệu bằng Pydantic (backend) trước khi lưu DB
- Xử lý lỗi trả về đúng HTTP status code
- Mọi thao tác CRUD đều ghi audit log

### Mở rộng trong tương lai

- Quản lý sinh viên
- Quản lý đề tài nghiên cứu khoa học
- Thống kê báo cáo nâng cao (biểu đồ)
- Thông báo real-time (WebSocket)
- Hệ thống backup tự động (scheduled)

---

## Contributor

- xyanua. - maintainer & developer

## License

MIT License — Free for educational and commercial use.
