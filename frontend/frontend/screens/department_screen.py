# screens/department_screen.py — Fluent department management screen

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer

from qfluentwidgets import (
    PrimaryPushButton, PushButton, ToolButton,
    LineEdit, SearchLineEdit, ComboBox, TextEdit,
    TableWidget, ElevatedCardWidget, BodyLabel,
    FluentIcon as FIF,
)

from components.cards import SectionHeader
from components.dialogs import confirm, FluentFormDialog
from components.form_field import FormField
from components.pagination import PaginationBar
from components.loading import LoadingOverlay
from components.empty import EmptyStateWidget
from components.toast import toast_success, toast_error
import api.department_api as department_api


# ── Workers ───────────────────────────────────────────────────────

class LoadDeptWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def __init__(self, search: str = ""):
        super().__init__()
        self.search = search

    def run(self):
        try:
            r = department_api.get_departments(self.search)
            self.finished.emit(r if isinstance(r, list) else [])
        except Exception as e:
            self.error.emit(str(e))


class SaveDeptWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, mode: str, data: dict, dept_id: int = None):
        super().__init__()
        self.mode = mode
        self.data = data
        self.dept_id = dept_id

    def run(self):
        try:
            if self.mode == "add":
                self.finished.emit(department_api.create_department(self.data))
            else:
                self.finished.emit(department_api.update_department(self.dept_id, self.data))
        except Exception as e:
            self.error.emit(str(e))


class DeleteDeptWorker(QThread):
    finished = Signal()
    error    = Signal(str)

    def __init__(self, dept_id: int):
        super().__init__()
        self.dept_id = dept_id

    def run(self):
        try:
            department_api.delete_department(self.dept_id)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# ── Form dialog ────────────────────────────────────────────────────

class DepartmentFormDialog(FluentFormDialog):
    saved = Signal(dict)

    def __init__(self, mode: str = "add", dept: dict = None, parent=None):
        self._mode = mode
        self._dept = dept or {}
        self._save_worker = None
        title = "Thêm Khoa Mới" if mode == "add" else "Cập Nhật Khoa"
        super().__init__(title, parent, min_width=480)

    def _build_form(self, layout):
        dept = self._dept

        self._code_input = LineEdit()
        self._code_input.setPlaceholderText("VD: CNTT")
        self._code_input.setText(dept.get("code", ""))
        self._code_field = FormField("Mã Khoa *", self._code_input)
        layout.addWidget(self._code_field)

        self._name_input = LineEdit()
        self._name_input.setPlaceholderText("VD: Công nghệ Thông tin")
        self._name_input.setText(dept.get("name", ""))
        self._name_field = FormField("Tên Khoa *", self._name_input)
        layout.addWidget(self._name_field)

        self._desc_input = TextEdit()
        self._desc_input.setPlaceholderText("Mô tả ngắn về khoa (không bắt buộc)")
        self._desc_input.setPlainText(dept.get("description", "") or "")
        self._desc_input.setFixedHeight(90)
        layout.addWidget(FormField("Mô Tả", self._desc_input))

        self._required = [
            (self._code_input, self._code_field, "mã khoa"),
            (self._name_input, self._name_field, "tên khoa"),
        ]

    def _validate(self) -> bool:
        valid = True
        for widget, field, name in self._required:
            if not widget.text().strip():
                field.set_error(f"Vui lòng nhập {name}")
                valid = False
            else:
                field.clear_error()
        return valid

    def _collect(self) -> dict:
        return {
            "code":        self._code_input.text().strip(),
            "name":        self._name_input.text().strip(),
            "description": self._desc_input.toPlainText().strip() or None,
        }

    def _on_save(self):
        if not self._validate():
            return
        self.set_loading(True)
        self._error_lbl.hide()
        self._save_worker = SaveDeptWorker(self._mode, self._collect(), self._dept.get("id"))
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

class DepartmentScreen(QWidget):
    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DepartmentScreen")
        self.user_info  = user_info
        self.is_admin   = user_info.get("role") == "admin"
        self._row_data  = []
        self._worker    = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        header_row.addWidget(
            SectionHeader(
                "Quản Lý Khoa / Bộ Môn",
                "Tổ chức giảng viên theo khoa",
                icon="buildings",
            )
        )
        header_row.addStretch()
        if self.is_admin:
            add_btn = PrimaryPushButton(FIF.ADD, "  Thêm Khoa", self)
            add_btn.clicked.connect(self._on_add)
            header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Filter
        toolbar = ElevatedCardWidget()
        tb_h = QHBoxLayout(toolbar)
        tb_h.setContentsMargins(16, 10, 16, 10)
        tb_h.setSpacing(10)

        self._search_input = SearchLineEdit(self)
        self._search_input.setPlaceholderText("Tìm theo tên, mã khoa...")
        self._search_input.setFixedHeight(36)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._on_search)
        self._search_input.textChanged.connect(lambda: self._search_timer.start(300))

        reset_btn = PushButton(FIF.SYNC, "  Làm mới", self)
        reset_btn.clicked.connect(self._reset)
        tb_h.addWidget(self._search_input)
        tb_h.addWidget(reset_btn)
        layout.addWidget(toolbar)

        # Table
        table_card = ElevatedCardWidget()
        table_v = QVBoxLayout(table_card)
        table_v.setContentsMargins(0, 0, 0, 0)

        COLS = ["#", "Mã Khoa", "Tên Khoa", "Mô Tả", "Số GV", "Thao tác"]
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
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self._table.setColumnWidth(0, 44)
        self._table.setColumnWidth(1, 90)
        self._table.setColumnWidth(4, 70)
        self._table.setColumnWidth(5, 110 if self.is_admin else 56)
        self._table.verticalHeader().setDefaultSectionSize(44)

        self._empty = EmptyStateWidget("Không tìm thấy khoa nào", on_retry=self.refresh)
        self._empty.hide()

        table_v.addWidget(self._table, stretch=1)
        table_v.addWidget(self._empty)
        layout.addWidget(table_card, stretch=1)

        self._loading = LoadingOverlay(self)

    def refresh(self):
        search = self._search_input.text().strip()
        self._loading.show()
        self._worker = LoadDeptWorker(search)
        self._worker.finished.connect(self._on_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_loaded(self, items: list):
        self._loading.hide()
        self._row_data = items
        self._table.setRowCount(0)
        for i, dept in enumerate(items):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)
            cells = [
                (str(i + 1),                                    Qt.AlignmentFlag.AlignCenter),
                (dept.get("code", ""),                          Qt.AlignmentFlag.AlignCenter),
                (dept.get("name", ""),                          Qt.AlignmentFlag.AlignLeft),
                ((dept.get("description", "") or "")[:60],      Qt.AlignmentFlag.AlignLeft),
                (str(dept.get("lecturer_count", 0)),            Qt.AlignmentFlag.AlignCenter),
            ]
            for col, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(int(align | Qt.AlignmentFlag.AlignVCenter))
                self._table.setItem(row, col, item)
            self._table.setCellWidget(row, 5, self._make_actions(dept))

        if items:
            self._table.show()
            self._empty.hide()
        else:
            self._table.hide()
            self._empty.show()

    def _make_actions(self, dept: dict) -> QWidget:
        from PySide6.QtWidgets import QWidget
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(4)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.is_admin:
            edit_btn = ToolButton(FIF.EDIT, c)
            edit_btn.setToolTip("Chỉnh sửa")
            edit_btn.clicked.connect(lambda _, d=dept: self._on_edit(d))
            h.addWidget(edit_btn)
            del_btn = ToolButton(FIF.DELETE, c)
            del_btn.setToolTip("Xóa")
            del_btn.clicked.connect(lambda _, d=dept: self._on_delete(d))
            h.addWidget(del_btn)
        return c

    def _on_search(self):
        self.refresh()

    def _reset(self):
        self._search_input.clear()

    def _on_add(self):
        dlg = DepartmentFormDialog("add", parent=self)
        dlg.saved.connect(lambda _: (toast_success(self.window(), "Thêm khoa thành công!"), self.refresh()))
        dlg.exec()

    def _on_edit(self, dept: dict):
        dlg = DepartmentFormDialog("edit", dept=dept, parent=self)
        dlg.saved.connect(lambda _: (toast_success(self.window(), "Cập nhật khoa thành công!"), self.refresh()))
        dlg.exec()

    def _on_delete(self, dept: dict):
        name = dept.get("name", "")
        if not confirm("Xác nhận xóa", f'Xóa khoa "{name}"?\nCác giảng viên thuộc khoa này sẽ bị ảnh hưởng.', self, "Xóa"):
            return
        w = DeleteDeptWorker(dept["id"])
        w.finished.connect(lambda: (toast_success(self.window(), "Đã xóa khoa!"), self.refresh()))
        w.error.connect(lambda msg: toast_error(self.window(), msg))
        w.start()
        self._del_worker = w

    def _on_error(self, msg: str):
        self._loading.hide()
        toast_error(self.window(), msg)

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
