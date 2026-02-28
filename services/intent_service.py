"""
Sistema de intenciones: clasifica la pregunta del usuario en intent y nivel de profundidad.
Intenciones: explain_value, compare_to_target, diagnose_drop, drilldown, trend_analysis.
"""
import re
from dataclasses import dataclass
from typing import Tuple

# Keywords por intención (español)
EXPLAIN_VALUE = "explain_value"
COMPARE_TO_TARGET = "compare_to_target"
DIAGNOSE_DROP = "diagnose_drop"
DRILLDOWN = "drilldown"
TREND_ANALYSIS = "trend_analysis"

PATTERNS = {
    EXPLAIN_VALUE: [
        r"c[oó]mo se calcula",
        r"qu[eé] es (este|el) (valor|kpi|indicador)",
        r"explica (el )?valor",
        r"qu[eé] significa",
        r"f[oó]rmula",
        r"c[oó]mo se obtiene",
    ],
    COMPARE_TO_TARGET: [
        r"meta",
        r"objetivo",
        r"comparar con",
        r"vs\s*meta",
        r"llegamos a la meta",
        r"cumplimos",
        r"no (se )?lleg[oó]",
    ],
    DIAGNOSE_DROP: [
        r"por qu[eé] (dio|da|baj[oó]| cay[oó])",
        r"por qu[eé] no",
        r"qu[eé] pas[oó]",
        r"diagn[oó]stico",
        r"ca[ií]da",
        r"baj[oó]",
        r"anomal[ií]a",
    ],
    DRILLDOWN: [
        r"detalle",
        r"desglose",
        r"por (qué|quien|cu[aá]l)",
        r"drilldown",
        r"tuplas",
        r"registros",
        r"lista (de|con)",
    ],
    TREND_ANALYSIS: [
        r"tendencia",
        r"evoluci[oó]n",
        r"serie (temporal|de tiempo)",
        r"mes a mes",
        r"hist[oó]rico",
        r"gr[aá]fica (de )?(l[ií]nea|tendencia)",
    ],
}


@dataclass
class IntentResult:
    intent: str
    depth: str  # summary | full | detail


def classify(question: str) -> IntentResult:
    """
    Clasifica la pregunta en intent y depth.
    Si no hay match, devuelve explain_value y full por defecto.
    """
    if not question or not isinstance(question, str):
        return IntentResult(intent=EXPLAIN_VALUE, depth="full")
    q = question.lower().strip()
    scores: dict = {}
    for intent, patterns in PATTERNS.items():
        score = 0
        for pat in patterns:
            if re.search(pat, q, re.IGNORECASE):
                score += 1
        if score > 0:
            scores[intent] = score
    if not scores:
        return IntentResult(intent=EXPLAIN_VALUE, depth="full")
    best_intent = max(scores.keys(), key=lambda k: scores[k])
    depth = "detail" if best_intent in (DRILLDOWN, DIAGNOSE_DROP) else ("full" if best_intent != EXPLAIN_VALUE else "full")
    return IntentResult(intent=best_intent, depth=depth)
