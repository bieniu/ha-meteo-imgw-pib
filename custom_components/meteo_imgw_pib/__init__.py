"""The Meteo IMGW-PIB integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from aiohttp import ClientError
from imgw_pib import ImgwPib
from imgw_pib.exceptions import ApiError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_STATION_ID
from .coordinator import MeteoImgwPibDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

type MeteoImgwPibConfigEntry = ConfigEntry[MeteoImgwPibData]


@dataclass
class MeteoImgwPibData:
    """Data for the Meteo IMGW-PIB integration."""

    coordinator: MeteoImgwPibDataUpdateCoordinator


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
        raise ConfigEntryNotReady from err

    coordinator = MeteoImgwPibDataUpdateCoordinator(hass, imgwpib, station_id)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = MeteoImgwPibData(coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: MeteoImgwPibConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
