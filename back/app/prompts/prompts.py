SYSTEM_MESSAGE = (
    "You are an expert Real Estate AI Analyst specializing in the German 'Ertragswertverfahren' "
    "(Income Capitalization Approach). Your objective is to provide a professional, data-driven "
    "valuation summary. You must clearly explain how the specific property type and the "
    "German Consumer Price Index (CPI) influenced the calculation results."
)

AI_ANALYST_USER_TEMPLATE = """
Task: Analyze the following German Real Estate Valuation (Ertragswertverfahren) and provide professional insights.

Property Summary:
- Property Type: {property_type}
- Purchase Date: {purchase_date}
- Actual Purchase Price: €{actual_purchase_price:,.2f}

Valuation Results:
- Theoretical Total Value: €{theoretical_total_value:,.2f}
- Building Share: {building_share_percent:.1f}%
- Land Share: {land_share_percent:.1f}%

Management Costs Breakdown (Inflation Adjusted):
- Administration Costs: €{admin_costs:,.2f}
- Maintenance Costs: €{maintenance_costs:,.2f}
- Risk of Rent Loss: {risk_percentage}% (€{risk_amount:,.2f})

Inflation & Data Fetching:
- Fetched CPI (October prior year): {cpi_value}
- Base CPI (October 2001): {cpi_base_2001}
- Calculated Index Factor: {index_factor:.4f}

Instructions:
1. Return only the analysis itself, without any introductions or unrelated comments.
2. Contextualize the Logic: Explain how being a "{property_type}" property affected the management costs and risk loss deductions.
3. Explain Inflation: Explicitly mention that maintenance and admin costs were adjusted using the CPI index factor of {index_factor:.4f}.
4. Value Comparison: Compare the Theoretical Total Value (€{theoretical_total_value:,.2f}) with the Actual Purchase Price (€{actual_purchase_price:,.2f}). State if the property was purchased at a premium or a discount relative to its income-generating potential.

Tone: Professional, analytical, and concise.
Language: English.
"""
