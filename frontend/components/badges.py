# components/badges.py — Pill-shaped status badges (DESIGN.md palette)

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

_PRESETS: dict[str, tuple[str, str]] = {
    # (background, text)  — from DESIGN.md BADGE_* tokens
    "active":   ("#1A3A2A", "#3FB950"),
    "inactive": ("#2D1F1F", "#F85149"),
    "on_leave": ("#3A2A0A", "#D29922"),
    "admin":    ("#1A2A4A", "#388BFD"),
    "staff":    ("#2A1A3A", "#BC8CFF"),
    "success":  ("#1A3A2A", "#3FB950"),
    "error":    ("#3D1318", "#F85149"),
    "warning":  ("#3A2A0A", "#D29922"),
    "pending":  ("#3A2A0A", "#D29922"),
    "info":     ("#0D2349", "#58A6FF"),
    "login":    ("#0D2349", "#58A6FF"),
    "create":   ("#1A3A2A", "#3FB950"),
    "update":   ("#3A2A0A", "#D29922"),
    "delete":   ("#3D1318", "#F85149"),
    "blue":     ("#1A2A4A", "#388BFD"),
    "green":    ("#1A3A2A", "#3FB950"),
    "red":      ("#3D1318", "#F85149"),
    "yellow":   ("#3A2A0A", "#D29922"),
    "purple":   ("#2A1A3A", "#BC8CFF"),
    "gray":     ("#21262D", "#8B949E"),
}


class Badge(QLabel):
    """
    Pill-shaped coloured badge.
    Usage: Badge("Hoạt động", "active")
           Badge("Custom", bg="#1A3A2A", fg="#3FB950")
    """

    def __init__(self, text: str, preset: str = "gray",
                 bg: str = "", fg: str = "", parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if bg and fg:
            background, foreground = bg, fg
        else:
            background, foreground = _PRESETS.get(preset, _PRESETS["gray"])
        self.setStyleSheet(
            f"background:{background}; color:{foreground};"
            "border-radius:10px; padding:2px 10px;"
            "font-size:11px; font-weight:600; letter-spacing:0.3px;"
        )
