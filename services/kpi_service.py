from typing import Optional, TypedDict, List, Dict, Any

from core.models.kpi import KPIDefinition, KPIResult
from core.models.filters import FilterContext
from core.services.time_service import TimeService

from dashboard_core.query_builder import SmartQueryBuilder
from dashboard_core.db_helper import execute_dynamic_query


# ---------------------------
# Tipos auxiliares
# ---------------------------

class KPIQueryBuild(TypedDict):
    query: str


class KPIService:
    def __init__(self) -> None:
        self.qb = SmartQueryBuilder()

    async def get_kpi(
        self,
        kpi_id: str,
        definition: KPIDefinition,
        filters: FilterContext
    ) -> KPIResult:
        filters.time = TimeService.resolve_filter(filters.time)

        if definition.type == "simple":
            value = await self._resolve_simple_kpi(definition, filters)
        elif definition.type == "derived":
            value = await self._resolve_derived_kpi(definition, filters)
        else:
            value = 0.0

        display = self._format_value(value, definition.format)

        return KPIResult(
            id=kpi_id,
            value=value,
            display_value=display
        )

    # ---------------------------
    # KPI SIMPLE
    # ---------------------------
    async def _resolve_simple_kpi(
        self,
        definition: KPIDefinition,
        filters: FilterContext
    ) -> float:
        recipe = definition.recipe
        if recipe is None:
            return 0.0

        build: Optional[KPIQueryBuild] = self.qb.build_kpi_query(
            table=recipe.table,
            column=recipe.column,
            aggregation=recipe.aggregation,
            filters=filters,
            time_modifier=recipe.time_modifier
        )

        if build is None:
            return 0.0

        query = build.get("query")
        if not query:
            return 0.0

        rows: List[Dict[str, Any]] = await execute_dynamic_query(query)
        if not rows:
            return 0.0

        value = next(iter(rows[0].values()), 0.0)
        return float(value or 0.0)

    # ---------------------------
    # KPI DERIVADO (placeholder)
    # ---------------------------
    async def _resolve_derived_kpi(
        self,
        definition: KPIDefinition,
        filters: FilterContext
    ) -> float:
        return 0.0

    # ---------------------------
    # Formato de salida
    # ---------------------------
    def _format_value(self, value: float, fmt: str) -> str:
        if fmt == "currency":
            return f"${value:,.0f}"
        if fmt == "percent":
            return f"{value:.1f}%"
        if fmt == "integer":
            return f"{int(value):,}"
        return f"{value:.2f}"
