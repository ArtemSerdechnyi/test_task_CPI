# 1. Use Web Scraping for Germany Historical CPI Data

Date: 2026-02-04

## Context
The application requires historical Consumer Price Index (CPI) data for Germany to support financial calculations. Specifically, the system needs to look up CPI values for specific months (e.g., October of the previous year) to adjust for inflation.

We evaluated two primary sources for this data:
1.  **Destatis GENESIS-Online API:** The official database of the Federal Statistical Office of Germany.
2.  **Rateinflation.com:** A third-party aggregator that presents historical CPI data in a static HTML table.

## Decision
We will fetch CPI data by **web scraping `rateinflation.com`** using an asynchronous Python client (`httpx` and `BeautifulSoup`).

We explicitly decided **against** using the official GENESIS API at this stage.

## Detailed Rationale

### 1. Source Selection: Rateinflation.com vs. GENESIS API
* **Availability:** During evaluation, the official GENESIS API was found to be frequently overloaded and unreliable for real-time requests.
* **Complexity:** The official API requires complex authentication and strict query parameters. The third-party source (`rateinflation.com`) provides the exact dataset required in a single, publicly accessible HTML page.
* **Stability:** The target page uses a standard HTML `<table>` structure that has proven stable for the scope of this project.

### 2. Technical Implementation
* **Library Choice:**
    * `httpx`: Chosen for its native `async` support to prevent blocking the main application thread during network I/O.
    * `BeautifulSoup4`: Used for parsing the HTML. The parsing logic targets the specific table structure (`thead` for months, `tbody` for year-rows).
    * `tenacity`: Implemented to handle transient network failures. We use an exponential backoff strategy (wait 2s-10s) with a limit of 3 attempts to ensure resilience.
* **Data Structure:** Data is parsed into a hash map (Dictionary) keyed by a custom `CpiPeriod` object (Year/Month). This allows for O(1) lookup times during calculation requests.

## Consequences

### Positive
* **Reliability:** We avoid the downtime and timeouts associated with the official government API.
* **Performance:** Once parsed, data is served from in-memory storage, resulting in zero latency for read operations.
* **Simplicity:** The implementation is lightweight (~60 lines of code) compared to a full SOAP/REST client required for GENESIS.

### Negative
* **Fragility:** The implementation is tightly coupled to the DOM structure of `rateinflation.com`. If they change their table layout or CSS selectors, the parser will break and require code changes.
* **Data Freshness:** We are dependent on the third party to update their website. There may be a lag between the official release of numbers and the update on the aggregator site.

## Mitigation Strategies
* **Logging:** The parser includes warning logs if the table is not found, alerting developers immediately if the scraping target changes.
* **Retries:** The `tenacity` decorator mitigates temporary site unavailability or connection resets.