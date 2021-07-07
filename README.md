# ha-optimal-humidity

[![hacs][hacsbadge]][hacs]
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[Home Assistant](https:/home-assistant.io) Sensor Integration to assist with maintaining the optimal humidity in your home!

Please see this [Discussion on Humidity](https://www.weather.gov/lmk/humidity) for a good overview of some of the terms used in this integration.

Many signs of inadequate humidity levels can occur, but here are a few common examples:

Too much humidity
* Condensation on windows in winter
* Uncomfortable feeling in summer
* Moisture stains on walls
* Musty smell
* Mold

Not enough humidity
* Itchy eyes, nose, and skin
* Dry skin and chapped lips
* Static
* Damaged wood floors

Most systems use relative humidity as set-points for humidification systems, which of course, is relative to temperature.  That means setting a fixed relative humidity would also require a fixed temperature.  In an ideal world, we would maintain a fixed temperature, but in most environments, that comes at a high cost.

Apparent temperature, or the temperature we feel, is also impacted by humidity.  Therefore, we can maintain a comfortable environment by controlling humidity more fluidly, and also control costs, as it is significantly less expensive to add humidity to the air than heat.

In addition to how we feel, other organisms love humid environments, such as mold.  Mold can have detrimental effects on health and can do irreparable damage to your home.  Condensation on windows is also a factor. This sensor also considers these factors by allowing one to assign a critical temperature sensor for the coldest point in your controlled location.  For example, you can place critical temperature sensors at your window or on your basement floor.

This sensor integration attempts to determine the optimal relative humidity set point for your humidifiers and dehumidifiers based on those factors.

## Installation

### MANUAL INSTALLATION

1. Download the zip file from
   [latest release](https://github.com/TheRealWaldo/ha-optimal-humidity/releases/latest).
2. Unpack the release and copy the `custom_components/optimal_humidity` directory into the `custom_components` directory of your Home Assistant installation.
3. Configure the `optimal_humidity` sensor.
4. Restart Home Assistant.

## Configuration

```yaml
# Example configuration.yaml entry

sensor:
  - platform: optimal_humidity
    sensors:
      test_optimal_humidity:
        name: "Optimal Humidity"
        type: optimal_humidity
        indoor_temp_sensor: sensor.indoor_temp
        indoor_humidity_sensor: sensor.indoor_humidity
        critical_temp_sensor: sensor.critical_temp
        indoor_pressure_sensor: sensor.indoor_pressure
```

### Main Options

|Parameter |Required|Description
|:---|---|---
| `name` | No | Friendly name **Default**: Optimal Humidity
| `type` | No | The type of sensor to use for the primary state.  One of `optimal_humidity`, `specific_humidity`, `dewpoint`, `critical_humidity`, or `mold_warning` **Default**: `optimal_humidity`
| `indoor_temp_sensor` | Yes | Temperature sensor to use for calculations. Typically the warmest sensor in the room.
| `critical_temp_sensor` | Yes | Temperature sensor to use for calculations. Typically the coldest sensor in the room.
| `indoor_pressure_sensor` | No | Pressue sensor to use for calculations.
| `indoor_humidity_sensor` | Yes | Humidity sensor to use for calculations. Typically in the same location as the `indoor_temp_sensor`.
| `optimal_specific_humidity` | No | Optimal specific humidity in grams of H₂O per gram of Air⁻¹ **Default**: 7

## Contributions are welcome!

If you want to contribute to this integration, please read the [Contribution guidelines](CONTRIBUTING.md)


[commits]: https://github.com/TheRealWaldo/ha-optimal-humidity/commits/main
[commits-shield]: https://img.shields.io/github/commit-activity/m/therealwaldo/ha-optimal-humidity?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/therealwaldo/ha-optimal-humidity.svg?style=for-the-badge
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/therealwaldo/ha-optimal-humidity?include_prereleases&style=for-the-badge
[releases]: https://github.com/TheRealWaldo/ha-optimal-humidity/releases
