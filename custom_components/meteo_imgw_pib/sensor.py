"""IMGW-PIB sensor platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from imgw_pib.model import WeatherData

from .coordinator import MeteoImgwPibConfigEntry, MeteoImgwPibDataUpdateCoordinator
from .entity import MeteoImgwPibEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class MeteoImgwPibSensorEntityDescription(SensorEntityDescription):
    """Meteo IMGW-PIB sensor entity description."""

    value: Callable[[WeatherData], StateType]


SENSOR_TYPES: tuple[MeteoImgwPibSensorEntityDescription, ...] = (
    MeteoImgwPibSensorEntityDescription(
        key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value=lambda data: data.temperature.value,
    ),
    MeteoImgwPibSensorEntityDescription(
        key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value=lambda data: data.humidity.value,
    ),
    MeteoImgwPibSensorEntityDescription(
        key="pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value=lambda data: data.pressure.value,
    ),
    MeteoImgwPibSensorEntityDescription(
        key="wind_speed",
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value=lambda data: data.wind_speed.value,
    ),
    MeteoImgwPibSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value=lambda data: data.wind_direction.value,
    ),
    MeteoImgwPibSensorEntityDescription(
        key="precipitation",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value=lambda data: data.precipitation.value,
    ),
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: MeteoImgwPibConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add a Meteo IMGW-PIB sensor entity from a config_entry."""
    coordinator = entry.runtime_data.coordinator

    async_add_entities(
        MeteoImgwPibSensorEntity(coordinator, description)
        for description in SENSOR_TYPES
        if getattr(coordinator.data, description.key).value is not None
    )


class MeteoImgwPibSensorEntity(MeteoImgwPibEntity, SensorEntity):
    """Define MeteoIMGW-PIB sensor entity."""

    entity_description: MeteoImgwPibSensorEntityDescription

    def __init__(
        self,
        coordinator: MeteoImgwPibDataUpdateCoordinator,
        description: MeteoImgwPibSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{coordinator.station_id}_{description.key}"
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        return self.entity_description.value(self.coordinator.data)
