"""IMGW-PIB weather platform."""

from homeassistant.components.weather import WeatherEntity
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import MeteoImgwPibConfigEntry, MeteoImgwPibDataUpdateCoordinator
from .entity import MeteoImgwPibEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: MeteoImgwPibConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add a Meteo IMGW-PIB weather entity from a config_entry."""
    coordinator = entry.runtime_data.coordinator

    if not coordinator.data.proxy_used:
        return

    async_add_entities([MeteoImgwPibWeather(coordinator)])


class MeteoImgwPibWeather(MeteoImgwPibEntity, WeatherEntity):
    """Define Meteo IMGW-PIB weather entity."""

    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.METERS_PER_SECOND

    def __init__(
        self,
        coordinator: MeteoImgwPibDataUpdateCoordinator,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        self._attr_unique_id = coordinator.station_id

    @property
    def available(self) -> bool:
        """Return if the entity is available."""
        return super().available and self.coordinator.data.proxy_used

    @property
    def condition(self) -> str | None:
        """Return the current weather condition."""
        return self.coordinator.data.condition

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.coordinator.data.temperature.value

    @property
    def humidity(self) -> float | None:
        """Return the current humidity."""
        return self.coordinator.data.humidity.value

    @property
    def native_pressure(self) -> float | None:
        """Return the current pressure."""
        return self.coordinator.data.pressure.value

    @property
    def native_wind_speed(self) -> float | None:
        """Return the current wind speed."""
        return self.coordinator.data.wind_speed.value

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the current wind gust speed."""
        return self.coordinator.data.wind_gust.value

    @property
    def wind_bearing(self) -> float | None:
        """Return the current wind bearing."""
        return self.coordinator.data.wind_direction.value

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the current apparent temperature."""
        return self.coordinator.data.apparent_temperature.value

    @property
    def cloud_coverage(self) -> float | None:
        """Return the current cloud coverage."""
        return self.coordinator.data.cloud_coverage.value
