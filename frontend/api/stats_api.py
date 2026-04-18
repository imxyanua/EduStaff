# api/stats_api.py — Statistics & dashboard endpoints

import api.client as client


def get_overview() -> dict:
    return client.get("/stats/overview")


def get_by_department() -> list:
    return client.get("/stats/by-department") or []


def get_by_degree() -> list:
    return client.get("/stats/by-degree") or []


def get_by_position() -> list:
    return client.get("/stats/by-position") or []
