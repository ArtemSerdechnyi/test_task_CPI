import pytest
from unittest.mock import Mock

from back.app.api.dependencies import (
    get_cpi_service,
    get_valuation_service,
    get_llm_service,
)


class TestValuationCalculateEndpoint:
    def test_calculate_valuation_residential_success(
        self,
        app,
        client,
        mock_cpi_service,
        mock_valuation_service,
        override_cpi_dependency,
        override_valuation_dependency,
    ):
        app.dependency_overrides[get_cpi_service] = override_cpi_dependency
        app.dependency_overrides[get_valuation_service] = override_valuation_dependency

        request_data = {
            "property_type": "residential",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": 2000.00,
            "living_area": 150.0,
            "residential_units": 3,
            "parking_units": 2,
            "land_value_per_sqm": 500.00,
            "plot_area": 400.0,
            "remaining_useful_life": 50.0,
            "property_yield": 5.0,
            "actual_purchase_price": 500000.00,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 200
        data = response.json()

        assert "theoretical_total_value" in data
        assert "building_share_percent" in data
        assert "land_share_percent" in data
        assert "management_costs" in data

        mock_cpi_service.get_cpi_october_previous_year.assert_called_once_with(
            year=2024
        )
        mock_valuation_service.calculate_valuation.assert_called_once()

        app.dependency_overrides.clear()

    def test_calculate_valuation_commercial_success(
        self,
        app,
        client,
        mock_cpi_service,
        mock_valuation_service,
        override_cpi_dependency,
        override_valuation_dependency,
    ):
        app.dependency_overrides[get_cpi_service] = override_cpi_dependency
        app.dependency_overrides[get_valuation_service] = override_valuation_dependency

        request_data = {
            "property_type": "commercial",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": 5000.00,
            "living_area": 300.0,
            "residential_units": None,
            "parking_units": 5,
            "land_value_per_sqm": 800.00,
            "plot_area": 500.0,
            "remaining_useful_life": 40.0,
            "property_yield": 6.0,
            "actual_purchase_price": 1000000.00,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 200
        mock_valuation_service.calculate_valuation.assert_called_once()

        app.dependency_overrides.clear()

    def test_calculate_valuation_without_actual_price(
        self,
        app,
        client,
        mock_cpi_service,
        mock_valuation_service,
        override_cpi_dependency,
        override_valuation_dependency,
    ):
        app.dependency_overrides[get_cpi_service] = override_cpi_dependency
        app.dependency_overrides[get_valuation_service] = override_valuation_dependency

        request_data = {
            "property_type": "residential",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": 2000.00,
            "living_area": 150.0,
            "residential_units": 3,
            "parking_units": 2,
            "land_value_per_sqm": 500.00,
            "plot_area": 400.0,
            "remaining_useful_life": 50.0,
            "property_yield": 5.0,
            "actual_purchase_price": None,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 200

        app.dependency_overrides.clear()

    def test_calculate_valuation_invalid_property_type(self, client):
        request_data = {
            "property_type": "invalid_type",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": 2000.00,
            "living_area": 150.0,
            "residential_units": 3,
            "parking_units": 2,
            "land_value_per_sqm": 500.00,
            "plot_area": 400.0,
            "remaining_useful_life": 50.0,
            "property_yield": 5.0,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 422

    def test_calculate_valuation_negative_rent(self, client):
        request_data = {
            "property_type": "residential",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": -2000.00,
            "living_area": 150.0,
            "residential_units": 3,
            "parking_units": 2,
            "land_value_per_sqm": 500.00,
            "plot_area": 400.0,
            "remaining_useful_life": 50.0,
            "property_yield": 5.0,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 422

    def test_calculate_valuation_invalid_yield(self, client):
        request_data = {
            "property_type": "residential",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": 2000.00,
            "living_area": 150.0,
            "residential_units": 3,
            "parking_units": 2,
            "land_value_per_sqm": 500.00,
            "plot_area": 400.0,
            "remaining_useful_life": 50.0,
            "property_yield": 150.0,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 422

    def test_calculate_valuation_service_exception(
        self, app, client, override_cpi_dependency, override_valuation_dependency
    ):
        mock_val_service = Mock()
        mock_val_service.calculate_valuation = Mock(
            side_effect=Exception("Calculation failed")
        )

        def _override_val():
            return mock_val_service

        app.dependency_overrides[get_cpi_service] = override_cpi_dependency
        app.dependency_overrides[get_valuation_service] = _override_val

        request_data = {
            "property_type": "residential",
            "purchase_date": "2024-01-15",
            "monthly_net_rent": 2000.00,
            "living_area": 150.0,
            "residential_units": 3,
            "parking_units": 2,
            "land_value_per_sqm": 500.00,
            "plot_area": 400.0,
            "remaining_useful_life": 50.0,
            "property_yield": 5.0,
        }

        response = client.post("/api/valuation/calculate", json=request_data)

        assert response.status_code == 500
        assert "Calculation error" in response.json()["detail"]

        app.dependency_overrides.clear()


class TestValuationAnalysisEndpoint:
    def test_ai_analysis_success(
        self,
        app,
        client,
        mock_llm_service,
        override_llm_dependency,
        sample_residential_input,
        sample_cpi_data,
    ):
        app.dependency_overrides[get_llm_service] = override_llm_dependency

        valuation_result = {
            "input_data": {
                "property_type": "residential",
                "purchase_date": "2024-01-15",
                "monthly_net_rent": 2000.00,
                "living_area": 150.0,
                "residential_units": 3,
                "parking_units": 2,
                "land_value_per_sqm": 500.00,
                "plot_area": 400.0,
                "remaining_useful_life": 50.0,
                "property_yield": 5.0,
                "actual_purchase_price": 500000.00,
            },
            "cpi_used": {
                "year": 2024,
                "month": 1,
                "index_value": 120.5,
                "base_year": 2020,
            },
            "cpi_base_2001": 88.9,
            "index_factor": 1.355,
            "annual_gross_income": 24000,
            "land_value": 200000,
            "management_costs": {
                "administration": 500,
                "maintenance": 1500,
                "risk_of_rent_loss": 360,
                "total": 2360,
                "risk_percentage": 1.50,
            },
            "annual_net_income": 21640,
            "land_interest": 10000,
            "building_net_income": 11640,
            "multiplier": 18.2559,
            "theoretical_building_value": 212499,
            "theoretical_total_value": 412499,
            "building_share_percent": 51.52,
            "land_share_percent": 48.48,
            "actual_building_value": 257600,
            "actual_land_value": 242400,
        }

        response = client.post(
            "/api/valuation/calculate/analysis", json=valuation_result
        )

        assert response.status_code == 200
        analysis = response.json()
        assert isinstance(analysis, str)
        assert len(analysis) > 0
        mock_llm_service.get_llm_analysis.assert_called_once()

        app.dependency_overrides.clear()

    def test_ai_analysis_llm_exception(self, app, client, override_llm_dependency):
        from unittest.mock import AsyncMock

        mock_service = Mock()
        mock_service.get_llm_analysis = AsyncMock(
            side_effect=Exception("LLM API error")
        )

        def _override():
            return mock_service

        app.dependency_overrides[get_llm_service] = _override

        valuation_result = {
            "input_data": {
                "property_type": "residential",
                "purchase_date": "2024-01-15",
                "monthly_net_rent": 2000.00,
                "living_area": 150.0,
                "residential_units": 3,
                "parking_units": 2,
                "land_value_per_sqm": 500.00,
                "plot_area": 400.0,
                "remaining_useful_life": 50.0,
                "property_yield": 5.0,
                "actual_purchase_price": 500000.00,
            },
            "cpi_used": {
                "year": 2024,
                "month": 1,
                "index_value": 120.5,
                "base_year": 2020,
            },
            "cpi_base_2001": 88.9,
            "index_factor": 1.355,
            "annual_gross_income": 24000,
            "land_value": 200000,
            "management_costs": {
                "administration": 500,
                "maintenance": 1500,
                "risk_of_rent_loss": 360,
                "total": 2360,
                "risk_percentage": 1.50,
            },
            "annual_net_income": 21640,
            "land_interest": 10000,
            "building_net_income": 11640,
            "multiplier": 18.2559,
            "theoretical_building_value": 212499,
            "theoretical_total_value": 412499,
            "building_share_percent": 51.52,
            "land_share_percent": 48.48,
            "actual_building_value": 257600,
            "actual_land_value": 242400,
        }

        response = client.post(
            "/api/valuation/calculate/analysis", json=valuation_result
        )

        assert response.status_code == 500
        assert "AI analysis error" in response.json()["detail"]

        app.dependency_overrides.clear()

    def test_ai_analysis_invalid_input(self, client):
        invalid_result = {"invalid_field": "invalid_value"}

        response = client.post("/api/valuation/calculate/analysis", json=invalid_result)

        assert response.status_code == 422
