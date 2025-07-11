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
from imgw_pib.const import WEATHER_ALERTS_MAP
from imgw_pib.model import WeatherData

from .coordinator import MeteoImgwPibConfigEntry, MeteoImgwPibDataUpdateCoordinator
from .entity import MeteoImgwPibEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class MeteoImgwPibSensorEntityDescription(SensorEntityDescription):
    """Meteo IMGW-PIB sensor entity description."""

    value: Callable[[WeatherData], StateType]
    attrs: Callable[[WeatherData], dict[str, StateType]] | None = None


WEATHER_ALERT_DESCRIPTION = MeteoImgwPibSensorEntityDescription(
    key="weather_alert",
    translation_key="weather_alert",
    device_class=SensorDeviceClass.ENUM,
    options=[*WEATHER_ALERTS_MAP.values(), "none"],
    value=lambda data: data.alert.event if data.alert else "none",
    attrs=lambda data: {
        "level": data.alert.level,
        "probability": data.alert.probability,
        "valid_from": data.alert.valid_from,
        "valid_to": data.alert.valid_to,
    }
    if data.alert is not None
    else {},
)
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
        device_class=SensorDeviceClass.WIND_DIRECTION,
        state_class=SensorStateClass.MEASUREMENT_ANGLE,
        suggested_display_precision=0,
        value=lambda data: data.wind_direction.value,
        attrs=lambda data: {
            "direction_name": _get_wind_direction(data.wind_direction.value)
        }
        if data.wind_direction.value is not None
        else {},
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

    entities = [
        *(
            MeteoImgwPibSensorEntity(coordinator, description)
            for description in SENSOR_TYPES
            if getattr(coordinator.data, description.key).value is not None
        ),
        MeteoImgwPibSensorEntity(coordinator, WEATHER_ALERT_DESCRIPTION),
    ]

    async_add_entities(entities)


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
    def extra_state_attributes(self) -> dict[str, StateType]:
        """Return the state attributes."""
        if self.entity_description.attrs:
            return self.entity_description.attrs(self.coordinator.data)

        return {}


def _get_wind_direction(wind_direction_degree: float) -> str:  # noqa: PLR0911,PLR0912
    """Convert wind direction degree to named direction."""
    if 11.25 <= wind_direction_degree < 33.75:  # noqa: PLR2004
        return "nne"
    if 33.75 <= wind_direction_degree < 56.25:  # noqa: PLR2004
        return "ne"
    if 56.25 <= wind_direction_degree < 78.75:  # noqa: PLR2004
        return "ene"
    if 78.75 <= wind_direction_degree < 101.25:  # noqa: PLR2004
        return "e"
    if 101.25 <= wind_direction_degree < 123.75:  # noqa: PLR2004
        return "ese"
    if 123.75 <= wind_direction_degree < 146.25:  # noqa: PLR2004
        return "se"
    if 146.25 <= wind_direction_degree < 168.75:  # noqa: PLR2004
        return "sse"
    if 168.75 <= wind_direction_degree < 191.25:  # noqa: PLR2004
        return "s"
    if 191.25 <= wind_direction_degree < 213.75:  # noqa: PLR2004
        return "ssw"
    if 213.75 <= wind_direction_degree < 236.25:  # noqa: PLR2004
        return "sw"
    if 236.25 <= wind_direction_degree < 258.75:  # noqa: PLR2004
        return "wsw"
    if 258.75 <= wind_direction_degree < 281.25:  # noqa: PLR2004
        return "w"
    if 281.25 <= wind_direction_degree < 303.75:  # noqa: PLR2004
        return "wnw"
    if 303.75 <= wind_direction_degree < 326.25:  # noqa: PLR2004
        return "nw"
    if 326.25 <= wind_direction_degree < 348.75:  # noqa: PLR2004
        return "nnw"
    return "n"
