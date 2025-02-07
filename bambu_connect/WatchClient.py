from .utils.models import PrinterStatus
import json
from typing import Optional, Callable

class WatchClient:
    """Client for monitoring printer status."""
    
    def __init__(self, hostname: str, access_code: str, serial: str, mqtt_client=None):
        """Initialize watch client.
        
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
        self.values = {}
        self.printerStatus = None
        self.message_callback = None
        self.on_connect_callback = None

    def start(self, message_callback: Optional[Callable[[PrinterStatus], None]] = None,
              on_connect_callback: Optional[Callable[[], None]] = None):
        """Start monitoring printer status."""
        if not self.client:
            raise RuntimeError("No MQTT client available")
            
        self.message_callback = message_callback
        self.on_connect_callback = on_connect_callback
        
        # Subscribe to printer status topic
        self.client.subscribe(f"device/{self.serial}/report")
        self.client.on_message = self.on_message
        
        if self.on_connect_callback:
            self.on_connect_callback()

    def stop(self):
        """Stop monitoring."""
        if self.client:
            self.client.unsubscribe(f"device/{self.serial}/report")


    def on_message(self, client, userdata, msg):
        """Process incoming printer status messages.
        
        Updates internal state and triggers callback if set.
        
        Args:
            client: MQTT client instance  
            userdata: User-defined data
            msg: MQTT message payload
        """
        doc = json.loads(msg.payload)
        try:
            if not doc:
                return

            self.values = dict(self.values, **doc["print"])
            self.printerStatus = PrinterStatus(**self.values)

            if self.message_callback:
                self.message_callback(self.printerStatus)
        except KeyError:
            pass
