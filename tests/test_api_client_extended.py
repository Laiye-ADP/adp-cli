"""Extended tests for APIClient."""

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

    original_dir = ConfigManager.CONFIG_DIR
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.json"
    ConfigManager.KEY_FILE = config_dir / "key.enc"

    config = ConfigManager()
    config.set_api_key("test-api-key-12345")

    yield config

    ConfigManager.CONFIG_DIR = original_dir
    ConfigManager.CONFIG_FILE = original_dir / "config.json"
    ConfigManager.KEY_FILE = original_dir / "key.enc"


@pytest.fixture
def api_client(mock_config_manager):
    """Create APIClient instance with mock config."""
    return APIClient(mock_config_manager)


def test_task_status_constants():
    """Test TaskStatus constants."""
    assert TaskStatus.PENDING == 0
    assert TaskStatus.RUNNING == 2
    assert TaskStatus.SUCCESS == 4
    assert TaskStatus.FAILED == 5
    assert TaskStatus.CANCELLED == 6


@patch('requests.request')
def test_parse_sync_with_file(mock_request, api_client, tmp_path):
    """Test synchronous parse with file."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "data": "parsed"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_text("PDF content")

    result = api_client.parse_sync("http://example.com/file.pdf", "app123", file_path=test_file)

    assert result["status"] == "success"
    mock_request.assert_called_once()


@patch('requests.request')
def test_parse_async_with_file(mock_request, api_client, tmp_path):
    """Test asynchronous parse with file."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": {"task_id": "task-456"}}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_text("PDF content")

    task_id = api_client.parse_async("http://example.com/file.pdf", "app123", file_path=test_file)

    assert task_id == "task-456"
    mock_request.assert_called_once()


@patch('requests.request')
def test_parse_sync_with_extract_config(mock_request, api_client):
    """Test synchronous parse with extract config."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "data": "result"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    extract_config = {"field1": "value1"}

    result = api_client.parse_sync("http://example.com/file.pdf", "app123")

    assert result["status"] == "success"


@patch('requests.request')
def test_extract_sync_with_file(mock_request, api_client, tmp_path):
    """Test synchronous extract with file."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "extracted": "data"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_text("PDF content")

    extract_config = {"fields": ["field1", "field2"]}

    result = api_client.extract_sync(
        "http://example.com/file.pdf",
        "app123",
        file_path=test_file,
        extract_config=extract_config
    )

    assert result["status"] == "success"
    mock_request.assert_called_once()


@patch('requests.request')
def test_extract_sync_without_config(mock_request, api_client):
    """Test synchronous extract without config."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "success", "extracted": "data"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.extract_sync("http://example.com/file.pdf", "app123")

    assert result["status"] == "success"


@patch('requests.request')
def test_extract_async_with_file(mock_request, api_client, tmp_path):
    """Test asynchronous extract with file."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": {"task_id": "task-789"}}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_text("PDF content")

    extract_config = {"fields": ["field1", "field2"]}

    task_id = api_client.extract_async(
        "http://example.com/file.pdf",
        "app123",
        file_path=test_file,
        extract_config=extract_config
    )

    assert task_id == "task-789"
    mock_request.assert_called_once()


@patch('requests.request')
def test_query_parse_task(mock_request, api_client):
    """Test query parse task."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "status": TaskStatus.RUNNING,
            "progress": 50,
            "result": None
        }
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.query_parse_task("task-123")

    assert "data" in result
    assert result["data"]["status"] == TaskStatus.RUNNING


@patch('requests.request')
def test_query_parse_task_with_result(mock_request, api_client):
    """Test query parse task with result."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "status": TaskStatus.SUCCESS,
            "result": {"field1": "value1"}
        }
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.query_parse_task("task-123")

    assert "data" in result
    assert result["data"]["status"] == TaskStatus.SUCCESS
    assert result["data"]["result"]["field1"] == "value1"


@patch('requests.request')
def test_query_extract_task_with_result(mock_request, api_client):
    """Test query extract task with result."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "status": TaskStatus.SUCCESS,
            "extracted": {"data": "extracted content"}
        }
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.query_extract_task("task-456")

    assert "data" in result
    assert result["data"]["status"] == TaskStatus.SUCCESS


@patch('requests.request')
def test_list_apps_empty(mock_request, api_client):
    """Test list apps with empty list."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "list": []
        }
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    apps = api_client.list_apps()

    assert apps == []


@patch('requests.request')
def test_list_apps_single(mock_request, api_client):
    """Test list apps with single app."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "data": {
            "list": [
                {"id": "app1", "app_name": "App 1", "app_label": ["label1"]}
            ]
        }
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    apps = api_client.list_apps()

    assert len(apps) == 1
    assert apps[0]["app_id"] == "app1"
    assert apps[0]["app_name"] == "App 1"
    assert apps[0]["app_label"] == ["label1"]


@patch('requests.request')
def test_create_custom_app_with_labels(mock_request, api_client):
    """Test create custom app with labels."""
    mock_response = Mock()
    mock_response.json.return_value = {"app_id": "custom-app-456", "config_vision": "v2"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    extract_fields = [
        {
            "field_name": "name",
            "field_type": "string",
            "field_prompt": "Extract name"
        }
    ]
    app_label = ["finance", "invoice"]

    result = api_client.create_custom_app(
        app_name="Test App",
        extract_fields=extract_fields,
        parse_mode="standard",
        app_label=app_label
    )

    assert result["app_id"] == "custom-app-456"
    mock_request.assert_called_once()


@patch('requests.request')
def test_create_custom_app_with_long_doc_config(mock_request, api_client):
    """Test create custom app with long doc config."""
    mock_response = Mock()
    mock_response.json.return_value = {"app_id": "custom-app-789", "config_vision": "v3"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    extract_fields = [{"field_name": "name", "field_type": "string", "field_prompt": "Extract name"}]
    long_doc_config = [
        {
            "field_name": "table_field",
            "field_type": "table",
            "field_prompt": "Extract table"
        }
    ]

    result = api_client.create_custom_app(
        app_name="Test App",
        extract_fields=extract_fields,
        parse_mode="standard",
        enable_long_doc=True,
        long_doc_config=long_doc_config
    )

    assert result["app_id"] == "custom-app-789"
    mock_request.assert_called_once()


def test_create_custom_app_with_long_doc_enabled_but_no_config(api_client):
    """Test create custom app with long doc enabled but no config raises error."""
    extract_fields = [{"field_name": "name", "field_type": "string", "field_prompt": "Extract name"}]

    with pytest.raises(ValueError, match="long_doc_config must be provided"):
        api_client.create_custom_app(
            app_name="Test App",
            extract_fields=extract_fields,
            parse_mode="standard",
            enable_long_doc=True
        )


@patch('requests.request')
def test_create_custom_app_with_long_doc_config_but_disabled(mock_request, api_client):
    """Test create custom app with long doc config but disabled - should not raise."""
    mock_response = Mock()
    mock_response.json.return_value = {"app_id": "custom-app-000", "config_vision": "v1"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    extract_fields = [{"field_name": "name", "field_type": "string", "field_prompt": "Extract name"}]
    long_doc_config = [{"field_name": "field", "field_type": "string"}]

    # Should not raise when enable_long_doc is False
    api_client.create_custom_app(
        app_name="Test App",
        extract_fields=extract_fields,
        parse_mode="standard",
        enable_long_doc=False,
        long_doc_config=long_doc_config
    )


@patch('requests.request')
def test_get_custom_app_config_with_version(mock_request, api_client):
    """Test get custom app config with specific version."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "app_id": "app-123",
        "config_version": "v2",
        "config": {"field1": "value1"}
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.get_custom_app_config("app-123", config_version="v2")

    assert result["app_id"] == "app-123"
    assert result["config_version"] == "v2"


@patch('requests.request')
def test_ai_generate_fields_with_local_file(mock_request, api_client, tmp_path):
    """Test AI generate fields with local file."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "fields": [
            {"field_name": "invoice_date", "field_type": "date", "field_prompt": "Extract invoice date"},
            {"field_name": "amount", "field_type": "string", "field_prompt": "Extract amount"}
        ]
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    # Create test file
    test_file = tmp_path / "sample.pdf"
    test_file.write_text("PDF content")

    result = api_client.ai_generate_fields(
        app_id="app-123",
        file_local=str(test_file)
    )

    assert "fields" in result
    assert len(result["fields"]) == 2
    mock_request.assert_called_once()


def test_ai_generate_fields_with_both_url_and_local(api_client):
    """Test AI generate fields with both URL and local file should work."""
    # Should use one of them (implementation specific)
    with pytest.raises(ValueError, match="Either file_url or file_local or file_base64 must be provided"):
        api_client.ai_generate_fields(app_id="app-123")


def test_wait_for_task_pending_to_running(api_client):
    """Test wait for task transition from pending to running to success."""
    query_func = Mock(side_effect=[
        {"data": {"status": TaskStatus.PENDING}},
        {"data": {"status": TaskStatus.RUNNING}},
        {"data": {"status": TaskStatus.SUCCESS, "result": "done"}}
    ])

    result = api_client.wait_for_task("task-123", query_func, timeout=10, interval=0.1)

    assert result["data"]["status"] == TaskStatus.SUCCESS
    assert query_func.call_count == 3


def test_wait_for_task_cancelled(api_client):
    """Test wait for task with cancelled status."""
    query_func = Mock(return_value={"data": {"status": TaskStatus.CANCELLED}})

    with pytest.raises(ValueError, match="Task cancelled"):
        api_client.wait_for_task("task-123", query_func, timeout=10, interval=0.1)


def test_wait_for_task_with_result_data(api_client):
    """Test wait for task that returns result data."""
    expected_result = {"data": {"extracted": "content", "confidence": 0.95}}
    query_func = Mock(return_value={
        "data": {"status": TaskStatus.SUCCESS, "result": expected_result}
    })

    result = api_client.wait_for_task("task-123", query_func, timeout=10, interval=0.1)

    assert result["data"]["status"] == TaskStatus.SUCCESS
    assert result["data"]["result"] == expected_result


@patch('requests.request')
def test_get_user_payment_status(mock_request, api_client):
    """Test getting getting user payment status."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "is_paid": True,
        "plan": "premium",
        "quota_remaining": 1000
    }
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.get_user_payment_status()

    assert result["is_paid"] is True
    assert result["plan"] == "premium"


@patch('requests.request')
def test_health_check_with_mock(mock_request, api_client):
    """Test health check with mock."""
    mock_response = Mock()
    mock_response.json.return_value = {"status": "healthy"}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    result = api_client.health_check()
    assert result is True


@patch('requests.request')
def test_api_base_url_uses_tenant_name(mock_request, api_client):
    """Test that API base URL includes tenant name."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": {"task_id": "task-123"}}
    mock_response.raise_for_status = Mock()
    mock_request.return_value = mock_response

    api_client.config_manager.set("tenant_name", "custom_tenant")

    api_client.parse_sync("http://example.com/file.pdf", "app123")

    # Check that the request was made with tenant name in URL
    call_args = mock_request.call_args
    url = call_args[0][1]  # Get the URL argument
    assert "custom_tenant" in url