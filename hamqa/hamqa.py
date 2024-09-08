import json
import logging

import paho.mqtt.client as mqtt


class HAMQTTDevice:
    def __init__(self, client: mqtt.Client, 
                 base_topic: str, 
                 device_id: str, 
                 device_type: str = 'sensor', 
                 path_pattern: str = None,
                 logging_enabled: bool = False):
        """
        Initializes the HAMQTTRegister instance for a device.
        
        Args:
            client (mqtt.Client): The MQTT client instance.
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
        
        if self.logging_enabled:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _log(self, msg, level='info'):
        if level == 'info':
            self.logger.info(msg)
        elif level == 'error':
            self.logger.error(msg)
        else:
            self.logger.debug(msg)

    def _generate_mqtt_path(self, sensor_name):
        """Generates the MQTT path using the Home Assistant discovery pattern."""
        path = self.path_pattern.format(
            device_id=self.device_id,
            sensor_name=sensor_name,
            device_type=self.device_type
        )
        return path

    def add_sensor(self, sensor_name: str, device_class: str, unit_of_measurement: str):
        """
        Add a sensor to the device. Sensors will be registered in one go.
        
        Args:
            sensor_name (str): The name of the sensor (e.g., 'temperature', 'humidity').
            device_class (str): The class of the sensor (e.g., 'temperature', 'humidity').
            unit_of_measurement (str): The unit of measurement (e.g., '°C', '%').
        """
        self.sensors[sensor_name] = {
            "device_class": device_class,
            "name": f"{self.device_id}_{sensor_name}",
            "unit_of_measurement": unit_of_measurement,
        }

    def register_sensors(self):
        """Registers all sensors added to the device with Home Assistant via MQTT."""
        for sensor_name, sensor_config in self.sensors.items():
            sensor_config_topic = self._generate_mqtt_path(sensor_name)
            if len(self.sensors) > 1:
                state_topic = f"{self.base_topic}{self.device_id}/state"
            else:
                state_topic = f"{self.base_topic}{self.device_id}/{sensor_name}/state"
            value_template = f"{{{{ value_json.{sensor_name} }}}}" if len(self.sensors) > 1 else "{{{{ value }}}}"

            # Update state topic and value template for either single or multi-sensor device
            sensor_config.update({
                "state_topic": state_topic,
                "value_template": value_template
            })
            
            self.client.publish(sensor_config_topic, json.dumps(sensor_config), retain=True)
            self._log(f"{sensor_config['device_class'].capitalize()} sensor '{sensor_name}' "
                      f"registered at {sensor_config_topic}", 'info')

    def publish_value(self, value):
        """
        Publish values to the MQTT state topics. Can handle single values or multiple sensors as a JSON object.
        
        Args:
            value (dict or any): If dict, treats it as multi-sensor JSON; 
                                 If a single value, publishes to a single sensor topic.
        """
        if isinstance(value, dict):
            # Multi-sensor mode: Publish a JSON object with multiple sensor values
            state_topic = f"{self.base_topic}{self.device_id}/state"
            self.client.publish(state_topic, json.dumps(value))
            self._log(f"Published multi-sensor JSON '{value}' to {state_topic}", 'info')
        else:
            # Single sensor mode: Publish to the individual sensor state topic
            if len(self.sensors) == 1:
                sensor_name = next(iter(self.sensors))
                state_topic = f"{self.base_topic}{self.device_id}/{sensor_name}/state"
                self.client.publish(state_topic, str(value))
                self._log(f"Published value '{value}' to {state_topic}", 'info')
            else:
                self._log("Error: Single value provided but multiple sensors registered", 'error')

    def remove_device(self):
        """Remove the registered device from Home Assistant"""
        for sensor_name in self.sensors.items():
            device_config_topic = f"{self._generate_mqtt_path(sensor_name)}/config"
            self.client.publish(device_config_topic, "", retain=True)
            self._log(f"Sensor '{sensor_name}' removed from {device_config_topic}", 'info')

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

