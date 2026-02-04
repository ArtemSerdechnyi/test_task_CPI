import pytest
from unittest.mock import Mock

from back.app.services.cpi_service import CpiService


@pytest.fixture
def cpi_service(mock_cpi_parser):
    return CpiService(cpi_parser_service=mock_cpi_parser)


@pytest.fixture
def cpi_service_empty():
    empty_parser = Mock()
    empty_parser._cpi_data = {}
    empty_parser.get_cpi_period_data = Mock(return_value=None)
    return CpiService(cpi_parser_service=empty_parser)
