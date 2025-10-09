from typing import Any


def create_success_response(
    message: str, *, data: Any = None, **extra_fields: Any
) -> dict:
    """Consistent envelope for successful API responses."""
    payload: dict[str, Any] = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    if extra_fields:
        payload.update(extra_fields)
    return payload


def create_error_response(
    message: str,
    *,
    error_code: str | None = None,
    errors: Any = None,
    **extra_fields: Any,
) -> dict:
    """Consistent envelope for failed API responses."""
    payload: dict[str, Any] = {"success": False, "message": message}
    if error_code is not None:
        payload["error_code"] = error_code
    if errors is not None:
        payload["errors"] = errors
    if extra_fields:
        payload.update(extra_fields)
    return payload
