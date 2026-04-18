# screens/audit_log_screen.py — Fluent audit log viewer (Admin only, read-only)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem, QHeaderView,
)
from PySide6.QtCore import Qt, QThread, Signal, QDate

from qfluentwidgets import (
    PushButton, ComboBox, TableWidget, ElevatedCardWidget,
    BodyLabel, CalendarPicker, FluentIcon as FIF,
    SearchLineEdit,
)

from components.badges import Badge
from components.cards import SectionHeader
from components.pagination import PaginationBar
from components.loading import LoadingOverlay
from components.empty import EmptyStateWidget
from components.toast import toast_error
import api.audit_api as audit_api


# ── Worker ────────────────────────────────────────────────────────

class LoadAuditWorker(QThread):
    finished = Signal(dict)
    error    = Signal(str)

    def __init__(self, filters: dict):
        super().__init__()
        self.filters = filters

    def run(self):
        try:
            self.finished.emit(audit_api.get_audit_logs(**self.filters))
        except Exception as e:
            self.error.emit(str(e))


# ── Screen ────────────────────────────────────────────────────────

class AuditLogScreen(QWidget):
    """Read-only audit log viewer. Supports filter by action, entity, date range."""

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("AuditLogScreen")
        self.user_info     = user_info
        self._row_data     = []
        self._current_page = 1
        self._worker       = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        layout.addWidget(
            SectionHeader(
                "Nhật Ký Hệ Thống",
                "Lịch sử đăng nhập và các thao tác dữ liệu (Admin only)",
                icon="clipboard-text",
            )
        )

        # ── Filter toolbar ────────────────────────────────────────
        toolbar = ElevatedCardWidget()
        tb_v = QVBoxLayout(toolbar)
        tb_v.setContentsMargins(16, 14, 16, 14)
        tb_v.setSpacing(10)

        # Row 1: action + entity filters
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        row1.addWidget(BodyLabel("Hành động:"))
        self._action_filter = ComboBox(self)
        self._action_filter.setFixedWidth(120)
        self._action_filter.addItem("Tất cả",  userData="")
        for a, label in [("login", "Đăng nhập"), ("create", "Tạo mới"),
                         ("update", "Cập nhật"), ("delete", "Xóa")]:
            self._action_filter.addItem(label, userData=a)
        row1.addWidget(self._action_filter)

        row1.addSpacing(4)
        row1.addWidget(BodyLabel("Đối tượng:"))
        self._entity_filter = ComboBox(self)
        self._entity_filter.setFixedWidth(140)
        self._entity_filter.addItem("Tất cả", userData="")
        for e, label in [("lecturer", "Giảng viên"), ("department", "Khoa"),
                         ("schedule", "Lịch dạy"),  ("account", "Tài khoản")]:
            self._entity_filter.addItem(label, userData=e)
        row1.addWidget(self._entity_filter)

        row1.addStretch()

        search_btn = PushButton(FIF.SEARCH, "  Lọc", self)
        search_btn.clicked.connect(self.refresh)
        reset_btn  = PushButton(FIF.SYNC, "  Xóa lọc", self)
        reset_btn.clicked.connect(self._reset)
        row1.addWidget(search_btn)
        row1.addWidget(reset_btn)
        tb_v.addLayout(row1)

        # Row 2: date range
        row2 = QHBoxLayout()
        row2.setSpacing(12)
        row2.addWidget(BodyLabel("Từ ngày:"))
        self._from_picker = CalendarPicker(self)
        self._from_picker.setFixedWidth(160)
        row2.addWidget(self._from_picker)
        row2.addWidget(BodyLabel("Đến ngày:"))
        self._to_picker = CalendarPicker(self)
        self._to_picker.setFixedWidth(160)
        row2.addWidget(self._to_picker)
        row2.addStretch()
        tb_v.addLayout(row2)
        layout.addWidget(toolbar)

        # ── Table ─────────────────────────────────────────────────
        table_card = ElevatedCardWidget()
        table_v = QVBoxLayout(table_card)
        table_v.setContentsMargins(0, 0, 0, 0)

        COLS = ["Thời Gian", "Người Dùng", "Hành Động", "Đối Tượng", "ID", "Mô Tả", "IP"]
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
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        hh.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setColumnWidth(0, 155)
        self._table.setColumnWidth(1, 120)
        self._table.setColumnWidth(2, 110)
        self._table.setColumnWidth(3, 110)
        self._table.setColumnWidth(4, 56)
        self._table.verticalHeader().setDefaultSectionSize(44)

        self._empty = EmptyStateWidget("Không có nhật ký nào", on_retry=self.refresh)
        self._empty.hide()
        table_v.addWidget(self._table, stretch=1)
        table_v.addWidget(self._empty)
        layout.addWidget(table_card, stretch=1)

        self._pagination = PaginationBar(self)
        self._pagination.page_changed.connect(self._on_page_changed)
        layout.addWidget(self._pagination)

        self._loading = LoadingOverlay(self)

    # ── Data ──────────────────────────────────────────────────────

    def refresh(self):
        self._load_data(page=1)

    def _build_filters(self) -> dict:
        f: dict = {
            "action":      self._action_filter.currentData() or "",
            "entity_type": self._entity_filter.currentData() or "",
            "page":        self._current_page,
            "size":        30,
        }
        from_date = self._from_picker.getDate()
        to_date   = self._to_picker.getDate()
        if from_date.isValid():
            f["date_from"] = from_date.toString("yyyy-MM-dd")
        if to_date.isValid():
            f["date_to"] = to_date.toString("yyyy-MM-dd")
        return f

    def _load_data(self, page: int = 1):
        self._current_page = page
        filters = self._build_filters()
        filters["page"] = page
        self._loading.show()
        self._worker = LoadAuditWorker(filters)
        self._worker.finished.connect(self._on_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_loaded(self, result: dict):
        self._loading.hide()
        items = result.get("items", [])
        total = result.get("total", 0)
        pages = result.get("pages", 1)
        self._row_data = items

        self._table.setRowCount(0)
        for log in items:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setRowHeight(row, 44)

            ts = str(log.get("created_at", ""))[:16].replace("T", " ")
            for col, (text, align) in enumerate([
                (ts,                    Qt.AlignmentFlag.AlignLeft),
                (log.get("username", "—"), Qt.AlignmentFlag.AlignLeft),
            ]):
                item = QTableWidgetItem(text)
                item.setTextAlignment(int(align | Qt.AlignmentFlag.AlignVCenter))
                self._table.setItem(row, col, item)

            # Action badge (col 2)
            self._table.setCellWidget(row, 2, self._centered(Badge.action(log.get("action", ""))))

            # Entity (col 3)
            ent = QTableWidgetItem(str(log.get("entity_type", "")).capitalize())
            ent.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, ent)

            # ID (col 4)
            id_item = QTableWidgetItem(str(log.get("entity_id", "")))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 4, id_item)

            # Description (col 5)
            desc = str(log.get("details", "") or "")[:100]
            desc_item = QTableWidgetItem(desc)
            desc_item.setTextAlignment(int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
            self._table.setItem(row, 5, desc_item)

            # IP (col 6)
            ip_item = QTableWidgetItem(str(log.get("ip_address", "")))
            ip_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 6, ip_item)

        self._pagination.update(self._current_page, pages, total)
        if items:
            self._table.show()
            self._empty.hide()
        else:
            self._table.hide()
            self._empty.show()

    def _centered(self, widget: QWidget) -> QWidget:
        c = QWidget()
        c.setStyleSheet("background:transparent;")
        h = QHBoxLayout(c)
        h.setContentsMargins(4, 0, 4, 0)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h.addWidget(widget)
        return c

    def _reset(self):
        self._action_filter.setCurrentIndex(0)
        self._entity_filter.setCurrentIndex(0)
        self._from_picker.setDate(QDate())
        self._to_picker.setDate(QDate())
        self.refresh()

    def _on_page_changed(self, page: int):
        self._load_data(page=page)

    def _on_error(self, msg: str):
        self._loading.hide()
        toast_error(self.window(), msg)

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
