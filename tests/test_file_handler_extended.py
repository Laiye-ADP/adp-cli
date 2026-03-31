"""Extended tests for FileHandler."""

import pytest
import tempfile
import json
from pathlib import Path

from adp_cli.adp.file_handler import FileHandler


@pytest.fixture
def temp_dir(tmp_path):
    """创建临时目录和测试文件。"""
    yield tmp_path


def test_is_valid_size_large_file(temp_dir):
    """测试检查文件大小 - 大文件场景。"""
    # 创建一个接近限制的文件 (49MB)
    large_file = temp_dir / "large.pdf"
    large_size = 49 * 1024 * 1024  # 49MB
    large_file.write_bytes(b"x" * large_size)

    assert FileHandler.is_valid_size(large_file) is True


def test_is_valid_size_exceeds_limit(temp_dir):
    """测试检查文件大小 - 超过限制。"""
    # 创建一个超过限制的文件 (51MB)
    huge_file = temp_dir / "huge.pdf"
    huge_size = 51 * 1024 * 1024  # 51MB
    huge_file.write_bytes(b"x" * huge_size)

    assert FileHandler.is_valid_size(huge_file) is False


def test_validate_file_too_large(temp_dir):
    """测试验证文件大小过大。"""
    huge_file = temp_dir / "huge.pdf"
    huge_size = 51 * 1024 * 1024  # 51MB
    huge_file.write_bytes(b"x" * huge_size)

    is_valid, error = FileHandler.validate_file(huge_file)
    assert is_valid is False
    assert "too large" in error.lower() or "过大" in error


def test_validate_file_directory_as_file(temp_dir):
    """测试验证目录作为文件。"""
    dir_path = temp_dir / "test_dir"
    dir_path.mkdir()

    is_valid, error = FileHandler.validate_file(dir_path)
    assert is_valid is False
    assert "not a file" in error.lower() or "不是文件" in error


def test_get_files_from_path_nonexistent(temp_dir):
    """测试从不存在的路径获取文件。"""
    nonexistent = temp_dir / "nonexistent"

    with pytest.raises(FileNotFoundError, match="not found" or "不存在"):
        FileHandler.get_files_from_path(nonexistent)


def test_get_files_from_path_empty_directory(temp_dir):
    """测试从空目录获取文件。"""
    empty_dir = temp_dir / "empty"
    empty_dir.mkdir()

    files = FileHandler.get_files_from_path(empty_dir)
    assert files == []


def test_get_files_from_path_mixed_directory(temp_dir):
    """测试从混合目录获取文件（支持的和不支持的）。"""
    # 创建支持的文件
    (temp_dir / "test1.pdf").write_text("PDF")
    (temp_dir / "test2.jpg").write_bytes(b"JPG")
    # 创建不支持的文件
    (temp_dir / "test3.txt").write_text("TXT")
    (temp_dir / "test4.xml").write_text("XML")
    # 创建子目录（应该被忽略）
    subdir = temp_dir / "subdir"
    subdir.mkdir()

    files = FileHandler.get_files_from_path(temp_dir)

    assert len(files) == 2
    assert (temp_dir / "test1.pdf") in files
    assert (temp_dir / "test2.jpg") in files
    assert (temp_dir / "test3.txt") not in files
    assert (temp_dir / "test4.xml") not in files


def test_read_url_list_file(temp_dir):
    """测试读取 URL 列表文件。"""
    url_file = temp_dir / "urls.txt"
    url_file.write_text("""http://example.com/file1.pdf
http://example.com/file2.jpg

https://example.com/file3.docx

invalid-url
http://example.com/file4.pdf""")

    urls = FileHandler.read_url_list_file(url_file)

    assert len(urls) == 4
    assert "http://example.com/file1.pdf" in urls
    assert "http://example.com/file2.jpg" in urls
    assert "https://example.com/file3.docx" in urls
    assert "http://example.com/file4.pdf" in urls


def test_read_url_list_file_nonexistent(temp_dir):
    """测试读取不存在的 URL 列表文件。"""
    nonexistent = temp_dir / "nonexistent.txt"

    with pytest.raises(FileNotFoundError, match="not found" or "不存在"):
        FileHandler.read_url_list_file(nonexistent)


def test_read_url_list_file_empty(temp_dir):
    """测试读取空的 URL 列表文件。"""
    empty_file = temp_dir / "empty.txt"
    empty_file.write_text("")

    urls = FileHandler.read_url_list_file(empty_file)
    assert urls == []


def test_read_url_list_file_comments_and_whitespace(temp_dir):
    """测试读取包含注释和空白行的 URL 列表文件。"""
    url_file = temp_dir / "urls.txt"
    url_file.write_text("""
    # This is a comment
    http://example.com/file1.pdf

    # Another comment
    https://example.com/file2.jpg

    """)

    urls = FileHandler.read_url_list_file(url_file)

    assert len(urls) == 2


def test_write_json_output(temp_dir):
    """测试写入 JSON 输出。"""
    output_file = temp_dir / "output.json"
    data = {
        "status": "success",
        "data": {
            "field1": "value1",
            "field2": 123,
            "nested": {"key": "value"}
        }
    }

    FileHandler.write_json_output(data, output_file)

    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    assert loaded_data == data


def test_write_json_output_create_directory(temp_dir):
    """测试写入 JSON 输出时创建目录。"""
    output_file = temp_dir / "subdir" / "nested" / "output.json"
    data = {"test": "data"}

    FileHandler.write_json_output(data, output_file)

    assert output_file.exists()
    assert output_file.parent.exists()


def test_get_mime_type(temp_dir):
    """测试获取 MIME 类型。"""
    # 创建各种类型的测试文件
    files = [
        ("test.pdf", "pdf"),
        ("test.jpg", "jpeg"),
        ("test.jpeg", "jpeg"),
        ("test.png", "png"),
        ("test.gif", "gif"),
        ("test.doc", "msword"),
        ("test.docx", "wordprocessingml"),
        ("test.xls", "ms-excel"),
        ("test.xlsx", "spreadsheetml"),
        ("test.ppt", "ms-powerpoint"),
        ("test.pptx", "presentationml"),
    ]

    for filename, expected_mime in files:
        test_file = temp_dir / filename
        test_file.write_text("content")
        mime = FileHandler.get_mime_type(test_file)
        assert expected_mime in mime or "application/octet-stream" in mime


def test_get_mime_type_unknown_extension(temp_dir):
    """测试获取未知扩展名文件的 MIME 类型。"""
    unknown_file = temp_dir / "test.unknown"
    unknown_file.write_text("content")

    mime = FileHandler.get_mime_type(unknown_file)
    assert mime == "application/octet-stream"


def test_format_file_size_bytes():
    """测试格式化文件大小 - 字节。"""
    assert FileHandler.format_file_size(0) == "0.00 B"
    assert FileHandler.format_file_size(1) == "1.00 B"
    assert FileHandler.format_file_size(999) == "999.00 B"


def test_format_file_size_kilobytes():
    """测试格式化文件大小 - 千字节。"""
    assert FileHandler.format_file_size(1024) == "1.00 KB"
    assert FileHandler.format_file_size(1536) == "1.50 KB"
    assert FileHandler.format_file_size(1024 * 999) == "999.00 KB"


def test_format_file_size_megabytes():
    """测试格式化文件大小 - 兆字节。"""
    assert FileHandler.format_file_size(1024 * 1024) == "1.00 MB"
    assert FileHandler.format_file_size(2 * 1024 * 1024) == "2.00 MB"
    assert FileHandler.format_file_size(2.5 * 1024 * 1024) == "2.50 MB"


def test_format_file_size_gigabytes():
    """测试格式化文件大小 - 吉字节。"""
    assert FileHandler.format_file_size(1024 * 1024 * 1024) == "1.00 GB"
    assert FileHandler.format_file_size(2 * 1024 * 1024 * 1024) == "2.00 GB"


def test_batch_process_single():
    """测试批量处理 - 单个批次。"""
    items = [1, 2, 3]
    batches = list(FileHandler.batch_process(items, batch_size=10))

    assert len(batches) == 1
    assert batches[0] == [1, 2, 3]


def test_batch_process_multiple():
    """测试批量处理 - 多个批次。"""
    items = list(range(10))
    batches = list(FileHandler.batch_process(items, batch_size=3))

    assert len(batches) == 4
    assert batches[0] == [0, 1, 2]
    assert batches[1] == [3, 4, 5]
    assert batches[2] == [6, 7, 8]
    assert batches[3] == [9]


def test_batch_process_empty():
    """测试批量处理 - 空列表。"""
    batches = list(FileHandler.batch_process([], batch_size=10))
    assert batches == []


def test_batch_process_batch_size_one():
    """测试批量处理 - 批次大小为 1。"""
    items = [1, 2, 3]
    batches = list(FileHandler.batch_process(items, batch_size=1))

    assert len(batches) == 3
    assert batches[0] == [1]
    assert batches[1] == [2]
    assert batches[2] == [3]


def test_is_supported_file_case_insensitive():
    """测试检查文件是否支持 - 大小写不敏感。"""
    pdf_upper = Path("test.PDF")
    pdf_lower = Path("test.pdf")
    pdf_mixed = Path("test.Pdf")

    assert FileHandler.is_supported_file(pdf_upper) is True
    assert FileHandler.is_supported_file(pdf_lower) is True
    assert FileHandler.is_supported_file(pdf_mixed) is True


def test_is_supported_file_all_supported_extensions():
    """测试所有支持的文件扩展名。"""
    supported_extensions = [
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"
    ]

    for ext in supported_extensions:
        test_file = Path(f"test{ext}")
        assert FileHandler.is_supported_file(test_file) is True


def test_validate_files_all_valid(temp_dir):
    """测试验证多个文件 - 全部有效。"""
    (temp_dir / "test1.pdf").write_text("PDF")
    (temp_dir / "test2.jpg").write_bytes(b"JPG")

    files = [temp_dir / "test1.pdf", temp_dir / "test2.jpg"]
    valid_files, invalid_files = FileHandler.validate_files(files)

    assert len(valid_files) == 2
    assert len(invalid_files) == 0


def test_validate_files_all_invalid(temp_dir):
    """测试验证多个文件 - 全部无效。"""
    (temp_dir / "test1.txt").write_text("TXT")
    (temp_dir / "test2.xml").write_text("XML")

    files = [temp_dir / "test1.txt", temp_dir / "test2.xml"]
    valid_files, invalid_files = FileHandler.validate_files(files)

    assert len(valid_files) == 0
    assert len(invalid_files) == 2


def test_validate_files_mixed(temp_dir):
    """测试验证多个文件 - 混合有效和无效。"""
    (temp_dir / "valid.pdf").write_text("PDF")
    (temp_dir / "invalid.txt").write_text("TXT")
    (temp_dir / "valid2.jpg").write_bytes(b"JPG")

    files = [
        temp_dir / "valid.pdf",
        temp_dir / "invalid.txt",
        temp_dir / "valid2.jpg"
    ]
    valid_files, invalid_files = FileHandler.validate_files(files)

    assert len(valid_files) == 2
    assert len(invalid_files) == 1
    assert (temp_dir / "valid.pdf") in valid_files
    assert (temp_dir / "valid2.jpg") in valid_files
