# frontend/main.py
# Entry point — khởi động ứng dụng EduStaff

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont


def main():
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("EduStaff")
    app.setOrganizationName("University Management")
    app.setApplicationVersion("1.0.0")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Append global theme on top of qfluentwidgets theme
    qss_path = os.path.join(os.path.dirname(__file__), "styles", "theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(app.styleSheet() + "\n" + f.read())

    from screens.login_screen import LoginScreen

    login = LoginScreen()
    _win_refs = []  # keep reference to prevent GC

    def on_login_success(user_info: dict):
        try:
            from screens.main_window import MainWindow
            win = MainWindow(user_info)
            win.show()
            _win_refs.append(win)
        except Exception:
            import traceback
            traceback.print_exc()
            with open("error.log", "w") as f:
                traceback.print_exc(file=f)

    login.login_success.connect(on_login_success)
    login.exec()

    if not _win_refs:
        sys.exit(0)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
