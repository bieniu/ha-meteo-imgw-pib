"""Test init of Meteo IMGW-PIB integration."""

from unittest.mock import Mock

from imgw_pib import ApiError
from pytest_homeassistant_custom_component.common import (
    HomeAssistant,
    MockConfigEntry,
    config_entries,
)

from custom_components.meteo_imgw_pib.const import CONF_STATION_ID, DOMAIN


async def test_config_entry_not_ready(
    hass: HomeAssistant, mock_imgw_pib_client: Mock
) -> None:
    """Test for setup failure if connection to IMGW-PIB is missing."""
    mock_imgw_pib_client.get_weather_data.side_effect = ApiError("exception")

    entry = MockConfigEntry(domain=DOMAIN, data={CONF_STATION_ID: "12200"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)

    assert entry.state == config_entries.ConfigEntryState.SETUP_RETRY


async def test_unload_entry(hass: HomeAssistant, mock_imgw_pib_client: Mock) -> None:
    """Test successful unload of entry."""
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_STATION_ID: "12200"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == config_entries.ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == config_entries.ConfigEntryState.NOT_LOADED
    assert not hass.data.get(DOMAIN)
