"""Constants for the Meteo IMGW-PIB integration."""

from datetime import timedelta

DOMAIN = "meteo_imgw_pib"

ATTRIBUTION = "Data provided by IMGW-PIB"

CONF_STATION_ID = "station_id"

UPDATE_INTERVAL = timedelta(minutes=30)
