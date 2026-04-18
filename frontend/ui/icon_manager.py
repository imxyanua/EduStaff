# ui/icon_manager.py — Maps Phosphor-style icon names to QIcon (using FluentIcon)

from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QSize
from qfluentwidgets import FluentIcon as FIF

_FLUENT_MAP: dict[str, FIF] = {
    "graduation-cap":  FIF.EDUCATION,
    "users":           FIF.PEOPLE,
    "buildings":       FIF.HOME,
    "calendar-blank":  FIF.CALENDAR,
    "squares-four":    FIF.TILES,
    "clipboard-text":  FIF.DOCUMENT,
    "sign-in":         FIF.SETTING,
    "plus-circle":     FIF.ADD,
    "pencil-simple":   FIF.EDIT,
    "trash":           FIF.DELETE,
    "info":            FIF.INFO,
    "shield-check":    FIF.FINGERPRINT,
    "people":          FIF.PEOPLE,
    "person":          FIF.PEOPLE,
    "library":         FIF.LIBRARY,
    "save":            FIF.SAVE,
    "history":         FIF.HISTORY,
    "close":           FIF.CLOSE,
    "sync":            FIF.SYNC,
    "search":          FIF.SEARCH,
    "filter":          FIF.FILTER,
    "download":        FIF.DOWNLOAD,
    "upload":          FIF.CLOUD,
    "chart":           FIF.PIE_SINGLE,
    "chart-bar":       FIF.PIE_SINGLE,
    "warning":         FIF.INFO,
    "check":           FIF.ACCEPT,
    "lock":            FIF.SETTING,
    "home":            FIF.HOME,
    "send":            FIF.SEND,
    "mail":            FIF.MAIL,
    "phone":           FIF.PHONE,
    "link":            FIF.LINK,
    "eye":             FIF.VIEW,
    "arrow-right":     FIF.CHEVRON_RIGHT,
    "arrow-left":      FIF.LEFT_ARROW,
    "more":            FIF.MORE,
    "refresh":         FIF.SYNC,
    "tag":             FIF.TAG,
}


class IconManager:
    """
    Returns a tinted QIcon for a given Phosphor-style name.
    Usage: IconManager.get("users", "#0099FF", 20).pixmap(20, 20)
    """

    @staticmethod
    def get(name: str, color: str = "#ffffff", size: int = 20) -> QIcon:
        fluent = _FLUENT_MAP.get(name)
        if fluent is not None:
            return IconManager._tint_fluent(fluent, color, size)
        return IconManager._placeholder(color, size)

    @staticmethod
    def _tint_fluent(icon: FIF, color: str, size: int) -> QIcon:
        src_pix = icon.icon().pixmap(QSize(size, size))
        if src_pix.isNull():
            return IconManager._placeholder(color, size)

        tinted = QPixmap(src_pix.size())
        tinted.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tinted)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.drawPixmap(0, 0, src_pix)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color))
        painter.end()
        return QIcon(tinted)

    @staticmethod
    def _placeholder(color: str, size: int) -> QIcon:
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        r = size // 4
        painter.drawEllipse(r, r, size - 2 * r, size - 2 * r)
        painter.end()
        return QIcon(pix)
