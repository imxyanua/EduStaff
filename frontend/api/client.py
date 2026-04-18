# api/client.py — HTTP client for EduStaff backend (FastAPI)

import requests
from typing import Any

BASE_URL = "http://localhost:8000"
_session = requests.Session()
_token: str | None = None


class APIError(Exception):
    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


def set_token(token: str):
    global _token
    _token = token
    _session.headers.update({"Authorization": f"Bearer {token}"})


def clear_token():
    global _token
    _token = None
    _session.headers.pop("Authorization", None)


def _handle(resp: requests.Response) -> Any:
    if resp.status_code == 401:
        raise APIError("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.", 401)
    if resp.status_code == 403:
        raise APIError("Bạn không có quyền thực hiện thao tác này.", 403)
    if resp.status_code == 404:
        raise APIError("Không tìm thấy tài nguyên.", 404)
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise APIError(str(detail), resp.status_code)
    if resp.status_code == 204 or not resp.content:
        return {}
    return resp.json()


def get(path: str, params: dict = None) -> Any:
    try:
        return _handle(_session.get(f"{BASE_URL}{path}", params=params, timeout=15))
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ. Kiểm tra kết nối mạng.")
    except requests.Timeout:
        raise ConnectionError("Máy chủ không phản hồi (timeout).")


def get_file(path: str) -> bytes:
    try:
        resp = _session.get(f"{BASE_URL}{path}", timeout=30)
        if not resp.ok:
            raise APIError(resp.text, resp.status_code)
        return resp.content
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ.")


def post(path: str, data: dict = None, json: dict = None) -> Any:
    try:
        return _handle(_session.post(f"{BASE_URL}{path}", data=data, json=json, timeout=15))
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ.")


def put(path: str, json: dict = None) -> Any:
    try:
        return _handle(_session.put(f"{BASE_URL}{path}", json=json, timeout=15))
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ.")


def patch(path: str, json: dict = None) -> Any:
    try:
        return _handle(_session.patch(f"{BASE_URL}{path}", json=json, timeout=15))
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ.")


def delete(path: str) -> Any:
    try:
        return _handle(_session.delete(f"{BASE_URL}{path}", timeout=15))
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ.")


def post_file(path: str, filename: str, file_bytes: bytes) -> Any:
    try:
        files = {"file": (filename, file_bytes, "application/octet-stream")}
        resp  = _session.post(f"{BASE_URL}{path}", files=files, timeout=60)
        return _handle(resp)
    except requests.ConnectionError:
        raise ConnectionError("Không thể kết nối đến máy chủ.")
