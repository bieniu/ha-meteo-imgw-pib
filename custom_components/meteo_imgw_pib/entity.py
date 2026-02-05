"""Define the IMGW-PIB entity."""

from homeassistant.const import ATTR_CONFIGURATION_URL
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, CONFIGURATION_URL, DOMAIN
from .coordinator import MeteoImgwPibDataUpdateCoordinator


class MeteoImgwPibEntity(CoordinatorEntity[MeteoImgwPibDataUpdateCoordinator]):
    """Define Meteo IMGW-PIB entity."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MeteoImgwPibDataUpdateCoordinator,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, coordinator.station_id)},
            manufacturer="IMGW-PIB",
            name=f"{coordinator.imgwpib.weather_stations[coordinator.station_id]}",
        )
        latitude = coordinator.data.latitude
        longitude = coordinator.data.longitude
        if latitude is not None and longitude is not None:
            device_info[ATTR_CONFIGURATION_URL] = CONFIGURATION_URL.format(
                latitude=latitude,
                longitude=longitude,
            )

        self._attr_device_info = device_info
