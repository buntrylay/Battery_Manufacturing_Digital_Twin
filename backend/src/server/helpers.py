def format_API_response(message: str, data: dict = None):
    return {
        "message": message,
        "data": data
    }