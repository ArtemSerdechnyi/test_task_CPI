from datetime import date

from fastapi import APIRouter, HTTPException

from back.app.api.dependencies import cpi_service_dep

cpi_router = APIRouter()


@cpi_router.get("/{year}/{month}")
async def get_cpi(
    year: int,
    month: int,
    cpi_service: cpi_service_dep,
) -> str | None:
    """
    Get the consumer price index (CPI) for a specific month
    """

    if not (1 <= month <= 12):
        raise HTTPException(status_code=400)

    if year < 2002 or year > date.today().year:
        raise HTTPException(status_code=400)

    try:
        return cpi_service.get_cpi(year=year, month=month)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CPI: {str(e)}")