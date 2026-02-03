## Frontend

This frontend provides the user interface for the **KPA Tool – Income Capitalization (Ertragswertverfahren)**.

### Features

- Valuation input form with a **Property Type selector**:
  - Residential (Wohnen)
  - Commercial (Gewerbe)
- Dynamic form behavior:
  - Residential Units field is only relevant for Residential properties
- User input fields:
  - Purchase Date
  - Monthly Net Cold Rent
  - Living / Usable Area
  - Number of Residential Units (Residential only)
  - Number of Parking Units
  - Standard Land Value (€/m²)
  - Plot Area (m²)
  - Remaining Useful Life (RND)
  - Property Yield (Liegenschaftszins)
  - Actual Purchase Price
- Result presentation:
  - Split of total value into Land and Building
  - Percentage allocation and Euro amounts based on the actual purchase price
  - Display of CPI data used for the calculation
  - Detailed management cost breakdown
- AI Analyst Insight:
  - After calculation, the user can request an AI-generated explanation
  - The analysis explains property type impact, CPI-based inflation adjustment, and value comparison

### User Flow

1. Enter valuation data and select property type
2. Submit the form to calculate the valuation
3. Review the calculated results
4. Optionally request an AI-generated analysis of the valuation
