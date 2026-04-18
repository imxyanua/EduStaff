# screens/dashboard_screen.py — Fluent dashboard with stat cards + charts

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal

from qfluentwidgets import (
    SmoothScrollArea, ElevatedCardWidget, BodyLabel, CaptionLabel,
    SubtitleLabel, TitleLabel, IndeterminateProgressBar,
    FluentIcon as FIF
)

from components.cards import StatCard, SectionHeader
from components.loading import LoadingOverlay
from components.toast import toast_error
from ui.icon_manager import IconManager
from ui.theme import CARD_ACCENT
import api.stats_api as stats_api
import api.audit_api as audit_api


# ── Worker ───────────────────────────────────────────────────────
class DashboardWorker(QThread):
    finished = Signal(dict, list, list, list, list)
    error    = Signal(str)

    def run(self):
        try:
            overview    = stats_api.get_overview()
            by_dept     = stats_api.get_by_department()
            by_degree   = stats_api.get_by_degree()
            by_position = stats_api.get_by_position()
            logs        = audit_api.get_audit_logs(size=8)
            recent_logs = logs.get("items", []) if isinstance(logs, dict) else []
            self.finished.emit(overview, by_dept, by_degree, by_position, recent_logs)
        except Exception as e:
            self.error.emit(str(e))


# ── Screen ────────────────────────────────────────────────────────
class DashboardScreen(SmoothScrollArea):
    """Dashboard — stat cards, bar charts, recent activity."""

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("DashboardScreen")
        self.user_info = user_info
        self.is_admin = user_info.get("role") == "admin"
        self._worker = None

        self._content = QWidget()
        self._content.setObjectName("dashboardContent")
        self.setWidget(self._content)
        self.setWidgetResizable(True)

        self._build_ui()
        self._loading = LoadingOverlay(self)

    def _build_ui(self):
        layout = QVBoxLayout(self._content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # Header
        layout.addWidget(
            SectionHeader(
                "Dashboard",
                "Tổng quan hệ thống — cập nhật theo thời gian thực",
                icon="squares-four",
            )
        )

        # ── Stat cards row ────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        acc = CARD_ACCENT
        self._card_lect  = StatCard("users",          "—", "Tổng Giảng Viên",  acc["lecturers"])
        self._card_dept  = StatCard("buildings",       "—", "Số Khoa / Bộ Môn", acc["departments"])
        self._card_sched = StatCard("calendar-blank",  "—", "Lịch Giảng Dạy",   acc["schedules"])
        self._card_acc   = StatCard("shield-check",    "—", "Tài Khoản",         acc["accounts"])

        for card in [self._card_lect, self._card_dept, self._card_sched, self._card_acc]:
            cards_row.addWidget(card)
        layout.addLayout(cards_row)

        # ── Charts row ────────────────────────────────────────────
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        # Left: department table
        self._dept_card = self._make_card(
            "buildings", "Giảng Viên theo Khoa", stretch=3
        )
        dept_inner_v = self._dept_card.property("inner_layout")
        self._dept_table = QTableWidget(0, 3)
        self._dept_table.setHorizontalHeaderLabels(["Tên Khoa", "Mã", "Số GV"])
        self._dept_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self._dept_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self._dept_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        self._dept_table.setColumnWidth(1, 70)
        self._dept_table.setColumnWidth(2, 70)
        self._dept_table.verticalHeader().setVisible(False)
        self._dept_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._dept_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._dept_table.setAlternatingRowColors(True)
        self._dept_table.setMaximumHeight(240)
        self._dept_table.setShowGrid(False)
        dept_inner_v.addWidget(self._dept_table)
        charts_row.addWidget(self._dept_card, stretch=3)

        # Right: degree bar chart
        self._degree_card = self._make_card(
            "graduation-cap", "Giảng Viên theo Học Vị", stretch=2
        )
        self._degree_inner = self._degree_card.property("inner_layout")
        charts_row.addWidget(self._degree_card, stretch=2)

        layout.addLayout(charts_row)

        # ── Second row ────────────────────────────────────────────
        second_row = QHBoxLayout()
        second_row.setSpacing(16)

        # Position chart
        self._pos_card = self._make_card("users", "Giảng Viên theo Chức Vụ", stretch=2)
        self._pos_inner = self._pos_card.property("inner_layout")
        second_row.addWidget(self._pos_card, stretch=2)

        # Recent activity (admin only)
        if self.is_admin:
            self._act_card = self._make_card("clipboard-text", "Hoạt Động Gần Đây", stretch=3)
            self._act_inner = self._act_card.property("inner_layout")
            self._act_list = QListWidget()
            self._act_list.setStyleSheet(
                "QListWidget{background:transparent;border:none;}"
                "QListWidget::item{padding:8px 4px;"
                "border-bottom:1px solid #21262D;"
                "color:#8B949E; font-size:12px;}"
                "QListWidget::item:hover{background:#21262D;}"
            )
            self._act_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
            self._act_inner.addWidget(self._act_list)
            second_row.addWidget(self._act_card, stretch=3)

        layout.addLayout(second_row)
        layout.addStretch()

    # ── Card factory ─────────────────────────────────────────────
    def _make_card(self, icon_name: str, title: str, stretch: int = 1) -> ElevatedCardWidget:
        card = ElevatedCardWidget()
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(16, 16, 16, 16)
        card_v.setSpacing(12)

        title_row = QHBoxLayout()
        icon_lbl = QLabel()
        icon_lbl.setStyleSheet("background:transparent;")
        icon_lbl.setPixmap(IconManager.get(icon_name, "#8B949E", 18).pixmap(18, 18))
        t_lbl = BodyLabel(title)
        t_lbl.setStyleSheet("font-size:14px; font-weight:600; background:transparent;")
        title_row.addWidget(icon_lbl)
        title_row.addSpacing(6)
        title_row.addWidget(t_lbl)
        title_row.addStretch()
        card_v.addLayout(title_row)

        inner = QVBoxLayout()
        inner.setSpacing(10)
        card_v.addLayout(inner)
        card_v.addStretch()

        # Attach inner layout as a property so we can append widgets
        card.setProperty("inner_layout", inner)
        return card

    # ── Refresh ────────────────────────────────────────────────────
    def refresh(self):
        self._loading.show()
        self._worker = DashboardWorker()
        self._worker.finished.connect(self._on_loaded)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_loaded(self, overview: dict, by_dept: list,
                   by_degree: list, by_position: list, recent_logs: list):
        self._loading.hide()

        # Stat cards
        self._card_lect.set_value(str(overview.get("total_lecturers", 0)))
        self._card_dept.set_value(str(overview.get("total_departments", 0)))
        self._card_sched.set_value(str(overview.get("total_schedules", 0)))
        self._card_acc.set_value(str(overview.get("total_accounts", 0)))

        # Dept table
        self._dept_table.setRowCount(0)
        for row_data in by_dept:
            r = self._dept_table.rowCount()
            self._dept_table.insertRow(r)
            self._dept_table.setItem(r, 0, QTableWidgetItem(row_data.get("department_name", "")))
            self._dept_table.setItem(r, 1, QTableWidgetItem(row_data.get("department_code", "")))
            cnt = QTableWidgetItem(str(row_data.get("count", 0)))
            cnt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._dept_table.setItem(r, 2, cnt)

        # Bar charts
        self._render_bar_chart(self._degree_inner, by_degree, "degree", "#0099FF")
        self._render_bar_chart(self._pos_inner,    by_position, "position", "#8764B8")

        # Activity feed
        if self.is_admin and hasattr(self, "_act_list"):
            self._act_list.clear()
            ACTION_ICONS = {
                "login": "sign-in", "create": "plus-circle",
                "update": "pencil-simple", "delete": "trash"
            }
            ACTION_COLORS = {
                "login": "#58A6FF", "create": "#3FB950",
                "update": "#D29922", "delete": "#F85149"
            }
            for log in recent_logs:
                action = log.get("action", "")
                color  = ACTION_COLORS.get(action, "#8B949E")
                user   = log.get("username", "—")
                entity = log.get("entity_type") or ""
                t      = log.get("created_at", "")[:16].replace("T", " ")

                item_w = QWidget()
                item_w.setStyleSheet("background:transparent;")
                row_h = QHBoxLayout(item_w)
                row_h.setContentsMargins(0, 4, 0, 4)
                row_h.setSpacing(8)

                icon_l = QLabel()
                icon_l.setPixmap(
                    IconManager.get(ACTION_ICONS.get(action, "info"), color, 14).pixmap(14, 14)
                )
                text_l = QLabel(f"{t}  —  {user}  →  {action} {entity}")
                text_l.setStyleSheet(f"color:{color}; font-size:12px;")
                row_h.addWidget(icon_l)
                row_h.addWidget(text_l)
                row_h.addStretch()

                list_item = QListWidgetItem()
                list_item.setSizeHint(item_w.sizeHint())
                self._act_list.addItem(list_item)
                self._act_list.setItemWidget(list_item, item_w)

    def _render_bar_chart(self, layout: QVBoxLayout, data: list, key: str, color: str):
        while layout.count():
            it = layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

        if not data:
            lbl = CaptionLabel("Không có dữ liệu")
            lbl.setStyleSheet("color:#484F58;")
            layout.addWidget(lbl)
            return

        total = sum(d.get("count", 0) for d in data) or 1

        for d in data[:8]:
            name  = str(d.get(key, "—"))
            count = d.get("count", 0)
            pct   = int(count / total * 100)

            row_w  = QWidget()
            row_w.setStyleSheet("background:transparent;")
            row_h = QHBoxLayout(row_w)
            row_h.setContentsMargins(0, 0, 0, 0)
            row_h.setSpacing(8)

            name_lbl = QLabel(name)
            name_lbl.setFixedWidth(110)
            name_lbl.setStyleSheet("color:#8B949E; font-size:12px; background:transparent;")

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(pct)
            bar.setFixedHeight(8)
            bar.setTextVisible(False)
            bar.setStyleSheet(
                f"QProgressBar{{background:#21262D;border:none;border-radius:4px;}}"
                f"QProgressBar::chunk{{background:{color};border-radius:4px;}}"
            )

            cnt_lbl = QLabel(str(count))
            cnt_lbl.setFixedWidth(30)
            cnt_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            cnt_lbl.setStyleSheet(f"color:{color}; font-size:12px; font-weight:600; background:transparent;")

            row_h.addWidget(name_lbl)
            row_h.addWidget(bar, stretch=1)
            row_h.addWidget(cnt_lbl)
            layout.addWidget(row_w)

    def _on_error(self, msg: str):
        self._loading.hide()
        for card in [self._card_lect, self._card_dept, self._card_sched, self._card_acc]:
            card.set_value("!")
        toast_error(self.window(), msg)

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
