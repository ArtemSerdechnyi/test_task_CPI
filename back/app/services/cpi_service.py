from back.app.schemas.cpi import CpiPeriod
from back.app.services.cpi_parser_service import GermanyHistoricalCpiParser


class CpiService:
    def __init__(self, cpi_parser_service: GermanyHistoricalCpiParser):
        self._cpi_parser_service = cpi_parser_service

    def get_cpi_october_previous_year(self, year: int) -> float | None:
        key = CpiPeriod(year=year - 1, month=10)
        return self._cpi_parser_service.get_cpi_period_data(key)

    def get_cpi(self, year: int, month: int) -> float | None:
        key = CpiPeriod(year=year, month=month)
        return self._cpi_parser_service.get_cpi_period_data(key)
