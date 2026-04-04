"""Tests for APIClient."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import requests

from adp_cli.adp.api_client import APIClient, TaskStatus
from adp_cli.adp.config import ConfigManager


@pytest.fixture
def mock_config_manager(tmp_path):
    """Create mock config manager with temporary directory."""
    config_dir = tmp_path / ".adp"
    config_dir.mkdir()

    # Temporarily replace ConfigManager directory
    original_dir = ConfigManager.CONFIG_DIR
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.json"
    ConfigManager.KEY_FILE = config_dir / "key.enc"

    config = ConfigManager()
    config.set_api_key("test-api-key-12345")

    yield config

    # Restore original config directory
    ConfigManager.CONFIG_DIR = original_dir
    ConfigManager.CONFIG_FILE = original_dir / "config.json"
    ConfigManager.KEY_FILE = original_dir / "key.enc"


@pytest.fixture
def api_client(mock_config_manager):
    """Create APIClient instance with mock config."""
    return APIClient(mock_config_manager)


def test_api_client_initialization(api_client):
    """Test API client initialization."""
    assert api_client.config_manager is not None
    assert api_client.api_base_url == "http://127.0.0.1:8000"


def test_get_api_base_url_default(api_client):
    """Test getting default API base URL."""
    url = api_client._get_api_base_url()
    assert url == "http://127.0.0.1:8000"


def test_get_api_base_url_custom(api_client):
    """Test getting custom API base URL."""
    api_client.config_manager.set("api_base_url", "https://api.example.com")
    url = api_client._get_api_base_url()
    assert url == "https://api.example.com"


def test_get_headers(api_client):
    """Test getting request headers."""
    headers = api_client._get_headers()
    assert "Content-Type" in headers
    assert "X-Api-key" in headers
    assert headers["X-Api-key"] == "test-api-key-12345"


def test_get_headers_no_api_key(mock_config_manager):
    """Test getting headers without API key raises error."""
    mock_config_manager.clear()
    api_client = APIClient(mock_config_manager)

    with pytest.raises(ValueError, match="API Key not configured"):
        api_client._get_headers()


def test_encode_file_to_base64(tmp_path):
    """Test encoding file to base64."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello, World!")

    # Create mock config
    config_dir = tmp_path / ".adp"
    config_dir.mkdir()

    original_dir = ConfigManager.CONFIG_DIR
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.json"
    ConfigManager.KEY_FILE = config_dir / "key.enc"

    config = ConfigManager()
    config.set_api_key("test-key")
    api_client = APIClient(config)

    # Test encoding
    encoded = api_client._encode_file_to_base64(test_file)

    assert isinstance(encoded, str)
    assert len(encoded) > 0

    # Restore
    ConfigManager.CONFIG_DIR = original_dir
    ConfigManager.CONFIG_FILE = original_dir / "config.json"
    ConfigManager.KEY_FILE = original_dir / "key.enc"


def test_get_mime_type(tmp_path):
    """Test getting MIME type for files."""
    # Create mock config
    config_dir = tmp_path / ".adp"
    config_dir.mkdir()

    original_dir = ConfigManager.CONFIG_DIR
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.json"
    ConfigManager.KEY_FILE = config_dir / "key.enc"

    config = ConfigManager()
    config.set_api_key("test-key")
    api_client = APIClient(config)

    # Test different file types
    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_text("PDF content")
    assert "pdf" in api_client._get_mime_type(pdf_file)

    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Text content")
    assert "text" in api_client._get_mime_type(txt_file)

    # Restore
    ConfigManager.CONFIG_DIR = original_dir
    ConfigManager.CONFIG_FILE = original_dir / "config.json"
    ConfigManager.KEY_FILE = original_dir / "key.enc"


@patch('requests.request')
def test_parse_sync_with_url(mock_request, api_client):
    """Test synchronous parse with URL."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "data": "parsed"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.parse_sync("http://example.com/file.pdf", "app123")

    assert result["status"] == "success"
    mock_request.assert_called_once()


@patch('requests.request')
def test_parse_async_with_url(mock_request, api_client):
    """Test asynchronous parse with URL."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": {"task_id": "task-123"}}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    task_id = api_client.parse_async("http://example.com/file.pdf", "app123")

    assert task_id == "task-123"
    mock_request.assert_called_once()


@patch('requests.request')
def test_extract_sync(mock_request, api_client):
    """Test synchronous extract."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "extracted": "data"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.extract_sync("http://example.com/file.pdf", "app123")

    assert result["status"] == "success"
    mock_request.assert_called_once()


@patch('requests.request')
def test_extract_async(mock_request, api_client):
    """Test asynchronous extract."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": {"task_id": "task-456"}}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    task_id = api_client.extract_async("http://example.com/file.pdf", "app123")

    assert task_id == "task-456"
    mock_request.assert_called_once()


@patch('requests.request')
def test_query_extract_task(mock_request, api_client):
    """Test query extract task."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "processing", "progress": 50}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.query_extract_task("task-123")

    assert result["status"] == "processing"
    mock_request.assert_called_once()


@patch('requests.request')
def test_list_apps(mock_request, api_client):
    """Test list apps."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "list": [
                {"id": "app1", "app_name": "App 1", "description": "Description 1", "app_label": ["label1"]},
                {"id": "app2", "app_name": "App 2", "description": "Description 2", "app_label": ["label2"]},
            ]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    apps = api_client.list_apps()

    assert len(apps) == 2
    assert apps[0]["app_id"] == "app1"
    assert apps[0]["app_name"] == "App 1"


@patch('requests.request')
def test_create_custom_app(mock_request, api_client):
    """Test create custom app."""
    mock_response = Mock()
    mock_response.json.return_value = {"app_id": "custom-app-123", "config_vision": "v1"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    extract_fields = [
        {
            "field_name": "name",
            "field_type": "string",
            "field_prompt": "Extract the name"
        }
    ]

    result = api_client.create_custom_app(
        app_name="Test App",
        extract_fields=extract_fields,
        parse_mode="standard"
    )

    assert result["app_id"] == "custom-app-123"
    mock_request.assert_called_once()


def test_create_custom_app_long_doc_config_validation(api_client):
    """Test create custom app with long doc config validation."""
    extract_fields = [{"field_name": "name", "field_type": "string", "field_prompt": "Extract name"}]

    # Should raise error when enable_long_doc is True but long_doc_config is not provided
    with pytest.raises(ValueError, match="long_doc_config must be provided"):
        api_client.create_custom_app(
            app_name="Test App",
            extract_fields=extract_fields,
            parse_mode="standard",
            enable_long_doc=True
        )


@patch('requests.request')
def test_get_custom_app_config(mock_request, api_client):
    """Test get custom app config."""
    mock_response = Mock()
    mock_response.json.return_value = {"app_id": "app-123", "config": {"field1": "value1"}}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.get_custom_app_config("app-123")

    assert result["app_id"] == "app-123"
    mock_request.assert_called_once()


@patch('requests.request')
def test_delete_custom_app(mock_request, api_client):
    """Test delete custom app."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "deleted"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.delete_custom_app("app-123")

    assert result["status"] == "deleted"
    mock_request.assert_called_once()


@patch('requests.request')
def test_delete_custom_app_version(mock_request, api_client):
    """Test delete custom app version."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "deleted"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.delete_custom_app_version("app-123", "v2")

    assert result["status"] == "deleted"
    mock_request.assert_called_once()


@patch('requests.request')
def test_ai_generate_fields_with_url(mock_request, api_client):
    """Test AI generate fields with URL."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "fields": [
            {"field_name": "name", "field_type": "string", "field_prompt": "Extract name"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.ai_generate_fields(
        app_id="app-123",
        file_url="http://example.com/sample.pdf"
    )

    assert "fields" in result
    mock_request.assert_called_once()


def test_ai_generate_fields_no_file(api_client):
    """Test AI generate fields without file raises error."""
    with pytest.raises(ValueError, match="Either file_url or file_local or file_base64 must be provided"):
        api_client.ai_generate_fields(app_id="app-123")


def test_wait_for_task_success(api_client):
    """Test wait for task with success."""
    query_func = Mock(side_effect=[
        {"data": {"status": TaskStatus.RUNNING}},
        {"data": {"status": TaskStatus.RUNNING}},
        {"data": {"status": TaskStatus.SUCCESS, "result": "done"}}
    ])

    result = api_client.wait_for_task("task-123", query_func, timeout=10, interval=0.1)

    assert result["data"]["status"] == TaskStatus.SUCCESS
    assert query_func.call_count == 3


def test_wait_for_task_failed(api_client):
    """Test wait for task with failure."""
    query_func = Mock(return_value={"data": {"status": TaskStatus.FAILED, "error": "Task failed"}})

    with pytest.raises(ValueError, match="Task failed"):
        api_client.wait_for_task("task-123", query_func, timeout=10, interval=0.1)


def test_wait_for_task_timeout(api_client):
    """Test wait for task timeout."""
    query_func = Mock(return_value={"status": TaskStatus.RUNNING})

    with pytest.raises(TimeoutError, match="Task timeout"):
        api_client.wait_for_task("task-123", query_func, timeout=0.2, interval=0.1)


@patch('requests.request')
def test_health_check_success(mock_request, api_client):
    """Test health check with successful response."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    assert api_client.health_check() is True


@patch('requests.request')
def test_health_check_failure(mock_request, api_client):
    """Test health check with failed response."""
    mock_request.side_effect = requests.RequestException("Connection failed")

    assert api_client.health_check() is False


def test_task_status_constants():
    """Test TaskStatus constants."""
    assert TaskStatus.PENDING == 0
    assert TaskStatus.RUNNING == 2
    assert TaskStatus.SUCCESS == 4
    assert TaskStatus.FAILED == 5
    assert TaskStatus.CANCELLED == 6
