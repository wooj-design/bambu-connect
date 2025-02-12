from bambu_connect import BambuClient
import time
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Load environment variables
load_dotenv()

# Verify required environment variables
required_env = ['HOSTNAME', 'ACCESS_CODE', 'SERIAL']
missing_env = [var for var in required_env if not os.getenv(var)]
if missing_env:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_env)}\n"
        f"Please create a .env file with HOSTNAME, ACCESS_CODE, and SERIAL"
    )

# Printer configuration from environment variables
hostname = os.getenv('HOSTNAME')
access_code = os.getenv('ACCESS_CODE')
serial = os.getenv('SERIAL')

def select_file(title="Select 3MF File", filetypes=[("3MF files", "*.3mf")]):
    """Open file picker dialog and return selected file path"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=filetypes
    )
    
    return file_path if file_path else None

class PrinterStatusMonitor:
    def __init__(self):
        self.last_state = None
        self.last_progress = None
        self.last_stage = None
        self.last_temps = None
        
    def __call__(self, status):
        """Callback to display relevant file and print status updates"""
        updates = []
        
        # Track print state changes
        current_state = status.gcode_state
        if current_state != self.last_state:
            if current_state:
                updates.append(f"Print State: {current_state}")
            self.last_state = current_state
            
        # Track print stage changes
        current_stage = status.mc_print_stage
        if current_stage != self.last_stage:
            if current_stage:
                updates.append(f"Stage: {current_stage}")
            self.last_stage = current_stage
            
        # Track significant progress changes (every 5%)
        if status.mc_percent is not None:
            current_progress = round(status.mc_percent)
            if self.last_progress is None or abs(current_progress - self.last_progress) >= 5:
                if current_progress > 0:
                    updates.append(f"Progress: {current_progress}%")
                self.last_progress = current_progress
                
        # Track temperature changes (when printing)
        if status.gcode_state == "RUNNING":
            current_temps = (
                round(status.nozzle_temper) if status.nozzle_temper is not None else None,
                round(status.bed_temper) if status.bed_temper is not None else None
            )
            if current_temps != self.last_temps and all(t is not None for t in current_temps):
                updates.append(f"Temperatures - Nozzle: {current_temps[0]}°C, Bed: {current_temps[1]}°C")
                self.last_temps = current_temps
        
        # Show remaining time if available and changed
        if status.mc_remaining_time:
            remaining_mins = status.mc_remaining_time
            if remaining_mins > 0:
                hours = remaining_mins // 60
                mins = remaining_mins % 60
                if hours > 0:
                    updates.append(f"Remaining Time: {hours}h {mins}m")
                else:
                    updates.append(f"Remaining Time: {mins}m")
        
        # Show any print errors
        if status.print_error:
            updates.append(f"Error: {status.print_error}")
            
        # Only print update if there are changes to report
        if updates:
            print("\nPrinter Status Update:")
            for update in updates:
                print(update)

def list_files(client):
    """List all files on printer with details"""
    try:
        print("\nListing files on printer...")
        files = client.get_files()
        if not files:
            print("No files found on printer")
            return
        
        print("\nFiles found:")
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")
        return files
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def upload_test_file(client, test_file):
    """Test file upload functionality"""
    try:
        print(f"\nUploading test file: {test_file}")
        success = client.fileClient.upload_file(test_file)
        if success:
            print("Upload successful!")
        else:
            print("Upload failed!")
        return success
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return False

def delete_file(client, filename):
    """Test file deletion functionality"""
    try:
        print(f"\nDeleting file: {filename}")
        success = client.fileClient.delete_file(filename)
        if success:
            print("Deletion successful!")
        else:
            print("Deletion failed!")
        return success
    except Exception as e:
        print(f"Error during deletion: {str(e)}")
        return False

def download_file(client, filename, local_path="downloads"):
    """Test file download functionality"""
    try:
        print(f"\nDownloading file: {filename}")
        os.makedirs(local_path, exist_ok=True)
        success = client.fileClient.download_file(
            remote_path="/" + filename,
            local_path=local_path
        )
        if success:
            print(f"Download successful! Saved to {local_path}/{filename}")
        else:
            print("Download failed!")
        return success
    except Exception as e:
        print(f"Error during download: {str(e)}")
        return False

def main():
    print("Starting file operations test script...")
    print(f"Connecting to printer at {hostname}")
    
    try:
        # Initialize client
        bambu_client = BambuClient(hostname, access_code, serial)
        
        # Initialize and start status monitoring
        status_monitor = PrinterStatusMonitor()
        bambu_client.start_watch_client(status_monitor)
        time.sleep(2)  # Wait for initial connection
        
        while True:
            print("\nFile Operations Test Menu:")
            print("1. List Files")
            print("2. Upload File")
            print("3. Download File")
            print("4. Delete File")
            print("5. Upload and Print File")
            print("6. Test File Lifecycle (Upload -> Print -> Delete)")
            print("0. Exit")
            
            choice = input("\nEnter command number: ")
            
            if choice == '1':
                list_files(bambu_client)
                
            elif choice == '2':
                file_path = select_file()
                if file_path:
                    upload_test_file(bambu_client, file_path)
                else:
                    print("No file selected!")
                    
            elif choice == '3':
                files = list_files(bambu_client)
                if files:
                    idx = int(input("Enter file number to download: ")) - 1
                    if 0 <= idx < len(files):
                        # Select download location
                        root = tk.Tk()
                        root.withdraw()
                        download_dir = filedialog.askdirectory(
                            title="Select Download Directory"
                        )
                        if download_dir:
                            download_file(bambu_client, files[idx], download_dir)
                        else:
                            print("No directory selected!")
                        
            elif choice == '4':
                files = list_files(bambu_client)
                if files:
                    idx = int(input("Enter file number to delete: ")) - 1
                    if 0 <= idx < len(files):
                        if messagebox.askyesno(
                            "Confirm Delete",
                            f"Are you sure you want to delete {files[idx]}?"
                        ):
                            delete_file(bambu_client, files[idx])
                        
            elif choice == '5':
                file_path = select_file()
                if file_path:
                    if upload_test_file(bambu_client, file_path):
                        filename = os.path.basename(file_path)
                        if messagebox.askyesno(
                            "Start Print",
                            f"Do you want to start printing {filename}?"
                        ):
                            print(f"\nStarting print of {filename}")
                            # Dump printer info before print
                            bambu_client.dump_info()
                            time.sleep(2)  # Wait for info
                            
                            try:
                                # Try to start print with various options
                                print("Attempting to start print...")
                                bambu_client.start_print(
                                    filename,
                                    use_ams=False,
                                    enable_timelapse=False
                                )
                                
                                # Monitor initial print state
                                for _ in range(10):  # Check for 10 seconds
                                    time.sleep(1)
                                    status = bambu_client.watchClient.printerStatus
                                    if status:
                                        print(f"Print State: {status.gcode_state}")
                                        print(f"Print Stage: {status.mc_print_stage}")
                                        if hasattr(status, 'print_error'):
                                            print(f"Print Error: {status.print_error}")
                            except Exception as e:
                                print(f"Error starting print: {str(e)}")
                                messagebox.showerror("Print Error", str(e))
                else:
                    print("No file selected!")
                    
            elif choice == '6':
                file_path = select_file()
                if not file_path:
                    print("No file selected!")
                    continue
                    
                filename = os.path.basename(file_path)
                print("\nStarting file lifecycle test...")
                
                # Upload
                print("\nStep 1: Upload")
                if not upload_test_file(bambu_client, file_path):
                    continue
                    
                # Print
                print("\nStep 2: Start Print")
                bambu_client.start_print(filename)
                
                # Monitor print completion
                print("\nMonitoring print progress...")
                while True:
                    time.sleep(5)
                    status = bambu_client.watchClient.printerStatus
                    if status and status.gcode_state == "FINISH":
                        print("\nPrint completed!")
                        break
                    elif status and status.gcode_state == "FAILED":
                        print("\nPrint failed!")
                        break
                    
                # Delete
                if messagebox.askyesno(
                    "File Cleanup",
                    f"Do you want to delete {filename} now that printing is complete?"
                ):
                    print("\nStep 3: Cleanup")
                    delete_file(bambu_client, filename)
                
            elif choice == '0':
                break
                
            else:
                print("Invalid choice!")
                
            time.sleep(1)  # Small delay between operations
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        messagebox.showerror("Error", str(e))
    finally:
        if 'bambu_client' in locals():
            bambu_client.stop_watch_client()
        print("\nTest script ended")

if __name__ == "__main__":
    main()