import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import ssl
from bambu_connect import BambuClient, PrinterStatus
from bambu_connect.utils.models import Upload, Online, AMS, IPCam

@pytest.fixture
def mock_socket():
    with patch('socket.create_connection') as mock_conn, \
         patch('socket.getaddrinfo') as mock_addr:
        mock_addr.return_value = [(2, 1, 6, '', ('127.0.0.1', 0))]
        yield mock_conn

@pytest.fixture
def mock_mqtt_client():
    mock = MagicMock()
    mock.connect.return_value = 0
    return mock

@pytest.fixture
def mock_mqtt(mock_mqtt_client):
    with patch('paho.mqtt.client.Client', return_value=mock_mqtt_client):
        yield mock_mqtt_client

@pytest.fixture
def test_config():
    return {
        'hostname': 'test.printer',
        'access_code': 'test123',
        'serial': 'PRINTER001'
    }

@pytest.fixture
def bambu_client(test_config, mock_mqtt, mock_socket):
    client = BambuClient(**test_config)
    return client

class TestBambuClient:
    def test_initialization(self, test_config, bambu_client):
        assert isinstance(bambu_client.cameraClient, object)
        assert isinstance(bambu_client.watchClient, object)
        assert isinstance(bambu_client.executeClient, object)
        assert isinstance(bambu_client.fileClient, object)

    @patch('bambu_connect.ExecuteClient.ExecuteClient.disconnect')
    def test_cleanup(self, mock_disconnect, bambu_client):
        bambu_client.__del__()
        mock_disconnect.assert_called_once()

class TestExecuteClient:
    def test_send_gcode(self, bambu_client, mock_mqtt):
        test_gcode = "G28"
        bambu_client.executeClient.send_gcode(test_gcode)
        
        expected_payload = {
            "print": {
                "command": "gcode_line",
                "sequence_id": 2006,
                "param": f"{test_gcode} \n"
            },
            "user_id": "1234567890"
        }
        
        mock_mqtt.publish.assert_called_with(
            f"device/{bambu_client.executeClient.serial}/request",
            json.dumps(expected_payload)
        )

class TestWatchClient:
    def test_message_callback(self, bambu_client):
        test_data = {
            "print": {
                "upload": {"status": "idle", "progress": 0},
                "nozzle_temper": 200.5,
                "bed_temper": 60.0,
                "online": {"ahb": True, "rfid": True, "version": 1}
            }
        }

        mock_callback = Mock()
        bambu_client.watchClient.message_callback = mock_callback
        
        mock_msg = Mock()
        mock_msg.payload = json.dumps(test_data)
        
        bambu_client.watchClient.on_message(None, None, mock_msg)
        
        mock_callback.assert_called_once()
        status_arg = mock_callback.call_args[0][0]
        assert isinstance(status_arg, PrinterStatus)
        assert status_arg.nozzle_temper == 200.5
        assert status_arg.bed_temper == 60.0

class TestFileClient:
    @patch('subprocess.run')
    def test_get_files(self, mock_run, bambu_client):
        mock_result = Mock()
        mock_result.stdout = "file1.3mf\nfile2.3mf\nother.txt"
        mock_run.return_value = mock_result

        files = bambu_client.fileClient.get_files(extension=".3mf")
        assert len(files) == 2
        assert "file1.3mf" in files
        assert "file2.3mf" in files

    @patch('subprocess.run')
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_download_file(self, mock_makedirs, mock_exists, mock_run, bambu_client):
        mock_exists.return_value = False
        mock_run.return_value = Mock(returncode=0)

        result = bambu_client.fileClient.download_file(
            remote_path="/test.gcode",
            local_path="./downloads/",
            verbose=False
        )

        assert result is True
        mock_makedirs.assert_called_once_with("./downloads/")