# EduStaff — Hệ Thống Quản Lý Giảng Viên Đại Học

> Phần mềm quản lý giảng viên dành cho các trường đại học, được xây dựng theo kiến trúc tách service với Backend REST API và Frontend Desktop Application.

---

## Mục Lục

- [Tổng Quan](#-tổng-quan)
- [Kiến Trúc Hệ Thống](#-kiến-trúc-hệ-thống)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Thiết Kế Database](#-thiết-kế-database)
- [API Endpoints](#-api-endpoints)
- [Hướng Dẫn Cài Đặt](#-hướng-dẫn-cài-đặt)
- [Hướng Dẫn Chạy](#-hướng-dẫn-chạy)
- [Tài Khoản Mặc Định](#-tài-khoản-mặc-định)
- [Tính Năng Nâng Cao](#-tính-năng-nâng-cao)

---

## Tổng Quan

**EduStaff** là hệ thống phần mềm quản lý giảng viên trong trường đại học, hỗ trợ các nghiệp vụ:

- **Quản lý giảng viên**: Thêm, sửa, xóa, tìm kiếm thông tin giảng viên
- **Quản lý khoa/bộ môn**: Tổ chức giảng viên theo khoa
- **Quản lý lịch giảng dạy**: Phân công lịch dạy theo học kỳ, kiểm tra trùng lịch
- **Quản lý tài khoản**: Tạo, phân quyền, khóa/mở tài khoản người dùng
- **Phân quyền người dùng**: Admin, Nhân sự (Staff), Giảng viên (Lecturer)
- **Thống kê & báo cáo**: Thống kê theo khoa, học vị, chức vụ
- **Xuất báo cáo**: Export danh sách giảng viên ra Excel và PDF
- **Nhật ký hệ thống**: Ghi log đăng nhập, chỉnh sửa, xóa dữ liệu
- **Sao lưu dữ liệu**: Backup/Restore database
- **Dashboard**: Tổng quan thống kê nhanh

### Đặc điểm nổi bật

| Tính năng | Mô tả |
|-----------|--------|
| Bảo mật | JWT Authentication + bcrypt password hashing |
| Phân quyền | Role-based Access Control (Admin / Staff / Lecturer) |
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
| Excel | openpyxl | 3.1+ |

---



### Cài đặt Backend

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

### Cài đặt Frontend

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
| Admin | `admin` | `admin123` | Toàn quyền CRUD |
| Staff | `staff` | `staff123` | Chỉ xem (GET) |

> **Lưu ý**: Đổi mật khẩu mặc định khi triển khai production!

### Dữ liệu mẫu (seed data)

Khi khởi động lần đầu, hệ thống tự tạo dữ liệu test:

- **3 Khoa**: Công nghệ Thông tin, Điện tử Viễn thông, Quản trị Kinh doanh
- **5 Giảng viên**: Phân bổ trong các khoa
- **10 Lịch giảng dạy**: Lịch mẫu cho học kỳ HK1 - 2025

---

## Tính Năng Nâng Cao

| Tính năng | Trạng thái | Mô tả |
|-----------|-----------|-------|
| JWT Auth | Có | Xác thực bằng JSON Web Token |
| RBAC (3 roles) | Có | Phân quyền Admin / Staff / Lecturer |
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
| Giảng viên | lecturer | Xem lịch giảng dạy cá nhân |
---

## Ghi Chú Phát Triển

### Quy tắc code

- Tất cả code có **comment tiếng Việt** rõ ràng
- Backend: tách rõ Router → Service → Model
- Frontend: tách rõ Screen → API Client → UI Component
- Validate dữ liệu bằng Pydantic (backend) trước khi lưu DB
- Xử lý lỗi trả về đúng HTTP status code

### Mở rộng trong tương lai

- Quản lý sinh viên
- Quản lý đề tài nghiên cứu khoa học
- Thống kê báo cáo nâng cao (biểu đồ)
- Thông báo real-time (WebSocket)
- Hệ thống backup tự động

---

## Contributor

- xyanua. - maintainer & developer

## License

MIT License — Free for educational and commercial use.
