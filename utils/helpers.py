from typing import Any

def safe_get(data: Any, path: str, default: Any = 0) -> Any:
    if not data or not path:
        return default
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current