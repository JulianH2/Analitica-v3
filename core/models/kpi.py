from typing import Optional, Literal, Union
from pydantic import BaseModel, Field, ConfigDict

AggregationType = Literal["SUM", "COUNT", "AVG", "MAX", "MIN", "DISTINCT"]
MetricFormat = Literal["currency", "integer", "percent", "decimal", "text"]
TimeModifier = Literal["ytd", "previous_year", "mtd", "rolling_12"]

class KPIRecipe(BaseModel):
    table: str
    column: str
    aggregation: AggregationType = "SUM"
    time_modifier: Optional[TimeModifier] = None
    format: MetricFormat = "decimal"

class KPIDefinition(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    description: Optional[str] = None
    type: Literal["simple", "derived"] = "simple"
    format: MetricFormat = "decimal"
    
    recipe: Optional[KPIRecipe] = None
    
    formula: Optional[str] = None

class KPIResult(BaseModel):
    id: str
    value: float = 0.0
    target: Optional[float] = None
    delta: Optional[float] = None
    display_value: str = ""
    label: str = ""
    status: Optional[str] = None

class KPIContext(BaseModel):
    main_value: KPIResult
    secondary_value: Optional[KPIResult] = None
    comparison_label: Optional[str] = None