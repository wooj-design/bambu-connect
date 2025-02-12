from bambu_connect import BambuClient
import time
import os

# Printer configuration
hostname=os.getenv('HOSTNAME'),
access_code=os.getenv('ACCESS_CODE'),
serial=os.getenv('SERIAL')

def save_frame(img_data):
    """Save received frame to file"""
    print(f"Received frame of size: {len(img_data)} bytes")
    # Save to a file to verify the data
    with open("test_frame.jpg", "wb") as f:
        f.write(img_data)

def main():
    print("Connecting to printer...")
    client = BambuClient(hostname, access_code, serial)
    
    print("Starting camera stream...")
    client.start_camera_stream(save_frame)
    
    print("Waiting for frames (10 seconds)...")
    time.sleep(10)
    
    print("Stopping camera stream...")
    client.stop_camera_stream()
    
    if os.path.exists("test_frame.jpg"):
        print("Frame was saved successfully!")
        print(f"Frame size: {os.path.getsize('test_frame.jpg')} bytes")
    else:
        print("No frame was saved!")

if __name__ == "__main__":
    main()