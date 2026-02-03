from datetime import date

# -----------------------------
# INPUTS
# -----------------------------
property_type = "Residential"  # "Residential" or "Commercial"
purchase_date = date(2023, 2, 1)  # YYYY, MM, DD
monthly_net_cold_rent = 1200      # € per month
usable_area_sqm = 100             # m²
num_residential_units = 2         # Only relevant for Residential
num_garage_units = 1
land_value_per_sqm = 500          # € per m²
plot_area_sqm = 300               # m²
remaining_useful_life = 50        # years (RND)
property_yield = 0.05             # Liegenschaftszins / Property Yield
actual_purchase_price = 400000    # €

# Optional CPI for index factor
CPI_base = 84.5
CPI_purchase = 120  # Example CPI at purchase date
index_factor = CPI_purchase / CPI_base

# -----------------------------
# STEP 1: Calculate Land Value
# -----------------------------
land_value = land_value_per_sqm * plot_area_sqm
land_value = round(land_value)  # Round to full €
print(f"Land Value: €{land_value}")

# -----------------------------
# STEP 2: Annual Gross Income
# -----------------------------
if property_type == "Residential":
    annual_gross_income = monthly_net_cold_rent * 12 * num_residential_units
else:
    annual_gross_income = monthly_net_cold_rent * 12  # Commercial
print(f"Annual Gross Income: €{annual_gross_income}")

# -----------------------------
# STEP 3: Management Costs
# -----------------------------
# Example rates (you can adjust)
administration_rate = 0.03  # 3%
maintenance_rate_per_sqm = 10  # € per m²
risk_rate = 0.02  # 2%

# Administration
administration_cost = annual_gross_income * administration_rate
administration_cost = round(administration_cost)
# Maintenance
maintenance_cost = round(maintenance_rate_per_sqm, 1) * usable_area_sqm * index_factor
maintenance_cost = round(maintenance_cost)
# Risk of Rent Loss
risk_cost = round(annual_gross_income * risk_rate)

# Total Deduction
total_deduction = administration_cost + maintenance_cost + risk_cost
print(f"Management Costs: Administration €{administration_cost}, Maintenance €{maintenance_cost}, Risk €{risk_cost}")
print(f"Total Deduction: €{total_deduction}")

# -----------------------------
# STEP 4: Annual Net Income
# -----------------------------
annual_net_income = annual_gross_income - total_deduction
print(f"Annual Net Income: €{annual_net_income}")

# -----------------------------
# STEP 5: Building Net Income
# -----------------------------
building_net_income = annual_net_income - (land_value * property_yield)
building_net_income = round(building_net_income)
print(f"Building Net Income: €{building_net_income}")

# -----------------------------
# STEP 6: Capitalize Building Value
# -----------------------------
building_value = building_net_income * remaining_useful_life
building_value = round(building_value)
print(f"Building Value: €{building_value}")

# -----------------------------
# STEP 7: Allocation
# -----------------------------
theoretical_total = building_value + land_value
building_share_pct = building_value / theoretical_total * 100
land_share_pct = land_value / theoretical_total * 100

building_portion_purchase_price = round(building_share_pct / 100 * actual_purchase_price)
land_portion_purchase_price = round(land_share_pct / 100 * actual_purchase_price)

print(f"\n--- Allocation ---")
print(f"Building Share: {building_share_pct:.2f}% → €{building_portion_purchase_price}")
print(f"Land Share: {land_share_pct:.2f}% → €{land_portion_purchase_price}")
