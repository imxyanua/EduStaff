# components/loading.py — Semi-transparent loading overlay

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from qfluentwidgets import IndeterminateProgressBar, BodyLabel


class LoadingOverlay(QWidget):
    """
    Full-size translucent overlay with a spinner.
    Attach to a parent widget, resize() whenever parent resizes.
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(13,17,23,0.75);")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)

        # Spinner card
        card = QFrame(self)
        card.setObjectName("loadingCard")
        card.setStyleSheet(
            "QFrame#loadingCard{"
            "background:rgba(22,27,34,0.96);"
            "border-radius:16px;"
            "border:1px solid #30363D;}"
        )
        card_v = QVBoxLayout(card)
        card_v.setContentsMargins(32, 24, 32, 24)
        card_v.setSpacing(12)

        self._bar = IndeterminateProgressBar(card)
        self._bar.setFixedWidth(180)

        self._label = BodyLabel("Đang tải...", card)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet("color:#8B949E; background:transparent;")

        card_v.addWidget(self._bar)
        card_v.addWidget(self._label)

        layout.addWidget(card)

    def set_text(self, text: str):
        self._label.setText(text)

    def show(self):
        self.resize(self.parent().size())
        self.raise_()
        super().show()
