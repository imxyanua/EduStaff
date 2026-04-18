# components/empty.py — Empty state widget

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt
from qfluentwidgets import BodyLabel, CaptionLabel, FluentIcon, TransparentPushButton


class EmptyStateWidget(QWidget):
    """Shown when a table has no data. Optionally shows a retry button."""

    def __init__(self, message: str = "Không có dữ liệu", on_retry=None, parent=None):
        super().__init__(parent)
        self.setObjectName("emptyState")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        icon_lbl = QLabel(self)
        icon_lbl.setPixmap(FluentIcon.DOCUMENT.icon().pixmap(40, 40))
        icon_lbl.setObjectName("emptyIcon")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg_lbl = BodyLabel("Chưa có dữ liệu", self)
        msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint_lbl = CaptionLabel(message, self)
        hint_lbl.setWordWrap(True)
        msg_lbl.setObjectName("emptyText")
        hint_lbl.setObjectName("emptyHint")
        hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon_lbl)
        layout.addWidget(msg_lbl)
        layout.addWidget(hint_lbl)

        if on_retry:
            retry_btn = TransparentPushButton(FluentIcon.SYNC, "Tải lại", self)
            retry_btn.clicked.connect(on_retry)
            layout.addWidget(retry_btn, alignment=Qt.AlignmentFlag.AlignCenter)
