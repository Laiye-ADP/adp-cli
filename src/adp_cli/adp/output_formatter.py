"""Output formatting utilities for ADP CLI."""

import json
from typing import Optional,Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.box import HEAVY


class OutputFormatter:
    """输出格式化工具，支持控制台和 JSON 输出。"""

    def __init__(self, console: Optional[Console] = None):
        """
        初始化输出格式化器。

        Args:
            console: Rich Console 实例（可选）
        """
        self.console = console or Console()
        self.json_mode = False
        self.quiet_mode = False
        self.status = {
            1: "PENDING",
            2: "RUNNING",
            4: "SUCCESS",
            5: "FAILED"
        }

    def set_json_mode(self, enabled: bool) -> None:
        """设置 JSON 模式。"""
        self.json_mode = enabled

    def set_quiet_mode(self, enabled: bool) -> None:
        """设置静默模式。"""
        self.quiet_mode = enabled

    def print(self, message: str, style: str = None) -> None:
        """
        打印消息。

        Args:
            message: 消息内容
            style: Rich 样式（可选）
        """
        if not self.quiet_mode:
            if style:
                self.console.print(message, style=style)
            else:
                self.console.print(message)

    def print_success(self, message: str) -> None:
        """打印成功消息。"""
        self.print(f"✓ {message}", style="green")

    def print_error(self, message: str) -> None:
        """打印错误消息。"""
        self.console.print(f"✗ {message}", style="red")

    def print_warning(self, message: str) -> None:
        """打印警告消息。"""
        self.print(f"⚠ {message}", style="yellow")

    def print_info(self, message: str) -> None:
        """打印信息消息。"""
        self.print(f"ℹ {message}", style="blue")

    def print_json(self, data: Any) -> None:
        """
        打印 JSON 格式的数据。

        Args:
            data: 要打印的数据
        """
        if self.json_mode:
            # 纯 JSON 输出
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            # 格式化的 JSON 输出
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai")
            self.console.print(syntax)

    def print_table(self, headers: List[str], rows: List[List[str]], title: str = None) -> None:
        """
        打印表格。

        Args:
            headers: 表头列表
            rows: 行数据列表
            title: 表格标题（可选）
        """
        table = Table(
            title=title,
            show_header=True,
            header_style="bold",
            box=HEAVY,                 # Use thick (heavy) box lines
            border_style="blue",       # Border color
            show_lines=True            # Show all inner lines (all grid lines)
        )

        for header in headers:
            table.add_column(header)

        for row in rows:
            table.add_row(*row)

        self.console.print(table)

    def print_panel(self, content: str, title: str = None, style: str = "blue") -> None:
        """
        打印面板。

        Args:
            content: 面板内容
            title: 面板标题（可选）
            style: 面板样式
        """
        panel = Panel(content, title=title, border_style=style)
        self.console.print(panel)

    def print_task_result(self, task_id: str, status: int, result: Dict[str, Any] = None) -> None:
        """
        打印任务结果。

        Args:
            task_id: 任务 ID
            status: 任务状态
            result: 任务结果（可选）
        """
        self.print_info(f"Task_ID: {task_id}")
        self.print_info(f"Status: {self.status.get(status, 'UNKNOWN')}")

        if result:
            self.print("Result:", style="bold")
            self.print_json(result)

    def print_file_list(self, files: List, show_size: bool = True) -> None:
        """
        打印文件列表。

        Args:
            files: 文件路径列表
            show_size: 是否显示文件大小
        """
        table = Table(title="Files", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right")
        table.add_column("File Path")

        if show_size:
            table.add_column("Size")

        from .file_handler import FileHandler

        for i, file_path in enumerate(files, 1):
            if show_size:
                size_str = FileHandler.format_file_size(file_path.stat().st_size)
                table.add_row(str(i), str(file_path), size_str)
            else:
                table.add_row(str(i), str(file_path))

        self.console.print(table)

    def print_config_summary(self, config: Dict[str, Any]) -> None:
        """
        打印配置摘要。

        Args:
            config: 配置数据
        """
        table = Table(title="Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Key")
        table.add_column("Value")

        for key, value in config.items():
            table.add_row(key, str(value))

        self.console.print(table)

    def print_progress(self, current: int, total: int, message: str = "") -> None:
        """
        打印进度。

        Args:
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        percentage = (current / total) * 100 if total > 0 else 0
        progress_text = f"[{current}/{total}] {percentage:.1f}%"

        if message:
            progress_text += f" - {message}"

        self.print(progress_text, style="cyan")

    def print_section(self, title: str) -> None:
        """
        打印章节标题。

        Args:
            title: 章节标题
        """
        separator = "─" * len(title)
        self.print(f"\n{title}", style="bold")
        self.print(separator, style="dim")

    @staticmethod
    def print_results(results: List[Dict[str, Any]], items: List[Any], mode: str, formatter_instance, t) -> None:
        """
        打印处理结果到控制台。

        Args:
            results: 处理结果列表
            items: 原始项目列表（文件或URL）
            mode: 处理模式 ('parse' 或 'extract')
            formatter_instance: OutputFormatter 实例（用于打印消息）
            t: 国际化函数
        """
        if results:
            if mode == "parse" or mode == "extract":
                if len(items) == 1:
                    # 单个文件/URL，直接打印结果
                    formatter_instance.print_json(results[0]["result"])
                # 多个文件/URL，不在控制台打印结果（避免输出过多）
