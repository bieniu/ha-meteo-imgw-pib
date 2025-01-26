"""Define the IMGW-PIB entity."""

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
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

        self._attr_device_info = coordinator.device_info
