from fastapi import APIRouter
from loguru import logger
from fastapi import status

from back.app.api.dependencies import (
    cpi_service_dep,
    valuation_service_dep,
    llm_service_dep,
)
from back.app.core.exceptions import BadRequestException, InternalServerException
from back.app.schemas.valuation import (
    ValuationInput,
    ValuationResult,
    CPIData,
    AIPromptSchema,
)

valuation_router = APIRouter()


@valuation_router.post("/calculate", status_code=status.HTTP_200_OK)
async def calculate_valuation(
    input_data: ValuationInput,
    cpi_service: cpi_service_dep,
    valuation_service: valuation_service_dep,
) -> ValuationResult:
    """
    Calculate a real estate valuation using the income capitalization method.
    """

    try:
        year = input_data.purchase_date.year
        month = input_data.purchase_date.month

        index_value = cpi_service.get_cpi(year=year)
        cpi_data = CPIData(year=year, month=month, index_value=float(index_value))

        result = valuation_service.calculate_valuation(input_data, cpi_data)

        return result

    except ValueError as e:
        logger.exception(e)
        raise BadRequestException
    except Exception as e:
        logger.exception(e)
        raise InternalServerException(detail=f"Calculation error: {str(e)}")


@valuation_router.post("/calculate/analysis", status_code=status.HTTP_200_OK)
async def get_ai_analysis(
    result: ValuationResult,
    llm_service: llm_service_dep,
) -> str:
    """
    Generate an AI-powered analysis of the valuation results.
    """

    try:
        mapped_result = AIPromptSchema(
            property_type=result.input_data.property_type,
            purchase_date=result.input_data.purchase_date.isoformat(),
            actual_purchase_price=result.input_data.actual_purchase_price,
            theoretical_total_value=result.theoretical_total_value,
            building_share_percent=result.building_share_percent,
            land_share_percent=result.land_share_percent,
            admin_costs=result.management_costs.administration,
            maintenance_costs=result.management_costs.maintenance,
            risk_amount=result.management_costs.risk_of_rent_loss,
            risk_percentage=result.management_costs.risk_percentage,
            index_factor=result.index_factor,
            cpi_value=result.cpi_used.index_value,
            cpi_base_2001=result.cpi_base_2001,
        )

        analysis = await llm_service.get_llm_analysis(mapped_result)
        return analysis

    except Exception as e:
        logger.exception(e)
        raise InternalServerException(detail=f"AI analysis error: {str(e)}")
