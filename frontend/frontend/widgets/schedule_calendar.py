"""Weekly calendar-like schedule widget for teaching plans."""

from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem, QVBoxLayout
from qfluentwidgets import BodyLabel, ElevatedCardWidget, TableWidget


class WeeklyScheduleCalendar(ElevatedCardWidget):
    """Hiển thị lịch giảng dạy theo tuần (Thứ 2 -> CN)."""

    DAY_LABELS = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "CN"]
    DAY_TO_COL = {
        "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6,
        2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("weeklyScheduleCalendar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self._title = BodyLabel("Lịch tuần")
        self._title.setStyleSheet("font-size:14px; font-weight:600;")
        layout.addWidget(self._title)

        self._table = TableWidget(self)
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(self.DAY_LABELS)
        self._table.verticalHeader().setVisible(True)
        self._table.setAlternatingRowColors(False)
        self._table.setShowGrid(True)
        self._table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionMode(TableWidget.SelectionMode.NoSelection)
        self._table.setWordWrap(True)
        self._table.verticalHeader().setDefaultSectionSize(76)

        hh = self._table.horizontalHeader()
        for col in range(7):
            hh.setSectionResizeMode(col, hh.ResizeMode.Stretch)

        layout.addWidget(self._table, stretch=1)

    def set_items(self, items: list):
        """Render lịch theo dữ liệu schedule đã lọc."""
        normalized = [i for i in items if isinstance(i, dict)]
        if not normalized:
            self._render_empty()
            return

        slot_labels = self._build_slot_labels(normalized)
        row_index = {slot: idx for idx, slot in enumerate(slot_labels)}

        self._table.clearContents()
        self._table.setRowCount(len(slot_labels))
        self._table.setVerticalHeaderLabels(slot_labels)

        grouped = defaultdict(list)
        for sched in normalized:
            col = self._resolve_day_column(sched.get("day_of_week"))
            if col is None:
                continue
            start = self._normalize_time(sched.get("start_time"))
            end = self._normalize_time(sched.get("end_time"))
            slot = f"{start} - {end}" if end else start
            if slot not in row_index:
                continue

            row = row_index[slot]
            grouped[(row, col)].append(sched)

        for (row, col), schedules in grouped.items():
            self._table.setItem(row, col, self._build_cell_item(schedules, col))

        for row in range(self._table.rowCount()):
            for col in range(self._table.columnCount()):
                if self._table.item(row, col) is None:
                    empty = QTableWidgetItem("-")
                    empty.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    empty.setForeground(QColor(170, 179, 195, 110))
                    self._table.setItem(row, col, empty)

    def _render_empty(self):
        self._table.clearContents()
        self._table.setRowCount(1)
        self._table.setVerticalHeaderLabels(["Khung giờ"])
        empty_item = QTableWidgetItem("Không có lịch giảng dạy")
        empty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_item.setForeground(QColor(190, 199, 214, 170))
        self._table.setSpan(0, 0, 1, 7)
        self._table.setItem(0, 0, empty_item)

    def _build_slot_labels(self, items: list) -> list:
        slots = []
        for sched in items:
            start = self._normalize_time(sched.get("start_time"))
            end = self._normalize_time(sched.get("end_time"))
            if not start:
                continue
            slots.append(f"{start} - {end}" if end else start)

        if not slots:
            return ["08:00 - 10:00"]

        return sorted(set(slots), key=lambda s: s.split(" - ")[0])

    def _resolve_day_column(self, day_value):
        if day_value in self.DAY_TO_COL:
            return self.DAY_TO_COL[day_value]
        day_text = str(day_value or "").strip()
        if day_text in self.DAY_TO_COL:
            return self.DAY_TO_COL[day_text]
        if day_text.isdigit():
            return self.DAY_TO_COL.get(int(day_text))
        return None

    @staticmethod
    def _normalize_time(value) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        if len(text) >= 5:
            return text[:5]
        return text

    def _build_cell_item(self, schedules: list, day_index: int) -> QTableWidgetItem:
        lines = []
        for sched in schedules:
            lecturer = (sched.get("lecturer") or {}).get("full_name", "")
            subject = sched.get("subject_code") or sched.get("subject_name") or "Môn học"
            room = sched.get("room") or "---"
            text = f"{subject}\nPhòng {room}"
            if lecturer:
                text += f"\n{lecturer}"
            lines.append(text)

        item = QTableWidgetItem("\n\n".join(lines))
        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        day_colors = [
            QColor(80, 130, 210, 60),
            QColor(102, 162, 214, 60),
            QColor(115, 170, 155, 60),
            QColor(125, 148, 210, 60),
            QColor(182, 144, 194, 60),
            QColor(200, 154, 133, 60),
            QColor(165, 165, 182, 60),
        ]
        item.setBackground(day_colors[day_index])
        return item
