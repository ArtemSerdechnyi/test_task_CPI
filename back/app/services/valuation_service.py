import math
from decimal import Decimal, getcontext, ROUND_HALF_UP

from back.app.core.constants import CPI_BASE_OCT_2001
from back.app.schemas.valuation import (
    ValuationInput,
    CpiData,
    ValuationResult,
    ManagementCosts,
    PropertyType,
)

getcontext().prec = 28


class ValuationService:
    CPI_BASE_OCT_2001 = Decimal(str(CPI_BASE_OCT_2001))
    MONTHS_IN_YEAR = Decimal("12")

    # RESIDENTIAL CONSTANTS
    RES_ADMIN_BASE_RATE_PER_UNIT = Decimal("270.0")
    RES_MAINTENANCE_BASE_RATE = Decimal("7.5")
    RES_RENT_LOSS_PERCENT = Decimal("0.015")

    # COMMERCIAL CONSTANTS
    COM_ADMIN_PERCENT = Decimal("0.03")
    COM_MAINTENANCE_BASE_RATE = Decimal("9.00")
    COM_RENT_LOSS_PERCENT = Decimal("0.04")

    MAINTENANCE_RATE_DECIMALS = Decimal("0.1")
    EURO = Decimal("1")

    def calculate_valuation(
        self, input_data: ValuationInput, cpi_data: CpiData
    ) -> ValuationResult:
        land_value = self._calculate_land_value(
            Decimal(str(input_data.land_value_per_sqm)),
            Decimal(str(input_data.plot_area)),
        )

        annual_gross_income = self._calculate_annual_gross_income(
            Decimal(str(input_data.monthly_net_rent))
        )

        index_factor = self._calculate_index_factor(Decimal(str(cpi_data.index_value)))

        management_costs = self._calculate_management_costs(
            input_data, index_factor, annual_gross_income
        )

        annual_net_income = annual_gross_income - management_costs.total

        land_interest = land_value * (
            Decimal(str(input_data.property_yield)) / Decimal("100")
        )

        building_net_income = annual_net_income - land_interest

        multiplier = self._calculate_multiplier(
            Decimal(str(input_data.property_yield)),
            Decimal(str(input_data.remaining_useful_life)),
        )

        theoretical_building_value = building_net_income * multiplier
        theoretical_total_value = theoretical_building_value + land_value

        building_share_percent = (
            theoretical_building_value / theoretical_total_value * Decimal("100")
        )

        land_share_percent = land_value / theoretical_total_value * Decimal("100")

        actual_building_value = None
        actual_land_value = None

        if input_data.actual_purchase_price:
            price = Decimal(str(input_data.actual_purchase_price))
            actual_building_value = price * building_share_percent / Decimal("100")
            actual_land_value = price * land_share_percent / Decimal("100")

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
            multiplier=multiplier,
            theoretical_building_value=self._round_euro(theoretical_building_value),
            theoretical_total_value=self._round_euro(theoretical_total_value),
            building_share_percent=building_share_percent.quantize(Decimal("0.01")),
            land_share_percent=land_share_percent.quantize(Decimal("0.01")),
            actual_building_value=self._round_euro(actual_building_value),
            actual_land_value=self._round_euro(actual_land_value),
        )

    @staticmethod
    def _calculate_land_value(
        land_value_per_sqm: Decimal, plot_area: Decimal
    ) -> Decimal:
        return land_value_per_sqm * plot_area

    def _calculate_annual_gross_income(self, monthly_net_rent: Decimal) -> Decimal:
        return monthly_net_rent * self.MONTHS_IN_YEAR

    def _calculate_index_factor(self, current_cpi: Decimal) -> Decimal:
        return current_cpi / self.CPI_BASE_OCT_2001

    def _calculate_management_costs(
        self,
        input_data: ValuationInput,
        index_factor: Decimal,
        annual_gross_income: Decimal,
    ) -> ManagementCosts:
        if input_data.property_type == PropertyType.RESIDENTIAL:
            return self._calculate_residential_costs(
                input_data, index_factor, annual_gross_income
            )
        return self._calculate_commercial_costs(
            input_data, index_factor, annual_gross_income
        )

    def _calculate_residential_costs(
        self,
        input_data: ValuationInput,
        index_factor: Decimal,
        annual_gross_income: Decimal,
    ) -> ManagementCosts:
        units = Decimal(str(input_data.residential_units or 0))

        if units > 0:
            administration = (
                (Decimal("4.5") + Decimal("0.25") * units)
                * index_factor
                * units
                * self.MONTHS_IN_YEAR
            ).quantize(self.EURO, ROUND_HALF_UP)
        else:
            administration = Decimal("0")

        maintenance_per_sqm = (self.RES_MAINTENANCE_BASE_RATE * index_factor).quantize(
            self.MAINTENANCE_RATE_DECIMALS, ROUND_HALF_UP
        )

        maintenance = maintenance_per_sqm * Decimal(str(input_data.living_area))

        risk_of_rent_loss = annual_gross_income * self.RES_RENT_LOSS_PERCENT

        total = administration + maintenance + risk_of_rent_loss

        return ManagementCosts(
            administration=self._round_euro(administration),
            maintenance=self._round_euro(maintenance),
            risk_of_rent_loss=self._round_euro(risk_of_rent_loss),
            total=self._round_euro(total),
            risk_percentage=(
                risk_of_rent_loss / annual_gross_income * Decimal("100")
            ).quantize(Decimal("0.01")),
        )

    def _calculate_commercial_costs(
        self,
        input_data: ValuationInput,
        index_factor: Decimal,
        annual_gross_income: Decimal,
    ) -> ManagementCosts:
        administration = annual_gross_income * self.COM_ADMIN_PERCENT

        maintenance_per_sqm = (self.COM_MAINTENANCE_BASE_RATE * index_factor).quantize(
            self.MAINTENANCE_RATE_DECIMALS, ROUND_HALF_UP
        )

        maintenance = maintenance_per_sqm * Decimal(str(input_data.living_area))

        risk_of_rent_loss = annual_gross_income * self.COM_RENT_LOSS_PERCENT

        total = administration + maintenance + risk_of_rent_loss

        return ManagementCosts(
            administration=self._round_euro(administration),
            maintenance=self._round_euro(maintenance),
            risk_of_rent_loss=self._round_euro(risk_of_rent_loss),
            total=self._round_euro(total),
            risk_percentage=(
                risk_of_rent_loss / annual_gross_income * Decimal("100")
            ).quantize(Decimal("0.01")),
        )

    def _calculate_multiplier(
        self, property_yield: Decimal, remaining_useful_life: Decimal
    ) -> Decimal:
        i = float(property_yield / Decimal("100"))
        n = float(remaining_useful_life)

        if i == 0:
            return remaining_useful_life

        value = (1 - math.pow(1 + i, -n)) / i
        return Decimal(str(value))

    @staticmethod
    def _round_euro(value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        return value.quantize(Decimal("1"), ROUND_HALF_UP)
