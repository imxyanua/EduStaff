# components/cards.py — Stat card + header card helpers

from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from qfluentwidgets import ElevatedCardWidget, BodyLabel, CaptionLabel, IconWidget, FluentIcon
from ui.icon_manager import IconManager


def _apply_soft_shadow(widget: QWidget):
    # Shadow nhẹ đúng tinh thần Fluent, tránh quá đậm để giữ độ thoáng.
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(24)
    shadow.setXOffset(0)
    shadow.setYOffset(4)
    shadow.setColor(QColor(0, 0, 0, 70))
    widget.setGraphicsEffect(shadow)


class StatCard(ElevatedCardWidget):
    """
    Dashboard stat card:
      ┌─────────────────────────────────┐
      │  [icon]          [accent bar]   │
      │                                 │
      │  1 234                          │  ← big number
      │  Tổng Giảng Viên               │  ← label
      └─────────────────────────────────┘
    """

    def __init__(self, icon_name: str, value: str, label: str,
                 accent: str = "#0099FF", parent=None):
        super().__init__(parent)
        self._accent = accent
        self.setFixedHeight(120)
        self.setObjectName("statCard")
        _apply_soft_shadow(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(6)

        # Top row: icon + accent pill
        top = QHBoxLayout()
        self._icon_lbl = QLabel()
        self._icon_lbl.setStyleSheet("background: transparent;")
        self._icon_lbl.setPixmap(
            IconManager.get(icon_name, accent, 22).pixmap(22, 22)
        )
        top.addWidget(self._icon_lbl)
        top.addStretch()

        # Small colored accent bar
        bar = QFrame()
        bar.setObjectName("accentBar")
        bar.setFixedSize(36, 4)
        bar.setStyleSheet(f"background-color:{accent}; border-radius:2px;")
        top.addWidget(bar)
        root.addLayout(top)

        # Value
        self._value_lbl = QLabel(value)
        self._value_lbl.setStyleSheet(
            f"font-size:28px; font-weight:700; color:{accent}; background: transparent;"
        )
        root.addWidget(self._value_lbl)

        # Label
        self._label_lbl = CaptionLabel(label, self)
        self._label_lbl.setStyleSheet("color:#8B949E; background: transparent;")
        root.addWidget(self._label_lbl)
        root.addStretch()

    def set_value(self, value: str):
        self._value_lbl.setText(value)


class SectionHeader(QWidget):
    """Page-level header with title + subtitle."""

    def __init__(self, title: str, subtitle: str = "", icon: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("pageHeader")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(8)

        if icon:
            icon_lbl = QLabel(self)
            icon_lbl.setPixmap(IconManager.get(icon, "#76baff", 18).pixmap(18, 18))
            title_row.addWidget(icon_lbl)

        title_lbl = QLabel(title, self)
        title_lbl.setObjectName("pageTitle")
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        layout.addLayout(title_row)

        if subtitle:
            sub_lbl = CaptionLabel(subtitle, self)
            sub_lbl.setObjectName("pageSubtitle")
            layout.addWidget(sub_lbl)
