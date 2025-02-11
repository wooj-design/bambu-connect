import json

class ExecuteClient:
    """Client for sending commands to Bambu printer."""
    
    def __init__(self, hostname: str, access_code: str, serial: str, mqtt_client=None):
        self.hostname = hostname
        self.access_code = access_code
        self.serial = serial
        self.client = mqtt_client

    def send_command(self, payload):
        """Send command payload to printer."""
        if not self.client:
            raise RuntimeError("No MQTT client available")
            
        if isinstance(payload, dict):
            payload = json.dumps(payload)
            
        self.client.publish(f"device/{self.serial}/request", payload)

    # Light Control
    def set_chamber_light(self, on: bool):
        """Control the chamber light."""
        command = {
            "system": {
                "sequence_id": "0",
                "command": "ledctrl",
                "led_node": "chamber_light",
                "led_mode": "on" if on else "off",
                "led_on_time": 500,
                "led_off_time": 500,
                "loop_times": 0,
                "interval_time": 0
            }
        }
        self.send_command(command)

    # Print Control Commands
    def set_print_speed(self, speed_profile: str):
        """Set the print speed profile."""
        command = {
            "print": {
                "sequence_id": "0",
                "command": "print_speed",
                "param": speed_profile
            }
        }
        self.send_command(command)

    def pause_print(self):
        """Pause the current print."""
        command = {"print": {"sequence_id": "0", "command": "pause"}}
        self.send_command(command)

    def resume_print(self):
        """Resume the paused print."""
        command = {"print": {"sequence_id": "0", "command": "resume"}}
        self.send_command(command)

    def stop_print(self):
        """Stop the current print."""
        command = {"print": {"sequence_id": "0", "command": "stop"}}
        self.send_command(command)

    def send_gcode(self, gcode: str):
        """Send G-code command to printer."""
        command = {
            "print": {
                "sequence_id": "0",
                "command": "gcode_line",
                "param": f"{gcode}\n"
            }
        }
        self.send_command(command)

    def start_print(self, file: str, use_ams: bool = False, enable_timelapse: bool = False):
        """Start printing specified file.
        
        Args:
            file: Filename to print
            use_ams: Whether to use Automatic Material System
            enable_timelapse: Whether to record timelapse
        """
        command = {
            "print": {
                "sequence_id": "0",
                "command": "project_file",
                "param": "Metadata/plate_1.gcode",
                "url": f"ftp://{file}",
                "bed_type": "auto",
                "timelapse": enable_timelapse,
                "bed_leveling": True,
                "flow_cali": True,
                "vibration_cali": True,
                "layer_inspect": True,
                "use_ams": use_ams,
                "ams_mapping": [0] if use_ams else None,
                "subtask_name": file,
                "profile_id": "0",
                "project_id": "0",
                "subtask_id": "0",
                "task_id": "0",
            }
        }
        self.send_command(command)

    def skip_objects(self, object_list: list):
        """Skip specified objects in current print.
        
        Args:
            object_list: List of object indices to skip
        """
        command = {
            "print": {
                "sequence_id": "0",
                "command": "skip_objects",
                "obj_list": object_list
            }
        }
        self.send_command(command)

    def get_version(self):
        """Request printer version information."""
        command = {"info": {"sequence_id": "0", "command": "get_version"}}
        self.send_command(command)

    def dump_info(self):
        """Request full printer status dump."""
        command = {"pushing": {"sequence_id": "0", "command": "pushall"}}
        self.send_command(command)

    def start_monitoring(self):
        """Start continuous status monitoring."""
        command = {"pushing": {"sequence_id": "0", "command": "start"}}
        self.send_command(command)