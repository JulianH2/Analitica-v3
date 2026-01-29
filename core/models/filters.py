from typing import Optional, List, Dict, Any, Literal
from datetime import date
from pydantic import BaseModel, Field, ConfigDict

TimePeriod = Literal["custom", "ytd", "mtd", "rolling_12", "previous_year", "today"]

class DateFilter(BaseModel):
    model_config = ConfigDict(extra="ignore")

    start_date: Optional[date] = None
    end_date: Optional[date] = None
    year: Optional[int] = None
    month: Optional[int] = None
    period: TimePeriod = "ytd"

class FilterContext(BaseModel):
    model_config = ConfigDict(extra="ignore")

    time: DateFilter = Field(default_factory=DateFilter)

    banks: Optional[List[str]] = Field(default=None, description="IDs o nombres de bancos")
    routes: Optional[List[str]] = Field(default=None, description="IDs de rutas operativas")
    suppliers: Optional[List[str]] = Field(default=None, description="IDs de proveedores")
    cost_centers: Optional[List[str]] = Field(default=None, description="Centros de costos")
    
    extra_filters: Dict[str, List[Any]] = Field(default_factory=dict)

    def add_extra(self, column: str, values: List[Any]):
        self.extra_filters[column] = values