"""IMGW-PIB weather platform."""

from homeassistant.components.weather import (
    ATTR_FORECAST_CLOUD_COVERAGE,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_HUMIDITY,
    ATTR_FORECAST_IS_DAYTIME,
    ATTR_FORECAST_NATIVE_APPARENT_TEMP,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_PRESSURE,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_NATIVE_WIND_GUST_SPEED,
    ATTR_FORECAST_NATIVE_WIND_SPEED,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    Forecast,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import UnitOfPressure, UnitOfSpeed, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from imgw_pib.utils import parse_weather_icon

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
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_TWICE_DAILY | WeatherEntityFeature.FORECAST_HOURLY
    )

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

    async def async_forecast_twice_daily(self) -> list[Forecast] | None:
        """Return the twice daily forecast in native units."""
        if (
            not hasattr(self.coordinator.data, "forecast_twice_daily")
            or self.coordinator.data.forecast_twice_daily is None
        ):
            return None

        return [
            {
                ATTR_FORECAST_TIME: item["date"].replace("Z", "+00:00"),
                ATTR_FORECAST_IS_DAYTIME: item["is_day"],
                ATTR_FORECAST_CLOUD_COVERAGE: item["cloud_avg"],
                ATTR_FORECAST_NATIVE_TEMP: item["temp_max"],
                ATTR_FORECAST_NATIVE_TEMP_LOW: item["temp_min"],
                ATTR_FORECAST_NATIVE_PRECIPITATION: item["precip"],
                ATTR_FORECAST_NATIVE_WIND_SPEED: item["wind_max"],
                ATTR_FORECAST_CONDITION: parse_weather_icon(item.get("icon")),
            }
            for item in self.coordinator.data.forecast_twice_daily
        ]

    async def async_forecast_hourly(self) -> list[Forecast] | None:
        """Return the hourly forecast in native units."""
        if (
            not hasattr(self.coordinator.data, "forecast_hourly")
            or self.coordinator.data.forecast_hourly is None
        ):
            return None

        return [
            {
                ATTR_FORECAST_TIME: item["date"].replace("Z", "+00:00"),
                ATTR_FORECAST_CLOUD_COVERAGE: item["cloud"],
                ATTR_FORECAST_NATIVE_APPARENT_TEMP: item["feels_like"],
                ATTR_FORECAST_HUMIDITY: item["humidity"],
                ATTR_FORECAST_NATIVE_PRESSURE: item["pressure"],
                ATTR_FORECAST_NATIVE_TEMP: item["temp"],
                ATTR_FORECAST_NATIVE_PRECIPITATION: item["precip"],
                ATTR_FORECAST_NATIVE_WIND_SPEED: item["wind_speed"],
                ATTR_FORECAST_NATIVE_WIND_GUST_SPEED: item["wind_gust"],
                ATTR_FORECAST_WIND_BEARING: item["wind_dir"],
                ATTR_FORECAST_CONDITION: parse_weather_icon(item["icon"]),
            }
            for item in self.coordinator.data.forecast_hourly
        ]
