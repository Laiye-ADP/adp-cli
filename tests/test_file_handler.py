"""Tests for FileHandler."""

import pytest
import tempfile
from pathlib import Path

from adp_cli.adp.file_handler import FileHandler


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时目录和测试文件。"""
    # 创建支持的文件
    (tmp_path / "test.pdf").write_text("PDF content")
    (tmp_path / "test.jpg").write_bytes(b"JPG content")
    (tmp_path / "test.docx").write_text("DOCX content")
    (tmp_path / "unsupported.txt").write_text("TXT content")

    # 创建子目录
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.pdf").write_text("Nested PDF")

    yield tmp_path


def test_is_supported_file(temp_dir):
    """测试检查文件是否支持。"""
    assert FileHandler.is_supported_file(temp_dir / "test.pdf") is True
    assert FileHandler.is_supported_file(temp_dir / "test.jpg") is True
    assert FileHandler.is_supported_file(temp_dir / "test.docx") is True
    assert FileHandler.is_supported_file(temp_dir / "unsupported.txt") is False


def test_is_valid_size(temp_dir):
    """测试检查文件大小是否有效。"""
    assert FileHandler.is_valid_size(temp_dir / "test.pdf") is True


def test_validate_file(temp_dir):
    """测试验证文件。"""
    # 有效文件
    is_valid, error = FileHandler.validate_file(temp_dir / "test.pdf")
    assert is_valid is True
    assert error is None

    # 不存在的文件
    is_valid, error = FileHandler.validate_file(temp_dir / "nonexistent.pdf")
    assert is_valid is False
    assert "not found" in error

    # 不支持的文件
    is_valid, error = FileHandler.validate_file(temp_dir / "unsupported.txt")
    assert is_valid is False
    assert "Unsupported" in error


def test_get_files_from_path_file(temp_dir):
    """测试从文件路径获取文件列表。"""
    files = FileHandler.get_files_from_path(temp_dir / "test.pdf")

    assert len(files) == 1
    assert files[0] == temp_dir / "test.pdf"


def test_get_files_from_path_directory(temp_dir):
    """测试从目录路径获取文件列表。"""
    files = FileHandler.get_files_from_path(temp_dir)

    assert len(files) == 4  # test.pdf, test.jpg, test.docx, nested.pdf
    assert (temp_path / "unsupported.txt") not in files


def test_validate_files(temp_dir):
    """测试验证多个文件。"""
    files = [
        temp_dir / "test.pdf",
        temp_dir / "unsupported.txt",
        temp_dir / "nonexistent.pdf",
    ]

    valid_files, invalid_files = FileHandler.validate_files(files)

    assert len(valid_files) == 1
    assert len(invalid_files) == 2


def test_format_file_size():
    """测试格式化文件大小。"""
    assert FileHandler.format_file_size(100) == "100.00 B"
    assert "KB" in FileHandler.format_file_size(1024 * 2)
    assert "MB" in FileHandler.format_file_size(1024 * 1024 * 2)


def test_batch_process():
    """测试批量处理。"""
    items = list(range(25))
    batches = list(FileHandler.batch_process(items, batch_size=10))

    assert len(batches) == 3
    assert len(batches[0]) == 10
    assert len(batches[1]) == 10
    assert len(batches[2]) == 5
