"""
Unit tests for CpiService
"""
import pytest

from back.app.schemas.cpi import CpiPeriod


class TestCpiService:
    """Test suite for CpiService"""

    def test_get_cpi_october_previous_year_success(self, cpi_service):
        """Test getting CPI for October of previous year"""
        # Given
        year = 2024

        # When
        result = cpi_service.get_cpi_october_previous_year(year)

        # Then
        assert result == 118.5
        cpi_service._cpi_parser_service.get_cpi_period_data.assert_called_once_with(
            CpiPeriod(year=2023, month=10)
        )

    def test_get_cpi_october_previous_year_not_found(self, cpi_service_empty):
        """Test getting CPI when data doesn't exist"""
        # Given
        year = 2024

        # When
        result = cpi_service_empty.get_cpi_october_previous_year(year)

        # Then
        assert result is None

    def test_get_cpi_success(self, cpi_service):
        """Test getting CPI for specific year and month"""
        # Given
        year = 2024
        month = 1

        # When
        result = cpi_service.get_cpi(year, month)

        # Then
        assert result == 120.5
        cpi_service._cpi_parser_service.get_cpi_period_data.assert_called_once_with(
            CpiPeriod(year=2024, month=1)
        )

    def test_get_cpi_not_found(self, cpi_service):
        """Test getting CPI for non-existent period"""
        # Given
        year = 2025
        month = 12

        # When
        result = cpi_service.get_cpi(year, month)

        # Then
        assert result is None

    def test_get_cpi_multiple_calls(self, cpi_service):
        """Test multiple CPI requests"""
        # Given
        test_cases = [
            (2023, 10, 118.5),
            (2024, 1, 120.5),
            (2024, 6, 122.0),
        ]

        # When & Then
        for year, month, expected in test_cases:
            result = cpi_service.get_cpi(year, month)
            assert result == expected

    def test_get_cpi_boundary_months(self, cpi_service):
        """Test CPI retrieval for boundary month values"""
        # Test January (month 1)
        result_jan = cpi_service.get_cpi(2024, 1)
        assert result_jan == 120.5

        # Test October (month 10)
        result_oct = cpi_service.get_cpi(2023, 10)
        assert result_oct == 118.5