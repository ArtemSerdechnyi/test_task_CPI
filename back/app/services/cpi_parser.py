import pandas as pd
import requests
from bs4 import BeautifulSoup

from back.app.schemas.cpi import CpiPeriod

__all__ = ["germany_historical_cpi_parser"]

class GermanyHistoricalCpiParser:
    cpi_data: dict[CpiPeriod, str] = {}

    def __init__(self):
        self.url = "https://www.rateinflation.com/consumer-price-index/germany-historical-cpi/"
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

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
        "dec": "12"
    }

    def parse_into_csv(self) -> dict[str, str]:
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table")
        if not table:
            return {"detail": "Data not found."}

        headers_row = [th.text.strip() for th in table.find("thead").find_all("th")]

        rows = []
        for tr in table.find("tbody").find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue

            year = cells[0].text.strip()

            for i in range(1, 13):
                month_name = self.months[headers_row[i]]
                value = cells[i].text.strip()

                if value:
                    rows.append({
                        "Date": f"{year}-{month_name}",
                        "CPI": value
                    })

        df = pd.DataFrame(rows)

        df.to_csv("germany_cpi_historical.csv", index=False, encoding="utf-8")
        return {"detail": "Data parsed successfully."}

    def parse_into_mapper(self) -> dict[str, str]:
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table")
        if not table:
            return {"detail": "Data not found."}

        headers_row = [th.text.strip().lower() for th in table.find("thead").find_all("th")]

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

    def get_cpi(self, year: int, month: int) -> str | None:
        """Получить CPI по году и месяцу."""
        key = CpiPeriod(year=year, month=month)
        return self.cpi_data.get(key)

germany_historical_cpi_parser = GermanyHistoricalCpiParser()
germany_historical_cpi_parser.parse_into_mapper()

