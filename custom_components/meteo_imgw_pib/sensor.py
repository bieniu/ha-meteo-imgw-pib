"""IMGW-PIB sensor platform."""

from __future__ import annotations

import bisect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

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
from imgw_pib.const import NO_ALERT, WEATHER_ALERTS_MAP
from imgw_pib.model import WeatherData

from .coordinator import MeteoImgwPibConfigEntry, MeteoImgwPibDataUpdateCoordinator
from .entity import MeteoImgwPibEntity

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class MeteoImgwPibSensorEntityDescription(SensorEntityDescription):
    """Meteo IMGW-PIB sensor entity description."""

    value: Callable[[WeatherData], StateType]
    attrs: Callable[[WeatherData], dict[str, Any] | None] | None = None


SENSOR_TYPES: tuple[MeteoImgwPibSensorEntityDescription, ...] = (
    MeteoImgwPibSensorEntityDescription(
        key="weather_alert",
        translation_key="weather_alert",
        device_class=SensorDeviceClass.ENUM,
        options=list(WEATHER_ALERTS_MAP.values()),
        value=lambda data: data.weather_alert.value,
        attrs=lambda data: {
            "level": data.weather_alert.level,
            "probability": data.weather_alert.probability,
            "valid_from": data.weather_alert.valid_from,
            "valid_to": data.weather_alert.valid_to,
        }
        if data.weather_alert.value != NO_ALERT
        else None,
    ),
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
        device_class=SensorDeviceClass.WIND_DIRECTION,
        state_class=SensorStateClass.MEASUREMENT_ANGLE,
        suggested_display_precision=0,
        value=lambda data: data.wind_direction.value,
        attrs=lambda data: {
            "direction_name": _get_wind_direction(data.wind_direction.value)
        }
        if data.wind_direction.value is not None
        else None,
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

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes."""
        if self.entity_description.attrs:
            return self.entity_description.attrs(self.coordinator.data)

        return None


# Wind direction boundaries and corresponding names
_WIND_DIRECTIONS = [
    (0.0, "n"),
    (11.25, "nne"),
    (33.75, "ne"),
    (56.25, "ene"),
    (78.75, "e"),
    (101.25, "ese"),
    (123.75, "se"),
    (146.25, "sse"),
    (168.75, "s"),
    (191.25, "ssw"),
    (213.75, "sw"),
    (236.25, "wsw"),
    (258.75, "w"),
    (281.25, "wnw"),
    (303.75, "nw"),
    (326.25, "nnw"),
    (348.75, "n"),  # Wrap around for degrees >= 348.75
]


def _get_wind_direction(wind_direction_degree: float) -> str:
    """Convert wind direction degree to named direction."""
    # Normalize degree to 0-360 range
    normalized_degree = wind_direction_degree % 360
    # Find the insertion point
    idx = bisect.bisect_right(_WIND_DIRECTIONS, (normalized_degree,))
    # Get the direction, default to "n" if not found
    return _WIND_DIRECTIONS[idx - 1][1] if idx > 0 else "n"
