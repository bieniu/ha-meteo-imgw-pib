"""The Meteo IMGW-PIB integration."""

from __future__ import annotations

import logging

from aiohttp import ClientError
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from imgw_pib import ImgwPib
from imgw_pib.exceptions import ApiError

from .const import CONF_STATION_ID, DOMAIN
from .coordinator import (
    MeteoImgwPibConfigEntry,
    MeteoImgwPibData,
    MeteoImgwPibDataUpdateCoordinator,
)

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: MeteoImgwPibConfigEntry
) -> bool:
    """Set up Meteo IMGW-PIB from a config entry."""
    station_id: str = entry.data[CONF_STATION_ID]

    _LOGGER.debug("Using weather station ID: %s", station_id)

    client_session = async_get_clientsession(hass)

    try:
        imgwpib = await ImgwPib.create(
            client_session,
            weather_station_id=station_id,
        )
    except (ClientError, TimeoutError, ApiError) as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="cannot_connect",
            translation_placeholders={"entry": entry.title},
        ) from err

    coordinator = MeteoImgwPibDataUpdateCoordinator(hass, entry, imgwpib, station_id)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = MeteoImgwPibData(coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: MeteoImgwPibConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
