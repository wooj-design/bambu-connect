from bambu_connect import BambuClient
from dotenv import load_dotenv
import os
import time

load_dotenv()

def status_callback(status):
    # These are the relevant fields for the current print file
    print("\nPrinter Status Update:")
    print(f"Current gcode file: {status.gcode_file}")
    print(f"Current subtask name: {status.subtask_name}")
    print(f"Print state: {status.gcode_state}")
    print(f"Print type: {status.print_type}")
    print(f"Progress: {status.gcode_file_prepare_percent}%")

def on_connect():
    print("Connected to printer. Requesting status...")
    # Request full printer status
    bambu_client.dump_info()

# Initialize with your printer details
bambu_client = BambuClient(
    hostname=os.getenv('HOSTNAME'),
    access_code=os.getenv('ACCESS_CODE'),
    serial=os.getenv('SERIAL')
)

# Start watching printer status with both callbacks
bambu_client.start_watch_client(
    message_callback=status_callback,
    on_connect_callback=on_connect
)

try:
    # Keep the script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    bambu_client.stop_watch_client()