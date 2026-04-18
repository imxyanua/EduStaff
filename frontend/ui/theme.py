# ui/theme.py — Design tokens (GitHub-dark palette per DESIGN.md)

_TOKENS: dict[str, str] = {
    # ── Background layers (dark to light) ────────────────────────
    "bg_deep":     "#0D1117",   # App root background
    "bg_base":     "#161B22",   # Sidebar, panels
    "bg_surface":  "#1C2333",   # Cards, table header
    "bg_elevated": "#21262D",   # Table rows, inputs
    "bg_overlay":  "#2D333B",   # Hover, selected row

    # ── Borders ───────────────────────────────────────────────────
    "border":        "#30363D",
    "border_focus":  "#388BFD",
    "border_subtle": "#21262D",

    # ── Text ──────────────────────────────────────────────────────
    "text_primary":   "#E6EDF3",
    "text_secondary": "#8B949E",
    "text_muted":     "#484F58",
    "text_link":      "#58A6FF",

    # ── Accent blue (primary action) ──────────────────────────────
    "primary":       "#1F6FEB",
    "primary_hover": "#388BFD",
    "primary_press": "#1158C7",
    "primary_dim":   "#0D2349",

    # ── Semantic colors ───────────────────────────────────────────
    "success":      "#3FB950",
    "success_bg":   "#1A3A2A",
    "warning":      "#D29922",
    "warning_bg":   "#3A2A0A",
    "danger":       "#F85149",
    "danger_bg":    "#3D1318",
    "info":         "#58A6FF",
    "info_bg":      "#0D2349",

    # ── Table ─────────────────────────────────────────────────────
    "table_row_alt":      "#1A1F2B",
    "table_row_hover":    "#2D333B",
    "table_row_selected": "#1A3A5C",

    # ── Legacy aliases (used in ui/styles.py) ─────────────────────
    "bg_mantle":  "#161B22",
    "bg_crust":   "#0D1117",
    "bg_overlay_subtle": "#2D333B",
}

CARD_ACCENT: dict[str, str] = {
    "lecturers":   "#1F6FEB",
    "departments": "#3FB950",
    "schedules":   "#D29922",
    "accounts":    "#BC8CFF",
}

# Badge presets aligned with DESIGN.md
BADGE: dict[str, dict] = {
    "active":   {"bg": "#1A3A2A", "text": "#3FB950"},
    "inactive": {"bg": "#2D1F1F", "text": "#F85149"},
    "on_leave": {"bg": "#3A2A0A", "text": "#D29922"},
    "admin":    {"bg": "#1A2A4A", "text": "#388BFD"},
    "staff":    {"bg": "#2A1A3A", "text": "#BC8CFF"},
    "login":    {"bg": "#0D2349", "text": "#58A6FF"},
    "create":   {"bg": "#1A3A2A", "text": "#3FB950"},
    "update":   {"bg": "#3A2A0A", "text": "#D29922"},
    "delete":   {"bg": "#3D1318", "text": "#F85149"},
}


class Theme:
    @staticmethod
    def get(key: str, fallback: str = "#ffffff") -> str:
        return _TOKENS.get(key, fallback)

    @staticmethod
    def tokens() -> dict[str, str]:
        return dict(_TOKENS)
