# components/pagination.py — Fluent-style pagination bar

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from qfluentwidgets import PushButton, TransparentPushButton, CaptionLabel, FluentIcon as FIF


class PaginationBar(QWidget):
    """
    Emits page_changed(page: int) when the user navigates.
    Call update(current, total, page_size, item_count) to refresh state.
    """

    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current  = 1
        self._total    = 1
        self._page_size = 20
        self._item_count = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(6)

        self._info_lbl = CaptionLabel("", self)
        self._info_lbl.setStyleSheet("color:rgba(160,175,200,0.6); background:transparent;")

        self._prev_btn = PushButton(FIF.PAGE_LEFT, "", self)
        self._prev_btn.setFixedSize(32, 32)
        self._prev_btn.clicked.connect(self._go_prev)

        self._page_lbl = CaptionLabel("1 / 1", self)
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_lbl.setFixedWidth(60)
        self._page_lbl.setStyleSheet(
            "color:rgba(200,210,230,0.85); background:transparent; font-weight:600;"
        )

        self._next_btn = PushButton(FIF.PAGE_RIGHT, "", self)
        self._next_btn.setFixedSize(32, 32)
        self._next_btn.clicked.connect(self._go_next)

        layout.addWidget(self._info_lbl)
        layout.addStretch()
        layout.addWidget(self._prev_btn)
        layout.addWidget(self._page_lbl)
        layout.addWidget(self._next_btn)

    def update_state(self, current: int, total: int,
                     page_size: int = 20, item_count: int = 0):
        self._current    = max(1, current)
        self._total      = max(1, total)
        self._page_size  = page_size
        self._item_count = item_count

        self._page_lbl.setText(f"{self._current} / {self._total}")
        self._prev_btn.setEnabled(self._current > 1)
        self._next_btn.setEnabled(self._current < self._total)

        start = (self._current - 1) * page_size + 1
        end   = start + item_count - 1
        self._info_lbl.setText(
            f"Hiển thị {start}–{end}"
            if item_count else "Không có dữ liệu"
        )

    def _go_prev(self):
        if self._current > 1:
            self.page_changed.emit(self._current - 1)

    def _go_next(self):
        if self._current < self._total:
            self.page_changed.emit(self._current + 1)

    @property
    def current_page(self) -> int:
        return self._current
