# screens/schedule_screen.py — Fluent teaching schedule management screen

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView, QStackedWidget,
)
from PySide6.QtCore import Qt, QThread, Signal, QTime

from qfluentwidgets import (
    PrimaryPushButton, PushButton, ToolButton,
    ComboBox,
    TableWidget, ElevatedCardWidget, BodyLabel,
    TimePicker, FluentIcon as FIF, SegmentedWidget,
)

from components.cards import SectionHeader
from components.dialogs import confirm, FluentFormDialog
from components.form_field import FormField
from components.pagination import PaginationBar
from components.loading import LoadingOverlay
from components.empty import EmptyStateWidget
from components.toast import toast_success, toast_error
from widgets.schedule_calendar import WeeklyScheduleCalendar
import api.schedule_api as schedule_api
import api.lecturer_api as lecturer_api


# ── Workers ───────────────────────────────────────────────────────

class LoadSchedulesWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, filters: dict):
        super().__init__()
        self.filters = filters

    def run(self):
        try:
            self.finished.emit(schedule_api.get_schedules(**self.filters))
        except Exception as e:
            self.error.emit(str(e))


class SaveScheduleWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, mode: str, data: dict, schedule_id: int = None):
        super().__init__()
        self.mode = mode
        self.data = data
        self.schedule_id = schedule_id

    def run(self):
        try:
            if self.mode == "add":
                self.finished.emit(schedule_api.create_schedule(self.data))
            else:
                self.finished.emit(schedule_api.update_schedule(self.schedule_id, self.data))
        except Exception as e:
            self.error.emit(str(e))


class DeleteScheduleWorker(QThread):
    finished = Signal()
    error    = Signal(str)

    def __init__(self, schedule_id: int):
        super().__init__()
        self.schedule_id = schedule_id

    def run(self):
        try:
            schedule_api.delete_schedule(self.schedule_id)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# ── Form dialog ────────────────────────────────────────────────────

class ScheduleFormDialog(FluentFormDialog):
    saved = Signal(dict)

    DAYS = [
        ("Mon", "Thứ 2"),
        ("Tue", "Thứ 3"),
        ("Wed", "Thứ 4"),
        ("Thu", "Thứ 5"),
        ("Fri", "Thứ 6"),
        ("Sat", "Thứ 7"),
        ("Sun", "Chủ nhật"),
    ]
    SEMESTERS = ["HK1", "HK2", "HK3"]
    YEARS = [str(y) for y in range(2023, 2030)]

    def __init__(self, mode: str = "add", schedule: dict = None,
                 lecturers: list = None, parent=None):
        self._mode = mode
        self._schedule = schedule or {}
        self._lecturers = lecturers or []
        self._save_worker = None
        title = "Thêm Lịch Giảng Dạy" if mode == "add" else "Cập Nhật Lịch Giảng Dạy"
        super().__init__(title, parent, min_width=600)

    def _build_form(self, layout):
        sched = self._schedule

        def row2(a, b):
            h = QHBoxLayout()
            h.setSpacing(16)
            h.addWidget(a)
            h.addWidget(b)
            return h

        # Lecturer
        self._lect_combo = ComboBox()
        lect_id = sched.get("lecturer_id") or (sched.get("lecturer") or {}).get("id")
        for l in self._lecturers:
            self._lect_combo.addItem(l["full_name"], userData=l["id"])
        if lect_id:
            idx = self._lect_combo.findData(lect_id)
            if idx >= 0:
                self._lect_combo.setCurrentIndex(idx)
        self._lect_field = FormField("Giảng Viên *", self._lect_combo)
        layout.addWidget(self._lect_field)

        self._subject_input = LineEdit()
        self._subject_input.setPlaceholderText("VD: Lập trình Python")
        self._subject_input.setText(sched.get("subject_name", ""))
        self._subject_field = FormField("Tên Môn Học *", self._subject_input)

        self._code_input = LineEdit()
        self._code_input.setPlaceholderText("VD: CS101")
        self._code_input.setText(sched.get("subject_code", ""))
        self._code_field = FormField("Mã Môn *", self._code_input)

        layout.addLayout(row2(self._subject_field, self._code_field))

        self._room_input = LineEdit()
        self._room_input.setPlaceholderText("VD: A101")
        self._room_input.setText(sched.get("room", ""))
        self._room_field = FormField("Phòng Học *", self._room_input)

        self._day_combo = ComboBox()
        for code, label in self.DAYS:
            self._day_combo.addItem(label, userData=code)
        dow = self._normalize_day_code(sched.get("day_of_week", "Mon"))
        idx = self._day_combo.findData(dow)
        if idx >= 0:
            self._day_combo.setCurrentIndex(idx)
        day_field = FormField("Thứ *", self._day_combo)

        layout.addLayout(row2(self._room_field, day_field))

        # Time pickers
        self._start_picker = TimePicker()
        start_str = sched.get("start_time", "08:00")
        if start_str:
            parts = start_str.split(":")
            self._start_picker.setTime(QTime(int(parts[0]), int(parts[1])))
        start_field = FormField("Giờ Bắt Đầu *", self._start_picker)

        self._end_picker = TimePicker()
        end_str = sched.get("end_time", "10:00")
        if end_str:
            parts = end_str.split(":")
            self._end_picker.setTime(QTime(int(parts[0]), int(parts[1])))
        end_field = FormField("Giờ Kết Thúc *", self._end_picker)

        layout.addLayout(row2(start_field, end_field))

        self._semester_combo = ComboBox()
        for s in self.SEMESTERS:
            self._semester_combo.addItem(s, userData=s)
        idx = self._semester_combo.findData(sched.get("semester", "HK1"))
        if idx >= 0:
            self._semester_combo.setCurrentIndex(idx)
        semester_field = FormField("Học Kỳ *", self._semester_combo)

        self._year_combo = ComboBox()
        for y in self.YEARS:
            self._year_combo.addItem(y, userData=y)
        cur_year = sched.get("academic_year", "2026")
        idx = self._year_combo.findData(cur_year)
        if idx >= 0:
            self._year_combo.setCurrentIndex(idx)
        year_field = FormField("Năm Học *", self._year_combo)

        layout.addLayout(row2(semester_field, year_field))

        self._required = [
            (self._subject_input, self._subject_field, "tên môn học"),
            (self._code_input, self._code_field, "mã môn"),
            (self._room_input, self._room_field, "phòng học"),
        ]

    @staticmethod
    def _normalize_day_code(day_value) -> str:
        day_map = {
            2: "Mon", 3: "Tue", 4: "Wed", 5: "Thu",
            6: "Fri", 7: "Sat", 8: "Sun",
            "2": "Mon", "3": "Tue", "4": "Wed", "5": "Thu",
            "6": "Fri", "7": "Sat", "8": "Sun",
        }
        if day_value in day_map:
            return day_map[day_value]
        return str(day_value or "Mon")

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
            "lecturer_id":   self._lect_combo.currentData(),
            "subject_name":  self._subject_input.text().strip(),
            "subject_code":  self._code_input.text().strip(),
            "room":          self._room_input.text().strip(),
            "day_of_week":   self._day_combo.currentData(),
            "start_time":    self._start_picker.getTime().toString("HH:mm"),
            "end_time":      self._end_picker.getTime().toString("HH:mm"),
            "semester":      self._semester_combo.currentData(),
            "academic_year": self._year_combo.currentData(),
        }

    def _on_save(self):
        if not self._validate():
            return
        self.set_loading(True)
        self._save_worker = SaveScheduleWorker(
            self._mode, self._collect(), self._schedule.get("id")
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

class ScheduleScreen(QWidget):
    DAY_OPTIONS = [
        ("", "Tất cả"),
        ("Mon", "Thứ 2"),
        ("Tue", "Thứ 3"),
        ("Wed", "Thứ 4"),
        ("Thu", "Thứ 5"),
        ("Fri", "Thứ 6"),
        ("Sat", "Thứ 7"),
        ("Sun", "Chủ nhật"),
    ]

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ScheduleScreen")
        self.user_info    = user_info
        self.is_admin     = user_info.get("role") == "admin"
        self._lecturers   = []
        self._row_data    = []
        self._current_page = 1
        self._view_mode   = "table"
        self._worker      = None
        self._build_ui()
        self._load_lecturers()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.addWidget(
            SectionHeader(
                "Lịch Giảng Dạy",
                "Quản lý phân công lịch dạy theo học kỳ",
                icon="calendar-blank",
            )
        )
        header_row.addStretch()
        if self.is_admin:
            add_btn = PrimaryPushButton(FIF.ADD, "  Thêm Lịch", self)
            add_btn.clicked.connect(self._on_add)
            header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Filter
        toolbar = ElevatedCardWidget()
        tb_h = QHBoxLayout(toolbar)
        tb_h.setContentsMargins(16, 10, 16, 10)
        tb_h.setSpacing(12)

        tb_h.addWidget(BodyLabel("Giảng viên:"))
        self._lecturer_filter = ComboBox(self)
        self._lecturer_filter.setFixedWidth(220)
        self._lecturer_filter.addItem("Tất cả", userData=None)
        self._lecturer_filter.currentIndexChanged.connect(self._on_filter_changed)
        tb_h.addWidget(self._lecturer_filter)

        tb_h.addWidget(BodyLabel("Học kỳ:"))
        self._semester_filter = ComboBox(self)
        self._semester_filter.setFixedWidth(90)
        self._semester_filter.addItem("Tất cả", userData="")
        for s in ["HK1", "HK2", "HK3"]:
            self._semester_filter.addItem(s, userData=s)
        self._semester_filter.currentIndexChanged.connect(self._on_filter_changed)
        tb_h.addWidget(self._semester_filter)

        tb_h.addWidget(BodyLabel("Năm học:"))
        self._year_filter = ComboBox(self)
        self._year_filter.setFixedWidth(90)
        self._year_filter.addItem("Tất cả", userData="")
        for y in [str(x) for x in range(2023, 2030)]:
            self._year_filter.addItem(y, userData=y)
        self._year_filter.currentIndexChanged.connect(self._on_filter_changed)
        tb_h.addWidget(self._year_filter)

        tb_h.addWidget(BodyLabel("Thứ:"))
        self._day_filter = ComboBox(self)
        self._day_filter.setFixedWidth(110)
        for code, label in self.DAY_OPTIONS:
            self._day_filter.addItem(label, userData=code)
        self._day_filter.currentIndexChanged.connect(self._on_filter_changed)
        tb_h.addWidget(self._day_filter)

        reset_btn = PushButton(FIF.SYNC, "  Làm mới", self)
        reset_btn.clicked.connect(self._reset)
        tb_h.addWidget(reset_btn)

        tb_h.addSpacing(10)
        tb_h.addWidget(BodyLabel("Chế độ:"))
        self._view_switch = SegmentedWidget(self)
        self._view_switch.addItem("table", "Bảng", onClick=lambda: self._set_view_mode("table"))
        self._view_switch.addItem("calendar", "Lịch tuần", onClick=lambda: self._set_view_mode("calendar"))
        self._view_switch.setCurrentItem("table")
        tb_h.addWidget(self._view_switch)

        layout.addWidget(toolbar)

        # Table
        table_card = ElevatedCardWidget()
        table_v = QVBoxLayout(table_card)
        table_v.setContentsMargins(0, 0, 0, 0)

        COLS = ["#", "Giảng Viên", "Mã Môn", "Tên Môn", "Phòng",
                "Thứ", "Giờ BD", "Giờ KT", "Học Kỳ", "Năm", "Thao tác"]
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
        for i in range(len(COLS)):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(0, 44)
        self._table.verticalHeader().setDefaultSectionSize(44)

        self._empty = EmptyStateWidget("Không tìm thấy lịch giảng dạy nào", on_retry=self.refresh)
        self._empty.hide()
        table_v.addWidget(self._table, stretch=1)
        table_v.addWidget(self._empty)

        calendar_card = ElevatedCardWidget()
        calendar_v = QVBoxLayout(calendar_card)
        calendar_v.setContentsMargins(0, 0, 0, 0)
        self._calendar_view = WeeklyScheduleCalendar(calendar_card)
        calendar_v.addWidget(self._calendar_view)

        self._content_stack = QStackedWidget(self)
        self._content_stack.addWidget(table_card)
        self._content_stack.addWidget(calendar_card)
        self._content_stack.setCurrentIndex(0)
        layout.addWidget(self._content_stack, stretch=1)

        self._pagination = PaginationBar(self)
        self._pagination.page_changed.connect(self._on_page_changed)
        layout.addWidget(self._pagination)
        self._loading = LoadingOverlay(self)

    def _load_lecturers(self):
        try:
            r = lecturer_api.get_lecturers(size=500)
            self._lecturers = r.get("items", []) if isinstance(r, dict) else []
            current = self._lecturer_filter.currentData() if hasattr(self, "_lecturer_filter") else None
            if hasattr(self, "_lecturer_filter"):
                self._lecturer_filter.blockSignals(True)
                self._lecturer_filter.clear()
                self._lecturer_filter.addItem("Tất cả", userData=None)
                for lect in self._lecturers:
                    label = f"{lect.get('employee_code', '')} - {lect.get('full_name', '')}".strip(" -")
                    self._lecturer_filter.addItem(label, userData=lect.get("id"))
                idx = self._lecturer_filter.findData(current)
                self._lecturer_filter.setCurrentIndex(idx if idx >= 0 else 0)
                self._lecturer_filter.blockSignals(False)
        except Exception:
            pass

    def refresh(self):
        self._load_data(page=1)

    def _build_filters(self) -> dict:
        if self._view_mode == "calendar":
            return {
                "lecturer_id":   self._lecturer_filter.currentData(),
                "semester":      self._semester_filter.currentData() or "",
                "academic_year": self._year_filter.currentData() or "",
                "day_of_week":   self._day_filter.currentData() or "",
                "page":          1,
                "size":          200,
            }

        return {
            "lecturer_id":   self._lecturer_filter.currentData(),
            "semester":      self._semester_filter.currentData() or "",
            "academic_year": self._year_filter.currentData() or "",
            "day_of_week":   self._day_filter.currentData() or "",
            "page":          self._current_page,
            "size":          20,
        }

    def _load_data(self, page: int = 1):
        if self._view_mode == "calendar":
            page = 1
        self._current_page = page
        f = self._build_filters()
        f["page"] = page
        self._table.setEnabled(False)
        self._loading.show()
        self._worker = LoadSchedulesWorker(f)
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

        DAY_NAMES = {
            "Mon": "Thứ 2", "Tue": "Thứ 3", "Wed": "Thứ 4",
            "Thu": "Thứ 5", "Fri": "Thứ 6", "Sat": "Thứ 7", "Sun": "CN",
            2: "Thứ 2", 3: "Thứ 3", 4: "Thứ 4", 5: "Thứ 5",
            6: "Thứ 6", 7: "Thứ 7", 8: "CN",
            "2": "Thứ 2", "3": "Thứ 3", "4": "Thứ 4", "5": "Thứ 5",
            "6": "Thứ 6", "7": "Thứ 7", "8": "CN",
        }

        self._table.setRowCount(0)
        offset = (self._current_page - 1) * 20
        for i, s in enumerate(items):
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)
            lect = s.get("lecturer") or {}
            cells = [
                (str(offset + i + 1),                     Qt.AlignmentFlag.AlignCenter),
                (lect.get("full_name", "—"),               Qt.AlignmentFlag.AlignLeft),
                (s.get("subject_code", ""),                Qt.AlignmentFlag.AlignCenter),
                (s.get("subject_name", ""),                Qt.AlignmentFlag.AlignLeft),
                (s.get("room", ""),                        Qt.AlignmentFlag.AlignCenter),
                (DAY_NAMES.get(s.get("day_of_week", 0), "—"), Qt.AlignmentFlag.AlignCenter),
                (str(s.get("start_time", ""))[:5],             Qt.AlignmentFlag.AlignCenter),
                (str(s.get("end_time", ""))[:5],               Qt.AlignmentFlag.AlignCenter),
                (s.get("semester", ""),                    Qt.AlignmentFlag.AlignCenter),
                (str(s.get("academic_year", "")),          Qt.AlignmentFlag.AlignCenter),
            ]
            for col, (text, align) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(int(align | Qt.AlignmentFlag.AlignVCenter))
                self._table.setItem(row, col, item)
            self._table.setCellWidget(row, 10, self._make_actions(s))

        self._calendar_view.set_items(items)

        if self._view_mode == "table":
            self._content_stack.setCurrentIndex(0)
            self._pagination.show()
            self._pagination.update(self._current_page, pages, total)
            if items:
                self._table.show()
                self._empty.hide()
            else:
                self._table.hide()
                self._empty.show()
        else:
            self._content_stack.setCurrentIndex(1)
            self._pagination.hide()

    def _make_actions(self, sched: dict) -> QWidget:
        from PySide6.QtWidgets import QWidget
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 2, 4, 2)
        h.setSpacing(4)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.is_admin:
            edit_btn = ToolButton(FIF.EDIT, c)
            edit_btn.clicked.connect(lambda _, s=sched: self._on_edit(s))
            h.addWidget(edit_btn)
            del_btn = ToolButton(FIF.DELETE, c)
            del_btn.clicked.connect(lambda _, s=sched: self._on_delete(s))
            h.addWidget(del_btn)
        return c

    def _on_filter_changed(self):
        self._load_data(page=1)

    def _set_view_mode(self, mode: str):
        if mode == self._view_mode:
            return
        self._view_mode = mode
        self._load_data(page=1)

    def _reset(self):
        self._lecturer_filter.setCurrentIndex(0)
        self._semester_filter.setCurrentIndex(0)
        self._year_filter.setCurrentIndex(0)
        self._day_filter.setCurrentIndex(0)

    def _on_page_changed(self, page: int):
        if self._view_mode != "table":
            return
        self._load_data(page=page)

    def _on_add(self):
        dlg = ScheduleFormDialog("add", lecturers=self._lecturers, parent=self)
        dlg.saved.connect(lambda _: (toast_success(self.window(), "Thêm lịch thành công!"), self.refresh()))
        dlg.exec()

    def _on_edit(self, sched: dict):
        dlg = ScheduleFormDialog("edit", schedule=sched, lecturers=self._lecturers, parent=self)
        dlg.saved.connect(lambda _: (toast_success(self.window(), "Cập nhật lịch thành công!"), self.refresh()))
        dlg.exec()

    def _on_delete(self, sched: dict):
        name = (sched.get("lecturer") or {}).get("full_name", "")
        if not confirm("Xác nhận xóa", f'Xóa lịch dạy của "{name}"?', self, "Xóa"):
            return
        w = DeleteScheduleWorker(sched["id"])
        w.finished.connect(lambda: (toast_success(self.window(), "Đã xóa lịch!"), self.refresh()))
        w.error.connect(lambda msg: toast_error(self.window(), msg))
        w.start()
        self._del_worker = w

    def _on_error(self, msg: str):
        self._loading.hide()
        toast_error(self.window(), msg)

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
