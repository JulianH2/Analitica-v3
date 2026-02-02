from typing import Any

def safe_get(data: Any, path, default: Any = 0) -> Any:
    if not data:
        return default
    
    if isinstance(path, str):
        keys = path.split('.')
    elif isinstance(path, (list, tuple)):
        keys = path
    else:
        return default
    
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current

def format_value(val: float, prefix: str = "", format_type: str = "abbreviated") -> str:
    if val is None:
        return f"{prefix}---"
    
    if format_type == "full":
        return f"{prefix}{val:,.2f}"
    if format_type == "integer":
        return f"{prefix}{int(val):,}"
    if format_type == "percent":
        return f"{val:.1%}"
    if format_type == "currency":
        abs_val = abs(val)
        if abs_val >= 1_000_000_000:
            return f"{prefix}{val/1_000_000_000:,.1f}B"
        if abs_val >= 1_000_000:
            return f"{prefix}{val/1_000_000:,.1f}M"
        if abs_val >= 10_000:
            return f"{prefix}{val/1_000:,.1f}k"
        return f"{prefix}{val:,.0f}"
    
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{prefix}{val/1_000_000_000:,.2f}B"
    if abs_val >= 1_000_000:
        return f"{prefix}{val/1_000_000:,.2f}M"
    if abs_val >= 10_000:
        return f"{prefix}{val/1_000:,.1f}k"
    return f"{prefix}{val:,.2f}"