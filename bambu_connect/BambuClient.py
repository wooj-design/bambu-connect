import paho.mqtt.client as mqtt
import ssl
import time
from typing import Optional, Callable
from .CameraClient import CameraClient
from .WatchClient import WatchClient
from .ExecuteClient import ExecuteClient
from .FileClient import FileClient
from .utils.models import PrinterStatus

class BambuClient:
    """Main client interface for Bambu printer control."""
    
    def __init__(self, hostname: str, access_code: str, serial: str):
        """Initialize the BambuClient with shared MQTT connection.
        
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code for authentication
            serial: Printer's serial number
        """
        self.hostname = hostname
        self.access_code = access_code
        self.serial = serial
        self.connected = False
        
        # Create shared MQTT client
        self.mqtt_client = self._setup_mqtt_client()
        
        # Initialize sub-clients with shared MQTT client
        self.cameraClient = CameraClient(hostname, access_code)
        self.watchClient = WatchClient(hostname, access_code, serial, self.mqtt_client)
        self.executeClient = ExecuteClient(hostname, access_code, serial, self.mqtt_client)
        self.fileClient = FileClient(hostname, access_code, serial)

    def _setup_mqtt_client(self) -> mqtt.Client:
        """Configure and connect shared MQTT client."""
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.username_pw_set("bblp", self.access_code)
        client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
        
        # Set up callbacks
        client.on_connect = self._on_connect
        client.on_disconnect = self._on_disconnect
        
        try:
            client.connect(self.hostname, 8883, 60)
            client.loop_start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                raise ConnectionError("Failed to connect to printer")
            
            return client
            
        except Exception as e:
            if client:
                client.loop_stop()
                client.disconnect()
            raise ConnectionError(f"Failed to connect to printer: {str(e)}")

    def _on_connect(self, client, userdata, flags, rc):
        """Handle successful connection."""
        if rc == 0:
            self.connected = True
        else:
            print(f"Connection failed with code {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection."""
        self.connected = False
        print("Disconnected from printer")

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'mqtt_client'):
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

    ############# Camera Wrappers #############
    def start_camera_stream(self, img_callback):
        self.cameraClient.start_stream(img_callback)

    def stop_camera_stream(self):
        self.cameraClient.stop_stream()

    def capture_camera_frame(self):
        return self.cameraClient.capture_frame()

    ############# WatchClient Wrappers #############
    def start_watch_client(
        self,
        message_callback: Optional[Callable[[PrinterStatus], None]] = None,
        on_connect_callback: Optional[Callable[[], None]] = None,
    ):
        self.watchClient.start(message_callback, on_connect_callback)

    def stop_watch_client(self):
        self.watchClient.stop()

    ############# ExecuteClient Wrappers #############
    def set_chamber_light(self, on: bool):
        """Control the chamber light."""
        self.executeClient.set_chamber_light(on)

    def set_print_speed(self, speed_profile: str):
        """Set the print speed profile (silent/normal/sport/ludicrous)."""
        self.executeClient.set_print_speed(speed_profile)

    def pause_print(self):
        """Pause the current print."""
        self.executeClient.pause_print()

    def resume_print(self):
        """Resume the paused print."""
        self.executeClient.resume_print()

    def stop_print(self):
        """Stop the current print."""
        self.executeClient.stop_print()

    def send_gcode(self, gcode: str):
        """Send G-code command to printer."""
        self.executeClient.send_gcode(gcode)

    def start_print(self, file: str, use_ams: bool = False, enable_timelapse: bool = False):
        """Start printing specified file."""
        self.executeClient.start_print(file, use_ams, enable_timelapse)

    def skip_objects(self, object_list: list):
        """Skip specified objects in current print."""
        self.executeClient.skip_objects(object_list)

    def get_version(self):
        """Request printer version information."""
        self.executeClient.get_version()

    def dump_info(self):
        """Request full printer status dump."""
        self.executeClient.dump_info()

    def start_monitoring(self):
        """Start continuous status monitoring."""
        self.executeClient.start_monitoring()

    ############# FileClient Wrappers #############
    def get_files(self, path="/", extension=".3mf"):
        return self.fileClient.get_files(path, extension)

    def download_file(
        self, local_path: str, remote_path="/timelapse", extension="", verbose=True
    ):
        return self.fileClient.download_file(
            remote_path, local_path=local_path, verbose=verbose
        )
