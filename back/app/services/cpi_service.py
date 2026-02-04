from back.app.schemas.cpi import CpiPeriod


class CPIService:
    def __init__(self, cpi_mapper: dict[CpiPeriod, str]):
        self._cpi_mapper = cpi_mapper

    def get_cpi(self, year: int) -> str | None:
        key = CpiPeriod(year=year - 1, month=10)
        return self._cpi_mapper.get(key)
