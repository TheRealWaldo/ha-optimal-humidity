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
VERSION = "0.0.1"
ISSUE_URL = "https://github.com/TheRealWaldo/ha-optimal-humidity/issues"

ATTR_DEWPOINT = "dewpoint"
ATTR_ABSOLUTE_HUMIDITY = "absolute_humidity"
ATTR_OPTIMAL_HUMIDITY = "optimal_humidity"
ATTR_CRITICAL_HUMIDITY = "critical_humidity"
ATTR_MOLD_WARNING = "mold_warning"

CONF_CRITICAL_TEMP = "critical_temp_sensor"
CONF_INDOOR_HUMIDITY = "indoor_humidity_sensor"
CONF_INDOOR_TEMP = "indoor_temp_sensor"
CONF_INDOOR_PRESSURE = "indoor_pressure_sensor"
CONF_OPTIMAL_ABSOLUTE_HUMIDITY = "optimal_absolute_humidity"
# 7g/m³ seems to be a comfortable default
DEFAULT_OPTIMAL_ABSOLUTE_HUMIDITY = 7

DEFAULT_NAME = "Optimal Humidity"

SENSOR_TYPES = {
    ATTR_DEWPOINT: (
        "dewpoint",
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_ABSOLUTE_HUMIDITY: (
        "absolute_humidity",
        "g_H₂O g_Air⁻¹",
        "",
        "mdi:water",
    ),
    ATTR_OPTIMAL_HUMIDITY: (
        "optimal_humidity",
        PERCENTAGE,
        DEVICE_CLASS_HUMIDITY,
        "mdi:water-percent",
    ),
    ATTR_CRITICAL_HUMIDITY: (
        "critical_humidity",
        PERCENTAGE,
        DEVICE_CLASS_HUMIDITY,
        "mdi:water-percent",
    ),
}

DEFAULT_NAME = NAME
