import json
from typing import Optional

class ExecuteClient:
    """Client for sending commands to Bambu printer."""
    
    def __init__(self, hostname: str, access_code: str, serial: str, mqtt_client=None):
        """Initialize execute client.
        
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code
            serial: Printer's serial number
            mqtt_client: Optional shared MQTT client instance
        """
        self.hostname = hostname
        self.access_code = access_code
        self.serial = serial
        self.client = mqtt_client  # Use shared client if provided

    def send_command(self, payload):
        """Send command payload to printer."""
        if not self.client:
            raise RuntimeError("No MQTT client available")
            
        if isinstance(payload, dict):
            payload = json.dumps(payload)
            
        self.client.publish(f"device/{self.serial}/request", payload)

    def send_gcode(self, gcode):
        """Send G-code command to printer."""
        payload = {
            "print": {
                "command": "gcode_line",
                "sequence_id": 2006,
                "param": f"{gcode} \n"
            },
            "user_id": "1234567890"
        }
        self.send_command(payload)

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
