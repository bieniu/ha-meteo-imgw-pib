"""Tests for Meteo IMGW-PIB."""

from homeassistant.core import HomeAssistant
from pytest_homeassistant.common import MockConfigEntry


async def init_integration(hass: HomeAssistant, config_entry: MockConfigEntry) -> None:
    """Set up the IMGW-PIB integration in Home Assistant."""
    config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
