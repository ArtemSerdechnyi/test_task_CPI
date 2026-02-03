from datetime import date

from fastapi import APIRouter, HTTPException

from back.app.api.dependencies import cpi_service_dep
from back.app.schemas.valuation import CPIData

cpi_router = APIRouter()


@cpi_router.get("/cpi/{year}/{month}")
async def get_cpi(
    year: int,
    month: int,
    cpi_service: cpi_service_dep,
) -> CPIData:
    """
    Получить индекс потребительских цен (CPI) за конкретный месяц

    - **year**: Год (например, 2024)
    - **month**: Месяц (1-12)

    Возвращает официальный CPI из Федерального статистического управления Германии
    """

    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Месяц должен быть от 1 до 12")

    if year < 2002 or year > date.today().year:
        raise HTTPException(status_code=400, detail="Год вне допустимого диапазона")

    try:
        # Создаем фиктивную дату покупки для получения CPI
        # Добавляем 1 к году, так как метод вычитает 1
        purchase_date = date(year + 1, month, 1)
        cpi_data_dict = await cpi_service.get_cpi_for_purchase_date(purchase_date)

        return CPIData(**cpi_data_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения CPI: {str(e)}")