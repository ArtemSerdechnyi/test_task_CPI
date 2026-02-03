import requests
from bs4 import BeautifulSoup
import pandas as pd

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

url = "https://www.rateinflation.com/consumer-price-index/germany-historical-cpi/"

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

table = soup.find("table")
if not table:
    print("Table not found.")
    exit()

headers_row = [th.text.strip() for th in table.find("thead").find_all("th")]

rows = []
for tr in table.find("tbody").find_all("tr"):
    cells = tr.find_all("td")
    if not cells:
        continue

    year = cells[0].text.strip()

    for i in range(1, 13):
        month_name = months[headers_row[i]]
        value = cells[i].text.strip()

        if value:
            rows.append({
                "Date": f"{year}-{month_name}",
                "CPI": value
            })

df = pd.DataFrame(rows)

df.to_csv("germany_cpi_historical.csv", index=False, encoding="utf-8")