from ui.theme import Theme

def get_global_qss() -> str:
    return f"""
/* ══════════════════════════════════════════════════════
   ROOT — NỀN VÀ CHỮ MẶC ĐỊNH
══════════════════════════════════════════════════════ */
QMainWindow, QDialog, QWidget, QFrame {{
    background-color: {Theme.get('bg_base')};
    color: {Theme.get('text_primary')};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}}

/* Label mặc định nền trong suốt để tránh tạo mảng nền tối trong card/panel */
QLabel, BodyLabel, CaptionLabel, SubtitleLabel, TitleLabel {{
    background-color: transparent;
}}

QSplitter::handle {{
    background-color: {Theme.get('bg_overlay')};
    width: 1px;
    height: 1px;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {Theme.get('bg_overlay')};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {Theme.get('text_muted')}; }}
QScrollBar::handle:vertical:pressed {{ background: #7f849c; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: transparent; }}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; }}

QScrollBar:horizontal {{
    background: transparent;
    height: 6px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {Theme.get('bg_overlay')};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: {Theme.get('text_muted')}; }}
QScrollBar::handle:horizontal:pressed {{ background: #7f849c; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0px; background: transparent; }}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}

/* ══════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════ */
#sidebar {{
    background-color: {Theme.get('bg_mantle')};
    border-right: 1px solid {Theme.get('bg_surface')};
    min-width: 240px;
    max-width: 240px;
}}

#logo_area {{
    background-color: {Theme.get('bg_mantle')};
    padding: 20px 16px 16px 16px;
    border-bottom: 1px solid {Theme.get('bg_surface')};
}}

#app_name {{
    color: {Theme.get('primary')};
    font-size: 18px;
    font-weight: 700;
}}

#app_tagline {{
    color: {Theme.get('text_muted')};
    font-size: 11px;
}}

/* Nút điều hướng sidebar */
#sidebar_btn {{
    background-color: transparent;
    color: {Theme.get('text_secondary')};
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    margin: 1px 8px;
}}
#sidebar_btn:hover {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
}}
#sidebar_btn[active="true"] {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('primary')};
    font-weight: 600;
    border-left: 3px solid {Theme.get('primary')};
    padding-left: 11px;
}}

#sidebar_divider {{
    background-color: {Theme.get('bg_surface')};
    min-height: 1px;
    max-height: 1px;
    margin: 8px 16px;
}}

/* User info và nút đăng xuất dưới sidebar */
#user_area {{
    background-color: {Theme.get('bg_mantle')};
    border-top: 1px solid {Theme.get('bg_surface')};
    padding: 12px 16px;
}}
#user_name {{
    color: {Theme.get('text_primary')};
    font-size: 13px;
    font-weight: 600;
}}
#user_role_badge {{
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 10px;
}}

/* ══════════════════════════════════════════════════════
   STATUS BAR (dưới cùng)
══════════════════════════════════════════════════════ */
#status_bar {{
    background-color: {Theme.get('bg_crust')};
    border-top: 1px solid {Theme.get('bg_surface')};
    padding: 4px 16px;
    min-height: 28px;
    max-height: 28px;
}}
#status_bar QLabel {{
    color: {Theme.get('text_muted')};
    font-size: 11px;
}}

/* ══════════════════════════════════════════════════════
   CONTENT AREA & TIÊU ĐỀ TRANG
══════════════════════════════════════════════════════ */
#content_area {{
    background-color: {Theme.get('bg_base')};
    padding: 0;
}}

#page_header {{
    background-color: {Theme.get('bg_base')};
    padding: 20px 24px 16px 24px;
    border-bottom: 1px solid {Theme.get('bg_surface')};
}}

#page_title {{
    font-size: 20px;
    font-weight: 700;
    color: {Theme.get('text_primary')};
}}

#page_subtitle {{
    font-size: 12px;
    color: {Theme.get('text_muted')};
}}

/* ══════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════ */

/* Primary — xanh (Lưu, Thêm, Đăng nhập) */
QPushButton#btn_primary {{
    background-color: {Theme.get('primary')};
    color: {Theme.get('bg_base')};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 34px;
}}
QPushButton#btn_primary:hover   {{ background-color: {Theme.get('primary_hover')}; }}
QPushButton#btn_primary:pressed  {{ background-color: #6ab0e0; }}
QPushButton#btn_primary:disabled {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_muted')};
}}

/* Success — xanh lá (Export, Backup) */
QPushButton#btn_success {{
    background-color: {Theme.get('success')};
    color: {Theme.get('bg_base')};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 34px;
}}
QPushButton#btn_success:hover   {{ background-color: #94d89a; }}
QPushButton#btn_success:pressed  {{ background-color: #82cc88; }}

/* Danger — đỏ (Xóa) */
QPushButton#btn_danger {{
    background-color: {Theme.get('danger')};
    color: {Theme.get('bg_base')};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 34px;
}}
QPushButton#btn_danger:hover   {{ background-color: #e87898; }}
QPushButton#btn_danger:pressed  {{ background-color: #dc6680; }}

/* Ghost — viền (Hủy, Đóng, Làm mới) */
QPushButton#btn_ghost {{
    background-color: transparent;
    color: {Theme.get('text_primary')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    min-height: 34px;
}}
QPushButton#btn_ghost:hover   {{ background-color: {Theme.get('bg_surface')}; border-color: {Theme.get('primary')}; }}
QPushButton#btn_ghost:pressed  {{ background-color: {Theme.get('bg_overlay')}; }}

/* Warning — vàng */
QPushButton#btn_warning {{
    background-color: {Theme.get('warning')};
    color: {Theme.get('bg_base')};
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-weight: 600;
    font-size: 13px;
    min-height: 34px;
}}
QPushButton#btn_warning:hover {{ background-color: #e8d19e; }}

/* Nút nhỏ trong bảng */
QPushButton#btn_icon_edit {{
    background-color: transparent;
    color: {Theme.get('primary')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    min-width: 32px;
    min-height: 26px;
}}
QPushButton#btn_icon_edit:hover {{ background-color: {Theme.get('bg_surface')}; border-color: {Theme.get('primary')}; }}

QPushButton#btn_icon_delete {{
    background-color: transparent;
    color: {Theme.get('danger')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    min-width: 32px;
    min-height: 26px;
}}
QPushButton#btn_icon_delete:hover {{ background-color: {Theme.get('bg_surface')}; border-color: {Theme.get('danger')}; }}

QPushButton#btn_icon_view {{
    background-color: transparent;
    color: {Theme.get('text_secondary')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    min-width: 32px;
    min-height: 26px;
}}
QPushButton#btn_icon_view:hover {{ background-color: {Theme.get('bg_surface')}; color: {Theme.get('text_primary')}; }}

QPushButton#btn_icon_lock {{
    background-color: transparent;
    color: {Theme.get('warning')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 12px;
    min-width: 32px;
    min-height: 26px;
}}
QPushButton#btn_icon_lock:hover {{ background-color: {Theme.get('bg_surface')}; border-color: {Theme.get('warning')}; }}

/* ══════════════════════════════════════════════════════
   INPUTS
══════════════════════════════════════════════════════ */
QLineEdit {{
    background-color: {Theme.get('bg_mantle')};
    border: 1px solid {Theme.get('bg_surface')};
    border-radius: 8px;
    padding: 10px 14px;
    color: {Theme.get('text_primary')};
    font-size: 13px;
    min-height: 38px;
    selection-background-color: {Theme.get('primary')};
    selection-color: {Theme.get('bg_base')};
}}
QLineEdit:focus    {{ border-color: {Theme.get('primary')}; }}
QLineEdit:disabled {{ background-color: {Theme.get('bg_base')}; color: {Theme.get('text_muted')}; }}
QLineEdit[error="true"] {{ border-color: {Theme.get('danger')}; }}

QTextEdit, QPlainTextEdit {{
    background-color: {Theme.get('bg_mantle')};
    border: 1px solid {Theme.get('bg_surface')};
    border-radius: 8px;
    padding: 10px 14px;
    color: {Theme.get('text_primary')};
    font-size: 13px;
}}
QTextEdit:focus {{ border-color: {Theme.get('primary')}; }}

QComboBox {{
    background-color: {Theme.get('bg_mantle')};
    border: 1px solid {Theme.get('bg_surface')};
    border-radius: 8px;
    padding: 10px 32px 10px 14px;
    color: {Theme.get('text_primary')};
    font-size: 13px;
    min-height: 38px;
    min-width: 140px;
}}
QComboBox:focus   {{ border-color: {Theme.get('primary')}; }}
QComboBox:hover   {{ border-color: {Theme.get('text_muted')}; }}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox::down-arrow {{
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {Theme.get('text_secondary')};
    margin-right: 8px;
}}
QComboBox QAbstractItemView {{
    background-color: {Theme.get('bg_surface')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 6px;
    color: {Theme.get('text_primary')};
    selection-background-color: {Theme.get('bg_overlay')};
    selection-color: {Theme.get('text_primary')};
    padding: 4px;
    outline: none;
}}
QComboBox QAbstractItemView::item {{
    padding: 6px 12px;
    border-radius: 4px;
    min-height: 28px;
}}
QComboBox QAbstractItemView::item:hover    {{ background-color: {Theme.get('bg_overlay')}; }}
QComboBox QAbstractItemView::item:selected {{ background-color: {Theme.get('bg_surface')}; color: {Theme.get('primary')}; }}

QDateEdit, QTimeEdit {{
    background-color: {Theme.get('bg_mantle')};
    border: 1px solid {Theme.get('bg_surface')};
    border-radius: 8px;
    padding: 10px 14px;
    color: {Theme.get('text_primary')};
    font-size: 13px;
    min-height: 38px;
}}
QDateEdit:focus, QTimeEdit:focus {{ border-color: {Theme.get('primary')}; }}
QDateEdit::drop-down, QTimeEdit::drop-down {{
    border: none;
    width: 20px;
}}
QCalendarWidget {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
}}
QCalendarWidget QToolButton {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
    border: none;
    padding: 4px;
}}
QCalendarWidget QAbstractItemView:enabled {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
    selection-background-color: {Theme.get('primary')};
    selection-color: {Theme.get('bg_base')};
}}

QCheckBox {{
    color: {Theme.get('text_primary')};
    font-size: 13px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 4px;
    background-color: {Theme.get('bg_surface')};
}}
QCheckBox::indicator:checked {{
    background-color: {Theme.get('primary')};
    border-color: {Theme.get('primary')};
}}
QCheckBox::indicator:hover {{ border-color: {Theme.get('primary')}; }}

QRadioButton {{
    color: {Theme.get('text_primary')};
    font-size: 13px;
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 8px;
    background-color: {Theme.get('bg_surface')};
}}
QRadioButton::indicator:checked {{
    background-color: {Theme.get('primary')};
    border-color: {Theme.get('primary')};
}}

/* ══════════════════════════════════════════════════════
   TABLE
══════════════════════════════════════════════════════ */
QTableWidget {{
    background-color: {Theme.get('bg_base')};
    alternate-background-color: {Theme.get('table_row_alt')};
    border: 1px solid {Theme.get('bg_surface')};
    border-radius: 8px;
    gridline-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
    font-size: 13px;
    selection-background-color: {Theme.get('bg_overlay')};
    selection-color: {Theme.get('text_primary')};
    outline: none;
}}
QTableWidget::item {{
    padding: 10px 12px;
    border: none;
}}
QTableWidget::item:hover     {{ background-color: {Theme.get('bg_surface')}; }}
QTableWidget::item:selected  {{ background-color: {Theme.get('bg_overlay')}; color: {Theme.get('text_primary')}; }}

QHeaderView {{
    background-color: {Theme.get('bg_surface')};
}}
QHeaderView::section {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_secondary')};
    font-weight: 600;
    font-size: 12px;
    padding: 10px 12px;
    border: none;
    border-right: 1px solid {Theme.get('bg_overlay')};
    border-bottom: 2px solid {Theme.get('primary')};
}}
QHeaderView::section:first  {{ border-radius: 8px 0 0 0; }}
QHeaderView::section:last   {{ border-right: none; border-radius: 0 8px 0 0; }}
QHeaderView::section:hover  {{ background-color: {Theme.get('bg_overlay')}; }}

QTableWidget QTableCornerButton::section {{
    background-color: {Theme.get('bg_surface')};
    border: none;
}}

/* ══════════════════════════════════════════════════════
   CARDS (Dashboard)
══════════════════════════════════════════════════════ */
QFrame#stat_card {{
    background-color: {Theme.get('bg_surface')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 12px;
    padding: 20px;
}}
QFrame#stat_card:hover {{
    border-color: {Theme.get('primary')};
}}

/* ══════════════════════════════════════════════════════
   TOOLBAR / FILTER BAR
══════════════════════════════════════════════════════ */
QFrame#toolbar {{
    background-color: {Theme.get('bg_mantle')};
    border: 1px solid {Theme.get('bg_surface')};
    border-radius: 8px;
    padding: 12px 16px;
}}

/* ══════════════════════════════════════════════════════
   DIALOGS
══════════════════════════════════════════════════════ */
QDialog {{
    background-color: {Theme.get('bg_base')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 12px;
}}

#dialog_header {{
    background-color: {Theme.get('bg_mantle')};
    border-bottom: 1px solid {Theme.get('bg_surface')};
    padding: 16px 24px;
    border-radius: 12px 12px 0 0;
}}
#dialog_title {{
    font-size: 16px;
    font-weight: 700;
    color: {Theme.get('text_primary')};
}}

#dialog_body {{
    padding: 20px 24px;
    background-color: {Theme.get('bg_base')};
}}

#dialog_footer {{
    background-color: {Theme.get('bg_mantle')};
    border-top: 1px solid {Theme.get('bg_surface')};
    padding: 12px 24px;
    border-radius: 0 0 12px 12px;
}}

/* ══════════════════════════════════════════════════════
   FORM LABELS
══════════════════════════════════════════════════════ */
QLabel#form_label {{
    color: {Theme.get('text_secondary')};
    font-size: 12px;
    font-weight: 600;
}}
QLabel#required_star {{
    color: {Theme.get('danger')};
    font-size: 12px;
    font-weight: 600;
}}
QLabel#error_label {{
    color: {Theme.get('danger')};
    font-size: 11px;
}}
QLabel#section_label {{
    color: {Theme.get('text_muted')};
    font-size: 11px;
    font-weight: 600;
}}

/* ══════════════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════════════ */
QProgressBar {{
    background-color: {Theme.get('bg_surface')};
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {Theme.get('primary')};
    border-radius: 4px;
}}

/* ══════════════════════════════════════════════════════
   TOOLTIP
══════════════════════════════════════════════════════ */
QToolTip {{
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
    border: 1px solid {Theme.get('bg_overlay')};
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}}

/* ══════════════════════════════════════════════════════
   CONTEXT MENU
══════════════════════════════════════════════════════ */
QMenu {{
    background-color: {Theme.get('bg_surface')};
    border: 1px solid {Theme.get('bg_overlay')};
    border-radius: 8px;
    padding: 4px;
    color: {Theme.get('text_primary')};
    font-size: 13px;
}}
QMenu::item {{
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}}
QMenu::item:selected {{ background-color: {Theme.get('bg_overlay')}; }}
QMenu::separator {{
    height: 1px;
    background-color: {Theme.get('bg_overlay')};
    margin: 4px 8px;
}}

/* ══════════════════════════════════════════════════════
   MESSAGE BOX
══════════════════════════════════════════════════════ */
QMessageBox {{
    background-color: {Theme.get('bg_base')};
    color: {Theme.get('text_primary')};
}}
QMessageBox QPushButton {{
    min-width: 80px;
    min-height: 32px;
    border-radius: 6px;
    padding: 4px 16px;
    background-color: {Theme.get('bg_surface')};
    color: {Theme.get('text_primary')};
    border: 1px solid {Theme.get('bg_overlay')};
}}
QMessageBox QPushButton:hover {{ background-color: {Theme.get('bg_overlay')}; }}
"""
