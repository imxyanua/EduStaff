# screens/lecturer_screen.py — Fluent lecturer management screen

import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QFileDialog, QApplication, QButtonGroup, QRadioButton,
    QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal, QDate, QTimer
from PySide6.QtGui import QKeySequence, QShortcut

from qfluentwidgets import (
    PrimaryPushButton, PushButton, TransparentPushButton, ToolButton,
    LineEdit, SearchLineEdit, ComboBox,
    TableWidget, SmoothScrollArea,
    BodyLabel, CaptionLabel, SubtitleLabel,
    CardWidget, ElevatedCardWidget,
    MessageBox, FluentIcon as FIF,
    DatePicker,
    IndeterminateProgressBar,
)

from components.badges import Badge
from components.cards import SectionHeader
from components.dialogs import confirm, FluentFormDialog
from components.pagination import PaginationBar
from components.loading import LoadingOverlay
from components.empty import EmptyStateWidget
from components.form_field import FormField
from components.toast import toast_success, toast_error
from ui.icon_manager import IconManager
import api.lecturer_api as lecturer_api
import api.department_api as department_api


# ── Workers ───────────────────────────────────────────────────────

class LoadLecturersWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, filters: dict):
        super().__init__()
        self.filters = filters

    def run(self):
        try:
            self.finished.emit(lecturer_api.get_lecturers(**self.filters))
        except Exception as e:
            self.error.emit(str(e))


class SaveLecturerWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, mode: str, data: dict, lecturer_id: int = None):
        super().__init__()
        self.mode = mode
        self.data = data
        self.lecturer_id = lecturer_id

    def run(self):
        try:
            if self.mode == "add":
                self.finished.emit(lecturer_api.create_lecturer(self.data))
            else:
                self.finished.emit(lecturer_api.update_lecturer(self.lecturer_id, self.data))
        except Exception as e:
            self.error.emit(str(e))


class DeleteLecturerWorker(QThread):
    finished = Signal()
    error    = Signal(str)

    def __init__(self, lecturer_id: int):
        super().__init__()
        self.lecturer_id = lecturer_id

    def run(self):
        try:
            lecturer_api.delete_lecturer(self.lecturer_id)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# ── Detail dialog ─────────────────────────────────────────────────

class LecturerDetailDialog(FluentFormDialog):
    """Read-only detail view for a lecturer."""

    edit_requested = Signal(dict)

    def __init__(self, lecturer: dict, is_admin: bool, parent=None):
        self._lecturer = lecturer
        self._is_admin = is_admin
        super().__init__("Chi Tiết Giảng Viên", parent, min_width=660)
        # Replace default Save with Edit button
        self._save_btn.hide()
        self._cancel_btn.setText("Đóng")
        if is_admin:
            edit_btn = PrimaryPushButton(FIF.EDIT, "  Chỉnh sửa", self)
            edit_btn.clicked.connect(
                lambda: (self.edit_requested.emit(self._lecturer), self.reject())
            )
            self._save_btn.parent().layout().insertWidget(1, edit_btn)

    def _build_form(self, layout: QVBoxLayout):
        lect = self._lecturer
        dept = lect.get("department") or {}

        # Header card
        header_card = QFrame()
        header_card.setObjectName("lecturerHeaderCard")
        hc_h = QHBoxLayout(header_card)
        hc_h.setContentsMargins(16, 12, 16, 12)
        hc_h.setSpacing(12)

        initials = "".join([p[0] for p in lect.get("full_name", "?").split()[:2]]).upper() or "?"
        avatar = QLabel(initials)
        avatar.setObjectName("detailAvatar")
        avatar.setFixedSize(56, 56)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hc_h.addWidget(avatar)

        info_v = QVBoxLayout()
        info_v.setSpacing(4)

        name_lbl = SubtitleLabel(lect.get("full_name", "—"))
        name_lbl.setWordWrap(True)
        code_lbl = CaptionLabel("Mã: " + lect.get("employee_code", "—"))

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)
        badge_row.addWidget(Badge.status(lect.get("status", "active")))
        badge_row.addWidget(Badge.degree(lect.get("degree", "—")))
        badge_row.addStretch()

        info_v.addWidget(name_lbl)
        info_v.addWidget(code_lbl)
        info_v.addLayout(badge_row)
        hc_h.addLayout(info_v, stretch=1)
        layout.addWidget(header_card)

        # Grid helper
        def field_row(items: list) -> QWidget:
            w = QWidget()
            w.setStyleSheet("background:transparent;")
            h = QHBoxLayout(w)
            h.setContentsMargins(0, 0, 0, 0)
            h.setSpacing(24)
            for label, value in items:
                col = QVBoxLayout()
                col.setSpacing(2)
                l = QLabel(label)
                l.setObjectName("sectionLabel")
                v = QLabel(str(value) if value else "—")
                v.setObjectName("fieldValue")
                v.setWordWrap(True)
                col.addWidget(l)
                col.addWidget(v)
                col_w = QWidget()
                col_w.setStyleSheet("background:transparent;")
                col_w.setLayout(col)
                h.addWidget(col_w, stretch=1)
            return w

        # Personal info
        section_lbl_1 = QLabel("THÔNG TIN CÁ NHÂN")
        section_lbl_1.setObjectName("sectionLabel")
        layout.addWidget(section_lbl_1)

        GENDER_MAP = {"male": "Nam", "female": "Nữ", "other": "Khác"}
        layout.addWidget(field_row([
            ("Ngày sinh",  lect.get("date_of_birth", "—")),
            ("Giới tính",  GENDER_MAP.get(lect.get("gender", ""), "—")),
        ]))
        layout.addWidget(field_row([
            ("Email",      lect.get("email", "—")),
            ("Điện thoại", lect.get("phone", "—")),
        ]))

        # Work info
        section_lbl_2 = QLabel("THÔNG TIN CÔNG TÁC")
        section_lbl_2.setObjectName("sectionLabel")
        layout.addWidget(section_lbl_2)

        layout.addWidget(field_row([
            ("Khoa",       dept.get("name", "—")),
            ("Học vị",     lect.get("degree", "—")),
        ]))
        layout.addWidget(field_row([
            ("Chức vụ",    lect.get("position", "—") or "—"),
            ("Ngày vào làm", lect.get("hire_date", "—")),
        ]))

    def _on_save(self):
        self.reject()


# ── Form dialog ────────────────────────────────────────────────────

class LecturerFormDialog(FluentFormDialog):
    """Add / Edit lecturer form dialog."""

    saved = Signal(dict)

    DEGREE_OPTIONS   = ["ThS", "TS", "PGS", "GS"]
    STATUS_OPTIONS   = [("active", "Hoạt động"), ("inactive", "Nghỉ việc"), ("on_leave", "Tạm nghỉ")]
    GENDER_OPTIONS   = [("male", "Nam"), ("female", "Nữ"), ("other", "Khác")]
    POSITION_OPTIONS = [
        "Giảng viên", "Trưởng bộ môn", "Phó trưởng bộ môn",
        "Trưởng khoa", "Phó khoa", "Giảng viên chính", "Giảng viên cao cấp"
    ]

    def __init__(self, mode: str = "add", lecturer: dict = None,
                 departments: list = None, parent=None):
        self._mode = mode
        self._lecturer = lecturer or {}
        self._departments = departments or []
        self._save_worker = None
        title = "Thêm Giảng Viên Mới" if mode == "add" else "Cập Nhật Giảng Viên"
        super().__init__(title, parent, min_width=660)

    def _build_form(self, layout: QVBoxLayout):
        lect = self._lecturer

        def row2(*fields) -> QHBoxLayout:
            h = QHBoxLayout()
            h.setSpacing(16)
            for f in fields:
                h.addWidget(f)
            return h

        # ── Basic info ────────────────────────────────────────────
        section_basic = QLabel("THÔNG TIN CƠ BẢN")
        section_basic.setStyleSheet(
            "color:#484F58; font-size:10px; font-weight:700; letter-spacing:1.2px;"
        )
        layout.addWidget(section_basic)

        self._code_input = LineEdit()
        self._code_input.setPlaceholderText("VD: GV001")
        self._code_input.setText(lect.get("employee_code", ""))
        self._code_field = FormField("Mã Giảng Viên *", self._code_input)

        self._name_input = LineEdit()
        self._name_input.setPlaceholderText("Họ và tên đầy đủ")
        self._name_input.setText(lect.get("full_name", ""))
        self._name_field = FormField("Họ & Tên *", self._name_input)

        layout.addLayout(row2(self._code_field, self._name_field))

        self._email_input = LineEdit()
        self._email_input.setPlaceholderText("email@university.edu.vn")
        self._email_input.setText(lect.get("email", ""))
        self._email_field = FormField("Email *", self._email_input)

        self._phone_input = LineEdit()
        self._phone_input.setPlaceholderText("0901234567")
        self._phone_input.setText(lect.get("phone", "") or "")
        phone_field = FormField("Số Điện Thoại", self._phone_input)

        layout.addLayout(row2(self._email_field, phone_field))

        # Gender radios
        gender_w = QWidget()
        gender_w.setStyleSheet("background:transparent;")
        gender_h = QHBoxLayout(gender_w)
        gender_h.setContentsMargins(0, 0, 0, 0)
        gender_h.setSpacing(16)
        self._gender_group = QButtonGroup()
        current_gender = lect.get("gender", "male")
        for val, label in self.GENDER_OPTIONS:
            rb = QRadioButton(label)
            rb.setProperty("gender_val", val)
            if val == current_gender:
                rb.setChecked(True)
            self._gender_group.addButton(rb)
            gender_h.addWidget(rb)
        gender_h.addStretch()
        gender_field = FormField("Giới Tính *", gender_w)

        self._dob_picker = DatePicker()
        dob_str = lect.get("date_of_birth", "")
        if dob_str:
            try:
                parts = dob_str.split("-")
                self._dob_picker.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except Exception:
                pass
        dob_field = FormField("Ngày Sinh", self._dob_picker)

        layout.addLayout(row2(gender_field, dob_field))

        # ── Work info ─────────────────────────────────────────────
        section_work = QLabel("THÔNG TIN CÔNG TÁC")
        section_work.setStyleSheet(
            "color:#484F58; font-size:10px; font-weight:700; letter-spacing:1.2px;"
        )
        layout.addWidget(section_work)

        self._dept_combo = ComboBox()
        dept_id = (lect.get("department") or {}).get("id") or lect.get("department_id")
        for d in self._departments:
            self._dept_combo.addItem(d["name"], userData=d["id"])
        if dept_id:
            idx = self._dept_combo.findData(dept_id)
            if idx >= 0:
                self._dept_combo.setCurrentIndex(idx)
        dept_field = FormField("Khoa / Bộ Môn *", self._dept_combo)

        self._degree_combo = ComboBox()
        for d in self.DEGREE_OPTIONS:
            self._degree_combo.addItem(d, userData=d)
        idx = self._degree_combo.findData(lect.get("degree", "ThS"))
        if idx >= 0:
            self._degree_combo.setCurrentIndex(idx)
        degree_field = FormField("Học Vị *", self._degree_combo)

        layout.addLayout(row2(dept_field, degree_field))

        self._position_combo = ComboBox()
        self._position_combo.addItem("— Không có —", userData="")
        for p in self.POSITION_OPTIONS:
            self._position_combo.addItem(p, userData=p)
        idx = self._position_combo.findData(lect.get("position", "") or "")
        if idx >= 0:
            self._position_combo.setCurrentIndex(idx)
        position_field = FormField("Chức Vụ", self._position_combo)

        self._hire_picker = DatePicker()
        hire_str = lect.get("hire_date", "")
        if hire_str:
            try:
                parts = hire_str.split("-")
                self._hire_picker.setDate(QDate(int(parts[0]), int(parts[1]), int(parts[2])))
            except Exception:
                pass
        else:
            self._hire_picker.setDate(QDate.currentDate())
        hire_field = FormField("Ngày Vào Làm *", self._hire_picker)

        layout.addLayout(row2(position_field, hire_field))

        self._status_combo = ComboBox()
        for val, label in self.STATUS_OPTIONS:
            self._status_combo.addItem(label, userData=val)
        idx = self._status_combo.findData(lect.get("status", "active"))
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        layout.addWidget(FormField("Trạng Thái", self._status_combo))

        # Save required fields list for validation
        self._required = [
            (self._code_input, self._code_field, "Mã giảng viên"),
            (self._name_input, self._name_field, "Họ & tên"),
            (self._email_input, self._email_field, "Email"),
        ]

    def _validate(self) -> bool:
        valid = True
        for widget, field, name in self._required:
            if not widget.text().strip():
                field.set_error(f"Vui lòng nhập {name}")
                valid = False
            else:
                field.clear_error()
        email = self._email_input.text().strip()
        if email and "@" not in email:
            self._email_field.set_error("Email không đúng định dạng")
            valid = False
        return valid

    def _collect(self) -> dict:
        gender = "male"
        for btn in self._gender_group.buttons():
            if btn.isChecked():
                gender = btn.property("gender_val")
                break
        return {
            "employee_code": self._code_input.text().strip(),
            "full_name":     self._name_input.text().strip(),
            "email":         self._email_input.text().strip(),
            "phone":         self._phone_input.text().strip() or None,
            "gender":        gender,
            "date_of_birth": self._dob_picker.getDate().toString("yyyy-MM-dd"),
            "degree":        self._degree_combo.currentData(),
            "position":      self._position_combo.currentData() or None,
            "department_id": self._dept_combo.currentData(),
            "hire_date":     self._hire_picker.getDate().toString("yyyy-MM-dd"),
            "status":        self._status_combo.currentData(),
        }

    def _on_save(self):
        if not self._validate():
            return
        data = self._collect()
        self.set_loading(True)
        self._error_lbl.hide()
        lect_id = self._lecturer.get("id")
        self._save_worker = SaveLecturerWorker(self._mode, data, lect_id)
        self._save_worker.finished.connect(self._on_saved)
        self._save_worker.error.connect(self._on_save_error)
        self._save_worker.start()

    def _on_saved(self, result: dict):
        self.set_loading(False)
        self.saved.emit(result)
        self.accept()

    def _on_save_error(self, msg: str):
        self.set_loading(False)
        self.show_error(msg)


# ── Main screen ────────────────────────────────────────────────────

class LecturerScreen(QWidget):
    """Main lecturer list screen with search, filter, table, pagination."""

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("LecturerScreen")
        self.user_info = user_info
        self.is_admin  = user_info.get("role") == "admin"
        self._departments = []
        self._current_page = 1
        self._row_data: list = []
        self._worker = None
        self._del_worker = None
        self._build_ui()
        self._load_departments()

    # ── UI ────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        header_row.addWidget(
            SectionHeader(
                "Quản Lý Giảng Viên",
                "Xem, tìm kiếm và quản lý hồ sơ giảng viên",
                icon="users",
            )
        )
        header_row.addStretch()

        # Export buttons
        self._excel_btn = PushButton(FIF.DOWNLOAD, "  Excel", self)
        self._excel_btn.clicked.connect(self._export_excel)
        self._pdf_btn   = PushButton(FIF.DOCUMENT,  "  PDF",   self)
        self._pdf_btn.clicked.connect(self._export_pdf)
        header_row.addWidget(self._excel_btn)
        header_row.addSpacing(6)
        header_row.addWidget(self._pdf_btn)

        if self.is_admin:
            add_btn = PrimaryPushButton(FIF.ADD, "  Thêm Giảng Viên", self)
            add_btn.clicked.connect(self._on_add)
            header_row.addSpacing(8)
            header_row.addWidget(add_btn)

        layout.addLayout(header_row)

        # ── Filter toolbar ────────────────────────────────────────
        toolbar = ElevatedCardWidget()
        tb_layout = QVBoxLayout(toolbar)
        tb_layout.setContentsMargins(16, 12, 16, 12)
        tb_layout.setSpacing(10)

        # Row 1: search
        search_row = QHBoxLayout()
        self._search_input = SearchLineEdit(self)
        self._search_input.setPlaceholderText("Tìm theo tên, mã GV, email...  (Ctrl+F)")
        self._search_input.setFixedHeight(36)
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._on_filter_changed)
        self._search_input.textChanged.connect(lambda: self._search_timer.start(300))

        reset_btn = PushButton(FIF.SYNC, "  Làm mới", self)
        reset_btn.clicked.connect(self._reset_filters)

        search_row.addWidget(self._search_input)
        search_row.addWidget(reset_btn)
        tb_layout.addLayout(search_row)

        # Row 2: filter combos
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        filter_row.addWidget(BodyLabel("Khoa:"))
        self._dept_filter = ComboBox(self)
        self._dept_filter.setFixedWidth(170)
        self._dept_filter.addItem("Tất cả khoa", userData=None)
        self._dept_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._dept_filter)

        filter_row.addWidget(BodyLabel("Học vị:"))
        self._degree_filter = ComboBox(self)
        self._degree_filter.setFixedWidth(110)
        self._degree_filter.addItem("Tất cả", userData="")
        for d in ["ThS", "TS", "PGS", "GS"]:
            self._degree_filter.addItem(d, userData=d)
        self._degree_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._degree_filter)

        filter_row.addWidget(BodyLabel("Trạng thái:"))
        self._status_filter = ComboBox(self)
        self._status_filter.setFixedWidth(130)
        self._status_filter.addItem("Tất cả", userData="")
        self._status_filter.addItem("Hoạt động",  userData="active")
        self._status_filter.addItem("Nghỉ việc",  userData="inactive")
        self._status_filter.addItem("Tạm nghỉ",   userData="on_leave")
        self._status_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self._status_filter)
        filter_row.addStretch()
        tb_layout.addLayout(filter_row)
        layout.addWidget(toolbar)

        # ── Table ─────────────────────────────────────────────────
        table_card = ElevatedCardWidget()
        table_v = QVBoxLayout(table_card)
        table_v.setContentsMargins(0, 0, 0, 0)
        table_v.setSpacing(0)

        COLS = ["#", "Mã GV", "Họ & Tên", "Email", "SĐT",
                "Khoa", "Học vị", "Chức vụ", "Trạng thái", "Thao tác"]
        self._table = TableWidget(self)
        self._table.setColumnCount(len(COLS))
        self._table.setHorizontalHeaderLabels(COLS)
        self._table.verticalHeader().setVisible(False)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.setSortingEnabled(True)
        self._table.setBorderVisible(True)
        self._table.setBorderRadius(8)

        hh = self._table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed)

        self._table.setColumnWidth(0, 44)
        self._table.setColumnWidth(1, 80)
        self._table.setColumnWidth(4, 110)
        self._table.setColumnWidth(6, 60)
        self._table.setColumnWidth(8, 108)
        self._table.setColumnWidth(9, 120 if self.is_admin else 56)
        self._table.verticalHeader().setDefaultSectionSize(44)
        self._table.doubleClicked.connect(
            lambda idx: self._on_view(self._row_data[idx.row()])
            if 0 <= idx.row() < len(self._row_data) else None
        )
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._on_context_menu)

        self._empty = EmptyStateWidget("Không tìm thấy giảng viên nào", on_retry=self.refresh)
        self._empty.hide()

        table_v.addWidget(self._table, stretch=1)
        table_v.addWidget(self._empty)
        layout.addWidget(table_card, stretch=1)

        # Pagination
        self._pagination = PaginationBar(self)
        self._pagination.page_changed.connect(self._on_page_changed)
        layout.addWidget(self._pagination)

        # Loading
        self._loading = LoadingOverlay(self)

        # Shortcuts
        QShortcut(QKeySequence("F5"),     self).activated.connect(self.refresh)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._search_input.setFocus)
        if self.is_admin:
            QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self._on_add)
            QShortcut(QKeySequence("Delete"), self).activated.connect(self._delete_selected)

    # ── Data ──────────────────────────────────────────────────────

    def _load_departments(self):
        try:
            depts = department_api.get_departments()
            self._departments = depts if isinstance(depts, list) else []
            self._dept_filter.clear()
            self._dept_filter.addItem("Tất cả khoa", userData=None)
            for d in self._departments:
                self._dept_filter.addItem(d["name"], userData=d["id"])
        except Exception:
            pass

    def refresh(self):
        self._load_data(page=1)

    def _build_filters(self) -> dict:
        return {
            "search":        self._search_input.text().strip(),
            "department_id": self._dept_filter.currentData(),
            "degree":        self._degree_filter.currentData() or "",
            "status":        self._status_filter.currentData() or "",
            "page":          self._current_page,
            "size":          20,
        }

    def _load_data(self, page: int = 1):
        self._current_page = page
        filters = self._build_filters()
        filters["page"] = page

        self._table.setEnabled(False)
        self._loading.show()
        self._empty.hide()

        self._worker = LoadLecturersWorker(filters)
        self._worker.finished.connect(self._on_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_loaded(self, result: dict):
        self._loading.hide()
        self._table.setEnabled(True)
        items = result.get("items", [])
        total = result.get("total", 0)
        pages = result.get("pages", 1)
        self._row_data = items
        self._populate_table(items)
        self._pagination.update(self._current_page, pages, total)
        if items:
            self._table.show()
            self._empty.hide()
        else:
            self._table.hide()
            self._empty.show()

    def _populate_table(self, items: list):
        self._table.setRowCount(0)
        offset = (self._current_page - 1) * 20
        for i, lect in enumerate(items):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)
            dept = lect.get("department") or {}
            cells = [
                (str(offset + i + 1),             Qt.AlignmentFlag.AlignCenter),
                (lect.get("employee_code", ""),    Qt.AlignmentFlag.AlignCenter),
                (lect.get("full_name", ""),         Qt.AlignmentFlag.AlignLeft),
                (lect.get("email", ""),              Qt.AlignmentFlag.AlignLeft),
                (lect.get("phone", "") or "—",     Qt.AlignmentFlag.AlignCenter),
                (dept.get("name", "—"),              Qt.AlignmentFlag.AlignLeft),
            ]
            for col, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(int(align | Qt.AlignmentFlag.AlignVCenter))
                self._table.setItem(row, col, item)

            # Degree badge
            self._table.setCellWidget(row, 6, self._center(Badge.degree(lect.get("degree", ""))))
            # Position
            pos_item = QTableWidgetItem(lect.get("position", "") or "—")
            pos_item.setTextAlignment(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
            self._table.setItem(row, 7, pos_item)
            # Status badge
            self._table.setCellWidget(row, 8, self._center(Badge.status(lect.get("status", "active"))))
            # Actions
            self._table.setCellWidget(row, 9, self._make_actions(lect))

    def _center(self, widget: QWidget) -> QWidget:
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 0, 4, 0)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(widget)
        return c

    def _make_actions(self, lect: dict) -> QWidget:
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(4)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        view_btn = ToolButton(FIF.VIEW, c)
        view_btn.setToolTip("Xem chi tiết")
        view_btn.clicked.connect(lambda _, l=lect: self._on_view(l))
        h.addWidget(view_btn)

        if self.is_admin:
            edit_btn = ToolButton(FIF.EDIT, c)
            edit_btn.setToolTip("Chỉnh sửa")
            edit_btn.clicked.connect(lambda _, l=lect: self._on_edit(l))
            h.addWidget(edit_btn)

            del_btn = ToolButton(FIF.DELETE, c)
            del_btn.setToolTip("Xóa")
            del_btn.setStyleSheet("ToolButton{color:#F85149;}")
            del_btn.clicked.connect(lambda _, l=lect: self._on_delete(l))
            h.addWidget(del_btn)

        return c

    # ── Slots ─────────────────────────────────────────────────────

    def _on_filter_changed(self):
        self._load_data(page=1)

    def _reset_filters(self):
        self._search_input.clear()
        self._dept_filter.setCurrentIndex(0)
        self._degree_filter.setCurrentIndex(0)
        self._status_filter.setCurrentIndex(0)

    def _on_page_changed(self, page: int):
        self._load_data(page=page)

    def _on_context_menu(self, pos):
        from PySide6.QtWidgets import QMenu
        row = self._table.rowAt(pos.y())
        if row < 0 or row >= len(self._row_data):
            return
        lect = self._row_data[row]
        menu = QMenu(self)
        menu.addAction("Xem chi tiết").triggered.connect(lambda: self._on_view(lect))
        if self.is_admin:
            menu.addSeparator()
            menu.addAction("Chỉnh sửa").triggered.connect(lambda: self._on_edit(lect))
            act_del = menu.addAction("Xóa")
            act_del.triggered.connect(lambda: self._on_delete(lect))
        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _delete_selected(self):
        row = self._table.currentRow()
        if 0 <= row < len(self._row_data):
            self._on_delete(self._row_data[row])

    def _on_view(self, lect: dict):
        dlg = LecturerDetailDialog(lect, self.is_admin, parent=self)
        dlg.edit_requested.connect(self._on_edit)
        dlg.exec()

    def _on_add(self):
        dlg = LecturerFormDialog("add", departments=self._departments, parent=self)
        dlg.saved.connect(self._on_saved)
        dlg.exec()

    def _on_edit(self, lect: dict):
        dlg = LecturerFormDialog("edit", lecturer=lect,
                                 departments=self._departments, parent=self)
        dlg.saved.connect(self._on_saved)
        dlg.exec()

    def _on_saved(self):
        toast_success(self.window(), "Lưu giảng viên thành công!")
        self.refresh()

    def _on_delete(self, lect: dict):
        name = lect.get("full_name", "")
        if not confirm(
            "Xác nhận xóa",
            f'Bạn có chắc muốn xóa giảng viên "{name}"?\nThao tác này không thể hoàn tác.',
            parent=self,
            yes_text="Xóa",
            cancel_text="Hủy"
        ):
            return
        self._del_worker = DeleteLecturerWorker(lect["id"])
        self._del_worker.finished.connect(self._on_deleted)
        self._del_worker.error.connect(lambda msg: toast_error(self.window(), msg))
        self._del_worker.start()

    def _on_deleted(self):
        toast_success(self.window(), "Đã xóa giảng viên thành công!")
        self.refresh()

    def _on_error(self, msg: str):
        self._loading.hide()
        self._table.setEnabled(True)
        if not self._row_data:
            self._empty.show()
        toast_error(self.window(), msg)

    def _export_excel(self):
        try:
            f = self._build_filters()
            data = lecturer_api.export_excel(
                search=f.get("search", ""), department_id=f.get("department_id"),
                degree=f.get("degree", ""), status=f.get("status", "")
            )
            path, _ = QFileDialog.getSaveFileName(
                self, "Lưu file Excel", "danh_sach_giang_vien.xlsx", "Excel (*.xlsx)"
            )
            if path:
                with open(path, "wb") as fh:
                    fh.write(data)
                toast_success(self.window(), "Xuất Excel thành công!")
        except Exception as e:
            toast_error(self.window(), str(e))

    def _export_pdf(self):
        try:
            f = self._build_filters()
            data = lecturer_api.export_pdf(
                search=f.get("search", ""), department_id=f.get("department_id"),
                degree=f.get("degree", ""), status=f.get("status", "")
            )
            path, _ = QFileDialog.getSaveFileName(
                self, "Lưu file PDF", "danh_sach_giang_vien.pdf", "PDF (*.pdf)"
            )
            if path:
                with open(path, "wb") as fh:
                    fh.write(data)
                toast_success(self.window(), "Xuất PDF thành công!")
        except Exception as e:
            toast_error(self.window(), str(e))

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
