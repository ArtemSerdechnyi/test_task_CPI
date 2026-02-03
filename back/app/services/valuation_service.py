import math

from back.app.schemas.valuation import ValuationInput, CPIData, ValuationResult, ManagementCosts, PropertyType


class ValuationService:
    """
    Сервис для расчета оценки недвижимости по методу капитализации доходов
    (Ertragswertverfahren)
    """

    CPI_BASE_OCT_2001 = 84.5  # Фиксированное значение

    def calculate_valuation(
        self,
        input_data: ValuationInput,
        cpi_data: CPIData
    ) -> ValuationResult:
        """
        Основной метод расчета оценки
        """

        # Step 1: Стоимость земли
        land_value = self._calculate_land_value(
            input_data.land_value_per_sqm,
            input_data.plot_area
        )

        # Step 2: Годовой чистый доход
        annual_gross_income = self._calculate_annual_gross_income(
            input_data.monthly_net_rent
        )

        # Фактор индекса для корректировки затрат
        index_factor = self._calculate_index_factor(cpi_data.index_value)

        # Расчет затрат на управление
        management_costs = self._calculate_management_costs(
            input_data=input_data,
            index_factor=index_factor
        )

        annual_net_income = annual_gross_income - management_costs.total

        # Step 3: Чистый доход от здания
        land_interest = land_value * (input_data.property_yield / 100)
        building_net_income = annual_net_income - land_interest

        # Step 4: Капитализация стоимости здания
        multiplier = self._calculate_multiplier(
            input_data.property_yield,
            input_data.remaining_useful_life
        )

        theoretical_building_value = building_net_income * multiplier

        # Step 5: Распределение
        theoretical_total_value = theoretical_building_value + land_value

        building_share_percent = (theoretical_building_value / theoretical_total_value) * 100
        land_share_percent = (land_value / theoretical_total_value) * 100

        # Если указана фактическая цена покупки
        actual_building_value = None
        actual_land_value = None

        if input_data.actual_purchase_price:
            actual_building_value = input_data.actual_purchase_price * (building_share_percent / 100)
            actual_land_value = input_data.actual_purchase_price * (land_share_percent / 100)

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
            actual_building_value=self._round_euro(actual_building_value) if actual_building_value else None,
            actual_land_value=self._round_euro(actual_land_value) if actual_land_value else None
        )

    def _calculate_land_value(self, land_value_per_sqm: float, plot_area: float) -> float:
        """
        Step 1: Bodenwert = Bodenrichtwert × Grundstücksfläche
        """
        return land_value_per_sqm * plot_area

    def _calculate_annual_gross_income(self, monthly_net_rent: float) -> float:
        """
        Jahresrohertrag = Monatliche Nettokaltmiete × 12
        """
        return monthly_net_rent * 12

    def _calculate_index_factor(self, current_cpi: float) -> float:
        """
        Index-Faktor = CPI (Oktober Jahr-1) / CPI (Oktober 2001)
        """
        return current_cpi / self.CPI_BASE_OCT_2001

    def _calculate_management_costs(
            self,
            input_data: ValuationInput,
            index_factor: float
    ) -> ManagementCosts:
        """
        Step 2: Bewirtschaftungskosten
        Логика различается для Residential vs Commercial
        """

        if input_data.property_type == PropertyType.RESIDENTIAL:
            return self._calculate_residential_costs(input_data, index_factor)
        else:
            return self._calculate_commercial_costs(input_data, index_factor)

    def _calculate_residential_costs(
            self,
            input_data: ValuationInput,
            index_factor: float
    ) -> ManagementCosts:
        """
        Расчет для жилой недвижимости (Wohnen)
        """

        # 1. Verwaltungskosten (Administration)
        if input_data.residential_units and input_data.residential_units > 0:
            # Динамическая формула
            base_rate_per_unit = 270
            admin_per_unit = round(base_rate_per_unit * index_factor, 2)
            administration = admin_per_unit * input_data.residential_units
        else:
            administration = 0

        # 2. Instandhaltungskosten (Maintenance)
        base_maintenance_rate = 9.00  # €/м² базовая ставка
        maintenance_per_sqm = round(base_maintenance_rate * index_factor, 1)  # Округление до 1 знака!
        maintenance = maintenance_per_sqm * input_data.living_area

        # 3. Mietausfallwagnis (Risk of Rent Loss)
        annual_gross_income = self._calculate_annual_gross_income(input_data.monthly_net_rent)
        risk_of_rent_loss = annual_gross_income * 0.02  # 2%

        total = administration + maintenance + risk_of_rent_loss

        return ManagementCosts(
            administration=self._round_euro(administration),
            maintenance=self._round_euro(maintenance),
            risk_of_rent_loss=self._round_euro(risk_of_rent_loss),
            total=self._round_euro(total),
            risk_percentage=self._round_euro(risk_of_rent_loss) / annual_gross_income * 100,
        )

    def _calculate_commercial_costs(
            self,
            input_data: ValuationInput,
            index_factor: float
    ) -> ManagementCosts:
        """
        Расчет для коммерческой недвижимости (Gewerbe)
        """

        annual_gross_income = self._calculate_annual_gross_income(input_data.monthly_net_rent)

        # 1. Verwaltungskosten (Administration) - процентная формула
        administration = annual_gross_income * 0.03  # 3%

        # 2. Instandhaltungskosten (Maintenance) - такая же формула как у Residential
        base_maintenance_rate = 9.00
        maintenance_per_sqm = round(base_maintenance_rate * index_factor, 1)  # Округление до 1 знака!
        maintenance = maintenance_per_sqm * input_data.living_area

        # 3. Mietausfallwagnis (Risk of Rent Loss)
        risk_of_rent_loss = annual_gross_income * 0.04  # 4% (выше чем у жилой)

        total = administration + maintenance + risk_of_rent_loss

        return ManagementCosts(
            administration=self._round_euro(administration),
            maintenance=self._round_euro(maintenance),
            risk_of_rent_loss=self._round_euro(risk_of_rent_loss),
            total=self._round_euro(total)
        )

    def _calculate_multiplier(self, property_yield: float, remaining_useful_life: float) -> float:
        """
        Step 4: Barwertfaktor (Multiplier)

        Formula: (1 - (1 + i)^(-n)) / i
        где i = property_yield / 100, n = remaining_useful_life
        """
        i = property_yield / 100
        n = remaining_useful_life

        if i == 0:
            return n  # Если ставка 0, то просто n

        multiplier = (1 - math.pow(1 + i, -n)) / i
        return multiplier

    @staticmethod
    def _round_euro(value: float) -> float:
        """
        Коммерческое округление до целого евро
        """
        if value is None:
            return None
        return round(value)