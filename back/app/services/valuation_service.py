import math

from back.app.core.constants import CPI_BASE_OCT_2001
from back.app.schemas.valuation import (
    ValuationInput,
    CPIData,
    ValuationResult,
    ManagementCosts,
    PropertyType,
)


class ValuationService:
    # CPI / INDEX
    CPI_BASE_OCT_2001 = CPI_BASE_OCT_2001
    MONTHS_IN_YEAR = 12

    # RESIDENTIAL CONSTANTS
    RES_ADMIN_BASE_RATE_PER_UNIT = 270.0  # € / unit
    RES_MAINTENANCE_BASE_RATE = 9.00  # € / m²
    RES_RENT_LOSS_PERCENT = 0.02  # 2%

    # COMMERCIAL CONSTANTS
    COM_ADMIN_PERCENT = 0.03  # 3%
    COM_MAINTENANCE_BASE_RATE = 9.00  # € / m²
    COM_RENT_LOSS_PERCENT = 0.04  # 4%

    # ROUNDING RULES
    MAINTENANCE_RATE_DECIMALS = 1
    ADMIN_RATE_DECIMALS = 0

    def calculate_valuation(
        self, input_data: ValuationInput, cpi_data: CPIData
    ) -> ValuationResult:
        land_value = self._calculate_land_value(
            input_data.land_value_per_sqm, input_data.plot_area
        )

        annual_gross_income = self._calculate_annual_gross_income(
            input_data.monthly_net_rent
        )

        index_factor = self._calculate_index_factor(cpi_data.index_value)

        management_costs = self._calculate_management_costs(
            input_data=input_data, index_factor=index_factor
        )

        annual_net_income = annual_gross_income - management_costs.total

        land_interest = land_value * (input_data.property_yield / 100)
        building_net_income = annual_net_income - land_interest

        multiplier = self._calculate_multiplier(
            input_data.property_yield, input_data.remaining_useful_life
        )

        theoretical_building_value = building_net_income * multiplier
        theoretical_total_value = theoretical_building_value + land_value

        building_share_percent = (
            theoretical_building_value / theoretical_total_value
        ) * 100
        land_share_percent = (land_value / theoretical_total_value) * 100

        actual_building_value = None
        actual_land_value = None

        if input_data.actual_purchase_price:
            actual_building_value = input_data.actual_purchase_price * (
                building_share_percent / 100
            )
            actual_land_value = input_data.actual_purchase_price * (
                land_share_percent / 100
            )

        return ValuationResult(
            input_data=input_data,
            cpi_used=cpi_data,
            cpi_base_2001=self.CPI_BASE_OCT_2001,
            index_factor=index_factor,
            annual_gross_income=annual_gross_income,
            land_value=self._round_euro(land_value),
            management_costs=management_costs,
            annual_net_income=self._round_euro(annual_net_income),
            land_interest=self._round_euro(land_interest),
            building_net_income=self._round_euro(building_net_income),
            multiplier=round(multiplier, 4),
            theoretical_building_value=self._round_euro(theoretical_building_value),
            theoretical_total_value=self._round_euro(theoretical_total_value),
            building_share_percent=round(building_share_percent, 2),
            land_share_percent=round(land_share_percent, 2),
            actual_building_value=self._round_euro(actual_building_value)
            if actual_building_value
            else None,
            actual_land_value=self._round_euro(actual_land_value)
            if actual_land_value
            else None,
        )

    def _calculate_land_value(
        self, land_value_per_sqm: float, plot_area: float
    ) -> float:
        return land_value_per_sqm * plot_area

    def _calculate_annual_gross_income(self, monthly_net_rent: float) -> float:
        return monthly_net_rent * self.MONTHS_IN_YEAR

    def _calculate_index_factor(self, current_cpi: float) -> float:
        return current_cpi / self.CPI_BASE_OCT_2001

    def _calculate_management_costs(
        self, input_data: ValuationInput, index_factor: float
    ) -> ManagementCosts:
        if input_data.property_type == PropertyType.RESIDENTIAL:
            return self._calculate_residential_costs(input_data, index_factor)
        return self._calculate_commercial_costs(input_data, index_factor)

    def _calculate_residential_costs(
        self, input_data: ValuationInput, index_factor: float
    ) -> ManagementCosts:
        # Verwaltungskosten
        if input_data.residential_units and input_data.residential_units > 0:
            admin_per_unit = round(
                self.RES_ADMIN_BASE_RATE_PER_UNIT * index_factor,
                self.ADMIN_RATE_DECIMALS,
            )
            administration = admin_per_unit * input_data.residential_units
        else:
            administration = 0

        # Instandhaltungskosten
        maintenance_per_sqm = round(
            self.RES_MAINTENANCE_BASE_RATE * index_factor,
            self.MAINTENANCE_RATE_DECIMALS,
        )
        maintenance = maintenance_per_sqm * input_data.living_area

        # Mietausfallwagnis
        annual_gross_income = self._calculate_annual_gross_income(
            input_data.monthly_net_rent
        )
        risk_of_rent_loss = annual_gross_income * self.RES_RENT_LOSS_PERCENT

        total = administration + maintenance + risk_of_rent_loss

        return ManagementCosts(
            administration=self._round_euro(administration),
            maintenance=self._round_euro(maintenance),
            risk_of_rent_loss=self._round_euro(risk_of_rent_loss),
            total=self._round_euro(total),
            risk_percentage=(risk_of_rent_loss / annual_gross_income) * 100,
        )

    def _calculate_commercial_costs(
        self, input_data: ValuationInput, index_factor: float
    ) -> ManagementCosts:
        annual_gross_income = self._calculate_annual_gross_income(
            input_data.monthly_net_rent
        )

        administration = annual_gross_income * self.COM_ADMIN_PERCENT

        maintenance_per_sqm = round(
            self.COM_MAINTENANCE_BASE_RATE * index_factor,
            self.MAINTENANCE_RATE_DECIMALS,
        )
        maintenance = maintenance_per_sqm * input_data.living_area

        risk_of_rent_loss = annual_gross_income * self.COM_RENT_LOSS_PERCENT

        total = administration + maintenance + risk_of_rent_loss

        return ManagementCosts(
            administration=self._round_euro(administration),
            maintenance=self._round_euro(maintenance),
            risk_of_rent_loss=self._round_euro(risk_of_rent_loss),
            risk_percentage=(risk_of_rent_loss / annual_gross_income) * 100,
            total=self._round_euro(total),
        )

    def _calculate_multiplier(
        self, property_yield: float, remaining_useful_life: float
    ) -> float:
        i = property_yield / 100
        n = remaining_useful_life

        if i == 0:
            return n

        multiplier = (1 - math.pow(1 + i, -n)) / i
        return multiplier

    @staticmethod
    def _round_euro(value: float) -> float | None:
        if value is None:
            return None
        return round(value)
