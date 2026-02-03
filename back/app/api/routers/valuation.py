from http.client import HTTPException

from fastapi import APIRouter

from back.app.api.dependencies import cpi_service_dep, valuation_service_dep, ai_service_dep
from back.app.schemas.valuation import ValuationInput, ValuationResult, CPIData, AIAnalysisResponse

valuation_router = APIRouter()


@valuation_router.post("/calculate")
async def calculate_valuation(
        input_data: ValuationInput,
        cpi_service: cpi_service_dep,
        valuation_service: valuation_service_dep,
) -> ValuationResult:
    """
    Рассчитать оценку недвижимости по методу капитализации доходов

    - **property_type**: Тип недвижимости (residential/commercial)
    - **purchase_date**: Дата покупки (для определения CPI)
    - **monthly_net_rent**: Месячная чистая аренда в €
    - **living_area**: Площадь в м²
    - И другие параметры...

    Возвращает полный расчет с распределением стоимости земли и здания
    """

    try:
        # Получаем CPI за октябрь года, предшествующего дате покупки
        cpi_data_dict = await cpi_service.get_cpi_for_purchase_date(input_data.purchase_date)
        cpi_data = CPIData(**cpi_data_dict)

        # Выполняем расчет оценки
        result = valuation_service.calculate_valuation(input_data, cpi_data)

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка расчета: {str(e)}")


@valuation_router.post("/calculate/{valuation_id}/analysis")
async def get_ai_analysis(
        result: ValuationResult,
        ai_service: ai_service_dep,
) -> AIAnalysisResponse:
    """
    Получить AI-анализ результатов оценки

    Принимает результат расчета и возвращает:
    - Детальный анализ с контекстом
    - Влияние типа недвижимости
    - Объяснение инфляционной корректировки
    - Сравнение с рыночной ценой
    - Ключевые выводы
    """

    try:
        analysis = await ai_service.analyze_valuation(result)
        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка AI-анализа: {str(e)}")


