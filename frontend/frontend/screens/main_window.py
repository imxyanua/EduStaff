# screens/main_window.py — FluentWindow với navigation sidebar

import sys
import datetime
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent

from qfluentwidgets import (
    FluentWindow, NavigationItemPosition,
    setTheme, Theme, setThemeColor,
    FluentIcon as FIF,
    NavigationAvatarWidget, InfoBar, InfoBarPosition,
    MessageBox
)

from components.toast import toast_success, toast_error


class MainWindow(FluentWindow):
    """
    Cửa sổ chính dùng FluentWindow — tự động tạo sidebar navigation
    và quản lý QStackedWidget. Screens được thêm qua addSubInterface().
    """

    def __init__(self, user_info: dict):
        super().__init__()
        self.user_info = user_info
        self.is_admin = user_info.get("role") == "admin"

        # ── Window setup ─────────────────────────────────────────
        self.setWindowTitle("EduStaff — Hệ Thống Quản Lý Giảng Viên")
        self.resize(1340, 860)
        self.setMinimumSize(1120, 700)

        # ── Theme ─────────────────────────────────────────────────
        setTheme(Theme.DARK)
        setThemeColor("#0099FF")
        self._apply_window_effect()

        # ── Screens + navigation ──────────────────────────────────
        self._init_screens()
        self._setup_navigation()

        # ── Clock in status bar ───────────────────────────────────
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self._update_status_tip)
        self._clock_timer.start(60_000)

    # ── Init screens ─────────────────────────────────────────────

    def _init_screens(self):
        from screens.dashboard_screen import DashboardScreen
        from screens.lecturer_screen import LecturerScreen
        from screens.department_screen import DepartmentScreen
        from screens.schedule_screen import ScheduleScreen
        from screens.account_screen import AccountScreen
        from screens.audit_log_screen import AuditLogScreen
        from screens.backup_screen import BackupScreen

        self.screen_dashboard   = DashboardScreen(self.user_info, self)
        self.screen_lecturers   = LecturerScreen(self.user_info, self)
        self.screen_departments = DepartmentScreen(self.user_info, self)
        self.screen_schedules   = ScheduleScreen(self.user_info, self)
        self.screen_accounts    = AccountScreen(self.user_info, self)
        self.screen_audit       = AuditLogScreen(self.user_info, self)
        self.screen_backup      = BackupScreen(self.user_info, self)

    # ── Navigation setup ──────────────────────────────────────────

    def _setup_navigation(self):
        nav = self.navigationInterface

        # ── Main screens ─────────────────────────────────────────
        self.addSubInterface(
            self.screen_dashboard, FIF.HOME, "Dashboard",
            position=NavigationItemPosition.SCROLL
        )
        self.addSubInterface(
            self.screen_lecturers, FIF.PEOPLE, "Giảng Viên",
            position=NavigationItemPosition.SCROLL
        )
        self.addSubInterface(
            self.screen_departments, FIF.LIBRARY, "Khoa / Bộ Môn",
            position=NavigationItemPosition.SCROLL
        )
        self.addSubInterface(
            self.screen_schedules, FIF.CALENDAR, "Lịch Giảng Dạy",
            position=NavigationItemPosition.SCROLL
        )

        # ── Admin-only section ────────────────────────────────────
        if self.is_admin:
            nav.addSeparator(position=NavigationItemPosition.SCROLL)
            self.addSubInterface(
                self.screen_accounts, FIF.PEOPLE, "Tài Khoản",
                position=NavigationItemPosition.SCROLL
            )
            self.addSubInterface(
                self.screen_audit, FIF.HISTORY, "Nhật Ký HT",
                position=NavigationItemPosition.SCROLL
            )
            self.addSubInterface(
                self.screen_backup, FIF.SAVE, "Sao Lưu",
                position=NavigationItemPosition.SCROLL
            )

        # ── Logout (bottom) ───────────────────────────────────────
        nav.addItem(
            routeKey="logout",
            icon=FIF.CLOSE,
            text="Đăng xuất",
            onClick=self._on_logout,
            position=NavigationItemPosition.BOTTOM,
        )

        # ── User avatar chip ──────────────────────────────────────
        name = self.user_info.get("full_name", "Người dùng")
        role = self.user_info.get("role", "staff")
        nav.addWidget(
            routeKey="avatar",
            widget=NavigationAvatarWidget(name[:1].upper(), name),
            onClick=lambda: None,
            position=NavigationItemPosition.BOTTOM,
        )

        nav.setExpandWidth(248)
        nav.setCollapsible(True)

    def _apply_window_effect(self):
        # Bật hiệu ứng Mica nếu qfluentwidgets hỗ trợ phiên bản đang dùng.
        try:
            self.setMicaEffectEnabled(True)
        except Exception:
            pass

    # ── Helpers ───────────────────────────────────────────────────

    def show_toast(self, content: str, kind: str = "success"):
        fn = {"success": toast_success, "error": toast_error}.get(kind, toast_success)
        fn(self, content)

    def _update_status_tip(self):
        now = datetime.datetime.now().strftime("%H:%M")
        self.setWindowTitle(f"EduStaff — {now}")

    def _on_logout(self):
        box = MessageBox("Đăng xuất", "Bạn có chắc muốn đăng xuất khỏi hệ thống?", self)
        box.yesButton.setText("Đăng xuất")
        box.cancelButton.setText("Hủy")
        if box.exec():
            import api.auth_api as auth_api
            auth_api.logout()
            self.close()
            from screens.login_screen import LoginScreen
            login = LoginScreen()
            login.login_success.connect(self._reopen)
            login.exec()

    def _reopen(self, user_info: dict):
        self._new_win = MainWindow(user_info)
        self._new_win.show()

    def closeEvent(self, event: QCloseEvent):
        self._clock_timer.stop()
        event.accept()
