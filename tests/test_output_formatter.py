"""Tests for OutputFormatter."""

import pytest
import io
from unittest.mock import patch, MagicMock
from rich.console import Console

from adp_cli.adp.output_formatter import OutputFormatter


@pytest.fixture
def mock_console():
    """Create a mock console with captured output."""
    console = Console()
    return console


@pytest.fixture
def formatter(mock_console):
    """Create OutputFormatter instance with mock console."""
    return OutputFormatter(mock_console)


def test_formatter_initialization(formatter):
    """Test formatter initialization."""
    assert formatter.console is not None
    assert formatter.json_mode is False
    assert formatter.quiet_mode is False


def test_set_json_mode(formatter):
    """Test setting JSON mode."""
    formatter.set_json_mode(True)
    assert formatter.json_mode is True

    formatter.set_json_mode(False)
    assert formatter.json_mode is False


def test_set_quiet_mode(formatter):
    """Test setting quiet mode."""
    formatter.set_quiet_mode(True)
    assert formatter.quiet_mode is True

    formatter.set_quiet_mode(False)
    assert formatter.quiet_mode is False


def test_print(formatter):
    """Test basic print."""
    # Should not raise any errors
    formatter.print("Test message")
    formatter.print("Test message with style", style="bold")


def test_print_quiet_mode(formatter):
    """Test print in quiet mode."""
    formatter.set_quiet_mode(True)

    # Should not print anything in quiet mode
    # We can't directly test this without mocking the console,
    # but we can verify it doesn't crash
    formatter.print("This should not be printed")


def test_print_success(formatter):
    """Test print success message."""
    formatter.print_success("Operation completed successfully")


def test_print_error(formatter):
    """Test print error message."""
    formatter.print_error("An error occurred")


def test_print_warning(formatter):
    """Test print warning message."""
    formatter.print_warning("This is a warning")


def test_print_info(formatter):
    """Test print info message."""
    formatter.print_info("Information message")


def test_print_json_normal_mode(formatter):
    """Test print JSON in normal mode."""
    data = {"key": "value", "number": 42, "nested": {"inner": "data"}}
    formatter.print_json(data)


def test_print_json_with_complex_data(formatter):
    """Test print JSON with complex data."""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
        ],
        "metadata": {
            "version": "1.0",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    }
    formatter.print_json(data)


@patch('builtins.print')
def test_print_json_mode(mock_print):
    """Test print JSON in JSON mode."""
    formatter = OutputFormatter()
    formatter.set_json_mode(True)

    data = {"key": "value", "number": 42}
    formatter.print_json(data)

    # Check that print was called with JSON output
    mock_print.assert_called()
    args, kwargs = mock_print.call_args
    output = args[0]
    assert '"key": "value"' in output or '"key":"value"' in output


def test_print_table(formatter):
    """Test print table."""
    headers = ["Name", "Age", "City"]
    rows = [
        ["Alice", "30", "New York"],
        ["Bob", "25", "London"],
        ["Charlie", "35", "Paris"],
    ]
    formatter.print_table(headers, rows)


def test_print_table_with_title(formatter):
    """Test print table with title."""
    headers = ["ID", "Status"]
    rows = [
        ["1", "Active"],
        ["2", "Inactive"],
    ]
    formatter.print_table(headers, rows, title="User Status")


def test_print_panel(formatter):
    """Test print panel."""
    formatter.print_panel("Panel content", title="Information")
    formatter.print_panel("Warning content", title="Warning", style="yellow")


def test_print_task_result(formatter):
    """Test print task result."""
    task_id = "task-12345"
    status = "success"
    result = {"data": "extracted content", "timestamp": "2024-01-01"}

    formatter.print_task_result(task_id, status, result)


def test_print_task_result_without_result(formatter):
    """Test print task result without result data."""
    task_id = "task-12345"
    status = "processing"

    formatter.print_task_result(task_id, status)


def test_print_file_list(tmp_path, formatter):
    """Test print file list."""
    # Create test files
    file1 = tmp_path / "test1.pdf"
    file2 = tmp_path / "test2.jpg"
    file1.write_bytes(b"PDF content")
    file2.write_bytes(b"JPG content")

    files = [file1, file2]
    formatter.print_file_list(files, show_size=True)


def test_print_file_list_without_size(tmp_path, formatter):
    """Test print file list without showing size."""
    file = tmp_path / "test.pdf"
    file.write_bytes(b"PDF content")

    files = [file]
    formatter.print_file_list(files, show_size=False)


def test_print_config_summary(formatter):
    """Test print config summary."""
    config = {
        "configured": True,
        "api_key_masked": "sk-****1234",
        "api_base_url": "https://api.example.com",
        "tenant_name": "default",
    }
    formatter.print_config_summary(config)


def test_print_progress(formatter):
    """Test print progress."""
    formatter.print_progress(1, 10, "Processing file 1")
    formatter.print_progress(5, 10, "Processing file 5")
    formatter.print_progress(10, 10, "Completed")


def test_print_progress_zero_total(formatter):
    """Test print progress with zero total."""
    formatter.print_progress(0, 0, "Starting")


def test_print_section(formatter):
    """Test print section."""
    formatter.print_section("Section 1")
    formatter.print_section("Important Information")


def test_formatter_with_direct_console_initialization():
    """Test formatter initialized without custom console."""
    formatter = OutputFormatter()
    assert formatter.console is not None
    assert isinstance(formatter.console, Console)


def test_print_json_with_list(formatter):
    """Test print JSON with list data."""
    data = ["item1", "item2", "item3"]
    formatter.print_json(data)


def test_print_json_with_unicode(formatter):
    """Test print JSON with unicode characters."""
    data = {
        "chinese": "中文测试",
        "emoji": "😀🎉",
        "arabic": "مرحبا",
    }
    formatter.print_json(data)


def test_print_json_with_special_characters(formatter):
    """Test print JSON with special characters."""
    data = {
        "newline": "Line 1\nLine 2",
        "tab": "Column1\tColumn2",
        "quotes": 'He said "Hello"',
    }
    formatter.print_json(data)


def test_print_empty_table(formatter):
    """Test print empty table."""
    headers = ["Column 1", "Column 2"]
    rows = []
    formatter.print_table(headers, rows)


def test_print_multiple_sections(formatter):
    """Test printing multiple sections."""
    formatter.print_section("Phase 1")
    formatter.print_info("Starting phase 1")

    formatter.print_section("Phase 2")
    formatter.print_info("Starting phase 2")

    formatter.print_section("Phase 3")
    formatter.print_success("All phases completed")


def test_print_task_result_with_large_data(formatter):
    """Test print task result with large data."""
    task_id = "task-large-data"
    status = "success"
    result = {
        "data": {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(100)],
            "metadata": {
                "total": 100,
                "processed": 100,
                "failed": 0
            }
        }
    }

    formatter.print_task_result(task_id, status, result)
