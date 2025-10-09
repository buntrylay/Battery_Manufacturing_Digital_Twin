from typing import Any


def create_success_response(message: str, *, data: Any = None, **extra_fields: Any) -> dict:
    """Consistent envelope for successful API responses."""
    payload: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    if extra_fields:
        payload.update(extra_fields)
    return payload