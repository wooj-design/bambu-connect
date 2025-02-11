from datetime import datetime
import struct
import socket
import ssl
import threading


class CameraClient:
    """Client for connecting to and streaming from a Bambu printer's camera.
    
    Handles authentication, frame capture, and continuous streaming of JPEG images.
    """
    def __init__(self, hostname, access_code, port=6000):
        """Initialize camera client with connection details.
        
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code for authentication
            port: Camera stream port (default: 6000)
        """
        self.hostname = hostname
        self.port = port
        self.username = "bblp"
        self.auth_packet = self.__create_auth_packet__(self.username, access_code)
        self.streaming = False
        self.stream_thread = None

    def __create_auth_packet__(self, username, access_code):
        """Create authentication packet for camera stream access.
        
        Args:
            username: Client username
            access_code: Printer access code
            
        Returns:
            Formatted authentication packet as bytearray
        """
        auth_data = bytearray()
        auth_data += struct.pack("<I", 0x40)  # '@'\0\0\0
        auth_data += struct.pack("<I", 0x3000)  # \0'0'\0\0
        auth_data += struct.pack("<I", 0)  # \0\0\0\0
        auth_data += struct.pack("<I", 0)  # \0\0\0\0
        for i in range(0, len(username)):
            auth_data += struct.pack("<c", username[i].encode('ascii'))
        for i in range(0, 32 - len(username)):
            auth_data += struct.pack("<x")
        for i in range(0, len(access_code)):
            auth_data += struct.pack("<c", access_code[i].encode('ascii'))
        for i in range(0, 32 - len(access_code)):
            auth_data += struct.pack("<x")
        return auth_data

    def __find_jpeg__(self, buf, start_marker, end_marker):
        """Find complete JPEG image in buffer using markers.
        
        Args:
            buf: Data buffer to search
            start_marker: JPEG start marker sequence
            end_marker: JPEG end marker sequence
            
        Returns:
            Tuple of (JPEG image if found, remaining buffer)
        """
        start = buf.find(start_marker)
        end = buf.find(end_marker, start + len(start_marker))
        if start != -1 and end != -1:
            return buf[start : end + len(end_marker)], buf[end + len(end_marker) :]
        return None, buf

    def capture_frame(self):
        """Capture single frame from camera stream.
        
        Returns:
            JPEG image data as bytes
        """
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        jpeg_start = bytearray([0xff, 0xd8, 0xff, 0xe0])
        jpeg_end = bytearray([0xff, 0xd9])
        read_chunk_size = 4096

        with socket.create_connection((self.hostname, self.port)) as sock:
            with ctx.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                ssock.write(self.auth_packet)
                buf = bytearray()
                while True:
                    dr = ssock.recv(read_chunk_size)
                    if not dr:
                        break
                    buf += dr
                    img, buf = self.__find_jpeg__(buf, jpeg_start, jpeg_end)
                    if img:
                        return bytes(img)

    def capture_stream(self, img_callback):
        """Continuously capture frames and pass to callback.
        
        Args:
            img_callback: Function to handle each captured frame
        """
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        jpeg_start = bytearray([0xff, 0xd8, 0xff, 0xe0])
        jpeg_end = bytearray([0xff, 0xd9])
        read_chunk_size = 4096

        with socket.create_connection((self.hostname, self.port)) as sock:
            with ctx.wrap_socket(sock, server_hostname=self.hostname) as ssock:
                ssock.write(self.auth_packet)
                buf = bytearray()
                while self.streaming:
                    dr = ssock.recv(read_chunk_size)
                    if not dr:
                        break
                    buf += dr
                    img, buf = self.__find_jpeg__(buf, jpeg_start, jpeg_end)
                    if img:
                        img_callback(bytes(img))

    def start_stream(self, img_callback):
        """Start continuous camera stream in background thread.
        
        Args:
            img_callback: Function to handle each captured frame
        """
        if self.streaming:
            print("Stream already running.")
            return

        self.streaming = True
        self.stream_thread = threading.Thread(
            target=self.capture_stream, args=(img_callback,)
        )
        self.stream_thread.start()

    def stop_stream(self):
        """Stop active camera stream and wait for thread completion."""
        if not self.streaming:
            print("Stream is not running.")
            return

        self.streaming = False
        self.stream_thread.join()