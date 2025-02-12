from bambu_connect import BambuClient
import time

# Printer configuration
hostname=os.getenv('HOSTNAME'),
access_code=os.getenv('ACCESS_CODE'),
serial=os.getenv('SERIAL')

def print_status_callback(status):
    """Callback to display printer status updates"""
    print("\nPrinter Status Update:")
    print(f"Nozzle: {status.nozzle_temper}°C")
    print(f"Bed: {status.bed_temper}°C")
    print(f"Progress: {status.mc_percent}%")
    print(f"State: {status.gcode_state}")
    print(f"Print Type: {status.print_type}")
    if status.gcode_file:
        print(f"Current File: {status.gcode_file}")

def main():
    print("Connecting to printer...")
    bambu_client = BambuClient(hostname, access_code, serial)

    # Start watching printer status
    bambu_client.start_watch_client(print_status_callback)
    time.sleep(2)  # Wait for initial connection

    while True:
        print("\nAvailable Commands:")
        print("1. Toggle Chamber Light")
        print("2. Set Print Speed")
        print("3. Send G-code Command")
        print("4. List Print Files")
        print("5. Start Print")
        print("6. Pause Print")
        print("7. Resume Print")
        print("8. Stop Print")
        print("9. Request Printer Info")
        print("0. Exit")

        choice = input("\nEnter command number: ")

        try:
            if choice == '1':
                state = input("Turn light on? (y/n): ").lower() == 'y'
                bambu_client.set_chamber_light(state)
                print(f"Chamber light {'on' if state else 'off'} command sent")

            elif choice == '2':
                print("\nSpeed Profiles:")
                print("1. Silent")
                print("2. Normal")
                print("3. Sport")
                print("4. Ludicrous")
                speed = input("Select speed profile (1-4): ")
                profiles = ['silent', 'normal', 'sport', 'ludicrous']
                if 1 <= int(speed) <= 4:
                    bambu_client.set_print_speed(profiles[int(speed)-1])
                    print(f"Speed set to {profiles[int(speed)-1]}")

            elif choice == '3':
                gcode = input("Enter G-code command: ")
                bambu_client.send_gcode(gcode)
                print("G-code command sent")

            elif choice == '4':
                files = bambu_client.get_files()
                print("\nAvailable Print Files:")
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")

            elif choice == '5':
                files = bambu_client.get_files()
                print("\nAvailable Files:")
                for i, file in enumerate(files, 1):
                    print(f"{i}. {file}")
                
                file_idx = int(input("Select file number to print: ")) - 1
                if 0 <= file_idx < len(files):
                    use_ams = input("Use AMS? (y/n): ").lower() == 'y'
                    timelapse = input("Enable timelapse? (y/n): ").lower() == 'y'
                    bambu_client.start_print(files[file_idx], use_ams, timelapse)
                    print(f"Starting print of {files[file_idx]}")

            elif choice == '6':
                bambu_client.pause_print()
                print("Print paused")

            elif choice == '7':
                bambu_client.resume_print()
                print("Print resumed")

            elif choice == '8':
                confirm = input("Are you sure you want to stop the print? (y/n): ").lower() == 'y'
                if confirm:
                    bambu_client.stop_print()
                    print("Print stopped")

            elif choice == '9':
                bambu_client.dump_info()
                print("Requested printer info dump")

            elif choice == '0':
                break

            else:
                print("Invalid choice")

            time.sleep(1)  # Wait for command to process

        except Exception as e:
            print(f"Error executing command: {str(e)}")

    # Cleanup
    bambu_client.stop_watch_client()
    print("Test script ended")

if __name__ == "__main__":
    main()
