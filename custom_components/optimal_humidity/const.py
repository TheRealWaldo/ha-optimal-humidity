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
ATTR_OPTIMAL_SPECIFIC_HUMIDITY = "optimal_specific_humidity"
ATTR_CRITICAL_HUMIDITY = "critical_humidity"
ATTR_MOLD_WARNING = "mold_warning"
ATTR_HUMIDEX = "humidex"
ATTR_HUMIDEX_COMFORT = "humidex_comfort"
ATTR_OPTIMAL_HUMIDEX = "optimal_humidex"

CONF_CRITICAL_TEMP = "critical_temp_sensor"
CONF_INDOOR_HUMIDITY = "indoor_humidity_sensor"
CONF_INDOOR_TEMP = "indoor_temp_sensor"
CONF_INDOOR_PRESSURE = "indoor_pressure_sensor"
CONF_OPTIMAL_SPECIFIC_HUMIDITY = "optimal_specific_humidity"

IDEAL_HUMIDITY = 0.45
IDEAL_TEMPERATURE = 21

DEFAULT_NAME = "Optimal Humidity"

GRAMS_OF_WATER_TO_GRAMS_OF_AIR = "g_H₂O g_Air⁻¹"
SENSOR_TYPES = {
    ATTR_DEWPOINT: (
        ATTR_DEWPOINT,
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_SPECIFIC_HUMIDITY: (
        ATTR_SPECIFIC_HUMIDITY,
        GRAMS_OF_WATER_TO_GRAMS_OF_AIR,
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
    ATTR_OPTIMAL_SPECIFIC_HUMIDITY: (
        ATTR_OPTIMAL_SPECIFIC_HUMIDITY,
        GRAMS_OF_WATER_TO_GRAMS_OF_AIR,
        "",
        "mdi:water",
    ),
    ATTR_OPTIMAL_HUMIDEX: (
        ATTR_OPTIMAL_HUMIDEX,
        TEMP_CELSIUS,
        DEVICE_CLASS_TEMPERATURE,
        "hass:thermometer",
    ),
}

DEFAULT_NAME = NAME
