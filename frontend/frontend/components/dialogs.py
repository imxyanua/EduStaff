# components/dialogs.py — Confirm + base form dialog helpers

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from qfluentwidgets import (
    MessageBox, SubtitleLabel, BodyLabel,
    PrimaryPushButton, PushButton, CaptionLabel
)


def confirm(title: str, content: str, parent=None, yes_text: str = "Xác nhận",
            cancel_text: str = "Hủy") -> bool:
    """Show a Fluent MessageBox and return True if user confirmed."""
    box = MessageBox(title, content, parent)
    box.yesButton.setText(yes_text)
    box.cancelButton.setText(cancel_text)
    return bool(box.exec())


class FluentFormDialog(QDialog):
    """
    Base class for all form dialogs.
    Subclasses should:
      1. Call super().__init__(title, parent)
      2. Override _build_form(body_layout) to add form widgets
      3. Override _collect() -> dict to return form data
      4. Override _validate() -> bool for validation
    """

    def __init__(self, title: str, parent=None, min_width: int = 560):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(min_width)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ───────────────────────────────────────────────
        header = QFrame()
        header.setObjectName("dialogHeader")
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(24, 16, 24, 16)

        self._title_lbl = SubtitleLabel(title, header)
        h_lay.addWidget(self._title_lbl)
        h_lay.addStretch()
        root.addWidget(header)

        # ── Body (scrollable) ─────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        body_w = QWidget()
        self._body_layout = QVBoxLayout(body_w)
        self._body_layout.setContentsMargins(24, 20, 24, 20)
        self._body_layout.setSpacing(14)
        self._build_form(self._body_layout)

        # Global error label
        self._error_lbl = QLabel()
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setStyleSheet(
            "color:#F85149; background:#3D1318; border:1px solid #5A1E24;"
            "border-radius:6px; padding:8px 12px; font-size:12px;"
        )
        self._error_lbl.hide()
        self._body_layout.addWidget(self._error_lbl)
        self._body_layout.addStretch()

        scroll.setWidget(body_w)
        root.addWidget(scroll, stretch=1)

        # ── Footer ────────────────────────────────────────────────
        footer = QFrame()
        footer.setObjectName("dialogFooter")
        f_lay = QHBoxLayout(footer)
        f_lay.setContentsMargins(24, 12, 24, 12)
        f_lay.addStretch()

        self._cancel_btn = PushButton("Hủy bỏ", footer)
        self._cancel_btn.clicked.connect(self.reject)

        self._save_btn = PrimaryPushButton("  Lưu lại", footer)
        self._save_btn.clicked.connect(self._on_save)

        f_lay.addWidget(self._cancel_btn)
        f_lay.addSpacing(8)
        f_lay.addWidget(self._save_btn)
        root.addWidget(footer)

    # ── Subclass hooks ────────────────────────────────────────────

    def _build_form(self, layout: QVBoxLayout):
        """Override: populate body layout with form fields."""
        pass

    def _validate(self) -> bool:
        """Override: validate fields. Call show_error() to report issues."""
        return True

    def _collect(self) -> dict:
        """Override: collect and return form data as dict."""
        return {}

    # ── Internals ─────────────────────────────────────────────────

    def _on_save(self):
        self._error_lbl.hide()
        if self._validate():
            self.accept()

    def show_error(self, msg: str):
        self._error_lbl.setText(f"⚠️  {msg}")
        self._error_lbl.show()

    def set_loading(self, loading: bool, text: str = "Đang lưu..."):
        self._save_btn.setEnabled(not loading)
        self._cancel_btn.setEnabled(not loading)
        self._save_btn.setText(text if loading else "  Lưu lại")

    def get_data(self) -> dict:
        return self._collect()
