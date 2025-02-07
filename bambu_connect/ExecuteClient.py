import paho.mqtt.client as mqtt
import ssl
import json
import subprocess
import re


class ExecuteClient:
    """Client for sending commands to Bambu printer via MQTT.
    
    Handles G-code execution, print jobs, and printer information requests.
    """
    def __init__(self, hostname: str, access_code: str, serial: str):
        """Initialize execute client with connection details.
        
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code for authentication
            serial: Printer's serial number
        """
        self.hostname = hostname
        self.access_code = access_code
        self.serial = serial
        self.client = self.__setup_mqtt_client()

    def __setup_mqtt_client(self):
        """Configure and return MQTT client with security settings.
        
        Returns:
            Configured MQTT client instance
        """
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.username_pw_set("bblp", self.access_code)
        client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
        client.connect(self.hostname, 8883, 60)
        return client

    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.disconnect()

    def send_command(self, payload):
        """Send command payload to printer.
        
        Args:
            payload: Command data as dict or JSON string
        """
        if isinstance(payload, dict):
            payload = json.dumps(payload)
        self.client.loop_start()
        self.client.publish(f"device/{self.serial}/request", payload)
        self.client.loop_stop()

    def send_gcode(self, gcode):
        """Send G-code command to printer.
        
        Args:
            gcode: G-code command string
        """
        payload = {
            "print": {
                "command": "gcode_line",
                "sequence_id": 2006,
                "param": f"{gcode} \n"
            },
            "user_id": "1234567890"
        }
        payload_json = json.dumps(payload)
        self.send_command(payload_json)

    def dump_info(self):
        """Request full printer status dump. For minor print updates the printer will send them automatically."""
        payload = {
            "pushing": {
                "sequence_id": 1,
                "command": "pushall"
            },
            "user_id": "1234567890"
        }
        payload_json = json.dumps(payload)
        print(f"DEBUG: Sending info dump -> {payload_json}")  # Debug print
        self.send_command(payload_json)

    def start_print(self, file):
        """Start printing specified file.
        
        File must be pre-loaded using Bambu or Cura slicer.
        
        Args:
            file: Filename to print (without path)
        """
        payload = json.dumps(
            {
                "print": {
                    "sequence_id": 13,
                    "command": "project_file",
                    "param": "Metadata/plate_1.gcode",
                    "subtask_name": f"{file}",
                    "url": f"ftp://{file}",
                    "bed_type": "auto",
                    "timelapse": False,
                    "bed_leveling": True,
                    "flow_cali": False,
                    "vibration_cali": True,
                    "layer_inspect": False,
                    "use_ams": False,
                    "profile_id": "0",
                    "project_id": "0",
                    "subtask_id": "0",
                    "task_id": "0",
                }
            }
        )
        self.send_command(payload)
