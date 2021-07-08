"""Calculates critical humidity given critical temperature, current temperature and current humidity."""
import logging
import bisect

import voluptuous as vol
import psychrolib

from .const import (
    DEFAULT_NAME,
    CONF_INDOOR_TEMP,
    CONF_INDOOR_HUMIDITY,
    CONF_CRITICAL_TEMP,
    CONF_INDOOR_PRESSURE,
    GRAMS_OF_WATER_TO_GRAMS_OF_AIR,
    IDEAL_HUMIDITY,
    IDEAL_TEMPERATURE,
    SENSOR_TYPES,
    ATTR_OPTIMAL_HUMIDITY,
    ATTR_CRITICAL_HUMIDITY,
    ATTR_DEWPOINT,
    ATTR_SPECIFIC_HUMIDITY,
    ATTR_MOLD_WARNING,
    ATTR_HUMIDEX,
    ATTR_HUMIDEX_COMFORT,
    CONF_OPTIMAL_SPECIFIC_HUMIDITY,
    ATTR_OPTIMAL_SPECIFIC_HUMIDITY,
)
from homeassistant import util
from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
)

from homeassistant.const import (
    ATTR_UNIT_OF_MEASUREMENT,
    CONF_NAME,
    CONF_SENSORS,
    CONF_TYPE,
    EVENT_HOMEASSISTANT_START,
    PERCENTAGE,
    PRESSURE_HPA,
    PRESSURE_PA,
    STATE_UNKNOWN,
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    DEVICE_CLASS_TEMPERATURE,
)
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, async_generate_entity_id
from homeassistant.helpers.event import async_track_state_change_event

_LOGGER = logging.getLogger(__name__)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_INDOOR_TEMP): cv.entity_id,
        vol.Required(CONF_CRITICAL_TEMP): cv.entity_id,
        vol.Required(CONF_INDOOR_HUMIDITY): cv.entity_id,
        vol.Optional(CONF_INDOOR_PRESSURE): cv.entity_id,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TYPE, default=ATTR_OPTIMAL_HUMIDITY): vol.All(
            cv.string,
            vol.In(
                (
                    ATTR_DEWPOINT,
                    ATTR_SPECIFIC_HUMIDITY,
                    ATTR_CRITICAL_HUMIDITY,
                    ATTR_OPTIMAL_HUMIDITY,
                    ATTR_MOLD_WARNING,
                    ATTR_HUMIDEX,
                    ATTR_HUMIDEX_COMFORT,
                    ATTR_OPTIMAL_SPECIFIC_HUMIDITY,
                )
            ),
        ),
        vol.Optional(CONF_OPTIMAL_SPECIFIC_HUMIDITY): cv.positive_float,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SENSORS): cv.schema_with_slug_keys(SENSOR_SCHEMA),
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up OptimalHumidity sensor."""

    for device, device_config in config[CONF_SENSORS].items():
        name = device_config.get(CONF_NAME, DEFAULT_NAME)
        indoor_temp_sensor = device_config.get(CONF_INDOOR_TEMP)
        critical_temp_sensor = device_config.get(CONF_CRITICAL_TEMP)
        indoor_humidity_sensor = device_config.get(CONF_INDOOR_HUMIDITY)
        indoor_pressure_sensor = device_config.get(CONF_INDOOR_PRESSURE)
        sensor_type = device_config.get(CONF_TYPE)
        optimal_specific_humidity = device_config.get(CONF_OPTIMAL_SPECIFIC_HUMIDITY)

        async_add_entities(
            [
                OptimalHumidity(
                    name,
                    device,
                    hass,
                    indoor_temp_sensor,
                    critical_temp_sensor,
                    indoor_humidity_sensor,
                    indoor_pressure_sensor,
                    sensor_type,
                    optimal_specific_humidity,
                )
            ],
            False,
        )


class OptimalHumidity(Entity):
    """Represents an OptimalHumidity sensor."""

    def __init__(
        self,
        name,
        device_id,
        hass,
        indoor_temp_sensor,
        critical_temp_sensor,
        indoor_humidity_sensor,
        indoor_pressure_sensor,
        sensor_type,
        optimal_specific_humidity,
    ):
        """Initialize the sensor."""
        self.hass = hass
        self._state = None
        self.entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, device_id, hass=hass
        )
        self._name = name
        self._indoor_temp_sensor = indoor_temp_sensor
        self._indoor_humidity_sensor = indoor_humidity_sensor
        self._critical_temp_sensor = critical_temp_sensor
        self._sensor_type = sensor_type
        self._is_metric = hass.config.units.is_metric

        psychrolib.SetUnitSystem(psychrolib.SI)
        self._indoor_pressure = psychrolib.GetStandardAtmPressure(hass.config.elevation)
        _LOGGER.debug(
            "Pressure at current elevation of %s m is %s Pa",
            hass.config.elevation,
            self._indoor_pressure,
        )

        if indoor_pressure_sensor is None:
            self._indoor_pressure_sensor = None
            self._entities = {
                self._indoor_temp_sensor,
                self._critical_temp_sensor,
                self._indoor_humidity_sensor,
            }
        else:
            self._indoor_pressure_sensor = indoor_pressure_sensor
            self._entities = {
                self._indoor_temp_sensor,
                self._critical_temp_sensor,
                self._indoor_humidity_sensor,
                self._indoor_pressure_sensor,
            }

        self._available = False
        self._dewpoint = None
        self._specific_humidity = None
        self._indoor_temp = None
        self._indoor_hum = None
        self._crit_temp = None
        self._crit_hum = None
        self._optimal_humidity = None
        self._mold_warning = None
        self._humidex = None
        self._humidex_comfort = None
        self._optimal_specific_humidity_from_config = optimal_specific_humidity
        self._optimal_humidity = self._optimal_specific_humidity_from_config

    async def async_added_to_hass(self):
        """Register callbacks."""

        @callback
        def critical_humidity_sensors_state_listener(event):
            """Handle for state changes for dependent sensors."""
            new_state = event.data.get("new_state")
            old_state = event.data.get("old_state")
            entity = event.data.get("entity_id")
            _LOGGER.debug(
                "Sensor state change for %s that had old state %s and new state %s",
                entity,
                old_state,
                new_state,
            )

            if self._update_sensor(entity, old_state, new_state):
                self.async_schedule_update_ha_state(True)

        @callback
        def critical_humidity_startup(event):
            """Add listeners."""
            _LOGGER.debug("Startup for %s", self.entity_id)

            async_track_state_change_event(
                self.hass,
                list(self._entities),
                critical_humidity_sensors_state_listener,
            )

            indoor_temp = self.hass.states.get(self._indoor_temp_sensor)
            crit_temp = self.hass.states.get(self._critical_temp_sensor)
            indoor_hum = self.hass.states.get(self._indoor_humidity_sensor)
            if self._indoor_pressure_sensor is not None:
                indoor_pressure = self.hass.states.get(self._indoor_pressure_sensor)

            schedule_update = self._update_sensor(
                self._indoor_temp_sensor, None, indoor_temp
            )

            schedule_update = (
                False
                if not self._update_sensor(self._critical_temp_sensor, None, crit_temp)
                else schedule_update
            )

            schedule_update = (
                False
                if not self._update_sensor(
                    self._indoor_humidity_sensor, None, indoor_hum
                )
                else schedule_update
            )

            if self._indoor_pressure_sensor is not None:
                schedule_update = (
                    False
                    if not self._update_sensor(
                        self._indoor_pressure_sensor, None, indoor_pressure
                    )
                    else schedule_update
                )

            if schedule_update:
                self.async_schedule_update_ha_state(True)

        self.hass.bus.async_listen_once(
            EVENT_HOMEASSISTANT_START, critical_humidity_startup
        )

    def _update_sensor(self, entity, old_state, new_state):
        """Update information based on new sensor states."""
        _LOGGER.debug("Sensor update for %s", entity)
        if new_state is None:
            return False

        if old_state is None and new_state.state == STATE_UNKNOWN:
            return False

        if entity == self._indoor_temp_sensor:
            self._indoor_temp = OptimalHumidity._update_temp_sensor(new_state)
        elif entity == self._critical_temp_sensor:
            self._crit_temp = OptimalHumidity._update_temp_sensor(new_state)
        elif entity == self._indoor_humidity_sensor:
            self._indoor_hum = OptimalHumidity._update_hum_sensor(new_state)
        elif entity == self._indoor_pressure_sensor:
            self._indoor_pressure = OptimalHumidity._update_pressure_sensor(new_state)

        return True

    @staticmethod
    def _update_temp_sensor(state):
        """Parse temperature sensor value."""
        _LOGGER.debug("Updating temp sensor with value %s", state.state)

        if state.state == STATE_UNKNOWN:
            _LOGGER.warning(
                "Unable to parse temperature sensor %s with state: %s",
                state.entity_id,
                state.state,
            )
            return None

        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        temp = util.convert(state.state, float)

        if temp is None:
            _LOGGER.warning(
                "Unable to convert temperature sensor %s with state: %s",
                state.entity_id,
                state.state,
            )
            return None

        if unit == TEMP_FAHRENHEIT:
            return util.temperature.fahrenheit_to_celsius(temp)
        if unit == TEMP_CELSIUS:
            return temp
        _LOGGER.warning(
            "Temp sensor %s has unsupported unit: %s (allowed: %s, %s)",
            state.entity_id,
            unit,
            TEMP_CELSIUS,
            TEMP_FAHRENHEIT,
        )

        return None

    @staticmethod
    def _update_hum_sensor(state):
        """Parse humidity sensor value."""
        _LOGGER.debug("Updating humidity sensor with value %s", state.state)

        if state.state == STATE_UNKNOWN:
            _LOGGER.warning(
                "Unable to parse humidity sensor %s, state: %s",
                state.entity_id,
                state.state,
            )
            return None

        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        hum = util.convert(state.state, float)

        if hum is None:
            _LOGGER.warning(
                "Unable to parse humidity sensor %s, state: %s",
                state.entity_id,
                state.state,
            )
            return None

        if unit != PERCENTAGE:
            _LOGGER.warning(
                "Humidity sensor %s has unsupported unit: %s (allowed: %s)",
                state.entity_id,
                unit,
                PERCENTAGE,
            )
            return None

        if hum > 100 or hum < 0:
            _LOGGER.warning(
                "Humidity sensor %s is out of range: %s %s",
                state.entity_id,
                hum,
                "(allowed: 0-100%)",
            )
            return None

        return hum / 100

    @staticmethod
    def _update_pressure_sensor(state):
        """Parse pressure sensor value."""
        _LOGGER.debug("Updating pressure sensor with value %s", state.state)

        if state.state == STATE_UNKNOWN:
            _LOGGER.warning(
                "Unable to parse pressure sensor %s, state: %s",
                state.entity_id,
                state.state,
            )
            return None

        unit = state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
        pressure = util.convert(state.state, float)

        if pressure is None:
            _LOGGER.warning(
                "Unable to parse pressure sensor %s, state: %s",
                state.entity_id,
                state.state,
            )
            return None

        if unit == PRESSURE_HPA:
            return pressure * 100

        if unit == PRESSURE_PA:
            return pressure

        _LOGGER.error(
            "Pressure sensor %s has unsupported unit: %s (allowed: %s, %s)",
            state.entity_id,
            unit,
            PRESSURE_HPA,
            PRESSURE_PA,
        )
        return None

    async def async_update(self):
        """Calculate latest state."""
        _LOGGER.debug("Update state for %s", self.entity_id)

        self._calc_dewpoint()
        # TODO: Discover critical temperature from a list of provided sensors (lowest/highest?)
        self._calc_critical_humidity()
        self._calc_optimal_specific_humidity()
        self._calc_specific_humidity()
        self._calc_optimal_humidity()
        self._set_mold_warning()
        self._calc_humidex()
        self._calc_humidex_comfort()

        self._set_state()

    def _set_state(self):
        """Set state based on sensor type"""
        if self._sensor_type == ATTR_DEWPOINT:
            self._state = self._dewpoint
        elif self._sensor_type == ATTR_SPECIFIC_HUMIDITY:
            self._state = self._specific_humidity
        elif self._sensor_type == ATTR_OPTIMAL_HUMIDITY:
            self._state = self._optimal_humidity
        elif self._sensor_type == ATTR_CRITICAL_HUMIDITY:
            self._state = self._crit_hum
        elif self._sensor_type == ATTR_MOLD_WARNING:
            self._state = self._mold_warning
        elif self._sensor_type == ATTR_HUMIDEX:
            self._state = self._humidex
        elif self._sensor_type == ATTR_HUMIDEX_COMFORT:
            self._state = self._humidex_comfort
        elif self._sensor_type == ATTR_OPTIMAL_SPECIFIC_HUMIDITY:
            self._state = self._optimal_specific_humidity

        if self._state is None:
            self._available = False
        else:
            self._available = True

    def _calc_humidex_comfort(self):
        if self._humidex is None:
            self._humidex_comfort = None
            return

        break_points = [29, 34, 39, 45, 54, 10000]
        comfort_level = [
            "Little or no discomfort",
            "Noticeable discomfort",
            "Evident discomfort",
            "Intense discomfort; avoid exertion",
            "Dangerous discomfort",
            "Heat stroke probable",
        ]
        self._humidex_comfort = comfort_level[
            bisect.bisect(break_points, self._humidex - 1)
        ]

    def _calc_humidex(self):
        """Calculate the humidex for the indoor air."""
        # It equals H = T + (0.5555 * (e - 10)), where T is the temperature in Celsius and e is the vapor pressure in millibars (mb)
        if None in (self._indoor_temp, self._indoor_hum):
            self._humidex = None
            return

        psychrolib.SetUnitSystem(psychrolib.SI)
        vapor_pressure = (
            psychrolib.GetVapPresFromRelHum(self._indoor_temp, self._indoor_hum) * 0.01
        )
        humidex = self._indoor_temp + (0.5555 * (vapor_pressure - 10))
        self._humidex = float(f"{humidex:.2f}")

    def _calc_dewpoint(self):
        """Calculate the dewpoint for the indoor air."""

        if None in (self._indoor_temp, self._indoor_hum):
            self._dewpoint = None
            return

        psychrolib.SetUnitSystem(psychrolib.SI)
        dewpoint = psychrolib.GetTDewPointFromRelHum(
            self._indoor_temp, self._indoor_hum
        )
        self._dewpoint = float(f"{dewpoint:.2f}")

        _LOGGER.debug("Dewpoint: %f %s", self._dewpoint, TEMP_CELSIUS)

    def _calc_specific_humidity(self):
        """Calculate the specific humidity in the room."""
        if None in (self._dewpoint, self._indoor_pressure):
            self._specific_humidity = None
            return

        psychrolib.SetUnitSystem(psychrolib.SI)

        specific_humidity = (
            psychrolib.GetSpecificHumFromHumRatio(
                psychrolib.GetHumRatioFromTDewPoint(
                    self._dewpoint, self._indoor_pressure
                )
            )
            * 1000
        )
        self._specific_humidity = float(f"{specific_humidity:.2f}")

        _LOGGER.debug(
            "Specific humidity: %s %s",
            self._specific_humidity,
            GRAMS_OF_WATER_TO_GRAMS_OF_AIR,
        )

    def _calc_critical_humidity(self):
        """Calculate the humidity at the critical temperature."""
        if None in (self._dewpoint, self._crit_temp):

            _LOGGER.debug(
                "Invalid inputs - dewpoint: %s %s crit_temp: %s %s",
                self._dewpoint,
                TEMP_CELSIUS,
                self._crit_temp,
                TEMP_CELSIUS,
            )
            self._crit_hum = None
            self._available = False
            return

        if self._dewpoint > self._crit_temp:
            _LOGGER.debug("Dewpoint is above dry bulb temperature")
            crit_humidity = 100
        else:
            psychrolib.SetUnitSystem(psychrolib.SI)
            crit_humidity = (
                psychrolib.GetRelHumFromTDewPoint(self._crit_temp, self._dewpoint) * 100
            )

        if crit_humidity > 100:
            self._crit_hum = 100
        elif crit_humidity < 0:
            self._crit_hum = 0
        else:
            self._crit_hum = float(f"{crit_humidity:.1f}")

        _LOGGER.debug("Critical humidity: %s", self._state)

    def _set_mold_warning(self):
        """Determine risk of mold"""
        if None in (self._indoor_hum, self._crit_hum):
            self._mold_warning = None
            return

        if float(self._indoor_hum) > 60:
            self._mold_warning = True
        elif self._crit_hum > 60:
            self._mold_warning = True
        else:
            self._mold_warning = False

        _LOGGER.debug("Risk of mold: %s", self._mold_warning)

    def _calc_optimal_specific_humidity(self):
        """Calculate the optimal specific humidity based on air pressure."""
        if self._indoor_pressure is None:
            self._optimal_specific_humidity = None
            return

        if not self._optimal_specific_humidity_from_config is None:
            self._optimal_specific_humidity = (
                self._optimal_specific_humidity_from_config
            )
            return

        psychrolib.SetUnitSystem(psychrolib.SI)
        optimal_specific_humidity = (
            psychrolib.GetSpecificHumFromHumRatio(
                psychrolib.GetHumRatioFromRelHum(
                    IDEAL_TEMPERATURE, IDEAL_HUMIDITY, self._indoor_pressure
                )
            )
            * 1000
        )
        self._optimal_specific_humidity = float(f"{optimal_specific_humidity:.2f}")
        _LOGGER.debug(
            "Optimal specific humidity set to %s%s",
            self._optimal_specific_humidity,
            GRAMS_OF_WATER_TO_GRAMS_OF_AIR,
        )

    def _calc_optimal_humidity(self):
        """Calculate the optimal humidity for the room."""

        if None in (
            self._indoor_temp,
            self._crit_temp,
            self._indoor_pressure,
            self._optimal_specific_humidity,
        ):
            self._optimal_humidity = None
            return

        psychrolib.SetUnitSystem(psychrolib.SI)

        comfortable_humidity = psychrolib.GetRelHumFromHumRatio(
            self._indoor_temp,
            float(self._optimal_specific_humidity) / 1000,
            self._indoor_pressure,
        )
        _LOGGER.debug("Comfortable relative humidity is: %s", comfortable_humidity)
        if comfortable_humidity > 1:
            _LOGGER.warn(
                "Not possible to reach a comfortable humidity at %s%s, will feel dry.",
                self._indoor_temp,
                TEMP_CELSIUS,
            )
            comfortable_humidity = 1

        comfortable_dew_point = psychrolib.GetTDewPointFromRelHum(
            self._crit_temp, comfortable_humidity
        )

        if comfortable_dew_point > self._indoor_temp:
            _LOGGER.debug("Comfortable dewpoint is above indoor dry bulb temperature")
            critical_humidity = 1
        else:
            critical_humidity = psychrolib.GetRelHumFromTDewPoint(
                self._indoor_temp, comfortable_dew_point
            )

        if critical_humidity > 0.6:
            # given condensation + mold forms at or above 60% RH at the _crit_temp; get dew point
            dew_point = psychrolib.GetTDewPointFromRelHum(self._crit_temp, 0.6)
            if dew_point > self._indoor_temp:
                _LOGGER.warn(
                    "Not possible to reach a mold free humidity at %s%s given a critical temperature of %s%s",
                    self._indoor_temp,
                    TEMP_CELSIUS,
                    self._crit_temp,
                    TEMP_CELSIUS,
                )
                self._optimal_humidity = None
                return
            else:
                optimal_humidity = (
                    psychrolib.GetRelHumFromTDewPoint(self._indoor_temp, dew_point)
                    * 100
                )
        else:
            optimal_humidity = comfortable_humidity * 100

        if optimal_humidity > 60:
            self._optimal_humidity = 60
        elif optimal_humidity < 0:
            self._optimal_humidity = 0
        else:
            self._optimal_humidity = float(f"{optimal_humidity:.1f}")

        _LOGGER.debug("Optimal humidity: %s %s", self._optimal_humidity, PERCENTAGE)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""

        if SENSOR_TYPES[self._sensor_type][3] == DEVICE_CLASS_TEMPERATURE:
            if self._is_metric:
                return TEMP_CELSIUS
            return TEMP_FAHRENHEIT

        return SENSOR_TYPES[self._sensor_type][1]

    @property
    def device_class(self):
        """Return device class."""
        return SENSOR_TYPES[self._sensor_type][2]

    @property
    def state_class(self):
        """Return state class."""
        return "measurement"

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return SENSOR_TYPES[self._sensor_type][3]

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def available(self):
        """Return the availability of this sensor."""
        return self._available

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._is_metric:
            return {
                ATTR_DEWPOINT: self._dewpoint,
                ATTR_SPECIFIC_HUMIDITY: self._specific_humidity,
                ATTR_OPTIMAL_HUMIDITY: self._optimal_humidity,
                ATTR_CRITICAL_HUMIDITY: self._crit_hum,
                ATTR_MOLD_WARNING: self._mold_warning,
                ATTR_HUMIDEX: self._humidex,
                ATTR_HUMIDEX_COMFORT: self._humidex_comfort,
                ATTR_OPTIMAL_SPECIFIC_HUMIDITY: self._optimal_specific_humidity,
            }

        dewpoint = (
            util.temperature.celsius_to_fahrenheit(self._dewpoint)
            if self._dewpoint is not None
            else None
        )

        humidex = (
            util.temperature.celsius_to_fahrenheit(self._humidex)
            if self._humidex is not None
            else None
        )

        return {
            ATTR_DEWPOINT: dewpoint,
            ATTR_SPECIFIC_HUMIDITY: self._specific_humidity,
            ATTR_OPTIMAL_HUMIDITY: self._optimal_humidity,
            ATTR_CRITICAL_HUMIDITY: self._crit_hum,
            ATTR_MOLD_WARNING: self._mold_warning,
            ATTR_HUMIDEX: humidex,
            ATTR_HUMIDEX_COMFORT: self._humidex_comfort,
            ATTR_OPTIMAL_SPECIFIC_HUMIDITY: self._optimal_specific_humidity,
        }
