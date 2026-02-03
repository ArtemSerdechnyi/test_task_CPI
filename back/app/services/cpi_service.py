from back.app.schemas.cpi import CpiPeriod
from back.app.services.cpi_parser import germany_historical_cpi_parser


class CPIService:
    cpi_mapper = germany_historical_cpi_parser.cpi_data

    def get_cpi(self, year: int, month: int) -> str | None:
        """Получить CPI по году и месяцу."""
        key = CpiPeriod(year=year, month=month)
        return self.cpi_mapper.get(key)
