# api/schedule_api.py — Teaching schedule CRUD endpoints

import api.client as client


def get_schedules(
    page: int = 1,
    size: int = 50,
    lecturer_id: int = None,
    day_of_week: str = "",
    semester: str = "",
    academic_year: str = "",
) -> dict:
    params: dict = {"page": page, "size": size}
    if lecturer_id:   params["lecturer_id"]  = lecturer_id
    if day_of_week:   params["day_of_week"]  = day_of_week
    if semester:      params["semester"]     = semester
    if academic_year: params["academic_year"] = academic_year
    return client.get("/schedules", params=params)


def get_schedule(schedule_id: int) -> dict:
    return client.get(f"/schedules/{schedule_id}")


def create_schedule(data: dict) -> dict:
    return client.post("/schedules", json=data)


def update_schedule(schedule_id: int, data: dict) -> dict:
    return client.put(f"/schedules/{schedule_id}", json=data)


def delete_schedule(schedule_id: int):
    return client.delete(f"/schedules/{schedule_id}")
