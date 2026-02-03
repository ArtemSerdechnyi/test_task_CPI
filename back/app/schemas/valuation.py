from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from typing import Optional


class PropertyType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"


class ValuationInput(BaseModel):
    property_type: PropertyType = Field(..., description="Тип недвижимости")
    purchase_date: date = Field(..., description="Дата покупки")
    monthly_net_rent: float = Field(..., gt=0, description="Месячная чистая арендная плата, €")
    living_area: float = Field(..., gt=0, description="Жилая/полезная площадь, м²")
    residential_units: Optional[int] = Field(None, ge=0, description="Количество жилых единиц (только для Residential)")
    parking_units: int = Field(0, ge=0, description="Количество гаражей/парковочных мест")
    land_value_per_sqm: float = Field(..., gt=0, description="Стандартная стоимость земли, €/м²")
    plot_area: float = Field(..., gt=0, description="Площадь участка, м²")
    remaining_useful_life: float = Field(..., gt=0, description="Остаточный срок службы, лет")
    property_yield: float = Field(..., gt=0, le=100, description="Доходность недвижимости, %")
    actual_purchase_price: Optional[float] = Field(None, gt=0, description="Фактическая цена покупки, €")


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
    # Входные данные
    input_data: ValuationInput

    # CPI данные
    cpi_used: CPIData
    cpi_base_2001: float = 84.5
    index_factor: float

    # Промежуточные расчеты
    annual_gross_income: float
    land_value: float
    management_costs: ManagementCosts
    annual_net_income: float
    land_interest: float
    building_net_income: float
    multiplier: float

    # Итоговые значения
    theoretical_building_value: float
    theoretical_total_value: float
    building_share_percent: float
    land_share_percent: float

    # Распределение по фактической цене (если указана)
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
