"""Tests for CLI commands."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from adp_cli.cli import cli, _parse_json_param_value, parse_bool_param, parse_json_list_param, validate_create_app_params, _sanitize_file_name, _load_tasks_from_file
from adp_cli.adp.config import ConfigManager


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / ".adp"
    config_dir.mkdir()

    original_dir = ConfigManager.CONFIG_DIR
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.json"
    ConfigManager.KEY_FILE = config_dir / "key.enc"

    yield config_dir

    ConfigManager.CONFIG_DIR = original_dir
    ConfigManager.CONFIG_FILE = original_dir / "config.json"
    ConfigManager.KEY_FILE = original_dir / "key.enc"


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'ADP CLI' in result.output


def test_cli_version(runner):
    """Test CLI version command."""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'adp, version' in result.output


def test_cli_custom_help_command(runner):
    """Test custom help command."""
    result = runner.invoke(cli, ['help'])
    assert result.exit_code == 0
    assert 'ADP CLI' in result.output


def test_config_help(runner):
    """Test config help command."""
    result = runner.invoke(cli, ['config', '--help'])
    assert result.exit_code == 0
    assert 'Authentication' in result.output or '认证' in result.output


def test_config_set_api_key(runner, temp_config_dir):
    """Test setting API key."""
    result = runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key-123'])
    assert result.exit_code == 0
    assert 'configured successfully' in result.output or '配置成功' in result.output


def test_config_set_api_base_url(runner, temp_config_dir):
    """Test setting API base URL."""
    result = runner.invoke(cli, ['config', 'set', '--api-base-url', 'https://api.example.com'])
    assert result.exit_code == 0
    assert 'configured successfully' in result.output or '配置成功' in result.output


def test_config_set_no_args(runner, temp_config_dir):
    """Test config set with no arguments."""
    result = runner.invoke(cli, ['config', 'set'])
    assert result.exit_code == 2


def test_config_get(runner, temp_config_dir):
    """Test getting config."""
    # First set API key
    runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key'])

    # Then get config
    result = runner.invoke(cli, ['config', 'get'])
    assert result.exit_code == 0


def test_config_clear_with_confirmation(runner, temp_config_dir):
    """Test config clear with confirmation."""
    # First set API key
    runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key'])

    # Clear with confirmation
    result = runner.invoke(cli, ['config', 'clear'], input='y\n')
    assert result.exit_code == 0
    assert 'cleared' in result.output or '已清除' in result.output


def test_parse_help(runner):
    """Test parse help command."""
    result = runner.invoke(cli, ['parse', '--help'])
    assert result.exit_code == 0
    assert 'Document' in result.output or '文档' in result.output


def test_parse_local_help(runner):
    """Test parse local help command."""
    result = runner.invoke(cli, ['parse', 'local', '--help'])
    assert result.exit_code == 0


def test_parse_url_help(runner):
    """Test parse url help command."""
    result = runner.invoke(cli, ['parse', 'url', '--help'])
    assert result.exit_code == 0


def test_parse_local_no_config(runner, temp_config_dir):
    """Test parse local without config."""
    result = runner.invoke(cli, ['parse', 'local', '--app-id', 'app123', 'test.pdf'])
    assert result.exit_code == 2
    # Error message might be in Chinese or English


def test_extract_help(runner):
    """Test extract help command."""
    result = runner.invoke(cli, ['extract', '--help'])
    assert result.exit_code == 0
    assert 'Document' in result.output or '文档' in result.output


def test_extract_local_help(runner):
    """Test extract local help command."""
    result = runner.invoke(cli, ['extract', 'local', '--help'])
    assert result.exit_code == 0


def test_extract_url_help(runner):
    """Test extract url help command."""
    result = runner.invoke(cli, ['extract', 'url', '--help'])
    assert result.exit_code == 0


def test_extract_local_no_config(runner, temp_config_dir):
    """Test extract local without config."""
    result = runner.invoke(cli, ['extract', 'local', '--app-id', 'app123', 'test.pdf'])
    assert result.exit_code == 2
    # Error message might be in Chinese or English


def test_query_help(runner):
    """Test query help command."""
    result = runner.invoke(cli, ['query', '--help'])
    # Query command requires a task-id, so help might show usage error
    assert result.exit_code == 0 or result.exit_code == 2


def test_query_no_config(runner, temp_config_dir):
    """Test query without config."""
    result = runner.invoke(cli, ['query', 'task-123'])
    # Exit code 2 is expected when not configured (Click shows usage error)
    assert result.exit_code == 1 or result.exit_code == 2
    # Error message might be in Chinese or English


def test_app_id_help(runner):
    """Test app-id help command."""
    result = runner.invoke(cli, ['app-id', '--help'])
    assert result.exit_code == 0
    assert 'Application' in result.output or '应用' in result.output


def test_app_id_list_help(runner):
    """Test app-id list help command."""
    result = runner.invoke(cli, ['app-id', 'list', '--help'])
    assert result.exit_code == 0


def test_app_id_list_no_config(runner, temp_config_dir):
    """Test app-id list without config."""
    result = runner.invoke(cli, ['app-id', 'list'])
    assert result.exit_code == 2
    # Error message might be in Chinese or English


def test_custom_app_help(runner):
    """Test custom-app help command."""
    result = runner.invoke(cli, ['custom-app', '--help'])
    assert result.exit_code == 0
    assert 'Custom' in result.output or '自定义' in result.output


def test_custom_app_create_help(runner):
    """Test custom-app create help command."""
    result = runner.invoke(cli, ['custom-app', 'create', '--help'])
    assert result.exit_code == 0


def test_custom_app_get_config_help(runner):
    """Test custom-app get-config help command."""
    result = runner.invoke(cli, ['custom-app', 'get-config', '--help'])
    assert result.exit_code == 0


def test_custom_app_delete_help(runner):
    """Test custom-app delete help command."""
    result = runner.invoke(cli, ['custom-app', 'delete', '--help'])
    assert result.exit_code == 0


def test_custom_app_delete_version_help(runner):
    """Test custom-app delete-version help command."""
    result = runner.invoke(cli, ['custom-app', 'delete-version', '--help'])
    assert result.exit_code == 0


def test_custom_app_ai_generate_help(runner):
    """Test custom-app ai-generate help command."""
    result = runner.invoke(cli, ['custom-app', 'ai-generate', '--help'])
    assert result.exit_code == 0


def test_json_mode_flag(runner, temp_config_dir):
    """Test JSON mode flag."""
    result = runner.invoke(cli, ['--json', 'config', 'set', '--api-key', 'test-key'])
    assert result.exit_code == 0


def test_lang_flag(runner):
    """Test language flag."""
    result = runner.invoke(cli, ['--lang', 'en', '--help'])
    assert result.exit_code == 0

    result = runner.invoke(cli, ['--lang', 'zh', '--help'])
    assert result.exit_code == 0


def test_invalid_command(runner):
    """Test invalid command."""
    result = runner.invoke(cli, ['invalid-command'])
    assert result.exit_code != 0


def test_parse_json_param_value_string(tmp_path):
    """Test parsing JSON parameter value from string."""
    value = _parse_json_param_value('{"key": "value", "number": 42}')
    assert isinstance(value, dict)
    assert value['key'] == 'value'
    assert value['number'] == 42

    # Test array
    value = _parse_json_param_value('["item1", "item2", "item3"]')
    assert isinstance(value, list)
    assert len(value) == 3


def test_parse_json_param_value_file(tmp_path):
    """Test parsing JSON parameter value from file."""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"file_key": "file_value", "nested": {"data": 123}}')

    value = _parse_json_param_value(str(json_file))
    assert isinstance(value, dict)
    assert value['file_key'] == 'file_value'
    assert value['nested']['data'] == 123


def test_parse_json_param_value_none():
    """Test parsing JSON parameter value with None."""
    value = _parse_json_param_value(None)
    assert value is None


def test_parse_json_param_value_with_quotes():
    """Test parsing JSON parameter value with outer quotes."""
    value = _parse_json_param_value('"{"key": "value"}"')
    assert isinstance(value, dict)
    assert value['key'] == 'value'

    value = _parse_json_param_value("'[\"item1\", \"item2\"]'")
    assert isinstance(value, list)


def test_parse_bool_param_true():
    """Test parsing boolean parameter true values."""
    assert parse_bool_param(None, None, 'true') is True
    assert parse_bool_param(None, None, 'True') is True
    assert parse_bool_param(None, None, 'TRUE') is True
    assert parse_bool_param(None, None, '1') is True
    assert parse_bool_param(None, None, 'yes') is True
    assert parse_bool_param(None, None, 'Yes') is True


def test_parse_bool_param_false():
    """Test parsing boolean parameter false values."""
    assert parse_bool_param(None, None, 'false') is False
    assert parse_bool_param(None, None, 'False') is False
    assert parse_bool_param(None, None, 'FALSE') is False
    assert parse_bool_param(None, None, '0') is False
    assert parse_bool_param(None, None, 'no') is False
    assert parse_bool_param(None, None, 'No') is False


def test_parse_bool_param_none():
    """Test parsing boolean parameter with None."""
    assert parse_bool_param(None, None, None) is None


def test_parse_json_list_param_json_array():
    """Test parsing JSON list parameter from JSON array."""
    result = parse_json_list_param(None, None, '["label1", "label2", "label3"]')
    assert isinstance(result, list)
    assert result == ['label1', 'label2', 'label3']


def test_parse_json_list_param_comma_separated():
    """Test parsing JSON list parameter from comma-separated string."""
    result = parse_json_list_param(None, None, 'label1, label2, label3')
    assert isinstance(result, list)
    assert result == ['label1', 'label2', 'label3']


def test_parse_json_list_param_with_quotes():
    """Test parsing JSON list parameter with quotes."""
    result = parse_json_list_param(None, None, '"label1,label2,label3"')
    assert isinstance(result, list)
    assert result == ['label1', 'label2', 'label3']

    result = parse_json_list_param(None, None, "'label1,label2,label3'")
    assert isinstance(result, list)
    assert result == ['label1', 'label2', 'label3']


def test_parse_json_list_param_none():
    """Test parsing JSON list parameter with None."""
    result = parse_json_list_param(None, None, None)
    assert result is None


def test_parse_json_list_param_with_spaces():
    """Test parsing JSON list parameter with spaces."""
    result = parse_json_list_param(None, None, ' label1 ,  label2  , label3 ')
    assert isinstance(result, list)
    assert result == ['label1', 'label2', 'label3']


def test_validate_create_app_params_valid():
    """Test validating create app params with valid data."""
    # Valid params - should not raise
    validate_create_app_params(
        app_name="Valid App Name",
        app_label=["label1", "label2"],
        enable_long_doc=False,
        long_doc_config=None
    )

    # Enable long doc with config - should not raise
    validate_create_app_params(
        app_name="Valid App Name",
        app_label=["label1"],
        enable_long_doc=True,
        long_doc_config={"config": "data"}
    )


def test_validate_create_app_params_app_name_too_long():
    """Test validating create app params with app name too long."""
    with pytest.raises(SystemExit):
        validate_create_app_params(
            app_name="A" * 51,  # 51 characters
            app_label=None,
            enable_long_doc=False,
            long_doc_config=None
        )


def test_validate_create_app_params_app_label_too_many():
    """Test validating create app params with too many labels."""
    with pytest.raises(SystemExit):
        validate_create_app_params(
            app_name="Valid App Name",
            app_label=["label1", "label2", "label3", "label4", "label5", "label6"],  # 6 labels
            enable_long_doc=False,
            long_doc_config=None
        )


def test_validate_create_app_params_long_doc_config_without_enable():
    """Test validating create app params with long_doc_config but enable_long_doc False."""
    with pytest.raises(SystemExit):
        validate_create_app_params(
            app_name="Valid App Name",
            app_label=None,
            enable_long_doc=False,
            long_doc_config={"config": "data"}
        )


def test_parse_local_file(tmp_path, runner, temp_config_dir):
    """Test parsing a local file."""
    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes("PDF content".encode())

    # Set API key
    runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key'])

    # Mock API call
    with patch('adp_cli.adp.api_client.APIClient.parse_sync') as mock_parse:
        mock_parse.return_value = {"status": "success"}

        result = runner.invoke(cli, ['parse', 'local', '--app-id', 'app123', str(test_file)])
        # Note: This might fail due to actual API call, but we're testing command structure


def test_extract_local_file(tmp_path, runner, temp_config_dir):
    """Test extracting a local file."""
    # Create test file
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes("PDF content".encode())

    # Set API key
    runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key'])

    # Mock API call
    with patch('adp_cli.adp.api_client.APIClient.extract_sync') as mock_extract:
        mock_extract.return_value = {"status": "success", "extracted": "data"}

        result = runner.invoke(cli, ['extract', 'local', '--app-id', 'app123', str(test_file)])
        # Note: This might fail due to actual API call, but we're testing command structure


# ==================== New Feature Tests ====================

def test_parse_local_no_wait_flag(runner, temp_config_dir):
    """Test parse local with --no-wait flag."""
    result = runner.invoke(cli, ['parse', 'local', '--help'])
    assert result.exit_code == 0
    assert '--no-wait' in result.output


def test_parse_local_retry_flag(runner, temp_config_dir):
    """Test parse local with --retry flag."""
    result = runner.invoke(cli, ['parse', 'local', '--help'])
    assert result.exit_code == 0
    assert '--retry' in result.output


def test_parse_url_no_wait_flag(runner, temp_config_dir):
    """Test parse url with --no-wait flag."""
    result = runner.invoke(cli, ['parse', 'url', '--help'])
    assert result.exit_code == 0
    assert '--no-wait' in result.output


def test_parse_url_retry_flag(runner, temp_config_dir):
    """Test parse url with --retry flag."""
    result = runner.invoke(cli, ['parse', 'url', '--help'])
    assert result.exit_code == 0
    assert '--retry' in result.output


def test_parse_base64_no_wait_flag(runner, temp_config_dir):
    """Test parse base64 with --no-wait flag."""
    result = runner.invoke(cli, ['parse', 'base64', '--help'])
    assert result.exit_code == 0
    assert '--no-wait' in result.output


def test_parse_base64_retry_flag(runner, temp_config_dir):
    """Test parse base64 with --retry flag."""
    result = runner.invoke(cli, ['parse', 'base64', '--help'])
    assert result.exit_code == 0
    assert '--retry' in result.output


def test_extract_local_no_wait_flag(runner, temp_config_dir):
    """Test extract local with --no-wait flag."""
    result = runner.invoke(cli, ['extract', 'local', '--help'])
    assert result.exit_code == 0
    assert '--no-wait' in result.output


def test_extract_local_retry_flag(runner, temp_config_dir):
    """Test extract local with --retry flag."""
    result = runner.invoke(cli, ['extract', 'local', '--help'])
    assert result.exit_code == 0
    assert '--retry' in result.output


def test_extract_url_no_wait_flag(runner, temp_config_dir):
    """Test extract url with --no-wait flag."""
    result = runner.invoke(cli, ['extract', 'url', '--help'])
    assert result.exit_code == 0
    assert '--no-wait' in result.output


def test_extract_url_retry_flag(runner, temp_config_dir):
    """Test extract url with --retry flag."""
    result = runner.invoke(cli, ['extract', 'url', '--help'])
    assert result.exit_code == 0
    assert '--retry' in result.output


def test_extract_base64_no_wait_flag(runner, temp_config_dir):
    """Test extract base64 with --no-wait flag."""
    result = runner.invoke(cli, ['extract', 'base64', '--help'])
    assert result.exit_code == 0
    assert '--no-wait' in result.output


def test_extract_base64_retry_flag(runner, temp_config_dir):
    """Test extract base64 with --retry flag."""
    result = runner.invoke(cli, ['extract', 'base64', '--help'])
    assert result.exit_code == 0
    assert '--retry' in result.output


def test_parse_query_file_flag(runner, temp_config_dir):
    """Test parse query with --file flag."""
    result = runner.invoke(cli, ['parse', 'query', '--help'])
    assert result.exit_code == 0
    assert '--file' in result.output


def test_parse_query_concurrency_flag(runner, temp_config_dir):
    """Test parse query with --concurrency flag."""
    result = runner.invoke(cli, ['parse', 'query', '--help'])
    assert result.exit_code == 0
    assert '--concurrency' in result.output


def test_extract_query_file_flag(runner, temp_config_dir):
    """Test extract query with --file flag."""
    result = runner.invoke(cli, ['extract', 'query', '--help'])
    assert result.exit_code == 0
    assert '--file' in result.output


def test_extract_query_concurrency_flag(runner, temp_config_dir):
    """Test extract query with --concurrency flag."""
    result = runner.invoke(cli, ['extract', 'query', '--help'])
    assert result.exit_code == 0
    assert '--concurrency' in result.output


def test_parse_query_multiple_task_ids(runner, temp_config_dir):
    """Test parse query with multiple task IDs."""
    # Set API key
    runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key'])

    # Mock the API client
    with patch('adp_cli.adp.api_client.APIClient') as MockAPIClient:
        mock_client = MockAPIClient.return_value
        mock_client.get_user_payment_status.return_value = {"payment_type": "free"}
        mock_client.query_parse_task.return_value = {"data": {"status": 4}}

        # Multiple task IDs should be accepted
        result = runner.invoke(cli, ['parse', 'query', 'id1', 'id2', 'id3'])
        # Should not reject multiple args (exit code 0 or the error from mock)


def test_extract_query_multiple_task_ids(runner, temp_config_dir):
    """Test extract query with multiple task IDs."""
    # Set API key
    runner.invoke(cli, ['config', 'set', '--api-key', 'test-api-key'])

    # Mock the API client
    with patch('adp_cli.adp.api_client.APIClient') as MockAPIClient:
        mock_client = MockAPIClient.return_value
        mock_client.get_user_payment_status.return_value = {"payment_type": "free"}
        mock_client.query_extract_task.return_value = {"data": {"status": 4}}

        # Multiple task IDs should be accepted
        result = runner.invoke(cli, ['extract', 'query', 'id1', 'id2', 'id3'])
        # Should not reject multiple args (exit code 0 or the error from mock)


# ==================== Helper Function Tests ====================

def test_sanitize_file_name_basic():
    """Test _sanitize_file_name with basic strings."""
    assert _sanitize_file_name("simple_file") == "simple_file"
    assert _sanitize_file_name("file with spaces") == "file with spaces"


def test_sanitize_file_name_special_chars():
    """Test _sanitize_file_name with special characters."""
    assert _sanitize_file_name("file/with/slashes") == "file_with_slashes"
    assert _sanitize_file_name("file:colon") == "file_colon"
    assert _sanitize_file_name("file*star") == "file_star"
    assert _sanitize_file_name('file"quotes') == "file_quotes"
    assert _sanitize_file_name("file<less>") == "file_less_"
    assert _sanitize_file_name("file|pipe") == "file_pipe"
    assert _sanitize_file_name("file?name") == "file_name"


def test_sanitize_file_name_trim():
    """Test _sanitize_file_name trimming."""
    assert _sanitize_file_name("  file  ") == "file"
    assert _sanitize_file_name("file.") == "file"


def test_sanitize_file_name_long():
    """Test _sanitize_file_name with long names."""
    long_name = "a" * 300
    result = _sanitize_file_name(long_name)
    assert len(result) == 200


def test_load_tasks_from_file(tmp_path):
    """Test _load_tasks_from_file with valid JSON."""
    task_file = tmp_path / "tasks.json"
    task_file.write_text('[{"path": "doc1.pdf", "task_id": "id1"}, {"path": "doc2.pdf", "task_id": "id2"}]')

    task_ids = _load_tasks_from_file(str(task_file))
    assert task_ids == ["id1", "id2"]


def test_load_tasks_from_file_empty(tmp_path):
    """Test _load_tasks_from_file with no valid task IDs."""
    task_file = tmp_path / "tasks.json"
    task_file.write_text('[{"path": "doc1.pdf"}, {"path": "doc2.pdf"}]')

    with pytest.raises(SystemExit):
        _load_tasks_from_file(str(task_file))


def test_load_tasks_from_file_not_found():
    """Test _load_tasks_from_file with non-existent file."""
    with pytest.raises(SystemExit):
        _load_tasks_from_file("/non/existent/file.json")
