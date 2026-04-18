# screens/login_screen.py — Fluent Design login dialog

from PySide6.QtWidgets import (
    QDialog, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QKeyEvent, QMouseEvent, QFont

from qfluentwidgets import (
    LineEdit, PasswordLineEdit, PrimaryPushButton, CheckBox,
    BodyLabel, TitleLabel, SubtitleLabel, CaptionLabel,
    setTheme, Theme, setThemeColor,
    CardWidget, ElevatedCardWidget,
    FluentIcon as FIF
)
from ui.icon_manager import IconManager
import api.auth_api as auth_api
from api.client import APIError


class LoginWorker(QThread):
    success = Signal(dict, dict)
    error   = Signal(str)

    def __init__(self, username: str, password: str):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        try:
            token_resp = auth_api.login(self.username, self.password)
            user_info  = auth_api.get_me()
            self.success.emit(token_resp, user_info)
        except APIError as e:
            self.error.emit(str(e))
        except ConnectionError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(f"Lỗi không xác định: {e}")


class LoginScreen(QDialog):
    """
    Fluent Design login dialog.
    Emits login_success(user_info) on successful authentication.
    """
    login_success = Signal(dict)

    def __init__(self):
        super().__init__()
        setTheme(Theme.DARK)
        setThemeColor("#0099FF")

        self.setWindowTitle("EduStaff — Đăng nhập")
        self.resize(1040, 680)
        self.setMinimumSize(900, 600)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._worker = None
        self._drag_pos = None
        self._left_panel = None
        self._feature_card = None
        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        # Outer rounded card — acts as window chrome
        self._outer = QFrame(self)
        self._outer.setObjectName("loginOuterCard")
        root_layout.addWidget(self._outer)

        root = QHBoxLayout(self._outer)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left panel — branding ─────────────────────────────────
        self._left_panel = QFrame()
        self._left_panel.setObjectName("loginLeftPanel")
        self._left_panel.setMinimumWidth(320)
        self._left_panel.setMaximumWidth(430)
        self._left_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_v = QVBoxLayout(self._left_panel)
        left_v.setContentsMargins(44, 0, 44, 32)
        left_v.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_v.setSpacing(0)

        # Close button (top-right of left panel area)
        close_btn_row = QHBoxLayout()
        close_btn_row.addStretch()
        close_q = PrimaryPushButton("✕", self)
        close_q.setFixedSize(28, 28)
        close_q.setStyleSheet(
            "PrimaryPushButton{border-radius:14px; font-size:12px;"
            "background:rgba(255,255,255,0.06); border:none;}"
            "PrimaryPushButton:hover{background:rgba(248,81,73,0.25);}"
        )
        close_q.clicked.connect(self.reject)
        close_btn_row.addWidget(close_q)
        left_v.addSpacing(16)
        left_v.addLayout(close_btn_row)

        # Logo
        logo_lbl = QLabel()
        logo_lbl.setPixmap(IconManager.get("graduation-cap", "#0099FF", 72).pixmap(72, 72))
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_name = QLabel("EduStaff")
        app_name.setObjectName("appName")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        tagline = CaptionLabel("Hệ Thống Quản Lý Giảng Viên Đại Học", self)
        tagline.setObjectName("loginSubtitle")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Feature list
        self._feature_card = QFrame()
        self._feature_card.setObjectName("loginFeatureCard")
        fc_v = QVBoxLayout(self._feature_card)
        fc_v.setContentsMargins(16, 12, 16, 12)
        fc_v.setSpacing(8)
        for feat in [
            "✦  Quản lý hồ sơ giảng viên",
            "✦  Phân công lịch giảng dạy",
            "✦  Thống kê & xuất báo cáo",
            "✦  Nhật ký và sao lưu dữ liệu",
        ]:
            l = QLabel(feat)
            l.setObjectName("statusHint")
            l.setStyleSheet("background:transparent;")
            fc_v.addWidget(l)

        left_v.addStretch()
        left_v.addWidget(logo_lbl)
        left_v.addSpacing(12)
        left_v.addWidget(app_name)
        left_v.addSpacing(4)
        left_v.addWidget(tagline)
        left_v.addSpacing(28)
        left_v.addWidget(self._feature_card)
        left_v.addStretch()

        version_lbl = CaptionLabel("v1.0.0 © 2026 EduStaff", self)
        version_lbl.setObjectName("statusHint")
        version_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_v.addWidget(version_lbl)
        left_v.addSpacing(4)

        root.addWidget(self._left_panel, stretch=5)

        # ── Right panel — login form ──────────────────────────────
        right = QWidget()
        right_v = QVBoxLayout(right)
        right_v.setContentsMargins(56, 40, 56, 40)
        right_v.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        right_v.setSpacing(0)

        greeting = CaptionLabel("Chào mừng trở lại", self)
        greeting.setObjectName("loginSubtitle")

        title = QLabel("Đăng nhập hệ thống")
        title.setObjectName("loginTitle")
        title.setStyleSheet("background:transparent;")

        subtitle = CaptionLabel("Nhập thông tin tài khoản để tiếp tục", self)
        subtitle.setObjectName("loginSubtitle")

        # Username
        user_lbl = QLabel("Tên đăng nhập")
        user_lbl.setObjectName("formFieldLabel")
        user_lbl.setStyleSheet("background:transparent;")
        self._username_input = LineEdit(self)
        self._username_input.setPlaceholderText("Nhập tên đăng nhập...")
        self._username_input.setMinimumHeight(42)
        self._username_input.setClearButtonEnabled(True)

        # Password
        pwd_lbl = QLabel("Mật khẩu")
        pwd_lbl.setObjectName("formFieldLabel")
        pwd_lbl.setStyleSheet("background:transparent;")
        self._password_input = PasswordLineEdit(self)
        self._password_input.setPlaceholderText("Nhập mật khẩu...")
        self._password_input.setMinimumHeight(42)
        self._password_input.returnPressed.connect(self._on_login)

        # Remember
        self._remember_cb = CheckBox("Ghi nhớ đăng nhập", self)

        # Error
        self._error_lbl = QLabel()
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setStyleSheet(
            "color:#F85149; background:#3D1318; border:1px solid #5A1E24;"
            "border-radius:8px; padding:10px 14px; font-size:12px;"
        )
        self._error_lbl.hide()

        # Login button
        self._login_btn = PrimaryPushButton(FIF.SEND, "  Đăng Nhập", self)
        self._login_btn.setMinimumHeight(44)
        self._login_btn.setMinimumWidth(200)
        self._login_btn.clicked.connect(self._on_login)

        right_v.addWidget(greeting)
        right_v.addSpacing(6)
        right_v.addWidget(title)
        right_v.addSpacing(4)
        right_v.addWidget(subtitle)
        right_v.addSpacing(36)
        right_v.addWidget(user_lbl)
        right_v.addSpacing(6)
        right_v.addWidget(self._username_input)
        right_v.addSpacing(18)
        right_v.addWidget(pwd_lbl)
        right_v.addSpacing(6)
        right_v.addWidget(self._password_input)
        right_v.addSpacing(14)
        right_v.addWidget(self._remember_cb)
        right_v.addSpacing(10)
        right_v.addWidget(self._error_lbl)
        right_v.addSpacing(24)
        right_v.addWidget(self._login_btn)

        root.addWidget(right, stretch=7)

    # ── Slots ─────────────────────────────────────────────────────

    def _on_login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text()

        if not username:
            self._show_error("Vui lòng nhập tên đăng nhập")
            self._username_input.setFocus()
            return
        if not password:
            self._show_error("Vui lòng nhập mật khẩu")
            self._password_input.setFocus()
            return

        self._set_loading(True)
        self._worker = LoginWorker(username, password)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_success(self, token_resp: dict, user_info: dict):
        self._set_loading(False)
        self._error_lbl.hide()
        self.login_success.emit(user_info)
        self.accept()

    def _on_error(self, msg: str):
        self._set_loading(False)
        self._show_error(msg)
        self._shake()

    def _show_error(self, msg: str):
        self._error_lbl.setText(f"⚠️  {msg}")
        self._error_lbl.show()

    def _set_loading(self, loading: bool):
        self._login_btn.setEnabled(not loading)
        self._username_input.setEnabled(not loading)
        self._password_input.setEnabled(not loading)
        self._login_btn.setText("⏳  Đang xử lý..." if loading else "  Đăng Nhập")

    def _shake(self):
        anim = QPropertyAnimation(self._password_input, b"pos")
        anim.setDuration(280)
        orig = self._password_input.pos()
        anim.setKeyValueAt(0.0,  orig)
        anim.setKeyValueAt(0.25, orig + QPoint(-5, 0))
        anim.setKeyValueAt(0.5,  orig + QPoint(5, 0))
        anim.setKeyValueAt(0.75, orig + QPoint(-3, 0))
        anim.setKeyValueAt(1.0,  orig)
        anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        anim.start()
        self._shake_anim = anim

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_login()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._drag_pos = None

    def resizeEvent(self, event):
        # Tối ưu trải nghiệm mobile-size: ẩn khối mô tả khi cửa sổ quá hẹp.
        narrow = self.width() < 980
        if self._feature_card is not None:
            self._feature_card.setVisible(not narrow)
        if self._left_panel is not None:
            self._left_panel.setMaximumWidth(360 if narrow else 430)
        super().resizeEvent(event)
