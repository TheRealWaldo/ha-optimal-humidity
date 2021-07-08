"""Constants for optimal_humidity."""

from homeassistant.components.sensor import (
    DEVICE_CLASS_HUMIDITY,
    DEVICE_CLASS_TEMPERATURE,
)

from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
)

NAME = "Optimal Humidity"
DOMAIN = "optimal_humidity"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.1.1"
ISSUE_URL = "https://github.com/TheRealWaldo/ha-optimal-humidity/issues"

ATTR_DEWPOINT = "dewpoint"
ATTR_SPECIFIC_HUMIDITY = "specific_humidity"
ATTR_OPTIMAL_HUMIDITY = "optimal_humidity"
ATTR_CRITICAL_HUMIDITY = "critical_humidity"
ATTR_MOLD_WARNING = "mold_warning"
ATTR_HUMIDEX = "humidex"
ATTR_HUMIDEX_COMFORT = "humidex_comfort"

CONF_CRITICAL_TEMP = "critical_temp_sensor"
CONF_INDOOR_HUMIDITY = "indoor_humidity_sensor"
CONF_INDOOR_TEMP = "indoor_temp_sensor"
CONF_INDOOR_PRESSURE = "indoor_pressure_sensor"
CONF_OPTIMAL_SPECIFIC_HUMIDITY = "optimal_specific_humidity"
# 7.8g_H₂O g_Air⁻¹ seems to be a comfortable default based on 45% RH
# and 21°C being the ideal conditions for humans
DEFAULT_OPTIMAL_SPECIFIC_HUMIDITY = 7.8

DEFAULT_NAME = "Optimal Humidity"

SENSOR_TYPES = {
    ATTR_DEWPOINT: (
        ATTR_DEWPOINT,
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_SPECIFIC_HUMIDITY: (
        ATTR_SPECIFIC_HUMIDITY,
        "g_H₂O g_Air⁻¹",
        "",
        "mdi:water",
    ),
    ATTR_OPTIMAL_HUMIDITY: (
        ATTR_OPTIMAL_HUMIDITY,
        PERCENTAGE,
        DEVICE_CLASS_HUMIDITY,
        "mdi:water-percent",
    ),
    ATTR_CRITICAL_HUMIDITY: (
        ATTR_CRITICAL_HUMIDITY,
        PERCENTAGE,
        DEVICE_CLASS_HUMIDITY,
        "mdi:water-percent",
    ),
    ATTR_HUMIDEX: (
        ATTR_HUMIDEX,
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_HUMIDEX_COMFORT: (
        ATTR_HUMIDEX_COMFORT,
        None,
        None,
        "hass:account",
    ),
}

DEFAULT_NAME = NAME
