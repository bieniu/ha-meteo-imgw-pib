"""Define the IMGW-PIB entity."""

from homeassistant.const import ATTR_CONFIGURATION_URL, ATTR_LATITUDE, ATTR_LONGITUDE
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
        # to remove this line after some time
        if hasattr(coordinator.data, ATTR_LATITUDE) and hasattr(  # noqa: SIM102
            coordinator.data, ATTR_LONGITUDE
        ):
            if (latitude := coordinator.data.latitude) is not None and (
                longitude := coordinator.data.longitude
            ) is not None:
                device_info[ATTR_CONFIGURATION_URL] = CONFIGURATION_URL.format(
                    latitude=latitude,
                    longitude=longitude,
                )
        self._attr_device_info = device_info
