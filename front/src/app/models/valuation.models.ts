export type PropertyType = 'residential' | 'commercial';

export interface ValuationCalculateRequest {
  property_type: PropertyType;
  purchase_date: string;

  monthly_net_rent: number;
  living_area: number;

  residential_units?: number;
  parking_units: number;

  land_value_per_sqm: number;
  plot_area: number;
  remaining_useful_life: number;
  property_yield: number;
  actual_purchase_price: number;
}

export interface CpiUsedDto {
  year: number;
  month: number;
  index_value: number;
  base_year: number;
}

export interface ManagementCostsDto {
  administration: number;
  maintenance: number;
  risk_of_rent_loss: number;
  total: number;
}

export interface ValuationResponseDto {
  building_share_percent: number;
  land_share_percent: number;
  actual_building_value: number;
  actual_land_value: number;
  theoretical_building_value: number;
  theoretical_total_value: number;
  land_value: number;
  land_interest: number;
  annual_gross_income: number;
  annual_net_income: number;
  building_net_income: number;
  cpi_base_2001: number;
  cpi_used: CpiUsedDto;
  index_factor: number;
  management_costs: ManagementCostsDto;
  multiplier: number;
  insight_text?: string;
  input_data?: Record<string, unknown>;
}

export interface InsightResponseDto {
  insight_text: string;
}
