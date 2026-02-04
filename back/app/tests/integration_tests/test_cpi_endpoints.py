import pytest
from datetime import date
from unittest.mock import Mock


from back.app.api.dependencies import get_cpi_service, cpi_service_dep


class TestCpiEndpoints:
    def test_get_cpi_invalid_month_too_low(self, app, client):
        year = 2024
        month = 0

        response = client.get(f"/api/cpi/{year}/{month}")

        assert response.status_code == 400
        assert "month must be between 1 and 12" in response.json()["detail"]

    def test_get_cpi_invalid_month_too_high(self, client):
        year = 2024
        month = 13

        response = client.get(f"/api/cpi/{year}/{month}")

        assert response.status_code == 400
        assert "month must be between 1 and 12" in response.json()["detail"]

    def test_get_cpi_invalid_year_too_early(self, client):
        year = 2001
        month = 6

        response = client.get(f"/api/cpi/{year}/{month}")

        assert response.status_code == 400
        assert "year must be between 2002 and today" in response.json()["detail"]

    def test_get_cpi_invalid_year_future(self, client):
        year = date.today().year + 1
        month = 6

        response = client.get(f"/api/cpi/{year}/{month}")

        assert response.status_code == 400
        assert "year must be between 2002 and today" in response.json()["detail"]

    def test_get_cpi_not_found(self, app, client, override_cpi_dependency):
        mock_service = Mock()
        mock_service.get_cpi = Mock(return_value=None)

        def _override():
            return mock_service

        app.dependency_overrides[get_cpi_service] = _override

        year = 2024
        month = 12

        response = client.get(f"/api/cpi/{year}/{month}")

        assert response.status_code == 200
        assert response.json() is None

        app.dependency_overrides.clear()

    def test_get_cpi_valid_boundary_values(
        self, app, client, mock_cpi_service, override_cpi_dependency
    ):
        app.dependency_overrides[cpi_service_dep] = override_cpi_dependency

        test_cases = [
            (2024, 1),
            (2024, 12),
            (2002, 1),
            (date.today().year, 1),
        ]

        for year, month in test_cases:
            response = client.get(f"/api/cpi/{year}/{month}")
            assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_get_cpi_service_exception(self, app, client, override_cpi_dependency):
        mock_service = Mock()
        mock_service.get_cpi = Mock(side_effect=Exception("Database error"))

        def _override():
            return mock_service

        app.dependency_overrides[get_cpi_service] = _override

        response = client.get("/api/cpi/2024/1")

        assert response.status_code == 500
        assert "CPI" in response.json()["detail"]

        app.dependency_overrides.clear()
