import subprocess
import re
import os


class FileClient:
    """Client for managing files on Bambu printer via FTPS.
    
    Handles file listing and downloads using secure FTP connection.
    """
    def __init__(self, hostname: str, access_code: str, serial: str):
        """Initialize file client with connection details.
        
        Args:
            hostname: Printer's IP address or hostname
            access_code: Printer's access code for authentication
            serial: Printer's serial number
        """
        self.hostname = hostname
        self.access_code = access_code
        self.serial = serial

    def get_files(self, directory="/", extension=".3mf"):
        """List files in printer directory filtered by extension.
        
        Args:
            directory: Remote directory path to list
            extension: File extension to filter by
            
        Returns:
            List of filenames matching extension
        """
        command = [
            "curl",
            "--ftp-pasv",
            "--insecure",
            f"ftps://{self.hostname}{directory}",
            "--user",
            f"bblp:{self.access_code}",
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        filtered_files = []
        for line in result.stdout.split("\n"):
            if line.strip():
                parts = re.split(r"\s+", line, maxsplit=8)
                filename = parts[-1]

                if filename.endswith(extension):
                    filtered_files.append(filename)

        return filtered_files

    def download_file(self, remote_path: str, local_path: str, verbose=True):
        """Download file from printer to local system.
        
        Args:
            remote_path: Path to file on printer
            local_path: Local directory to save file
            verbose: Whether to print download progress
            
        Returns:
            True if download successful, False otherwise
        """
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        local_file_path = os.path.join(local_path, os.path.basename(remote_path))
        command = [
            "curl",
            "-o",
            local_file_path,
            "--ftp-pasv",
            "--insecure",
            f"ftps://{self.hostname}{remote_path}",
            "--user",
            f"bblp:{self.access_code}",
        ]
        
        if verbose:
            result = subprocess.run(command)
        else:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            if verbose:
                print(result.stderr.decode())
            return False

        return True

    def upload_file(self, local_file: str, remote_path: str = "/", verbose: bool = True) -> bool:
        """Upload file to printer's SD card.
        
        Args:
            local_file: Path to local file to upload
            remote_path: Remote directory to upload to (default: root)
            verbose: Whether to print upload progress
            
        Returns:
            True if upload successful, False otherwise
        """
        if not os.path.exists(local_file):
            raise FileNotFoundError(f"Local file {local_file} not found")
            
        remote_file = os.path.join(remote_path, os.path.basename(local_file))
        command = [
            "curl",
            "-T",  # Upload file
            local_file,
            "--ftp-pasv",
            "--insecure",
            f"ftps://{self.hostname}{remote_file}",
            "--user",
            f"bblp:{self.access_code}",
        ]
        
        if verbose:
            result = subprocess.run(command)
        else:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        return result.returncode == 0

    def delete_file(self, remote_file: str, verbose: bool = True) -> bool:
        """Delete file from printer's SD card.
        
        Args:
            remote_file: Path to file to delete
            verbose: Whether to print progress
            
        Returns:
            True if deletion successful, False otherwise
        """
        command = [
            "curl",
            "--quote",  # Send raw FTP commands
            "DELE " + remote_file,  # Delete command
            "--ftp-pasv",
            "--insecure",
            f"ftps://{self.hostname}",
            "--user",
            f"bblp:{self.access_code}",
        ]
        
        if verbose:
            result = subprocess.run(command)
        else:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
        return result.returncode == 0
