import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock

from back.app.schemas.cpi import CpiPeriod
from back.app.schemas.valuation import (
    PropertyType,
    ValuationInput,
    CpiData,
)


@pytest.fixture
def sample_cpi_period():
    return CpiPeriod(year=2023, month=10)


@pytest.fixture
def sample_cpi_data():
    return CpiData(year=2024, month=1, index_value=Decimal("120.5"), base_year=2020)


@pytest.fixture
def sample_residential_input():
    return ValuationInput(
        property_type=PropertyType.RESIDENTIAL,
        purchase_date=date(2024, 1, 15),
        monthly_net_rent=Decimal("2000.00"),
        living_area=Decimal("150.0"),
        residential_units=Decimal("3"),
        parking_units=Decimal("2"),
        land_value_per_sqm=Decimal("500.00"),
        plot_area=Decimal("400.0"),
        remaining_useful_life=Decimal("50.0"),
        property_yield=Decimal("5.0"),
        actual_purchase_price=Decimal("500000.00"),
    )


@pytest.fixture
def sample_commercial_input():
    return ValuationInput(
        property_type=PropertyType.COMMERCIAL,
        purchase_date=date(2024, 1, 15),
        monthly_net_rent=Decimal("5000.00"),
        living_area=Decimal("300.0"),
        residential_units=None,
        parking_units=Decimal("5"),
        land_value_per_sqm=Decimal("800.00"),
        plot_area=Decimal("500.0"),
        remaining_useful_life=Decimal("40.0"),
        property_yield=Decimal("6.0"),
        actual_purchase_price=Decimal("1000000.00"),
    )


@pytest.fixture
def mock_cpi_parser():
    parser = Mock()
    parser._cpi_data = {
        CpiPeriod(year=2023, month=10): 118.5,
        CpiPeriod(year=2022, month=10): 115.2,
        CpiPeriod(year=2024, month=1): 120.5,
        CpiPeriod(year=2024, month=6): 122.0,
    }
    parser.get_cpi_period_data = Mock(
        side_effect=lambda period: parser._cpi_data.get(period)
    )
    return parser


@pytest.fixture
def mock_httpx_response():
    mock_response = Mock()
    mock_response.content = b"""
    <html>
        <table>
            <thead>
                <tr>
                    <th>Year</th>
                    <th>Jan</th>
                    <th>Feb</th>
                    <th>Mar</th>
                    <th>Apr</th>
                    <th>May</th>
                    <th>Jun</th>
                    <th>Jul</th>
                    <th>Aug</th>
                    <th>Sep</th>
                    <th>Oct</th>
                    <th>Nov</th>
                    <th>Dec</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>2023</td>
                    <td>115.0</td>
                    <td>115.5</td>
                    <td>116.0</td>
                    <td>116.5</td>
                    <td>117.0</td>
                    <td>117.5</td>
                    <td>118.0</td>
                    <td>118.5</td>
                    <td>119.0</td>
                    <td>118.5</td>
                    <td>119.5</td>
                    <td>120.0</td>
                </tr>
                <tr>
                    <td>2024</td>
                    <td>120.5</td>
                    <td>121.0</td>
                    <td>121.5</td>
                    <td>122.0</td>
                    <td>122.5</td>
                    <td>122.0</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </html>
    """
    mock_response.raise_for_status = Mock()
    return mock_response
