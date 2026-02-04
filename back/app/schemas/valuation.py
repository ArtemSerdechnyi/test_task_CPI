from decimal import Decimal

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
    monthly_net_rent: Decimal = Field(..., gt=0)
    living_area: Decimal = Field(..., gt=0)
    residential_units: Optional[Decimal] = Field(None, ge=0)
    parking_units: Decimal = Field(0, ge=0)
    land_value_per_sqm: Decimal = Field(..., gt=0)
    plot_area: Decimal = Field(..., gt=0)
    remaining_useful_life: Decimal = Field(..., gt=0)
    property_yield: Decimal = Field(..., gt=0, le=100)
    actual_purchase_price: Optional[Decimal] = Field(None, gt=0)


class CpiData(BaseModel):
    year: int
    month: int
    index_value: Decimal
    base_year: int = 2020


class ManagementCosts(BaseModel):
    administration: Decimal
    maintenance: Decimal
    risk_of_rent_loss: Decimal
    total: Decimal
    risk_percentage: Decimal


class ValuationResult(BaseModel):
    input_data: ValuationInput

    cpi_used: CpiData
    cpi_base_2001: Decimal = CPI_BASE_OCT_2001
    index_factor: Decimal

    annual_gross_income: Decimal
    land_value: Decimal
    management_costs: ManagementCosts
    annual_net_income: Decimal
    land_interest: Decimal
    building_net_income: Decimal
    multiplier: Decimal

    theoretical_building_value: Decimal
    theoretical_total_value: Decimal
    building_share_percent: Decimal
    land_share_percent: Decimal

    actual_building_value: Optional[Decimal] = None
    actual_land_value: Optional[Decimal] = None


class AIAnalysisRequest(BaseModel):
    valuation_result: ValuationResult


class AIAnalysisResponse(BaseModel):
    analysis: str
    key_points: list[str]


class AIPromptSchema(BaseModel):
    property_type: PropertyType
    purchase_date: str
    actual_purchase_price: Decimal
    theoretical_total_value: Decimal
    building_share_percent: Decimal
    land_share_percent: Decimal
    admin_costs: Decimal
    maintenance_costs: Decimal
    risk_percentage: Decimal
    risk_amount: Decimal
    index_factor: Decimal
    cpi_value: Decimal
    cpi_base_2001: Decimal
