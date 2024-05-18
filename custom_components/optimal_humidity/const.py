"""Constants for optimal_humidity."""

from homeassistant.components.sensor import SensorDeviceClass

from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)

NAME = "Optimal Humidity"
DOMAIN = "optimal_humidity"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "v2.0.10"
ISSUE_URL = "https://github.com/TheRealWaldo/ha-optimal-humidity/issues"

ATTR_DEWPOINT = "dewpoint"
ATTR_SPECIFIC_HUMIDITY = "specific_humidity"
ATTR_OPTIMAL_HUMIDITY = "optimal_humidity"
ATTR_COMFORTABLE_SPECIFIC_HUMIDITY = "comfortable_specific_humidity"
ATTR_CRITICAL_HUMIDITY = "critical_humidity"
ATTR_MOLD_WARNING = "mold_warning"
ATTR_HUMIDEX = "humidex"
ATTR_HUMIDEX_COMFORT = "humidex_comfort"
ATTR_OPTIMAL_HUMIDEX = "optimal_humidex"
ATTR_COMFORTABLE_HUMIDITY = "comfortable_humidity"

CONF_CRITICAL_TEMP = "critical_temp_sensor"
CONF_INDOOR_HUMIDITY = "indoor_humidity_sensor"
CONF_INDOOR_TEMP = "indoor_temp_sensor"
CONF_INDOOR_PRESSURE = "indoor_pressure_sensor"
CONF_COMFORTABLE_SPECIFIC_HUMIDITY = "comfortable_specific_humidity"

IDEAL_HUMIDITY = 0.45
IDEAL_TEMPERATURE = 21

DEFAULT_NAME = "Optimal Humidity"

MILLIGRAMS_OF_WATER_TO_GRAMS_OF_AIR = "mg_H₂O g_Air⁻¹"
SENSOR_TYPES = {
    ATTR_DEWPOINT: (
        ATTR_DEWPOINT,
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_SPECIFIC_HUMIDITY: (
        ATTR_SPECIFIC_HUMIDITY,
        MILLIGRAMS_OF_WATER_TO_GRAMS_OF_AIR,
        "",
        "mdi:water",
    ),
    ATTR_OPTIMAL_HUMIDITY: (
        ATTR_OPTIMAL_HUMIDITY,
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
        "mdi:water-percent",
    ),
    ATTR_CRITICAL_HUMIDITY: (
        ATTR_CRITICAL_HUMIDITY,
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
        "mdi:water-percent",
    ),
    ATTR_HUMIDEX: (
        ATTR_HUMIDEX,
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_HUMIDEX_COMFORT: (
        ATTR_HUMIDEX_COMFORT,
        None,
        None,
        "hass:account",
    ),
    ATTR_COMFORTABLE_SPECIFIC_HUMIDITY: (
        ATTR_COMFORTABLE_SPECIFIC_HUMIDITY,
        MILLIGRAMS_OF_WATER_TO_GRAMS_OF_AIR,
        "",
        "mdi:water",
    ),
    ATTR_OPTIMAL_HUMIDEX: (
        ATTR_OPTIMAL_HUMIDEX,
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
        "hass:thermometer",
    ),
    ATTR_COMFORTABLE_HUMIDITY: (
        ATTR_COMFORTABLE_HUMIDITY,
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
        "mdi:water-percent",
    ),
}

DEFAULT_NAME = NAME
