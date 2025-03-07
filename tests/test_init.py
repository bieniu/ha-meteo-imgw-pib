"""Test init of Meteo IMGW-PIB integration."""

from unittest.mock import AsyncMock

from imgw_pib import ApiError
from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    MockConfigEntry,
    config_entries,
)

from custom_components.meteo_imgw_pib.const import DOMAIN

from . import init_integration


async def test_config_entry_not_ready(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
) -> None:
    """Test for setup failure if connection to IMGW-PIB is missing."""
    mock_imgw_pib_client.get_weather_data.side_effect = ApiError("exception")

    await init_integration(hass, mock_config_entry)

    assert mock_config_entry.state == config_entries.ConfigEntryState.SETUP_RETRY


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_imgw_pib_client: AsyncMock,
) -> None:
    """Test successful unload of entry."""
    await init_integration(hass, mock_config_entry)

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert mock_config_entry.state == config_entries.ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state == config_entries.ConfigEntryState.NOT_LOADED
    assert not hass.data.get(DOMAIN)
