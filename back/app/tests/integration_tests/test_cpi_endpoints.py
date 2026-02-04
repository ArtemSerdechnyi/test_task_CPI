"""
Integration tests for CPI endpoints
"""
import pytest
from datetime import date
from unittest.mock import Mock


from back.app.api.dependencies import get_cpi_service


class TestCpiEndpoints:
    """Integration tests for CPI API endpoints"""

    def test_get_cpi_success(self, client, mock_cpi_service, override_cpi_dependency):
        """Test successful CPI retrieval"""
        # Given
        from back import app
        app.dependency_overrides[get_cpi_service] = override_cpi_dependency

        year = 2024
        month = 1

        # When
        response = client.get(f"/api/cpi/{year}/{month}")

        # Then
        assert response.status_code == 200
        assert response.json() == 120.5
        mock_cpi_service.get_cpi.assert_called_once_with(year=year, month=month)

        # Cleanup
        app.dependency_overrides.clear()

    def test_get_cpi_invalid_month_too_low(self, client):
        """Test CPI endpoint with invalid month (too low)"""
        # Given
        year = 2024
        month = 0  # Invalid

        # When
        response = client.get(f"/api/cpi/{year}/{month}")

        # Then
        assert response.status_code == 400
        assert "month must be between 1 and 12" in response.json()["detail"]

    def test_get_cpi_invalid_month_too_high(self, client):
        """Test CPI endpoint with invalid month (too high)"""
        # Given
        year = 2024
        month = 13  # Invalid

        # When
        response = client.get(f"/api/cpi/{year}/{month}")

        # Then
        assert response.status_code == 400
        assert "month must be between 1 and 12" in response.json()["detail"]

    def test_get_cpi_invalid_year_too_early(self, client):
        """Test CPI endpoint with year before 2002"""
        # Given
        year = 2001  # Too early
        month = 6

        # When
        response = client.get(f"/api/cpi/{year}/{month}")

        # Then
        assert response.status_code == 400
        assert "year must be between 2002 and today" in response.json()["detail"]

    def test_get_cpi_invalid_year_future(self, client):
        """Test CPI endpoint with future year"""
        # Given
        year = date.today().year + 1  # Future year
        month = 6

        # When
        response = client.get(f"/api/cpi/{year}/{month}")

        # Then
        assert response.status_code == 400
        assert "year must be between 2002 and today" in response.json()["detail"]

    def test_get_cpi_not_found(self, client, override_cpi_dependency):
        """Test CPI endpoint when data not found"""
        # Given
        from back import app

        mock_service = Mock()
        mock_service.get_cpi = Mock(return_value=None)

        def _override():
            return mock_service

        app.dependency_overrides[get_cpi_service] = _override

        year = 2024
        month = 12

        # When
        response = client.get(f"/api/cpi/{year}/{month}")

        # Then
        assert response.status_code == 200
        assert response.json() is None

        # Cleanup
        app.dependency_overrides.clear()

    def test_get_cpi_valid_boundary_values(self, client, mock_cpi_service, override_cpi_dependency):
        """Test CPI endpoint with boundary valid values"""
        # Given
        from back import app
        app.dependency_overrides[get_cpi_service] = override_cpi_dependency

        test_cases = [
            (2024, 1),  # January
            (2024, 12),  # December
            (2002, 1),  # Earliest allowed year
            (date.today().year, 1),  # Current year
        ]

        for year, month in test_cases:
            # When
            response = client.get(f"/api/cpi/{year}/{month}")

            # Then
            assert response.status_code == 200

        # Cleanup
        app.dependency_overrides.clear()

    def test_get_cpi_service_exception(self, client, override_cpi_dependency):
        """Test CPI endpoint when service raises exception"""
        # Given
        from back import app

        mock_service = Mock()
        mock_service.get_cpi = Mock(side_effect=Exception("Database error"))

        def _override():
            return mock_service

        app.dependency_overrides[get_cpi_service] = _override

        # When
        response = client.get("/api/cpi/2024/1")

        # Then
        assert response.status_code == 500
        assert "CPI" in response.json()["detail"]

        # Cleanup
        app.dependency_overrides.clear()