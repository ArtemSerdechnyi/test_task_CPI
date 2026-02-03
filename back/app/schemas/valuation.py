from pydantic import BaseModel, Field
from datetime import date
from enum import StrEnum
from typing import Optional

from back.app.core.constants import CPI_BASE_OCT_2001


class PropertyType(StrEnum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class ValuationInput(BaseModel):
    property_type: PropertyType
    purchase_date: date
    monthly_net_rent: float = Field(..., gt=0)
    living_area: float = Field(..., gt=0)
    residential_units: Optional[int] = Field(None, ge=0)
    parking_units: int = Field(0, ge=0)
    land_value_per_sqm: float = Field(..., gt=0)
    plot_area: float = Field(..., gt=0)
    remaining_useful_life: float = Field(..., gt=0)
    property_yield: float = Field(..., gt=0, le=100)
    actual_purchase_price: Optional[float] = Field(None, gt=0)


class CPIData(BaseModel):
    year: int
    month: int
    index_value: float
    base_year: int = 2020


class ManagementCosts(BaseModel):
    administration: float
    maintenance: float
    risk_of_rent_loss: float
    total: float
    risk_percentage: float


class ValuationResult(BaseModel):
    input_data: ValuationInput

    cpi_used: CPIData
    cpi_base_2001: float = CPI_BASE_OCT_2001
    index_factor: float

    annual_gross_income: float
    land_value: float
    management_costs: ManagementCosts
    annual_net_income: float
    land_interest: float
    building_net_income: float
    multiplier: float

    theoretical_building_value: float
    theoretical_total_value: float
    building_share_percent: float
    land_share_percent: float

    actual_building_value: Optional[float] = None
    actual_land_value: Optional[float] = None


class AIAnalysisRequest(BaseModel):
    valuation_result: ValuationResult


class AIAnalysisResponse(BaseModel):
    analysis: str
    key_points: list[str]


class AIPromptSchema(BaseModel):
    property_type: PropertyType
    purchase_date: str
    actual_purchase_price: float
    theoretical_total_value: float
    building_share_percent: float
    land_share_percent: float
    admin_costs: float
    maintenance_costs: float
    risk_percentage: float
    risk_amount: float
    index_factor: float
    cpi_value: float
    cpi_base_2001: float
