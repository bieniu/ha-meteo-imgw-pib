"""Data Update Coordinator for Meteo IMGW-PIB integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from imgw_pib import ApiError, ImgwPib, WeatherData

from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class MeteoImgwPibDataUpdateCoordinator(DataUpdateCoordinator[WeatherData]):
    """Class to manage fetching Meteo IMGW-PIB data API."""

    def __init__(
        self,
        hass: HomeAssistant,
        imgwpib: ImgwPib,
        station_id: str,
    ) -> None:
        """Initialize."""
        self.imgwpib = imgwpib
        self.station_id = station_id
        self.device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, station_id)},
            manufacturer="IMGW-PIB",
            name=f"{imgwpib.weather_stations[station_id]}",
        )

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)

    async def _async_update_data(self) -> WeatherData:
        """Update data via internal method."""
        try:
            return await self.imgwpib.get_weather_data()
        except ApiError as err:
            raise UpdateFailed(err) from err
