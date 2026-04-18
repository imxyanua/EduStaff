# components/toast.py — InfoBar-based toast notifications

from qfluentwidgets import InfoBar, InfoBarPosition, FluentIcon as FIF
from PySide6.QtWidgets import QWidget


def _show(parent: QWidget, title: str, content: str,
          kind: str, duration: int = 3000):
    fn = {
        "success": InfoBar.success,
        "error":   InfoBar.error,
        "warning": InfoBar.warning,
        "info":    InfoBar.info,
    }.get(kind, InfoBar.info)
    fn(
        title=title,
        content=content,
        orient=__import__("PySide6.QtCore", fromlist=["Qt"]).Qt.Orientation.Horizontal,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=duration,
        parent=parent,
    )


def toast_success(parent: QWidget, content: str, title: str = "Thành công"):
    _show(parent, title, content, "success")


def toast_error(parent: QWidget, content: str, title: str = "Lỗi"):
    _show(parent, title, content, "error", duration=5000)


def toast_warning(parent: QWidget, content: str, title: str = "Cảnh báo"):
    _show(parent, title, content, "warning", duration=4000)


def toast_info(parent: QWidget, content: str, title: str = "Thông báo"):
    _show(parent, title, content, "info")
