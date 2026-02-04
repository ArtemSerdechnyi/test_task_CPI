from datetime import date

from fastapi import APIRouter
from starlette import status

from back.app.api.dependencies import cpi_service_dep
from back.app.core.exceptions import BadRequestException, InternalServerException

cpi_router = APIRouter()


@cpi_router.get("/{year}/{month}", status_code=status.HTTP_200_OK)
def get_cpi(
    year: int,
    month: int,
    cpi_service: cpi_service_dep,
) -> str | None:
    """
    Get the consumer price index (CPI) for a specific month
    """

    if not (1 <= month <= 12):
        raise BadRequestException(detail="CPI month must be between 1 and 12")

    if year < 2002 or year > date.today().year:
        raise BadRequestException(detail="CPI year must be between 2002 and today.")

    try:
        return cpi_service.get_cpi(year=year, month=month)
    except Exception as e:
        raise InternalServerException(detail=f"CPI: {str(e)}")
