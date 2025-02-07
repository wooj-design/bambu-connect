from .utils.models import PrinterStatus
import json
import ssl
from typing import Any, Callable, Dict, Optional

import paho.mqtt.client as mqtt


class WatchClient:
    """Client for monitoring printer status via MQTT connection.
   
    Maintains connection to printer and processes status updates through callbacks.
    """
    def __init__(self, hostname: str, access_code: str, serial: str):
        """Initialize watch client with connection details.
       
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code for authentication  
            serial: Printer's serial number
        """
        self.hostname = hostname
        self.access_code = access_code
        self.serial = serial
        self.client = self.__setup_mqtt_client()
        self.values = {}
        self.printerStatus = None
        self.message_callback = None

    def __setup_mqtt_client(self) -> mqtt.Client:
        """Configure and return MQTT client with security settings.
        
        Returns:
            Configured MQTT client instance
        """
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        client.username_pw_set("bblp", self.access_code)
        client.tls_set(tls_version=ssl.PROTOCOL_TLS, cert_reqs=ssl.CERT_NONE)
        client.tls_insecure_set(True)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        return client

    def on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int):
        def on_connect(self, client: mqtt.Client, userdata: Any, flags: Any, rc: int):
        """Callback for when client connects to MQTT broker.
        
        Subscribes to printer status topic and triggers connect callback if set.
        
        Args:
            client: MQTT client instance
            userdata: User-defined data
            flags: Connection flags
            rc: Connection result code
        """
        client.subscribe(f"device/{self.serial}/report")
        if self.on_connect_callback:
            self.on_connect_callback()

    def start(
        self,
        message_callback: Optional[Callable[[PrinterStatus], None]] = None,
        on_connect_callback: Optional[Callable[[], None]] = None,
    ):
        """Start monitoring printer status.
        
        Args:
            message_callback: Handler for printer status updates
            on_connect_callback: Handler for successful connection
        """
        self.message_callback = message_callback
        self.on_connect_callback = on_connect_callback
        self.client.connect(self.hostname, 8883, 60)
        self.client.loop_start()

    def stop(self):
        """Stop monitoring and disconnect from printer."""
        self.client.loop_stop()
        self.client.disconnect()

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
