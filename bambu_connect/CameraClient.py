class CameraClient:
    """Client for connecting to and streaming from a Bambu printer's camera.
    
    Handles authentication, frame capture, and continuous streaming of JPEG images.
    """

    def __init__(self, hostname: str, access_code: str, port: int = 6000):
        """Initialize camera client with connection details.
        
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code for authentication
            port: Camera stream port (default: 6000)
        """

    def __create_auth_packet__(self, username: str, access_code: str) -> bytearray:
        """Create authentication packet for camera stream access.
        
        Args:
            username: Client username
            access_code: Printer access code
            
        Returns:
            Formatted authentication packet as bytearray
        """

    def __find_jpeg__(self, buf: bytearray, start_marker: bytearray, end_marker: bytearray) -> tuple[bytes | None, bytearray]:
        """Find complete JPEG image in buffer using markers.
        
        Args:
            buf: Data buffer to search
            start_marker: JPEG start marker sequence
            end_marker: JPEG end marker sequence
            
        Returns:
            Tuple of (JPEG image if found, remaining buffer)
        """

    def capture_frame(self) -> bytes:
        """Capture single frame from camera stream.
        
        Returns:
            JPEG image data as bytes
        """

    def capture_stream(self, img_callback: callable):
        """Continuously capture frames and pass to callback.
        
        Args:
            img_callback: Function to handle each captured frame
        """

    def start_stream(self, img_callback: callable):
        """Start continuous camera stream in background thread.
        
        Args:
            img_callback: Function to handle each captured frame
        """

    def stop_stream(self):
        """Stop active camera stream and wait for thread completion."""