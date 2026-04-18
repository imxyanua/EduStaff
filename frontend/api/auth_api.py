# api/auth_api.py — Authentication endpoints

import api.client as client
from api.client import APIError


def login(username: str, password: str) -> dict:
    """POST /auth/token — returns token response dict."""
    resp = client.post("/auth/token", data={
        "username": username,
        "password": password,
        "grant_type": "password",
    })
    token = resp.get("access_token")
    if not token:
        raise APIError("Máy chủ không trả về token xác thực.")
    client.set_token(token)
    return resp


def get_me() -> dict:
    """GET /auth/me — returns current user info."""
    return client.get("/auth/me")


def logout():
    """Clear stored credentials."""
    client.clear_token()


def change_password(old_password: str, new_password: str) -> dict:
    return client.post("/auth/change-password", json={
        "old_password": old_password,
        "new_password": new_password,
    })
