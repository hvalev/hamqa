# port of hamqa designed to work with https://github.com/peterhinch/micropython-mqtt
# leveraging  resilient wifi and mqtt broker connection and async mqtt publishing
import ujson as json
from mqtt_as import MQTTClient


class HAMQTTDevice:
    def __init__(self, client: MQTTClient,
                 base_topic: str,
                 device_id: str,
                 device_type: str = 'sensor',
                 path_pattern: str = None,
                 logging_enabled: bool = False):
        """
        Initializes the HAMQTTDevice instance for a device.

        Args:
            client (MQTTClient): The MQTT client instance.
            base_topic (str): The base topic for the MQTT messages.
            device_id (str): The device ID for this device.
            path_pattern (str): Pattern for custom MQTT paths with placeholders, default is None.
                                Supported placeholders:
                                - {device_type}
                                - {device_id}
                                - {sensor_name}
        """
        self.client = client
        self.base_topic = base_topic
        self.device_id = device_id
        self.device_type = device_type
        self.sensors = {}
        self.logging_enabled = logging_enabled

        # Set the default path pattern for Home Assistant MQTT discovery
        self.path_pattern = path_pattern or "homeassistant/{device_type}/{device_id}/{sensor_name}/config"

        if not self.base_topic.endswith('/'):
            self.base_topic += '/'

    def _log(self, msg):
        if self.logging_enabled:
            print(msg)

    def _generate_mqtt_path(self, sensor_name):
        """Generates the MQTT path using the Home Assistant discovery pattern."""
        path = self.path_pattern.format(
            device_id=self.device_id,
            sensor_name=sensor_name,
            device_type=self.device_type
        )
        return path

    def add_sensor(self, sensor_name: str, kwargs):
        """
        Add a sensor to the device. Sensors will be registered in one go.

        Args:
            sensor_name (str): The name of the sensor (e.g., 'temperature', 'humidity').
            kwargs: Additional key-value pairs to append to the sensor dictionary.
        """
        sensor_info = {
            "name": f"{self.device_id}_{sensor_name}",
        }
        sensor_info.update(kwargs)
        self.sensors[sensor_name] = sensor_info

    def register_sensors(self):
        """Registers all sensors added to the device with Home Assistant via MQTT."""
        for sensor_name, sensor_config in self.sensors.items():
            sensor_config_topic = self._generate_mqtt_path(sensor_name)
            sensor_config.update({
                "state_topic": f"{self.base_topic}{self.device_id}",
                "value_template": f"{{{{ value_json.{sensor_name} }}}}"
            })

            await self.client.publish(sensor_config_topic, 
                                      json.dumps(sensor_config).encode('utf-8'), 
                                      qos=1, 
                                      retain=True)
            self._log(f"Sensor '{sensor_name}' registered at {sensor_config_topic}")

    def publish_value(self, value):
        """
        Publish values to the MQTT state topics. Can handle single values or multiple sensors as a JSON object.

        Args:
            value (dict or any): If dict, treats it as multi-sensor JSON;
                                 If a single value, publishes to a single sensor topic.
        """
        if isinstance(value, dict):
            # Multi-sensor mode: Publish a JSON object with multiple sensor values
            state_topic = f"{self.base_topic}{self.device_id}"
            await self.client.publish(state_topic, json.dumps(value).encode('utf-8'), qos=1)
            self._log(f"Published value '{value}' to {state_topic}")
        else:
            self._log("Error: Invalid Format. Publish values as dict using as follows {'sensor_name': value}")

    def remove_device(self):
        """Remove the registered device from Home Assistant."""
        for sensor_name in self.sensors:
            device_config_topic = f"{self._generate_mqtt_path(sensor_name)}/config"
            await self.client.publish(device_config_topic, "", qos=1, retain=True)
            self._log(f"Sensor '{sensor_name}' removed from {device_config_topic}")

    def set_path_pattern(self, path_pattern: str):
        """
        Set a custom MQTT path pattern with placeholders.

        Args:
            path_pattern (str): The new path pattern with placeholders.
                                Supported placeholders:
                                - {device_id}
                                - {sensor_name}
        """
        self.path_pattern = path_pattern

