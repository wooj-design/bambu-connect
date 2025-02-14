# Bambu-Connect - Python Library for Bambu Lab Printers

## Overview
Bambu-Connect is a Python library designed to facilitate seamless interaction with Bambu Lab Printers. It provides an intuitive interface for monitoring printers, sending print jobs, accessing camera feeds, and performing various operations efficiently. 

This project is a fork of the original [Bambu-Connect](https://github.com/mattcar15/bambu-connect) developed by [mattcar15](https://github.com/mattcar15). We aim to build upon and enhance its functionality while maintaining its core capabilities.

## Features
- **Printer Status Monitoring**: Retrieve real-time printer data, including temperatures, print progress, and more.
- **Camera Feed Access**: Stream live video from your printer's camera to monitor print jobs remotely.
- **File Management**: Upload, download, and list files on your printer with ease.
- **G-code Execution**: Send G-code commands for advanced printer control.
- **Print Job Management**: Start, pause, resume, and stop print jobs remotely.
- **Error Handling**: Retrieve printer error codes and descriptions for troubleshooting.

## Installation
To install Bambu-Connect, run:
```bash
pip install bambu-connect
```

## Setup
### **Prerequisites**
Before using Bambu-Connect, ensure you have the following information from your printer:
- **IP Address**: `Settings > WLAN > IP`
- **Access Code**: `Settings > WLAN > Access Code`
- **Serial Number**: [Find your Serial Number](https://wiki.bambulab.com/en/general/find-sn)

Create a `.env` file in the project directory with the following format:
```ini
HOSTNAME= "YOUR_PRINTER_IP"
ACCESS_CODE= "YOUR_PRINTER_ACCESS_CODE"
SERIAL= "YOUR_PRINTER_SERIAL_NUMBER"
```

## Usage
### **Initialize Client**
```python
from bambu_connect import BambuClient
import os
from dotenv import load_dotenv

load_dotenv()

bambu_client = BambuClient(
    hostname=os.getenv('HOSTNAME'),
    access_code=os.getenv('ACCESS_CODE'),
    serial=os.getenv('SERIAL')
)
```

### **Monitor Printer Status**
```python
from bambu_connect import PrinterStatus
from dataclasses import asdict
import pprint

def status_callback(status: PrinterStatus):
    printer_status_dict = asdict(status)
    pprint.pprint(printer_status_dict)

bambu_client.start_watch_client(status_callback)
```

### **Start a Print Job**
```python
file_to_print = "test_model.3mf"
bambu_client.start_print(file_to_print, use_ams=True, enable_timelapse=True)
```

### **Send G-code Commands**
```python
gcode_command = "G28"  # Home all axes
bambu_client.send_gcode(gcode_command)
```

### **Stream Camera Feed**
```python
def save_latest_frame(img):
    with open("latest_frame.jpg", "wb") as f:
        f.write(img)

bambu_client.start_camera_stream(save_latest_frame)
```

### **File Management**
#### **List Available Files**
```python
files = bambu_client.get_files()
print("Available files:", files)
```

#### **Download a File**
```python
bambu_client.download_file("/timelapse/test_video.avi", "./downloads")
```

#### **Upload a File**
```python
bambu_client.fileClient.upload_file("local_model.3mf", "/")
```

## Examples
Check the [`examples/`](examples) directory for additional scripts demonstrating various functionalities:
- `camera_stream.py` - Live camera streaming.
- `download_timelapse.py` - Retrieve and convert timelapse videos.
- `file_list_and_gcode.py` - Manage files and send G-code.
- `printer_stream.py` - Monitor real-time printer status.

## Contributing
Contributions are welcome! Whether it's bug reports, feature requests, or code improvements, feel free to open an issue or submit a pull request on our [GitHub repository](https://github.com/woojdesign/bambu-connect).

## License
Bambu-Connect is released under the [MIT License](https://opensource.org/licenses/MIT).

---
*Note: Bambu-Connect is an independent project and is not affiliated with Bambu Lab.*

