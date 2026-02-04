import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx

from back.app.services.cpi_parser_service import GermanyHistoricalCpiParser
from back.app.schemas.cpi import CpiPeriod


class TestGermanyHistoricalCpiParser:
    @pytest.fixture
    def parser(self):
        return GermanyHistoricalCpiParser()

    @pytest.mark.asyncio
    async def test_parse_into_mapper_success(self, parser, mock_httpx_response):
        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_httpx_response.content

            await parser.parse_into_mapper()

            assert len(parser._cpi_data) > 0

            jan_2023 = CpiPeriod(year=2023, month="01")
            assert jan_2023 in parser._cpi_data
            assert parser._cpi_data[jan_2023] == 115.0

            oct_2023 = CpiPeriod(year=2023, month="10")
            assert oct_2023 in parser._cpi_data
            assert parser._cpi_data[oct_2023] == 118.5

    @pytest.mark.asyncio
    async def test_parse_into_mapper_no_table(self, parser):
        html_without_table = b"<html><body><p>No table here</p></body></html>"

        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = html_without_table

            await parser.parse_into_mapper()

            assert len(parser._cpi_data) == 0

    @pytest.mark.asyncio
    async def test_parse_handles_empty_cells(self, parser):
        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = b"""
            <html>
                <table>
                    <thead>
                        <tr>
                            <th>Year</th><th>Jan</th><th>Feb</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>2024</td>
                            <td>120.5</td>
                            <td></td>
                        </tr>
                    </tbody>
                </table>
            </html>
            """

            await parser.parse_into_mapper()

            jan_2024 = CpiPeriod(year=2024, month="01")
            feb_2024 = CpiPeriod(year=2024, month="02")

            assert jan_2024 in parser._cpi_data
            assert feb_2024 not in parser._cpi_data

    @pytest.mark.asyncio
    async def test_parse_handles_invalid_rows(self, parser):
        html_with_invalid = b"""
        <html>
            <table>
                <thead>
                    <tr><th>Year</th><th>Jan</th></tr>
                </thead>
                <tbody>
                    <tr><td>invalid</td><td>120.5</td></tr>
                    <tr><td>2024</td><td>121.0</td></tr>
                </tbody>
            </table>
        </html>
        """

        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = html_with_invalid

            await parser.parse_into_mapper()

            jan_2024 = CpiPeriod(year=2024, month="01")
            assert jan_2024 in parser._cpi_data
            assert parser._cpi_data[jan_2024] == 121.0

    @pytest.mark.asyncio
    async def test_fetch_page_success(self, parser):
        mock_response = Mock()
        mock_response.content = b"<html>test</html>"
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await parser._fetch_page()

            assert result == b"<html>test</html>"
            mock_response.raise_for_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_page_retry_on_request_error(self, parser):
        mock_response = Mock()
        mock_response.content = b"<html>test</html>"
        mock_response.raise_for_status = Mock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=[
                    httpx.RequestError("Connection failed"),
                    httpx.RequestError("Connection failed"),
                    mock_response,
                ]
            )

            result = await parser._fetch_page()

            assert result == b"<html>test</html>"

    @pytest.mark.asyncio
    async def test_fetch_page_retry_exhausted(self, parser):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.RequestError("Connection failed")
            )

            with pytest.raises(httpx.RequestError):
                await parser._fetch_page()

    @pytest.mark.asyncio
    async def test_fetch_page_http_status_error(self, parser):
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = Mock()
            mock_response.raise_for_status = Mock(
                side_effect=httpx.HTTPStatusError(
                    "404 Not Found", request=Mock(), response=Mock()
                )
            )
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            with pytest.raises(httpx.HTTPStatusError):
                await parser._fetch_page()

    def test_get_cpi_period_data_exists(self, parser):
        period = CpiPeriod(year=2023, month=10)
        parser._cpi_data[period] = 118.5

        result = parser.get_cpi_period_data(period)

        assert result == 118.5

    def test_get_cpi_period_data_not_exists(self, parser):
        period = CpiPeriod(year=2099, month=12)

        result = parser.get_cpi_period_data(period)

        assert result is None

    @pytest.mark.asyncio
    async def test_parse_decimal_separator(self, parser):
        html_with_comma = b"""
        <html>
            <table>
                <thead>
                    <tr><th>Year</th><th>Jan</th></tr>
                </thead>
                <tbody>
                    <tr><td>2024</td><td>120,5</td></tr>
                </tbody>
            </table>
        </html>
        """

        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = html_with_comma

            await parser.parse_into_mapper()

            jan_2024 = CpiPeriod(year=2024, month="01")
            assert parser._cpi_data[jan_2024] == 120.5

    def test_month_mapping(self, parser):
        assert parser.months["jan"] == "01"
        assert parser.months["feb"] == "02"
        assert parser.months["mar"] == "03"
        assert parser.months["apr"] == "04"
        assert parser.months["may"] == "05"
        assert parser.months["jun"] == "06"
        assert parser.months["jul"] == "07"
        assert parser.months["aug"] == "08"
        assert parser.months["sep"] == "09"
        assert parser.months["oct"] == "10"
        assert parser.months["nov"] == "11"
        assert parser.months["dec"] == "12"

    @pytest.mark.asyncio
    async def test_parse_multiple_years(self, parser, mock_httpx_response):
        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_httpx_response.content

            await parser.parse_into_mapper()

            has_2023_data = any(p.year == 2023 for p in parser._cpi_data.keys())
            has_2024_data = any(p.year == 2024 for p in parser._cpi_data.keys())

            assert has_2023_data
            assert has_2024_data

    @pytest.mark.asyncio
    async def test_parse_updates_existing_data(self, parser):
        old_period = CpiPeriod(year=2023, month="01")
        parser._cpi_data[old_period] = 100.0

        html = b"""
        <html>
            <table>
                <thead>
                    <tr><th>Year</th><th>Jan</th></tr>
                </thead>
                <tbody>
                    <tr><td>2023</td><td>115.0</td></tr>
                </tbody>
            </table>
        </html>
        """

        with patch.object(parser, "_fetch_page", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = html

            await parser.parse_into_mapper()

            assert parser._cpi_data[old_period] == 115.0
