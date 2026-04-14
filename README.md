# EduStaff — Hệ Thống Quản Lý Giảng Viên Đại Học

> Phần mềm **desktop** quản lý giảng viên dành cho các trường đại học.  
> Xây dựng bằng **PySide6 + SQLAlchemy** theo kiến trúc phân tầng (Layered Architecture).  
> Không dùng web server — chạy bằng một lệnh duy nhất.

---

## Mục Lục

- [Tổng Quan](#tổng-quan)
- [Kiến Trúc Hệ Thống](#kiến-trúc-hệ-thống)
- [Công Nghệ Sử Dụng](#công-nghệ-sử-dụng)
- [Cấu Trúc Dự Án](#cấu-trúc-dự-án)
- [Thiết Kế Database](#thiết-kế-database)
- [Phân Quyền Hệ Thống](#phân-quyền-hệ-thống)
- [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
- [Hướng Dẫn Chạy](#hướng-dẫn-chạy)
- [Tài Khoản Mặc Định](#tài-khoản-mặc-định)
- [Tính Năng](#tính-năng)

---

## Tổng Quan

**EduStaff** là ứng dụng desktop quản lý giảng viên trong trường đại học, hỗ trợ các nghiệp vụ:

- **Quản lý giảng viên**: Thêm, sửa, xóa, tìm kiếm thông tin giảng viên
- **Quản lý khoa/bộ môn**: Tổ chức giảng viên theo khoa
- **Quản lý lịch giảng dạy**: Phân công lịch dạy theo học kỳ, kiểm tra trùng lịch
- **Quản lý tài khoản**: Tạo, phân quyền, khóa/mở tài khoản người dùng
- **Thống kê & báo cáo**: Thống kê theo khoa, học vị, chức vụ
- **Xuất báo cáo**: Export danh sách giảng viên ra Excel và PDF
- **Nhật ký hệ thống**: Ghi log đăng nhập, chỉnh sửa, xóa dữ liệu
- **Sao lưu dữ liệu**: Backup / Restore database

| Tính năng | Mô tả |
|-----------|--------|
| Bảo mật | bcrypt password hashing + session phiên làm việc |
| Phân quyền | Role-based Access Control (Admin / Staff) |
| Giao diện | Desktop app hiện đại với dark theme (Qt6) |
| Báo cáo | Export Excel + PDF danh sách giảng viên |
| Thống kê | Theo khoa, học vị, chức vụ |
| Nhật ký | Audit logs — lịch sử login / edit / delete |
| Backup | Sao lưu và phục hồi database |

---

## Kiến Trúc Hệ Thống

Ứng dụng được xây dựng theo **Layered Architecture** (kiến trúc phân tầng 5 tầng):

```
╔══════════════════════════════════════════════════════╗
║         PRESENTATION LAYER — ui/screens/             ║
║  PySide6 Screens · Windows · Dialogs · Widgets       ║
╠══════════════════════════════════════════════════════╣
║         CONTROLLER LAYER — controllers/              ║
║  Nhận sự kiện UI, điều phối gọi Service              ║
╠══════════════════════════════════════════════════════╣
║         SERVICE LAYER — services/                    ║
║  Business logic · Validation · Export · Backup       ║
╠══════════════════════════════════════════════════════╣
║         REPOSITORY LAYER — repositories/             ║
║  SQLAlchemy queries · CRUD · Filter · Paginate       ║
╠══════════════════════════════════════════════════════╣
║         MODEL LAYER — models/                        ║
║  SQLAlchemy ORM · Ánh xạ bảng MySQL                 ║
╠══════════════════════════════════════════════════════╣
║         DATABASE — MySQL 8.0                         ║
║  SQLAlchemy Engine → PyMySQL → MySQL                 ║
╚══════════════════════════════════════════════════════╝
```

**Luồng xử lý điển hình:**

```
[User bấm "Thêm Giảng Viên"]
        ↓
[LecturerScreen]      → gom dữ liệu form
        ↓
[LecturerController]  → validate input cơ bản
        ↓
[LecturerService]     → kiểm tra business rules, ghi audit log
        ↓
[LecturerRepository]  → db.add() · db.commit()
        ↓
[MySQL]               → INSERT INTO lecturers ...
        ↓
[Kết quả trả lên]     → Controller cập nhật UI
```

**Quy tắc giữa các tầng — giao tiếp một chiều, không bỏ tầng:**

| Tầng | Được gọi bởi | Được phép gọi |
|------|-------------|---------------|
| UI (screens) | User | Controller |
| Controller | UI | Service |
| Service | Controller | Repository |
| Repository | Service | Model / SQLAlchemy |
| Model | Repository | SQLAlchemy Core |

---

## Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Phiên bản |
|------------|-----------|-----------|
| UI Framework | PySide6 (Qt6) | 6.6+ |
| ORM | SQLAlchemy | 2.0+ |
| DB Driver | PyMySQL | 1.1+ |
| Database | MySQL | 8.0+ |
| Password Hash | passlib + bcrypt | 1.7+ |
| Excel Export | openpyxl | 3.1+ |
| PDF Export | reportlab | 4.1+ |
| Logging | Python logging | stdlib |

---

## Hướng Dẫn Cài Đặt

### Yêu cầu

- Python 3.10+
- MySQL 8.0+

### 1. Clone project

```bash
git clone https://github.com/imxyanua/EduStaff.git
cd EduStaff
```

### 2. Tạo virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Cấu hình `.env`

```env
DB_URL=mysql+pymysql://edustaff:edustaff_password@localhost:3306/edustaff
APP_NAME=EduStaff
LOG_LEVEL=INFO
```

---

## Hướng Dẫn Chạy

```bash
# Activate venv
venv\Scripts\activate

# Chạy ứng dụng (1 lệnh duy nhất)
python main.py
```

Khi khởi động, `main.py` lần lượt thực hiện:

1. Đọc cấu hình từ `.env`
2. Khởi tạo SQLAlchemy engine, tạo tất cả bảng
3. Chạy seed data nếu DB trống
4. Khởi tạo `QApplication` với dark theme
5. Hiển thị `LoginScreen`

---

## Tài Khoản Mặc Định

| Vai trò | Username | Password | Quyền hạn |
|---------|----------|----------|-----------|
| Admin | `admin` | `admin123` | Toàn quyền |
| Staff | `staff` | `staff123` | Xem + export |

> **Lưu ý**: Đổi mật khẩu mặc định sau khi cài đặt!

**Dữ liệu mẫu tự động tạo:**
- 2 tài khoản (admin, staff)
- 3 khoa (CNTT, ĐTVT, QTKD)
- 5 giảng viên phân bổ theo khoa
- 10 lịch giảng dạy học kỳ HK1-2025

---

## Tính Năng

| Tính năng | Mô tả |
|-----------|-------|
| bcrypt Auth | Xác thực mật khẩu an toàn |
| RBAC 2 roles | Phân quyền Admin / Staff |
| App Session | Singleton lưu user đăng nhập trong bộ nhớ |
| Logging | Ghi log ra file + console |
| Audit Logs | Lịch sử login / edit / delete |
| Export Excel | Xuất danh sách GV ra .xlsx |
| Export PDF | Xuất danh sách GV ra .pdf |
| Thống kê | Theo khoa, học vị, chức vụ |
| Quản lý TK | CRUD + khóa/mở tài khoản |
| Backup/Restore | Sao lưu/phục hồi database |
| Seed Data | Dữ liệu mẫu tự động |
| Search & Filter | Tìm kiếm, lọc nhiều tiêu chí |
| Pagination | Phân trang danh sách |
| Conflict Check | Kiểm tra trùng lịch giảng dạy |

---

### Hình ảnh phác thảo (chèn vào đây)   
Vào GitHub repo

Add file → Upload files

Upload ảnh vào assets/images
ví dụ:  

![Sao Lưu & Phục Hồi Dữ Liệu](assets/SaoLuu_PhucHoi.png)   
Sao Lưu & Phục Hồi Dữ Liệu 
<<<<<<< HEAD

![Thêm Khoa](assets/Themkhoa.jpg)   
Thêm Khoa
 
![Quản Lý Khoa](assets/Quanlykhoa.jpg)
Quản Lý Khoa

![Quản Lý Lịch Giảng Dạy](assets/Quanlylichgiangday.jpg)
Quản Lý Lịch Giảng Dạy

![Quản Lý Tài Khoản](assets/Quanlytaikhoan.jpg)
Quản Lý Tài Khoản

![Thêm Lịch Giảng Dạy](assets/themlichgiangday.jpg)
Thêm Lịch Giảng Dạy
=======
>>>>>>> c7f0427af015f136b04f3116cfc16edbfd1d088f

![Giao diện đăng nhập](assets/Giaodiendangnhap.png)

![Main Window & Sidebar](assets/MainWindow&Sidebar.png)

![SideBar chi tiết](assets/Sidebarchitiet.png)

![Thêm sửa giảng viên](assets/ThemSuaGiangVien.png)

![Xem chi tiết giảng viên](assets/XemChiTietGiangVien.png)


## Contributor

- xyanua. — maintainer & developer
- Huy12-05 — developer
- pmhieu2004 — developer

## License

MIT License — Free for educational and commercial use.
