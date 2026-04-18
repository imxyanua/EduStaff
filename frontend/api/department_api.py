# api/department_api.py — Department CRUD endpoints

import api.client as client


def get_departments(page: int = 1, size: int = 50, search: str = "") -> dict:
    params: dict = {"page": page, "size": size}
    if search:
        params["search"] = search
    return client.get("/departments", params=params)


def get_department(dept_id: int) -> dict:
    return client.get(f"/departments/{dept_id}")


def create_department(data: dict) -> dict:
    return client.post("/departments", json=data)


def update_department(dept_id: int, data: dict) -> dict:
    return client.put(f"/departments/{dept_id}", json=data)


def delete_department(dept_id: int):
    return client.delete(f"/departments/{dept_id}")
