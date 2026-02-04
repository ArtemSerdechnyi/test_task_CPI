from typing import Annotated
from fastapi import Depends

from back.app.core.config import settings
from back.app.services.cpi_parser import germany_historical_cpi_parser
from back.app.services.cpi_service import CPIService
from back.app.services.llm_service import LLMService
from back.app.services.valuation_service import ValuationService


def get_cpi_service() -> CPIService:
    return CPIService(germany_historical_cpi_parser.cpi_data)


cpi_service_dep = Annotated[CPIService, Depends(get_cpi_service)]


def get_valuation_service() -> ValuationService:
    return ValuationService()


valuation_service_dep = Annotated[ValuationService, Depends(get_valuation_service)]


def get_llm_service() -> LLMService:
    return LLMService(model=settings.LLM, api_key=settings.OPENAI_API_KEY)


llm_service_dep = Annotated[LLMService, Depends(get_llm_service)]
