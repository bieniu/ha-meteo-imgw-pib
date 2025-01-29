"""Test init of Meteo IMGW-PIB integration."""

from unittest.mock import Mock

import pytest
from homeassistant.config_entries import ConfigEntryState
from pytest_homeassistant_custom_component.common import HomeAssistant, MockConfigEntry

from custom_components.meteo_imgw_pib.const import CONF_STATION_ID, DOMAIN


@pytest.mark.asyncio
async def test_config_entry_not_ready(
    hass: HomeAssistant, error_on_get_data: Mock
) -> None:
    """Test for setup failure if connection to IMGW-PIB is missing."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_STATION_ID: "12200"}, title="Test title"
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)

    assert entry.state == ConfigEntryState.SETUP_RETRY


@pytest.mark.asyncio
async def test_unload_entry(hass: HomeAssistant, bypass_get_data: Mock) -> None:
    """Test successful unload of entry."""
    entry = MockConfigEntry(
        domain=DOMAIN, data={CONF_STATION_ID: "12200"}, title="Test title"
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert len(hass.config_entries.async_entries(DOMAIN)) == 1
    assert entry.state == ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state == ConfigEntryState.NOT_LOADED
    assert not hass.data.get(DOMAIN)
