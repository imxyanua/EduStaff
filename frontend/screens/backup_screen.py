# screens/backup_screen.py — Fluent backup & restore UI (Admin only)

import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QFileDialog, QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal

from qfluentwidgets import (
    PrimaryPushButton, PushButton, TransparentPushButton, ToolButton,
    ElevatedCardWidget, CardWidget,
    SubtitleLabel, BodyLabel, CaptionLabel, StrongBodyLabel,
    IndeterminateProgressBar, ProgressBar,
    MessageBox, LineEdit,
    FluentIcon as FIF,
    InfoBar, InfoBarPosition,
)

from components.cards import SectionHeader
from components.loading import LoadingOverlay
from components.toast import toast_success, toast_error
import api.stats_api as stats_api  # backup endpoints via stats_api or separate


# ── Workers ───────────────────────────────────────────────────────

class CreateBackupWorker(QThread):
    finished = Signal(bytes, str)   # (file_bytes, suggested_filename)
    error    = Signal(str)

    def run(self):
        try:
            import api.client as client
            data = client.get_file("/backup/create")
            ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.finished.emit(data, f"backup_{ts}.db")
        except Exception as e:
            self.error.emit(str(e))


class ListBackupsWorker(QThread):
    finished = Signal(list)
    error    = Signal(str)

    def run(self):
        try:
            import api.client as client
            result = client.get("/backup/list")
            self.finished.emit(result if isinstance(result, list) else [])
        except Exception as e:
            self.error.emit(str(e))


class RestoreBackupWorker(QThread):
    finished = Signal()
    error    = Signal(str)

    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def run(self):
        try:
            import api.client as client
            client.post("/backup/restore", {"filename": self.filename})
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


# ── Backup file card ──────────────────────────────────────────────

class BackupFileCard(CardWidget):
    """One row in the backup list — shows filename, size, date, restore/delete actions."""

    restore_requested = Signal(str)   # filename
    delete_requested  = Signal(str)   # filename

    def __init__(self, info: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("backupFileCard")
        self._filename = info.get("filename", "")
        self.setFixedHeight(68)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 0, 16, 0)
        root.setSpacing(12)

        # File icon
        icon_lbl = QLabel("💾")
        icon_lbl.setStyleSheet("font-size:22px; background:transparent;")
        root.addWidget(icon_lbl)

        # Info column
        info_v = QVBoxLayout()
        info_v.setSpacing(2)
        name_lbl = StrongBodyLabel(self._filename)
        name_lbl.setObjectName("backupFileName")

        size_str = self._human_size(info.get("size_bytes", 0))
        ts_str   = str(info.get("created_at", ""))[:16].replace("T", " ")
        meta_lbl = CaptionLabel(f"{size_str}  ·  {ts_str}")
        meta_lbl.setObjectName("backupFileMeta")

        info_v.addWidget(name_lbl)
        info_v.addWidget(meta_lbl)
        root.addLayout(info_v)
        root.addStretch()

        # Actions
        restore_btn = PrimaryPushButton(FIF.SYNC, "  Restore", self)
        restore_btn.setFixedHeight(32)
        restore_btn.clicked.connect(lambda: self.restore_requested.emit(self._filename))

        del_btn = ToolButton(FIF.DELETE, self)
        del_btn.setToolTip("Xóa bản backup này")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._filename))

        root.addWidget(restore_btn)
        root.addWidget(del_btn)

    @staticmethod
    def _human_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        if size < 1024 ** 2:
            return f"{size / 1024:.1f} KB"
        return f"{size / 1024 ** 2:.1f} MB"


# ── Restore confirm dialog ────────────────────────────────────────

class RestoreConfirmDialog(MessageBox):
    """
    Extra-safe confirm: user must type 'RESTORE' before the button activates.
    """

    def __init__(self, filename: str, parent=None):
        super().__init__(
            "⚠️  Xác nhận Restore",
            f"Thao tác này sẽ GHI ĐÈ TOÀN BỘ dữ liệu hiện tại bằng bản backup\n"
            f'"{filename}".\n\n'
            f'Nhập "RESTORE" để xác nhận:',
            parent,
        )
        self.yesButton.setText("Xác nhận Restore")
        self.yesButton.setEnabled(False)
        self.cancelButton.setText("Hủy")

        # Inject a LineEdit into the dialog content area
        self._confirm_input = LineEdit(self)
        self._confirm_input.setPlaceholderText("Nhập RESTORE")
        self._confirm_input.textChanged.connect(self._on_text_changed)
        self.textLayout.addWidget(self._confirm_input)

    def _on_text_changed(self, text: str):
        self.yesButton.setEnabled(text.strip() == "RESTORE")


# ── Screen ────────────────────────────────────────────────────────

class BackupScreen(QWidget):
    """Backup & Restore management screen (Admin only)."""

    def __init__(self, user_info: dict, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("BackupScreen")
        self.user_info = user_info
        self._backup_worker   = None
        self._list_worker     = None
        self._restore_worker  = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        layout.addWidget(
            SectionHeader(
                "Sao Lưu & Phục Hồi",
                "Tạo bản sao lưu database và khôi phục khi cần (Admin only)",
                icon="archive",
            )
        )

        # ── Create backup card ────────────────────────────────────
        create_card = ElevatedCardWidget()
        create_v = QVBoxLayout(create_card)
        create_v.setContentsMargins(24, 20, 24, 20)
        create_v.setSpacing(12)

        header_row = QHBoxLayout()
        icon_lbl = QLabel("💾")
        icon_lbl.setStyleSheet("font-size:28px; background:transparent;")
        title_v = QVBoxLayout()
        title_v.setSpacing(2)
        title_v.addWidget(SubtitleLabel("Tạo Backup Mới"))
        title_v.addWidget(CaptionLabel("Sao lưu toàn bộ database về file .db trên máy của bạn"))
        header_row.addWidget(icon_lbl)
        header_row.addSpacing(12)
        header_row.addLayout(title_v)
        header_row.addStretch()
        create_v.addLayout(header_row)

        # Progress bar (hidden initially)
        self._backup_bar = IndeterminateProgressBar(create_card)
        self._backup_bar.hide()
        create_v.addWidget(self._backup_bar)

        self._backup_btn = PrimaryPushButton(FIF.SAVE, "  Tạo Backup Ngay", create_card)
        self._backup_btn.setFixedHeight(40)
        self._backup_btn.clicked.connect(self._on_create_backup)
        create_v.addWidget(self._backup_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(create_card)

        # ── Backup list card ──────────────────────────────────────
        list_card = ElevatedCardWidget()
        list_v = QVBoxLayout(list_card)
        list_v.setContentsMargins(0, 0, 0, 0)
        list_v.setSpacing(0)

        list_header = QFrame()
        list_header.setObjectName("listHeaderPanel")
        lh_row = QHBoxLayout(list_header)
        lh_row.setContentsMargins(20, 14, 20, 14)
        lh_lbl = SubtitleLabel("Danh Sách Bản Sao Lưu")
        refresh_btn = TransparentPushButton(FIF.SYNC, "  Làm mới", list_header)
        refresh_btn.clicked.connect(self.refresh)
        lh_row.addWidget(lh_lbl)
        lh_row.addStretch()
        lh_row.addWidget(refresh_btn)
        list_v.addWidget(list_header)

        # List content
        self._list_content = QWidget()
        self._list_content.setStyleSheet("background:transparent;")
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(16, 12, 16, 12)
        self._list_layout.setSpacing(8)

        self._empty_lbl = BodyLabel("Chưa có bản sao lưu nào")
        self._empty_lbl.setStyleSheet("color:#484F58; padding:16px;")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._list_layout.addWidget(self._empty_lbl)

        list_v.addWidget(self._list_content)
        list_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(list_card, stretch=1)

        self._loading = LoadingOverlay(self)

    # ── Create backup ──────────────────────────────────────────────

    def _on_create_backup(self):
        self._backup_btn.setEnabled(False)
        self._backup_bar.show()
        self._backup_bar.start()
        self._backup_worker = CreateBackupWorker()
        self._backup_worker.finished.connect(self._on_backup_created)
        self._backup_worker.error.connect(self._on_backup_error)
        self._backup_worker.start()

    def _on_backup_created(self, data: bytes, suggested: str):
        self._backup_bar.stop()
        self._backup_bar.hide()
        self._backup_btn.setEnabled(True)

        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu file backup", suggested, "Database Files (*.db);;All Files (*)"
        )
        if path:
            with open(path, "wb") as f:
                f.write(data)
            toast_success(self.window(), f"Đã lưu backup: {os.path.basename(path)}")
        self.refresh()

    def _on_backup_error(self, msg: str):
        self._backup_bar.stop()
        self._backup_bar.hide()
        self._backup_btn.setEnabled(True)
        toast_error(self.window(), msg)

    # ── List backups ───────────────────────────────────────────────

    def refresh(self):
        self._loading.show()
        self._list_worker = ListBackupsWorker()
        self._list_worker.finished.connect(self._on_list_loaded)
        self._list_worker.error.connect(self._on_list_error)
        self._list_worker.start()

    def _on_list_loaded(self, items: list):
        self._loading.hide()
        # Clear existing cards
        while self._list_layout.count():
            it = self._list_layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()

        if not items:
            self._empty_lbl = BodyLabel("Chưa có bản sao lưu nào")
            self._empty_lbl.setStyleSheet("color:#484F58; padding:16px;")
            self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(self._empty_lbl)
            return

        for info in items:
            card = BackupFileCard(info, self._list_content)
            card.restore_requested.connect(self._on_restore_requested)
            card.delete_requested.connect(self._on_delete_backup)
            self._list_layout.addWidget(card)
        self._list_layout.addStretch()

    def _on_list_error(self, msg: str):
        self._loading.hide()
        # Non-fatal — list may be empty or endpoint not available
        while self._list_layout.count():
            it = self._list_layout.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        note = CaptionLabel(f"Không thể tải danh sách backup: {msg}")
        note.setStyleSheet("color:#484F58; padding:16px;")
        self._list_layout.addWidget(note)

    # ── Restore ────────────────────────────────────────────────────

    def _on_restore_requested(self, filename: str):
        dlg = RestoreConfirmDialog(filename, self)
        if dlg.exec():
            self._do_restore(filename)

    def _do_restore(self, filename: str):
        self._loading.show()
        self._restore_worker = RestoreBackupWorker(filename)
        self._restore_worker.finished.connect(self._on_restored)
        self._restore_worker.error.connect(self._on_restore_error)
        self._restore_worker.start()

    def _on_restored(self):
        self._loading.hide()
        InfoBar.success(
            "Restore thành công",
            "Dữ liệu đã được khôi phục. Vui lòng khởi động lại ứng dụng để áp dụng.",
            duration=6000,
            position=InfoBarPosition.TOP,
            parent=self.window(),
        )

    def _on_restore_error(self, msg: str):
        self._loading.hide()
        toast_error(self.window(), msg)

    # ── Delete backup ──────────────────────────────────────────────

    def _on_delete_backup(self, filename: str):
        from components.dialogs import confirm
        if confirm("Xóa backup", f'Xóa file "{filename}"?', self, "Xóa"):
            try:
                import api.client as client
                client.delete(f"/backup/{filename}")
                toast_success(self.window(), "Đã xóa bản backup!")
                self.refresh()
            except Exception as e:
                toast_error(self.window(), str(e))

    def resizeEvent(self, event):
        self._loading.resize(self.size())
        super().resizeEvent(event)
