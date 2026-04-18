# screens/account_screen.py — Fluent account management (Admin only)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

from qfluentwidgets import (
    PrimaryPushButton, PushButton, ToolButton,
    LineEdit, SearchLineEdit, ComboBox, PasswordLineEdit,
    TableWidget, ElevatedCardWidget, BodyLabel,
    FluentIcon as FIF,
)

from components.badges import Badge
from components.cards import SectionHeader
from components.dialogs import confirm, FluentFormDialog
from components.form_field import FormField
from components.loading import LoadingOverlay
from components.empty import EmptyStateWidget
from components.toast import toast_success, toast_error
import api.account_api as account_api


# ── Workers ───────────────────────────────────────────────────────

class LoadAccountsWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def __init__(self, search: str, role: str, is_active):
        super().__init__()
        self.search = search
        self.role = role
        self.is_active = is_active

    def run(self):
        try:
            r = account_api.get_accounts(search=self.search, role=self.role, is_active=self.is_active)
            self.finished.emit(r if isinstance(r, list) else [])
        except Exception as e:
            self.error.emit(str(e))


class SaveAccountWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, mode: str, data: dict, account_id: int = None):
        super().__init__()
        self.mode = mode
        self.data = data
        self.account_id = account_id

    def run(self):
        try:
            if self.mode == "add":
                self.finished.emit(account_api.create_account(self.data))
            else:
                self.finished.emit(account_api.update_account(self.account_id, self.data))
        except Exception as e:
            self.error.emit(str(e))


class ToggleAccountWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, account_id: int):
        super().__init__()
        self.account_id = account_id

    def run(self):
        try:
            self.finished.emit(account_api.toggle_active(self.account_id))
        except Exception as e:
            self.error.emit(str(e))


# ── Form dialog ────────────────────────────────────────────────────

class AccountFormDialog(FluentFormDialog):
    saved = Signal(dict)

    def __init__(self, mode: str = "add", account: dict = None, parent=None):
        self._mode = mode
        self._account = account or {}
        self._save_worker = None
        title = "Tạo Tài Khoản Mới" if mode == "add" else "Cập Nhật Tài Khoản"
        super().__init__(title, parent, min_width=500)

    def _build_form(self, layout):
        acc = self._account

        self._username_input = LineEdit()
        self._username_input.setPlaceholderText("tên_đăng_nhập")
        self._username_input.setText(acc.get("username", ""))
        if self._mode == "edit":
            self._username_input.setEnabled(False)
        self._username_field = FormField("Tên Đăng Nhập *", self._username_input)
        layout.addWidget(self._username_field)

        self._fullname_input = LineEdit()
        self._fullname_input.setPlaceholderText("Họ và tên")
        self._fullname_input.setText(acc.get("full_name", ""))
        self._fullname_field = FormField("Họ & Tên *", self._fullname_input)
        layout.addWidget(self._fullname_field)

        self._role_combo = ComboBox()
        self._role_combo.addItem("Staff", userData="staff")
        self._role_combo.addItem("Admin", userData="admin")
        idx = self._role_combo.findData(acc.get("role", "staff"))
        if idx >= 0:
            self._role_combo.setCurrentIndex(idx)
        layout.addWidget(FormField("Vai Trò *", self._role_combo))

        # Password section
        from PySide6.QtWidgets import QLabel
        pwd_header = QLabel("MẬT KHẨU" + ("" if self._mode == "add" else " (Bỏ trống nếu không đổi)"))
        pwd_header.setStyleSheet(
            "color:#484F58; font-size:10px; font-weight:700; letter-spacing:1.2px;"
        )
        layout.addWidget(pwd_header)

        self._password_input = PasswordLineEdit()
        self._password_input.setPlaceholderText("Mật khẩu mới...")
        self._pwd_field = FormField("Mật Khẩu" + (" *" if self._mode == "add" else ""),
                                    self._password_input)
        layout.addWidget(self._pwd_field)

        self._confirm_input = PasswordLineEdit()
        self._confirm_input.setPlaceholderText("Nhập lại mật khẩu...")
        self._confirm_field = FormField("Xác Nhận Mật Khẩu", self._confirm_input)
        layout.addWidget(self._confirm_field)

        self._required = [
            (self._fullname_input, self._fullname_field, "họ & tên"),
        ]
        if self._mode == "add":
            self._required.append((self._username_input, self._username_field, "tên đăng nhập"))

    def _validate(self) -> bool:
        valid = True
        for widget, field, name in self._required:
            if not widget.text().strip():
                field.set_error(f"Vui lòng nhập {name}")
                valid = False
            else:
                field.clear_error()

        pwd = self._password_input.text()
        conf = self._confirm_input.text()
        if self._mode == "add" and not pwd:
            self._pwd_field.set_error("Vui lòng nhập mật khẩu")
            valid = False
        elif pwd and pwd != conf:
            self._confirm_field.set_error("Mật khẩu xác nhận không khớp")
            valid = False
        else:
            self._pwd_field.clear_error()
            self._confirm_field.clear_error()
        return valid

    def _collect(self) -> dict:
        data = {
            "username":  self._username_input.text().strip(),
            "full_name": self._fullname_input.text().strip(),
            "role":      self._role_combo.currentData(),
        }
        pwd = self._password_input.text()
        if pwd:
            data["password"] = pwd
        return data

    def _on_save(self):
        if not self._validate():
            return
        self.set_loading(True)
        self._save_worker = SaveAccountWorker(
            self._mode, self._collect(), self._account.get("id")
        )
        self._save_worker.finished.connect(self._on_saved)
        self._save_worker.error.connect(self._on_err)
        self._save_worker.start()

    def _on_saved(self, result: dict):
        self.set_loading(False)
        self.saved.emit(result)
        self.accept()

    def _on_err(self, msg: str):
        self.set_loading(False)
        self.show_error(msg)


# ── Main screen ────────────────────────────────────────────────────

class AccountScreen(QWidget):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("AccountScreen")
        self.user_info = user_info
        self._row_data = []
        self._worker   = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.addWidget(
            SectionHeader(
                "Quản Lý Tài Khoản",
                "Tạo và quản lý tài khoản người dùng (Admin only)",
                icon="shield-check",
            )
        )
        header_row.addStretch()
        add_btn = PrimaryPushButton(FIF.ADD, "  Tạo Tài Khoản", self)
        add_btn.clicked.connect(self._on_add)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Filter
        toolbar = ElevatedCardWidget()
        tb_h = QHBoxLayout(toolbar)
        tb_h.setContentsMargins(16, 10, 16, 10)
        tb_h.setSpacing(12)

        self._search_input = SearchLineEdit(self)
        self._search_input.setPlaceholderText("Tìm theo tên, username...")
        self._search_input.setFixedHeight(36)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.refresh)
        self._search_input.textChanged.connect(lambda: self._search_timer.start(300))
        tb_h.addWidget(self._search_input)

        tb_h.addWidget(BodyLabel("Vai trò:"))
        self._role_filter = ComboBox(self)
        self._role_filter.setFixedWidth(110)
        self._role_filter.addItem("Tất cả", userData="")
        self._role_filter.addItem("Admin", userData="admin")
        self._role_filter.addItem("Staff", userData="staff")
        self._role_filter.currentIndexChanged.connect(self.refresh)
        tb_h.addWidget(self._role_filter)

        tb_h.addWidget(BodyLabel("Trạng thái:"))
        self._status_filter = ComboBox(self)
        self._status_filter.setFixedWidth(130)
        self._status_filter.addItem("Tất cả", userData=None)
        self._status_filter.addItem("Hoạt động", userData=True)
        self._status_filter.addItem("Đã khóa",   userData=False)
        self._status_filter.currentIndexChanged.connect(self.refresh)
        tb_h.addWidget(self._status_filter)
        layout.addWidget(toolbar)

        # Table
        table_card = ElevatedCardWidget()
        table_v = QVBoxLayout(table_card)
        table_v.setContentsMargins(0, 0, 0, 0)

        COLS = ["#", "Username", "Họ & Tên", "Vai Trò", "Trạng Thái", "Ngày Tạo", "Thao tác"]
        self._table = TableWidget(self)
        self._table.setColumnCount(len(COLS))
        self._table.setHorizontalHeaderLabels(COLS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self._table.setShowGrid(False)
        self._table.setBorderVisible(True)
        self._table.setBorderRadius(8)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 44)
        self._table.setColumnWidth(1, 130)
        self._table.setColumnWidth(3, 90)
        self._table.setColumnWidth(4, 110)
        self._table.setColumnWidth(6, 140)
        self._table.verticalHeader().setDefaultSectionSize(44)

        self._empty = EmptyStateWidget("Không tìm thấy tài khoản nào", on_retry=self.refresh)
        self._empty.hide()
        table_v.addWidget(self._table, stretch=1)
        table_v.addWidget(self._empty)
        layout.addWidget(table_card, stretch=1)
        self._loading = LoadingOverlay(self)

    def refresh(self):
        self._loading.show()
        self._worker = LoadAccountsWorker(
            self._search_input.text().strip(),
            self._role_filter.currentData() or "",
            self._status_filter.currentData(),
        )
        self._worker.finished.connect(self._on_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_loaded(self, items: list):
        self._loading.hide()
        self._row_data = items
        self._table.setRowCount(0)
        for i, acc in enumerate(items):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)
            cells = [
                (str(i + 1),                     Qt.AlignmentFlag.AlignCenter),
                (acc.get("username", ""),         Qt.AlignmentFlag.AlignLeft),
                (acc.get("full_name", ""),         Qt.AlignmentFlag.AlignLeft),
            ]
            for col, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(int(align | Qt.AlignmentFlag.AlignVCenter))
                self._table.setItem(row, col, item)

            self._table.setCellWidget(row, 3, self._center(Badge.role(acc.get("role", "staff"))))
            self._table.setCellWidget(row, 4, self._center(Badge.account_status(acc.get("is_active", True))))

            created = str(acc.get("created_at", ""))[:10]
            date_item = QTableWidgetItem(created)
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 5, date_item)
            self._table.setCellWidget(row, 6, self._make_actions(acc))

        if items:
            self._table.show()
            self._empty.hide()
        else:
            self._table.hide()
            self._empty.show()

    def _center(self, widget: QWidget) -> QWidget:
        from PySide6.QtWidgets import QWidget
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 0, 4, 0)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(widget)
        return c

    def _make_actions(self, acc: dict) -> QWidget:
        from PySide6.QtWidgets import QWidget
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(4)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        edit_btn = ToolButton(FIF.EDIT, c)
        edit_btn.setToolTip("Chỉnh sửa")
        edit_btn.clicked.connect(lambda _, a=acc: self._on_edit(a))
        h.addWidget(edit_btn)

        is_active = acc.get("is_active", True)
        lock_btn = ToolButton(FIF.CANCEL if is_active else FIF.ACCEPT, c)
        lock_btn.setToolTip("Khóa tài khoản" if is_active else "Mở khóa tài khoản")
        lock_btn.clicked.connect(lambda _, a=acc: self._on_toggle(a))
        h.addWidget(lock_btn)

        del_btn = ToolButton(FIF.DELETE, c)
        del_btn.setToolTip("Xóa tài khoản")
        del_btn.clicked.connect(lambda _, a=acc: self._on_delete(a))
        h.addWidget(del_btn)
        return c

    def _on_add(self):
        dlg = AccountFormDialog("add", parent=self)
        dlg.saved.connect(lambda _: (toast_success(self.window(), "Tạo tài khoản thành công!"), self.refresh()))
        dlg.exec()

    def _on_edit(self, acc: dict):
        dlg = AccountFormDialog("edit", account=acc, parent=self)
        dlg.saved.connect(lambda _: (toast_success(self.window(), "Cập nhật tài khoản thành công!"), self.refresh()))
        dlg.exec()

    def _on_toggle(self, acc: dict):
        status = "khóa" if acc.get("is_active") else "mở khóa"
        name   = acc.get("username", "")
        if not confirm("Xác nhận", f'Bạn muốn {status} tài khoản "{name}"?', self, "Xác nhận"):
            return
        w = ToggleAccountWorker(acc["id"])
        w.finished.connect(lambda _: (toast_success(self.window(), f"Đã {status} tài khoản!"), self.refresh()))
        w.error.connect(lambda msg: toast_error(self.window(), msg))
        w.start()
        self._toggle_worker = w

    def _on_delete(self, acc: dict):
        name = acc.get("username", "")
        if acc.get("id") == self.user_info.get("id"):
            toast_error(self.window(), "Không thể xóa tài khoản đang đăng nhập!")
            return
        if not confirm("Xác nhận xóa", f'Xóa tài khoản "{name}"?', self, "Xóa"):
            return
        try:
            account_api.delete_account(acc["id"])
            toast_success(self.window(), "Đã xóa tài khoản!")
            self.refresh()
        except Exception as e:
            toast_error(self.window(), str(e))

    def _on_error(self, msg: str):
        self._loading.hide()
        toast_error(self.window(), msg)

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
