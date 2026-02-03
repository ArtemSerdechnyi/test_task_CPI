from back.app.schemas.cpi import CpiPeriod
from back.app.services.cpi_parser import germany_historical_cpi_parser


class CPIService:
    def __init__(self, cpi_mapper: dict[CpiPeriod, str]):
        self._cpi_mapper = cpi_mapper

    def get_cpi(self, year: int, month: int) -> str | None:
        key = CpiPeriod(year=year, month=month)
        return self._cpi_mapper.get(key)
