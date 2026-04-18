# api/account_api.py — User account management endpoints (Admin only)

import api.client as client


def get_accounts(search: str = "", role: str = "", is_active=None) -> list:
    params: dict = {}
    if search:             params["search"]    = search
    if role:               params["role"]      = role
    if is_active is not None: params["is_active"] = is_active
    result = client.get("/accounts", params=params)
    return result if isinstance(result, list) else result.get("items", [])


def get_account(account_id: int) -> dict:
    return client.get(f"/accounts/{account_id}")


def create_account(data: dict) -> dict:
    return client.post("/accounts", json=data)


def update_account(account_id: int, data: dict) -> dict:
    return client.put(f"/accounts/{account_id}", json=data)


def toggle_active(account_id: int) -> dict:
    return client.patch(f"/accounts/{account_id}/toggle-active")


def delete_account(account_id: int):
    return client.delete(f"/accounts/{account_id}")


def reset_password(account_id: int, new_password: str) -> dict:
    return client.post(f"/accounts/{account_id}/reset-password",
                       json={"new_password": new_password})
