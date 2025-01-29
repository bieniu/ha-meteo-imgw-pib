"""Define tests for the Meteo IMGW-PIB config flow."""

from unittest.mock import AsyncMock, Mock, patch

from homeassistant.data_entry_flow import FlowResultType
from imgw_pib.exceptions import ApiError
from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    config_entries,
)

from custom_components.meteo_imgw_pib.const import CONF_STATION_ID, DOMAIN

USER_INPUT = {CONF_STATION_ID: "12200"}


async def test_create_entry(
    hass: HomeAssistant, mock_imgw_pib_client: AsyncMock
) -> None:
    """Test that the user step works."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == config_entries.SOURCE_USER
    assert result["errors"] == {}

    with patch("custom_components.meteo_imgw_pib.async_setup_entry", return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], user_input=USER_INPUT
        )

        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Warszawa"
        assert result["data"][CONF_STATION_ID] == "12200"


async def test_duplicate_error(
    hass: HomeAssistant, mock_imgw_pib_client: Mock, mock_config_entry: AsyncMock
) -> None:
    """Test that errors are shown when duplicates are added."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
        data={CONF_STATION_ID: "12200"},
    )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_failed_config_flow(
    hass: HomeAssistant, mock_imgw_pib_client: AsyncMock
) -> None:
    """Test a failed config flow due to credential validation failure."""
    mock_imgw_pib_client.get_weather_data.side_effect = ApiError("exception")

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=USER_INPUT
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
