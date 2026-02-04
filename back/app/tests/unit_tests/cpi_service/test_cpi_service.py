from back.app.schemas.cpi import CpiPeriod


class TestCpiService:
    def test_get_cpi_october_previous_year_success(self, cpi_service):
        year = 2024

        result = cpi_service.get_cpi_october_previous_year(year)

        assert result == 118.5
        cpi_service._cpi_parser_service.get_cpi_period_data.assert_called_once_with(
            CpiPeriod(year=2023, month=10)
        )

    def test_get_cpi_october_previous_year_not_found(self, cpi_service_empty):
        year = 2024

        result = cpi_service_empty.get_cpi_october_previous_year(year)

        assert result is None

    def test_get_cpi_success(self, cpi_service):
        year = 2024
        month = 1

        result = cpi_service.get_cpi(year, month)

        assert result == 120.5
        cpi_service._cpi_parser_service.get_cpi_period_data.assert_called_once_with(
            CpiPeriod(year=2024, month=1)
        )

    def test_get_cpi_not_found(self, cpi_service):
        year = 2025
        month = 12

        result = cpi_service.get_cpi(year, month)

        assert result is None

    def test_get_cpi_multiple_calls(self, cpi_service):
        test_cases = [
            (2023, 10, 118.5),
            (2024, 1, 120.5),
            (2024, 6, 122.0),
        ]

        for year, month, expected in test_cases:
            result = cpi_service.get_cpi(year, month)
            assert result == expected

    def test_get_cpi_boundary_months(self, cpi_service):
        # Test January (month 1)
        result_jan = cpi_service.get_cpi(2024, 1)
        assert result_jan == 120.5

        # Test October (month 10)
        result_oct = cpi_service.get_cpi(2023, 10)
        assert result_oct == 118.5
