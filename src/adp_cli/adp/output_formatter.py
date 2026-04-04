"""Output formatting utilities for ADP CLI."""

import json
from typing import Optional,Any, Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.box import MARKDOWN


class OutputFormatter:
    """输出格式化工具，支持控制台和 JSON 输出。"""

    def __init__(self, console: Optional[Console] = None, stderr_console: Optional[Console] = None):
        """
        初始化输出格式化器。

        Args:
            console: Rich Console 实例，用于 stdout (JSON 输出)
            stderr_console: Rich Console 实例，用于 stderr (进度/警告/日志)
        """
        import sys
        # Configure stdout/stderr for UTF-8 on Windows
        if sys.platform == 'win32':
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')

        # 检测是否为 TTY，非 TTY 时去颜色、不截断
        self.is_tty = sys.stdout.isatty() if hasattr(sys.stdout, 'isatty') else False

        # stdout Console - 非 TTY 时去颜色、不截断
        if console:
            self.stdout_console = console
        else:
            self.stdout_console = Console(
                color_system=None if not self.is_tty else "auto",
                width=None if not self.is_tty else None,  # None = 不截断
                force_terminal=self.is_tty
            )

        # stderr Console - 同样处理
        if stderr_console:
            self.stderr_console = stderr_console
        else:
            self.stderr_console = Console(
                stderr=True,
                color_system=None if not self.is_tty else "auto",
                width=None if not self.is_tty else None,
                force_terminal=self.is_tty
            )

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

    def print(self, message: str, style: str = None, stderr: bool = True) -> None:
        """
        打印消息。

        Args:
            message: 消息内容
            style: Rich 样式（可选）
            stderr: 是否输出到 stderr（默认 True）
        """
        if not self.quiet_mode:
            console = self.stderr_console if stderr else self.stdout_console
            if style:
                console.print(message, style=style)
            else:
                console.print(message)

    def print_success(self, message: str) -> None:
        """打印成功消息到 stderr。"""
        if self.is_tty:
            self.print(f"✓ {message}", style="green")
        else:
            self.print(message)

    def print_error(self, message_or_error: Any) -> None:
        """
        打印错误消息到 stderr。

        支持两种格式：
        1. 字符串：简单的错误消息
        2. 字典：结构化错误信息（type, code, message, fix, retryable）

        Args:
            message_or_error: 错误消息字符串或结构化错误字典
        """
        if isinstance(message_or_error, dict):
            # 结构化错误信息
            error = message_or_error
            if self.is_tty:
                # TTY 模式：人类可读的格式化输出
                self.stderr_console.print(f"✗ Error: {error.get('message', '')}", style="red")
                if error.get('fix'):
                    self.stderr_console.print(f"  Fix: {error['fix']}", style="cyan")
                if error.get('retryable') is not None:
                    retry_text = "Yes" if error['retryable'] else "No"
                    self.stderr_console.print(f"  Retryable: {retry_text}", style="dim")
                if error.get('details'):
                    self.stderr_console.print(f"  Details: {error['details']}", style="dim")
            else:
                # 非 TTY 模式：输出 JSON
                print(json.dumps(error, indent=2, ensure_ascii=False))
        else:
            # 简单字符串消息
            if self.is_tty:
                self.stderr_console.print(f"✗ {message_or_error}", style="red")
            else:
                # 非 TTY：输出结构化格式
                error_dict = {
                    "type": "UNKNOWN_ERROR",
                    "message": str(message_or_error),
                    "retryable": False
                }
                print(json.dumps(error_dict, indent=2, ensure_ascii=False))

    def print_warning(self, message: str) -> None:
        """打印警告消息到 stderr。"""
        if self.is_tty:
            self.print(f"⚠ {message}", style="yellow")
        else:
            self.print(message)

    def print_info(self, message: str) -> None:
        """打印信息消息到 stderr。"""
        if self.is_tty:
            self.print(f"ℹ {message}", style="blue")
        else:
            self.print(message)

    def print_json(self, data: Any) -> None:
        """
        打印 JSON 格式的数据到 stdout。

        Args:
            data: 要打印的数据
        """
        # 非 TTY 时始终输出纯 JSON，不使用语法高亮
        if self.json_mode or not self.is_tty:
            # 纯 JSON 输出到 stdout
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            # 格式化的 JSON 输出（语法高亮）到 stdout
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai")
            self.stdout_console.print(syntax)

    def print_table(self, headers: List[str], rows: List[List[str]], title: str = None) -> None:
        """
        打印表格到 stderr。

        Args:
            headers: 表头列表
            rows: 行数据列表
            title: 表格标题（可选）
        """
        # 非 TTY 时输出 tab 分隔格式
        if not self.is_tty:
            self._print_table_tsv(headers, rows, title)
            return

        table = Table(
            title=title,
            show_header=True,
            header_style="bold",
            box=MARKDOWN,             # Markdown style: only header separator line
            border_style="blue",       # Border color
            show_lines=True            # Show horizontal lines
        )

        for header in headers:
            table.add_column(header, overflow='fold')  # Enable text wrapping

        for row in rows:
            table.add_row(*row)

        self.stderr_console.print(table)

    def _print_table_tsv(self, headers: List[str], rows: List[List[str]], title: str = None) -> None:
        """
        打印 tab 分隔格式的表格到 stderr（非 TTY 环境）。

        Args:
            headers: 表头列表
            rows: 行数据列表
            title: 表格标题（可选）
        """
        if title:
            self.stderr_console.print(f"# {title}")

        # 打印表头
        self.stderr_console.print("\t".join(headers))

        # 打印数据行
        for row in rows:
            self.stderr_console.print("\t".join(str(cell) for cell in row))

    def print_panel(self, content: str, title: str = None, style: str = "blue") -> None:
        """
        打印面板到 stderr。

        Args:
            content: 面板内容
            title: 面板标题（可选）
            style: 面板样式
        """
        panel = Panel(content, title=title, border_style=style)
        self.stderr_console.print(panel)

    def print_task_result(self, task_id: str, status: int, result: Dict[str, Any] = None) -> None:
        """
        打印任务结果到 stderr。

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
        打印文件列表到 stderr。

        Args:
            files: 文件路径列表
            show_size: 是否显示文件大小
        """
        from .file_handler import FileHandler

        # 非 TTY 时输出 tab 分隔格式
        if not self.is_tty:
            self.stderr_console.print("# Files")
            if show_size:
                self.stderr_console.print("#\tFile Path\tSize")
                for i, file_path in enumerate(files, 1):
                    size_str = FileHandler.format_file_size(file_path.stat().st_size)
                    self.stderr_console.print(f"{i}\t{file_path}\t{size_str}")
            else:
                self.stderr_console.print("#\tFile Path")
                for i, file_path in enumerate(files, 1):
                    self.stderr_console.print(f"{i}\t{file_path}")
            return

        table = Table(title="Files", show_header=True, header_style="bold magenta")
        table.add_column("#", justify="right")
        table.add_column("File Path")

        if show_size:
            table.add_column("Size")

        for i, file_path in enumerate(files, 1):
            if show_size:
                size_str = FileHandler.format_file_size(file_path.stat().st_size)
                table.add_row(str(i), str(file_path), size_str)
            else:
                table.add_row(str(i), str(file_path))

        self.stderr_console.print(table)

    def print_config_summary(self, config: Dict[str, Any]) -> None:
        """
        打印配置摘要到 stderr。

        Args:
            config: 配置数据
        """
        # 非 TTY 时输出 tab 分隔格式
        if not self.is_tty:
            self.stderr_console.print("# Configuration")
            self.stderr_console.print("Key\tValue")
            for key, value in config.items():
                self.stderr_console.print(f"{key}\t{value}")
            return

        table = Table(title="Configuration", show_header=True, header_style="bold magenta")
        table.add_column("Key")
        table.add_column("Value")

        for key, value in config.items():
            table.add_row(key, str(value))

        self.stderr_console.print(table)

    def print_progress(self, current: int, total: int, message: str = "") -> None:
        """
        打印进度到 stderr。

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
        打印章节标题到 stderr。

        Args:
            title: 章节标题
        """
        if self.is_tty:
            separator = "─" * len(title)
            self.print(f"\n{title}", style="bold")
            self.print(separator, style="dim")
        else:
            self.print(f"\n{title}")

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
                # 提取所有结果数据
                all_results = [r.get("result") for r in results]
                # 输出 JSON 到 stdout（非 TTY 环境）
                formatter_instance.print_json(all_results)
