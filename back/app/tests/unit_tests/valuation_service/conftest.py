import pytest
from decimal import Decimal

from back.app.services.valuation_service import ValuationService
from back.app.schemas.valuation import CpiData


@pytest.fixture
def valuation_service():
    return ValuationService()


@pytest.fixture
def cpi_data_high_inflation():
    return CpiData(year=2024, month=1, index_value=Decimal("130.0"), base_year=2020)


@pytest.fixture
def cpi_data_low_inflation():
    return CpiData(year=2024, month=1, index_value=Decimal("105.0"), base_year=2020)
