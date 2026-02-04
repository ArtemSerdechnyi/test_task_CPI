## Backend

This backend acts as the core engine for the **KPA Tool**, handling real estate valuation logic, historical data parsing, and AI-driven analysis.

### Features

- **CPI Data Management**: 
  - Automated scraper for German historical Consumer Price Index (CPI) data starting from 2002.
  - Built-in retry logic to handle connection issues during data fetching.
  - Provides indexed inflation data required for accurate property valuation.
- **Valuation Engine**:
  - Implements the German Income Capitalization Method (*Ertragswertverfahren*).
  - Calculates management costs, maintenance reserves, and risk of rent loss based on property type.
  - Automatically splits the final valuation into land and building components.
- **AI Analysis**:
  - Integration with OpenAI to interpret valuation results.
  - Generates summaries regarding property yield, inflation impacts, and cost breakdowns.
- **API Infrastructure**:
  - Built with FastAPI for asynchronous performance.
  - Structured error handling for invalid dates or calculation errors.

### Workflow

1. **Data Parsing**: The system fetches and maps historical CPI data into a usable format.
2. **Calculation**: 
   - Receives user inputs (purchase date, rent, area, etc.).
   - Matches the purchase date with the corresponding CPI index.
   - Calculates the total theoretical value and cost breakdown.
3. **AI Insight**: Maps the calculation results into a prompt to generate a human-readable expert analysis.

### API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/cpi/{year}/{month}` | Returns the CPI value for a specific month/year. |
| `POST` | `/calculate` | Performs the property valuation calculation. |
| `POST` | `/calculate/analysis` | Generates an AI expert insight from valuation data. |

### Tech Stack

- **Framework**: FastAPI
- **Data Scraping**: BeautifulSoup4 & Httpx
- **AI**: OpenAI SDK
- **Task Resilience**: Tenacity (Retry library)

## How to Run the Project

Follow these steps to set up and run the project locally.

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create and fill the .env file
Create a .env file in the project root and add required environment variables. Example:
```bash
SERVER_PORT=
SERVER_HOST=
FRONTEND_URLS=
OPENAI_API_KEY=
```

### 4. Run application as module
```bash
python3 -m back.main
```