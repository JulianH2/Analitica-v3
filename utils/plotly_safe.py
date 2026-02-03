import math
from decimal import Decimal

def is_valid_number(v):
    if v is None:
        return False
    if isinstance(v, Decimal):
        v = float(v)
    return isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v)

def clean_series(categories, values):
    x_clean, y_clean = [], []
    
    limit = min(len(categories), len(values))
    
    for i in range(limit):
        c = categories[i]
        v = values[i]
        
        if is_valid_number(v):
            x_clean.append(c)
            y_clean.append(float(v) if isinstance(v, Decimal) else v)
            
    return x_clean, y_clean

def safe_max(*vals):
    valid_nums = []
    for v in vals:
        if is_valid_number(v):
            valid_nums.append(float(v) if isinstance(v, Decimal) else v)
    
    return max(valid_nums) if valid_nums else 0