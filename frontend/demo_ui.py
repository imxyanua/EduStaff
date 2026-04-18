"""
Demo script — hiển thị UI EduStaff không cần backend
Dùng: python demo_ui.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from PySide6.QtWidgets import QApplication
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Thiếu PySide6. Hãy cài dependencies bằng lệnh: python -m pip install -r requirements.txt"
    ) from exc
from PySide6.QtGui import QFont

# Mock user info
MOCK_USER_ADMIN = {
    "id": 1,
    "username": "admin",
    "full_name": "Nguyễn Quản Trị",
    "role": "admin",
    "is_active": True
}

MOCK_USER_STAFF = {
    "id": 2,
    "username": "staff01",
    "full_name": "Trần Nhân Viên",
    "role": "staff",
    "is_active": True
}

def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("EduStaff Demo")
    app.setOrganizationName("University Management")
    app.setApplicationVersion("1.0.0")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    theme_path = os.path.join(os.path.dirname(__file__), "styles", "theme.qss")
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(app.styleSheet() + "\n" + f.read())

    # Mở MainWindow với user admin (demo, không qua login)
    try:
        from screens.main_window import MainWindow
    except ModuleNotFoundError as exc:
        if exc.name == "qfluentwidgets":
            raise ModuleNotFoundError(
                "Thiếu qfluentwidgets. Hãy cài dependencies bằng lệnh: python -m pip install -r requirements.txt"
            ) from exc
        raise
    win = MainWindow(MOCK_USER_ADMIN)
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
