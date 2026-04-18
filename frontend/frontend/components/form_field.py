"""Reusable form field wrapper (label + editor + inline error)."""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel


class FormField(QWidget):
    """Bọc input theo chuẩn Fluent để đồng bộ style và validate."""

    def __init__(self, label: str, widget: QWidget, required: bool = False, parent=None):
        super().__init__(parent)
        self._widget = widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._label = QLabel(label, self)
        self._label.setObjectName("formFieldLabel")
        if required:
            self._label.setProperty("required", True)
        layout.addWidget(self._label)

        layout.addWidget(widget)

        self._error = CaptionLabel("", self)
        self._error.setObjectName("formFieldError")
        self._error.hide()
        layout.addWidget(self._error)

    def widget(self) -> QWidget:
        return self._widget

    def set_error(self, msg: str):
        # Đánh dấu trạng thái lỗi bằng dynamic property để QSS xử lý đồng bộ.
        self._error.setText(msg)
        self._error.show()
        self._widget.setProperty("error", True)
        self._widget.style().unpolish(self._widget)
        self._widget.style().polish(self._widget)

    def clear_error(self):
        self._error.hide()
        self._widget.setProperty("error", False)
        self._widget.style().unpolish(self._widget)
        self._widget.style().polish(self._widget)
