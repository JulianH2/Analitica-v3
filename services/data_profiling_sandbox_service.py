"""
Perfilado de datos en sandbox: estadísticas sobre resultados de queries ya ejecutadas.
No ejecuta código arbitrario ni recibe SQL; solo datos (list of dicts) del motor determinístico.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _safe_numeric(v: Any) -> Optional[float]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _safe_date(v: Any):
    """Retorna un comparable para fechas (string o número)."""
    if v is None:
        return None
    return v


def profile(rows: List[Dict[str, Any]], max_rows: int = 10000) -> Dict[str, Any]:
    """
    Calcula estadísticas y detecta problemas sobre los datos.
    Entrada: lista de dicts (resultado de una query del KPIDiagnosticEngine).
    Salida: resumen numérico, nulos, distribución, huecos temporales, flags.
    """
    if not rows:
        return {"row_count": 0, "columns": {}, "flags": ["sin_datos"], "temporal_gaps": []}
    sample = rows[:max_rows]
    col_names = set()
    for r in sample:
        if isinstance(r, dict):
            col_names.update(r.keys())
    columns: Dict[str, Dict[str, Any]] = {}
    for col in sorted(col_names):
        values = []
        nulls = 0
        for r in sample:
            if not isinstance(r, dict):
                continue
            v = r.get(col)
            if v is None or (isinstance(v, str) and v.strip() == ""):
                nulls += 1
            else:
                values.append(v)
        col_stats = {"count": len(values), "nulls": nulls, "null_pct": round(100.0 * nulls / len(sample), 2) if sample else 0}
        nums = [_safe_numeric(x) for x in values]
        nums = [x for x in nums if x is not None]
        if nums:
            col_stats["min"] = min(nums)
            col_stats["max"] = max(nums)
            col_stats["mean"] = round(sum(nums) / len(nums), 4)
            s = sorted(nums)
            n = len(s)
            col_stats["p50"] = s[n // 2] if n else None
            col_stats["p95"] = s[int(n * 0.95)] if n > 1 else s[0]
            if n >= 4:
                q1 = s[n // 4]
                q3 = s[(3 * n) // 4]
                iqr = q3 - q1
                col_stats["iqr"] = round(iqr, 4)
                col_stats["outlier_low"] = q1 - 1.5 * iqr
                col_stats["outlier_high"] = q3 + 1.5 * iqr
        columns[col] = col_stats

    flags: List[str] = []
    if sample and any(c.get("null_pct", 0) > 50 for c in columns.values()):
        flags.append("alta_proporcion_nulos")
    if sample and len(sample) < 5:
        flags.append("muestra_pequena")

    temporal_gaps: List[Dict[str, Any]] = []
    date_candidates = [c for c in col_names if "fecha" in c.lower() or "date" in c.lower() or "period" in c.lower()]
    if date_candidates and sample:
        period_col = date_candidates[0]
        periods = []
        for r in sample:
            if isinstance(r, dict):
                p = _safe_date(r.get(period_col))
                if p is not None:
                    periods.append(p)
        if len(periods) >= 2:
            try:
                sorted_periods = sorted(set(periods))
                for i in range(1, len(sorted_periods)):
                    diff = None
                    if isinstance(sorted_periods[0], (int, float)) and isinstance(sorted_periods[i], (int, float)):
                        diff = sorted_periods[i] - sorted_periods[i - 1]
                        if diff > 1:
                            temporal_gaps.append({
                                "from": sorted_periods[i - 1],
                                "to": sorted_periods[i],
                                "gap_size": diff,
                            })
            except Exception:
                pass

    if temporal_gaps:
        flags.append("huecos_temporales")

    return {
        "row_count": len(sample),
        "columns": columns,
        "flags": flags,
        "temporal_gaps": temporal_gaps,
    }
