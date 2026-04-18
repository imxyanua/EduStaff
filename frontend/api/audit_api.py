# api/audit_api.py — Audit log read-only endpoints

import api.client as client


def get_audit_logs(
    page: int = 1,
    size: int = 30,
    action: str = "",
    entity_type: str = "",
    username: str = "",
    date_from: str = "",
    date_to: str = "",
) -> dict:
    params: dict = {"page": page, "size": size}
    if action:      params["action"]      = action
    if entity_type: params["entity_type"] = entity_type
    if username:    params["username"]    = username
    if date_from:   params["date_from"]   = date_from
    if date_to:     params["date_to"]     = date_to
    return client.get("/audit-logs", params=params)
