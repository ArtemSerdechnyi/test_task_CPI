"""
Unit tests for ValuationService
"""
import pytest
from decimal import Decimal

from back.app.schemas.valuation import PropertyType, ValuationInput, ManagementCosts
from datetime import date


class TestValuationServiceCalculations:
    """Test suite for ValuationService calculation methods"""

    def test_calculate_land_value(self, valuation_service):
        """Test land value calculation"""
        # Given
        land_value_per_sqm = Decimal("500.00")
        plot_area = Decimal("400.0")

        # When
        result = valuation_service._calculate_land_value(land_value_per_sqm, plot_area)

        # Then
        assert result == Decimal("200000.0")

    def test_calculate_annual_gross_income(self, valuation_service):
        """Test annual gross income calculation"""
        # Given
        monthly_net_rent = Decimal("2000.00")

        # When
        result = valuation_service._calculate_annual_gross_income(monthly_net_rent)

        # Then
        assert result == Decimal("24000.00")

    def test_calculate_index_factor(self, valuation_service):
        """Test index factor calculation"""
        # Given
        current_cpi = Decimal("120.5")

        # When
        result = valuation_service._calculate_index_factor(current_cpi)

        # Then
        # CPI_BASE_OCT_2001 is 88.9
        expected = Decimal("120.5") / Decimal("88.9")
        assert abs(result - expected) < Decimal("0.0001")

    def test_calculate_multiplier_normal_yield(self, valuation_service):
        """Test multiplier calculation with normal property yield"""
        # Given
        property_yield = Decimal("5.0")
        remaining_useful_life = Decimal("50.0")

        # When
        result = valuation_service._calculate_multiplier(property_yield, remaining_useful_life)

        # Then
        assert result > Decimal("0")
        assert result < remaining_useful_life

    def test_calculate_multiplier_zero_yield(self, valuation_service):
        """Test multiplier calculation with zero yield (edge case)"""
        # Given
        property_yield = Decimal("0")
        remaining_useful_life = Decimal("50.0")

        # When
        result = valuation_service._calculate_multiplier(property_yield, remaining_useful_life)

        # Then
        assert result == remaining_useful_life

    def test_calculate_multiplier_high_yield(self, valuation_service):
        """Test multiplier with high property yield"""
        # Given
        property_yield = Decimal("10.0")
        remaining_useful_life = Decimal("30.0")

        # When
        result = valuation_service._calculate_multiplier(property_yield, remaining_useful_life)

        # Then
        assert result > Decimal("0")
        assert result < Decimal("20")  # Higher yield = lower multiplier


class TestResidentialManagementCosts:
    """Test suite for residential property management costs"""

    def test_residential_costs_with_units(self, valuation_service, sample_residential_input, sample_cpi_data):
        """Test residential management costs calculation with units"""
        # Given
        index_factor = valuation_service._calculate_index_factor(sample_cpi_data.index_value)
        annual_gross_income = Decimal("24000.00")

        # When
        result = valuation_service._calculate_residential_costs(
            sample_residential_input,
            index_factor,
            annual_gross_income
        )

        # Then
        assert isinstance(result, ManagementCosts)
        assert result.administration > Decimal("0")
        assert result.maintenance > Decimal("0")
        assert result.risk_of_rent_loss > Decimal("0")
        assert result.total == (
                result.administration + result.maintenance + result.risk_of_rent_loss
        )
        assert result.risk_percentage == Decimal("1.50")  # RES_RENT_LOSS_PERCENT is 0.015

    def test_residential_costs_without_units(self, valuation_service, sample_cpi_data):
        """Test residential costs when residential_units is None"""
        # Given
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
        index_factor = valuation_service._calculate_index_factor(sample_cpi_data.index_value)
        annual_gross_income = Decimal("24000.00")

        # When
        result = valuation_service._calculate_residential_costs(
            input_data,
            index_factor,
            annual_gross_income
        )

        # Then
        assert result.administration == Decimal("0")
        assert result.maintenance > Decimal("0")

    def test_residential_maintenance_scales_with_area(self, valuation_service, sample_cpi_data):
        """Test that residential maintenance costs scale with living area"""
        # Given
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

        index_factor = valuation_service._calculate_index_factor(sample_cpi_data.index_value)

        # When
        costs_small = valuation_service._calculate_residential_costs(
            input_data_small, index_factor, Decimal("12000.00")
        )
        costs_large = valuation_service._calculate_residential_costs(
            input_data_large, index_factor, Decimal("24000.00")
        )

        # Then
        assert costs_large.maintenance > costs_small.maintenance


class TestCommercialManagementCosts:
    """Test suite for commercial property management costs"""

    def test_commercial_costs_calculation(self, valuation_service, sample_commercial_input, sample_cpi_data):
        """Test commercial management costs calculation"""
        # Given
        index_factor = valuation_service._calculate_index_factor(sample_cpi_data.index_value)
        annual_gross_income = Decimal("60000.00")

        # When
        result = valuation_service._calculate_commercial_costs(
            sample_commercial_input,
            index_factor,
            annual_gross_income
        )

        # Then
        assert isinstance(result, ManagementCosts)
        assert result.administration == annual_gross_income * Decimal("0.03")
        assert result.maintenance > Decimal("0")
        assert result.risk_of_rent_loss > Decimal("0")
        assert result.total == (
                result.administration + result.maintenance + result.risk_of_rent_loss
        )
        assert result.risk_percentage == Decimal("4.00")  # COM_RENT_LOSS_PERCENT is 0.04

    def test_commercial_admin_percentage_based(self, valuation_service, sample_commercial_input, sample_cpi_data):
        """Test that commercial admin is percentage of gross income"""
        # Given
        index_factor = valuation_service._calculate_index_factor(sample_cpi_data.index_value)
        annual_gross_income = Decimal("100000.00")

        # When
        result = valuation_service._calculate_commercial_costs(
            sample_commercial_input,
            index_factor,
            annual_gross_income
        )

        # Then
        expected_admin = annual_gross_income * Decimal("0.03")
        assert result.administration == expected_admin


class TestFullValuationCalculation:
    """Test suite for complete valuation calculations"""

    def test_residential_valuation_complete(
            self,
            valuation_service,
            sample_residential_input,
            sample_cpi_data
    ):
        """Test complete residential property valuation"""
        # When
        result = valuation_service.calculate_valuation(
            sample_residential_input,
            sample_cpi_data
        )

        # Then
        assert result.input_data == sample_residential_input
        assert result.cpi_used == sample_cpi_data
        assert result.annual_gross_income == Decimal("24000")
        assert result.land_value == Decimal("200000")
        assert result.theoretical_total_value > Decimal("0")
        assert result.actual_building_value is not None
        assert result.actual_land_value is not None

        # Verify percentages sum to 100
        total_percent = result.building_share_percent + result.land_share_percent
        assert abs(total_percent - Decimal("100.00")) < Decimal("0.01")

        # Verify actual values sum to actual purchase price
        if result.actual_building_value and result.actual_land_value:
            total_actual = result.actual_building_value + result.actual_land_value
            assert abs(total_actual - sample_residential_input.actual_purchase_price) < Decimal("1")

    def test_commercial_valuation_complete(
            self,
            valuation_service,
            sample_commercial_input,
            sample_cpi_data
    ):
        """Test complete commercial property valuation"""
        # When
        result = valuation_service.calculate_valuation(
            sample_commercial_input,
            sample_cpi_data
        )

        # Then
        assert result.input_data == sample_commercial_input
        assert result.cpi_used == sample_cpi_data
        assert result.annual_gross_income == Decimal("60000")
        assert result.land_value == Decimal("400000")
        assert result.theoretical_total_value > Decimal("0")

        # Verify management costs structure for commercial
        assert result.management_costs.administration > Decimal("0")
        assert result.management_costs.maintenance > Decimal("0")
        assert result.management_costs.risk_percentage == Decimal("4.00")

    def test_valuation_without_actual_purchase_price(
            self,
            valuation_service,
            sample_cpi_data
    ):
        """Test valuation when actual purchase price is not provided"""
        # Given
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
            actual_purchase_price=None  # No actual price
        )

        # When
        result = valuation_service.calculate_valuation(input_data, sample_cpi_data)

        # Then
        assert result.actual_building_value is None
        assert result.actual_land_value is None
        assert result.theoretical_total_value > Decimal("0")

    def test_valuation_with_high_inflation(
            self,
            valuation_service,
            sample_residential_input,
            cpi_data_high_inflation
    ):
        """Test how valuation changes with high inflation"""
        # When
        result = valuation_service.calculate_valuation(
            sample_residential_input,
            cpi_data_high_inflation
        )

        # Then
        # Higher CPI should increase management costs
        assert result.management_costs.total > Decimal("0")
        assert result.index_factor > Decimal("1.4")  # 130/88.9

    def test_valuation_rounding(self, valuation_service, sample_residential_input, sample_cpi_data):
        """Test that all monetary values are properly rounded to euros"""
        # When
        result = valuation_service.calculate_valuation(
            sample_residential_input,
            sample_cpi_data
        )

        # Then - all values should have no decimal places (rounded to euro)
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
    """Test edge cases and boundary conditions"""

    def test_minimal_property_values(self, valuation_service, sample_cpi_data):
        """Test with minimal valid property values"""
        # Given
        input_data = ValuationInput(
            property_type=PropertyType.RESIDENTIAL,
            purchase_date=date(2024, 1, 15),
            monthly_net_rent=Decimal("1.00"),  # Minimal rent
            living_area=Decimal("1.0"),  # Minimal area
            residential_units=Decimal("1"),
            parking_units=Decimal("0"),
            land_value_per_sqm=Decimal("1.00"),
            plot_area=Decimal("1.0"),
            remaining_useful_life=Decimal("1.0"),
            property_yield=Decimal("1.0"),
        )

        # When
        result = valuation_service.calculate_valuation(input_data, sample_cpi_data)

        # Then
        assert result.theoretical_total_value > Decimal("0")

    def test_very_high_property_yield(self, valuation_service, sample_residential_input, sample_cpi_data):
        """Test with maximum property yield"""
        # Given
        sample_residential_input.property_yield = Decimal("100.0")  # Max yield

        # When
        result = valuation_service.calculate_valuation(
            sample_residential_input,
            sample_cpi_data
        )

        # Then
        assert result.theoretical_total_value > Decimal("0")
        assert result.multiplier > Decimal("0")

    def test_long_remaining_useful_life(self, valuation_service, sample_residential_input, sample_cpi_data):
        """Test with very long remaining useful life"""
        # Given
        sample_residential_input.remaining_useful_life = Decimal("100.0")

        # When
        result = valuation_service.calculate_valuation(
            sample_residential_input,
            sample_cpi_data
        )

        # Then
        assert result.multiplier > Decimal("10")
        assert result.theoretical_building_value > Decimal("0")