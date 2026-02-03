import httpx
from bs4 import BeautifulSoup
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from back.app.core.config import settings
from back.app.schemas.cpi import CpiPeriod

__all__ = ["germany_historical_cpi_parser"]


class GermanyHistoricalCpiParser:
    cpi_data: dict[CpiPeriod, str] = {}

    def __init__(self):
        self.url = settings.CPI_SOURCE_URL
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    months = {
        "jan": "01",
        "feb": "02",
        "mar": "03",
        "apr": "04",
        "may": "05",
        "jun": "06",
        "jul": "07",
        "aug": "08",
        "sep": "09",
        "oct": "10",
        "nov": "11",
        "dec": "12",
    }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def _fetch_page(self) -> bytes:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(self.url)
            response.raise_for_status()
            return response.content

    async def parse_into_mapper(self) -> dict[str, str]:
        html = await self._fetch_page()

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table")
        if not table:
            return {"detail": "Data not found."}

        headers_row = [
            th.text.strip().lower() for th in table.find("thead").find_all("th")
        ]

        for tr in table.find("tbody").find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue

            year_str = cells[0].text.strip()
            if not year_str.isdigit():
                continue
            year = int(year_str)

            for i in range(1, 13):
                month_name = headers_row[i]
                month_num = self.months.get(month_name.lower())
                value = cells[i].text.strip()

                if month_num and value:
                    key = CpiPeriod(year=year, month=month_num)
                    self.cpi_data[key] = value

        return {"detail": "Data parsed into mapper successfully."}


germany_historical_cpi_parser = GermanyHistoricalCpiParser()
