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

## Installation

Install the dependencies required for this library:

`pip install hamqa`

## Example Usage

Below are examples for **single value sensors** and **multi-sensor devices**.

### Single Value Sensors

Here is an example of how to register a single value sensor and publish its values:

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
single_sensor.publish_value(300)
# single_sensor.remove_device()
```

### Multi-Sensor Devices

Here is an example of how to register a device with multiple sensors and publish their values as a JSON object:

```python
import paho.mqtt.client as mqtt
from hamqa import HAMQTTDevice

ip_address = 'xxx.xxx.xxx.xxx'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect(ip_address, 1883, 60)

# Create a multi-sensor device (for temperature and humidity)
multi_sensor = HAMQTTDevice(client=mqtt_client, 
                            base_topic="home",
                            device_id="temp_hum_device")

# Add sensors for the multi-sensor device
multi_sensor.add_sensor(sensor_name="temperature",
                        kwargs={"device_class":"temperature", "unit_of_measurement":"°C"})
multi_sensor.add_sensor(sensor_name="humidity",
                        kwargs={"device_class":"humidity", "unit_of_measurement":"%"})

multi_sensor.register_sensors()
sensor_values = {"temperature": 22, "humidity": 60}
multi_sensor.publish_value(sensor_values)
# multi_sensor.remove_device()
```

## Key Functions

### `__init__(self, client, base_topic, device_id, path_pattern=None)`
Initializes a new device instance.

- `client`: The MQTT client instance.
- `base_topic`: The base MQTT topic for sensor values.
- `device_id`: Unique identifier for the device.
- `path_pattern`: Optional path pattern for Home Assistant MQTT discovery topics.

### `add_sensor(self, sensor_name, sensor_type, device_class, unit_of_measurement)`
Adds a new sensor to the device.

- `sensor_name`: The name of the sensor (e.g., `temperature`, `humidity`).
- `kwargs`: keyword arguments passed as a dictionary, e.g.:
  - `device_class`: The device class (e.g., `temperature`, `humidity`).
  - `unit_of_measurement`: Unit of measurement for the sensor (e.g., `°C`, `%`).

### `register_sensors(self)`
Registers all added sensors with Home Assistant, configuring MQTT discovery topics.

### `publish_value(self, value)`
Publishes the sensor value(s) to MQTT. If the device has multiple sensors, the values are published as a JSON object.

- `value`: Either a single value (for single-sensor devices) or a dictionary of values (for multi-sensor devices).

### `remove_device(self)`
Removes all sensors associated with the device from Home Assistant by publishing an empty payload to the discovery topics.

### `set_path_pattern(self, path_pattern)`
Sets a custom MQTT path pattern with placeholders such as `{device_id}`, `{sensor_type}`, and `{sensor_name}`.

## Path Structure

The MQTT paths for Home Assistant discovery and sensor values are handled automatically. The discovery paths will include `sensor_type`, while the state topics used for publishing sensor values will not.

### Home Assistant Discovery Path Example

For a temperature sensor, the discovery topic will look like:

`homeassistant/sensor/multi_sensor/temperature/config`


### Sensor Value Topic Example

For the same temperature sensor, the sensor value topic will be:

`home/multi_sensor/temperature/state`


### Multi-Sensor Value Publishing

When multiple sensors are registered for the same device, the values are published as a JSON object:

```json
{
  "temperature": 22,
  "humidity": 60
}
```

### Custom Path Patterns

You can customize the MQTT path for Home Assistant discovery by providing a custom path_pattern. The placeholders {device_id}, {sensor_type}, and {sensor_name} will be replaced with the appropriate values.

Example:

```python custom_pattern = "custom/{device_id}/{sensor_type}/{sensor_name}/config" multi_sensor.set_path_pattern(custom_pattern)```

This will change the discovery path to:

`custom/multi_sensor/sensor/temperature/config`