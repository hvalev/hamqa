# hamqa - Home Assistant MQTT autodiscovery sensor registration library
[![build](https://github.com/hvalev/hamqa/actions/workflows/build.yml/badge.svg)](https://github.com/hvalev/hamqa/actions/workflows/build.yml)
[![Downloads](https://static.pepy.tech/badge/hamqa)](https://pepy.tech/project/hamqa)
[![Downloads](https://static.pepy.tech/badge/hamqa/month)](https://pepy.tech/project/hamqa)
[![Downloads](https://static.pepy.tech/badge/hamqa/week)](https://pepy.tech/project/hamqa)

The **hamqa** library provides an easy way to register and manage MQTT-based sensors for Home Assistant. It handles both devices producing a single or multiple values and allows to easily push updates from those devices to be consumed by Home Assistant.

## Features

- Register and manage multiple sensors for a single device.
- Automatically handle Home Assistant MQTT discovery.
- Publish sensor values in both single-sensor and multi-sensor devices.
- Flexible configuration of MQTT topic paths.
- Easily remove devices from Home Assistant via MQTT.
- Includes a micropython equivalent implementation

## Installation

Install the dependencies required for this library:

`pip install hamqa`

## Example Usage

Below are examples for one or more sensors.

```python
import paho.mqtt.client as mqtt
from hamqa import HAMQTTDevice

ip_address = 'xxx.xxx.xxx.xxx'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(ip_address, 1883, 60)

single_sensor = HAMQTTDevice(client=mqtt_client, 
                          base_topic="home",
                          device_id="lx_device")

single_sensor.add_sensor(sensor_name="illumination", 
                         kwargs={"device_class":"illuminance", "unit_of_measurement":"lx"})

single_sensor.register_sensors()
single_sensor.publish_value({'illumination': 300})
```

```python
import paho.mqtt.client as mqtt
from hamqa import HAMQTTDevice

ip_address = 'xxx.xxx.xxx.xxx'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(ip_address, 1883, 60)

multi_sensor = HAMQTTDevice(client=mqtt_client, 
                            base_topic="home",
                            device_id="temp_hum_device")

multi_sensor.add_sensor(sensor_name="temperature",
                        kwargs={"device_class":"temperature", "unit_of_measurement":"°C"})
multi_sensor.add_sensor(sensor_name="humidity",
                        kwargs={"device_class":"humidity", "unit_of_measurement":"%"})

multi_sensor.register_sensors()
sensor_values = {"temperature": 22, "humidity": 60}
multi_sensor.publish_value(sensor_values)
```

## Home Assistant Discovery Path Example

For a temperature sensor, the discovery topic will look like:

`homeassistant/sensor/multi_sensor/temperature/config`


## Sensor Value Topic Example

For the same temperature sensor, the sensor value topic will be:

`home/multi_sensor/temperature/state`


## Custom Path Patterns

You can customize the MQTT path for Home Assistant discovery by providing a custom path_pattern. The placeholders {device_id}, {sensor_type}, and {sensor_name} will be replaced with the appropriate values.

Example:

```python
custom_pattern = "custom/{device_id}/{sensor_type}/{sensor_name}/config" 
multi_sensor.set_path_pattern(custom_pattern)
```

This will change the discovery path to:

`custom/multi_sensor/sensor/temperature/config`