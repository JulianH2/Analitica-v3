from typing import Any

def safe_get(data: Any, path: str, default: Any = 0) -> Any:
    if not data or not path: return default
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else: return default
    return current

def format_value(val: float, prefix: str = "", format_type: str = "abbreviated") -> str:
    if format_type == "full":
        return f"{prefix}{val:,.2f}"
    
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{prefix}{val/1_000_000_000:,.2f}B" 
    if abs_val >= 1_000_000:
        return f"{prefix}{val/1_000_000:,.2f}M"
    if abs_val >= 10_000:
        return f"{prefix}{val/1_000:,.1f}k"
    return f"{prefix}{val:,.2f}"