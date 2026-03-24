"""File handling utilities for ADP CLI."""

import os
import json
from pathlib import Path
from typing import List, Optional, Iterator
import mimetypes


class FileHandler:
    """文件处理工具类，支持文件验证、批量处理等。"""

    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS = {
        # 图片
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif",
        # 文档
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    }

    # 最大文件大小：50MB
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes

    @classmethod
    def is_supported_file(cls, file_path: Path) -> bool:
        """
        检查文件是否支持。

        Args:
            file_path: 文件路径

        Returns:
            是否支持此文件
        """
        return file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def is_valid_size(cls, file_path: Path) -> bool:
        """
        检查文件大小是否有效。

        Args:
            file_path: 文件路径

        Returns:
            文件大小是否有效
        """
        return file_path.stat().st_size <= cls.MAX_FILE_SIZE

    @classmethod
    def validate_file(cls, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        验证文件。

        Args:
            file_path: 文件路径

        Returns:
            (是否有效, 错误信息)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"

        if not cls.is_supported_file(file_path):
            supported = ", ".join(cls.SUPPORTED_EXTENSIONS)
            return False, f"Unsupported file type: {file_path.suffix}. Supported types: {supported}"

        if not cls.is_valid_size(file_path):
            size_mb = file_path.stat().st_size / (1024 * 1024)
            return False, f"File too large: {size_mb:.2f}MB. Maximum size: 50MB"

        return True, None

    @classmethod
    def get_files_from_path(cls, path: Path) -> List[Path]:
        """
        从路径获取文件列表（支持文件或目录）。

        Args:
            path: 文件或目录路径

        Returns:
            文件路径列表
        """
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if path.is_file():
            return [path]

        if path.is_dir():
            files = []
            for item in path.rglob("*"):
                if item.is_file() and cls.is_supported_file(item):
                    files.append(item)
            return sorted(files)

        return []

    @classmethod
    def validate_files(cls, file_paths: List[Path]) -> tuple[List[Path], List[tuple[Path, str]]]:
        """
        验证多个文件。

        Args:
            file_paths: 文件路径列表

        Returns:
            (有效文件列表, 无效文件列表(路径, 错误信息))
        """
        valid_files = []
        invalid_files = []

        for file_path in file_paths:
            is_valid, error = cls.validate_file(file_path)
            if is_valid:
                valid_files.append(file_path)
            else:
                invalid_files.append((file_path, error))

        return valid_files, invalid_files

    @classmethod
    def read_url_list_file(cls, file_path: Path) -> List[str]:
        """
        读取包含 URL 列表的文件。

        Args:
            file_path: URL 列表文件路径

        Returns:
            URL 列表
        """
        if not file_path.exists():
            raise FileNotFoundError(f"URL list file not found: {file_path}")

        urls = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if url and url.startswith(("http://", "https://")):
                    urls.append(url)

        return urls

    @classmethod
    def write_json_output(cls, data: dict, output_path: Path) -> None:
        """
        将数据写入 JSON 文件。

        Args:
            data: 要写入的数据
            output_path: 输出文件路径
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def get_mime_type(cls, file_path: Path) -> str:
        """
        获取文件的 MIME 类型。

        Args:
            file_path: 文件路径

        Returns:
            MIME 类型字符串
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"

    @classmethod
    def format_file_size(cls, size_bytes: int) -> str:
        """
        格式化文件大小显示。

        Args:
            size_bytes: 文件大小（字节）

        Returns:
            格式化的文件大小字符串
        """
        units = ["B", "KB", "MB", "GB"]
        size = float(size_bytes)
        unit_index = 0

        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1

        return f"{size:.2f} {units[unit_index]}"

    @classmethod
    def batch_process(
        cls,
        items: List,
        batch_size: int = 10
    ) -> Iterator[List]:
        """
        将列表分成批次处理。

        Args:
            items: 要分批的列表
            batch_size: 每批大小

        Yields:
            批次列表
        """
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
