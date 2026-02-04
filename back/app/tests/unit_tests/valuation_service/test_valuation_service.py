from decimal import Decimal

from back.app.schemas.valuation import PropertyType, ValuationInput, ManagementCosts
from datetime import date


class TestValuationServiceCalculations:
    def test_calculate_land_value(self, valuation_service):
        land_value_per_sqm = Decimal("500.00")
        plot_area = Decimal("400.0")

        result = valuation_service._calculate_land_value(land_value_per_sqm, plot_area)

        assert result == Decimal("200000.0")

    def test_calculate_annual_gross_income(self, valuation_service):
        monthly_net_rent = Decimal("2000.00")

        result = valuation_service._calculate_annual_gross_income(monthly_net_rent)

        assert result == Decimal("24000.00")

    def test_calculate_index_factor(self, valuation_service):
        current_cpi = Decimal("120.5")

        result = valuation_service._calculate_index_factor(current_cpi)

        expected = Decimal("120.5") / valuation_service.CPI_BASE_OCT_2001
        assert abs(result - expected) < Decimal("0.0001")

    def test_calculate_multiplier_normal_yield(self, valuation_service):
        property_yield = Decimal("5.0")
        remaining_useful_life = Decimal("50.0")

        result = valuation_service._calculate_multiplier(
            property_yield, remaining_useful_life
        )

        assert result > Decimal("0")
        assert result < remaining_useful_life

    def test_calculate_multiplier_zero_yield(self, valuation_service):
        property_yield = Decimal("0")
        remaining_useful_life = Decimal("50.0")

        result = valuation_service._calculate_multiplier(
            property_yield, remaining_useful_life
        )

        assert result == remaining_useful_life

    def test_calculate_multiplier_high_yield(self, valuation_service):
        property_yield = Decimal("10.0")
        remaining_useful_life = Decimal("30.0")

        result = valuation_service._calculate_multiplier(
            property_yield, remaining_useful_life
        )

        assert result > Decimal("0")
        assert result < Decimal("20")


class TestResidentialManagementCosts:
    def test_residential_costs_with_units(
        self, valuation_service, sample_residential_input, sample_cpi_data
    ):
        index_factor = valuation_service._calculate_index_factor(
            sample_cpi_data.index_value
        )
        annual_gross_income = Decimal("24000.00")

        result = valuation_service._calculate_residential_costs(
            sample_residential_input, index_factor, annual_gross_income
        )

        assert isinstance(result, ManagementCosts)
        assert result.administration > Decimal("0")
        assert result.maintenance > Decimal("0")
        assert result.risk_of_rent_loss > Decimal("0")
        assert result.total == (
            result.administration + result.maintenance + result.risk_of_rent_loss
        )
        assert result.risk_percentage == Decimal("1.50")

    def test_residential_costs_without_units(self, valuation_service, sample_cpi_data):
        input_data = ValuationInput(
            property_type=PropertyType.RESIDENTIAL,
            purchase_date=date(2024, 1, 15),
            monthly_net_rent=Decimal("2000.00"),
            living_area=Decimal("150.0"),
            residential_units=None,  # No units specified
            parking_units=Decimal("0"),
            land_value_per_sqm=Decimal("500.00"),
            plot_area=Decimal("400.0"),
            remaining_useful_life=Decimal("50.0"),
            property_yield=Decimal("5.0"),
        )
        index_factor = valuation_service._calculate_index_factor(
            sample_cpi_data.index_value
        )
        annual_gross_income = Decimal("24000.00")

        result = valuation_service._calculate_residential_costs(
            input_data, index_factor, annual_gross_income
        )

        assert result.administration == Decimal("0")
        assert result.maintenance > Decimal("0")

    def test_residential_maintenance_scales_with_area(
        self, valuation_service, sample_cpi_data
    ):
        input_data_small = ValuationInput(
            property_type=PropertyType.RESIDENTIAL,
            purchase_date=date(2024, 1, 15),
            monthly_net_rent=Decimal("1000.00"),
            living_area=Decimal("50.0"),
            residential_units=Decimal("1"),
            parking_units=Decimal("0"),
            land_value_per_sqm=Decimal("500.00"),
            plot_area=Decimal("200.0"),
            remaining_useful_life=Decimal("50.0"),
            property_yield=Decimal("5.0"),
        )

        input_data_large = ValuationInput(
            property_type=PropertyType.RESIDENTIAL,
            purchase_date=date(2024, 1, 15),
            monthly_net_rent=Decimal("2000.00"),
            living_area=Decimal("200.0"),
            residential_units=Decimal("2"),
            parking_units=Decimal("0"),
            land_value_per_sqm=Decimal("500.00"),
            plot_area=Decimal("400.0"),
            remaining_useful_life=Decimal("50.0"),
            property_yield=Decimal("5.0"),
        )

        index_factor = valuation_service._calculate_index_factor(
            sample_cpi_data.index_value
        )

        costs_small = valuation_service._calculate_residential_costs(
            input_data_small, index_factor, Decimal("12000.00")
        )
        costs_large = valuation_service._calculate_residential_costs(
            input_data_large, index_factor, Decimal("24000.00")
        )

        assert costs_large.maintenance > costs_small.maintenance


class TestCommercialManagementCosts:
    def test_commercial_costs_calculation(
        self, valuation_service, sample_commercial_input, sample_cpi_data
    ):
        index_factor = valuation_service._calculate_index_factor(
            sample_cpi_data.index_value
        )
        annual_gross_income = Decimal("60000.00")

        result = valuation_service._calculate_commercial_costs(
            sample_commercial_input, index_factor, annual_gross_income
        )

        assert isinstance(result, ManagementCosts)
        assert result.administration == annual_gross_income * Decimal("0.03")
        assert result.maintenance > Decimal("0")
        assert result.risk_of_rent_loss > Decimal("0")
        assert result.total == (
            result.administration + result.maintenance + result.risk_of_rent_loss
        )
        assert result.risk_percentage == Decimal(
            "4.00"
        )  # COM_RENT_LOSS_PERCENT is 0.04

    def test_commercial_admin_percentage_based(
        self, valuation_service, sample_commercial_input, sample_cpi_data
    ):
        index_factor = valuation_service._calculate_index_factor(
            sample_cpi_data.index_value
        )
        annual_gross_income = Decimal("100000.00")

        result = valuation_service._calculate_commercial_costs(
            sample_commercial_input, index_factor, annual_gross_income
        )

        expected_admin = annual_gross_income * Decimal("0.03")
        assert result.administration == expected_admin


class TestFullValuationCalculation:
    def test_residential_valuation_complete(
        self, valuation_service, sample_residential_input, sample_cpi_data
    ):
        result = valuation_service.calculate_valuation(
            sample_residential_input, sample_cpi_data
        )

        assert result.input_data == sample_residential_input
        assert result.cpi_used == sample_cpi_data
        assert result.annual_gross_income == Decimal("24000")
        assert result.land_value == Decimal("200000")
        assert result.theoretical_total_value > Decimal("0")
        assert result.actual_building_value is not None
        assert result.actual_land_value is not None

        total_percent = result.building_share_percent + result.land_share_percent
        assert abs(total_percent - Decimal("100.00")) < Decimal("0.01")

        if result.actual_building_value and result.actual_land_value:
            total_actual = result.actual_building_value + result.actual_land_value
            assert abs(
                total_actual - sample_residential_input.actual_purchase_price
            ) < Decimal("1")

    def test_commercial_valuation_complete(
        self, valuation_service, sample_commercial_input, sample_cpi_data
    ):
        result = valuation_service.calculate_valuation(
            sample_commercial_input, sample_cpi_data
        )

        assert result.input_data == sample_commercial_input
        assert result.cpi_used == sample_cpi_data
        assert result.annual_gross_income == Decimal("60000")
        assert result.land_value == Decimal("400000")
        assert result.theoretical_total_value > Decimal("0")
        assert result.management_costs.administration > Decimal("0")
        assert result.management_costs.maintenance > Decimal("0")
        assert result.management_costs.risk_percentage == Decimal("4.00")

    def test_valuation_without_actual_purchase_price(
        self, valuation_service, sample_cpi_data
    ):
        input_data = ValuationInput(
            property_type=PropertyType.RESIDENTIAL,
            purchase_date=date(2024, 1, 15),
            monthly_net_rent=Decimal("2000.00"),
            living_area=Decimal("150.0"),
            residential_units=Decimal("3"),
            parking_units=Decimal("2"),
            land_value_per_sqm=Decimal("500.00"),
            plot_area=Decimal("400.0"),
            remaining_useful_life=Decimal("50.0"),
            property_yield=Decimal("5.0"),
            actual_purchase_price=None,  # No actual price
        )

        result = valuation_service.calculate_valuation(input_data, sample_cpi_data)

        assert result.actual_building_value is None
        assert result.actual_land_value is None
        assert result.theoretical_total_value > Decimal("0")

    def test_valuation_with_high_inflation(
        self, valuation_service, sample_residential_input, cpi_data_high_inflation
    ):
        result = valuation_service.calculate_valuation(
            sample_residential_input, cpi_data_high_inflation
        )

        assert result.management_costs.total > Decimal("0")
        assert result.index_factor > Decimal("1.4")  # 130/88.9

    def test_valuation_rounding(
        self, valuation_service, sample_residential_input, sample_cpi_data
    ):
        result = valuation_service.calculate_valuation(
            sample_residential_input, sample_cpi_data
        )

        assert result.land_value % 1 == 0
        assert result.annual_net_income % 1 == 0
        assert result.land_interest % 1 == 0
        assert result.building_net_income % 1 == 0
        assert result.theoretical_building_value % 1 == 0
        assert result.theoretical_total_value % 1 == 0
        assert result.management_costs.administration % 1 == 0
        assert result.management_costs.maintenance % 1 == 0
        assert result.management_costs.risk_of_rent_loss % 1 == 0
        assert result.management_costs.total % 1 == 0


class TestEdgeCases:
    def test_minimal_property_values(self, valuation_service, sample_cpi_data):
        input_data = ValuationInput(
            property_type=PropertyType.RESIDENTIAL,
            purchase_date=date(2024, 1, 15),
            monthly_net_rent=Decimal("500.00"),
            living_area=Decimal("50.0"),
            land_value_per_sqm=Decimal("100.00"),
            plot_area=Decimal("200.0"),
            remaining_useful_life=Decimal("30.0"),
            property_yield=Decimal("0.04"),
        )

        result = valuation_service.calculate_valuation(input_data, sample_cpi_data)

        assert result.theoretical_total_value > Decimal("0")

    def test_very_high_property_yield(
        self, valuation_service, sample_residential_input, sample_cpi_data
    ):
        sample_residential_input.property_yield = Decimal("100.0")  # Max yield

        result = valuation_service.calculate_valuation(
            sample_residential_input, sample_cpi_data
        )

        assert result.theoretical_total_value > Decimal("0")
        assert result.multiplier > Decimal("0")

    def test_long_remaining_useful_life(
        self, valuation_service, sample_residential_input, sample_cpi_data
    ):
        sample_residential_input.remaining_useful_life = Decimal("100.0")

        result = valuation_service.calculate_valuation(
            sample_residential_input, sample_cpi_data
        )

        assert result.multiplier > Decimal("10")
        assert result.theoretical_building_value > Decimal("0")
