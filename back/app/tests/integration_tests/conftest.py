from datetime import date

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from decimal import Decimal

from back.app.services.llm_service import LLMService
from back.main import create_app
from back.app.schemas.valuation import ValuationInput, PropertyType
from back.app.services.cpi_service import CpiService
from back.app.services.valuation_service import ValuationService


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_cpi_service():
    service = Mock(spec=CpiService)

    service.get_cpi_october_previous_year = Mock(return_value=118.5)
    service.get_cpi = Mock(return_value=120.5)

    return service


@pytest.fixture
def valuation_input():
    return ValuationInput(
        property_type=PropertyType.COMMERCIAL,
        purchase_date=date(2022, 6, 1),
        monthly_net_rent=Decimal("2000"),
        living_area=Decimal("80"),
        residential_units=Decimal("1"),
        parking_units=Decimal("1"),
        land_value_per_sqm=Decimal("500"),
        plot_area=Decimal("600"),
        remaining_useful_life=Decimal("50"),
        property_yield=Decimal("5.5"),
        actual_purchase_price=Decimal("450000"),
    )


@pytest.fixture
def mock_valuation_service(valuation_input: ValuationInput):
    from back.app.schemas.valuation import (
        ValuationResult,
        ManagementCosts,
        CpiData,
    )

    service = Mock(spec=ValuationService)

    sample_result = ValuationResult(
        input_data=valuation_input,
        cpi_used=CpiData(
            year=2024, month=1, index_value=Decimal("120.5"), base_year=2020
        ),
        cpi_base_2001=Decimal("88.9"),
        index_factor=Decimal("1.355"),
        annual_gross_income=Decimal("24000"),
        land_value=Decimal("200000"),
        management_costs=ManagementCosts(
            administration=Decimal("500"),
            maintenance=Decimal("1500"),
            risk_of_rent_loss=Decimal("360"),
            total=Decimal("2360"),
            risk_percentage=Decimal("1.50"),
        ),
        annual_net_income=Decimal("21640"),
        land_interest=Decimal("10000"),
        building_net_income=Decimal("11640"),
        multiplier=Decimal("18.2559"),
        theoretical_building_value=Decimal("212499"),
        theoretical_total_value=Decimal("412499"),
        building_share_percent=Decimal("51.52"),
        land_share_percent=Decimal("48.48"),
        actual_building_value=Decimal("257600"),
        actual_land_value=Decimal("242400"),
    )

    service.calculate_valuation = Mock(return_value=sample_result)

    return service


@pytest.fixture
def override_cpi_dependency(mock_cpi_service):
    def _override():
        return mock_cpi_service

    return _override


@pytest.fixture
def override_valuation_dependency(mock_valuation_service):
    def _override():
        return mock_valuation_service

    return _override


@pytest.fixture
def mock_llm_service():
    service = Mock(spec=LLMService)

    async def mock_analysis(*args, **kwargs):
        return """
        Based on the valuation analysis:

        1. The theoretical value is €412,499
        2. The actual purchase price is €500,000
        3. Building share: 51.52%
        4. Land share: 48.48%

        The property appears to be slightly overvalued compared to the theoretical calculation.
        """

    service.get_llm_analysis = AsyncMock(side_effect=mock_analysis)

    return service


@pytest.fixture
def override_llm_dependency(mock_llm_service):
    def _override():
        return mock_llm_service

    return _override
