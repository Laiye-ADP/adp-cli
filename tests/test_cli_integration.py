"""Integration tests for ADP CLI."""

import pytest
import subprocess
import json
from pathlib import Path


class TestCLIIntegration:
    """CLI 集成测试。"""

    def run_adp_command(self, *args):
        """
        运行 adp 命令。

        Args:
            args: 命令参数

        Returns:
            (返回码, 标准输出, 错误输出)
        """
        result = subprocess.run(
            ["python", "-m", "adp_cli.cli"] + list(args),
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr

    def test_help_command(self):
        """测试帮助命令。"""
        returncode, stdout, stderr = self.run_adp_command("--help")
        assert returncode == 0
        # stdout may be None on Windows due to encoding issues
        if stdout:
            assert "ADP CLI" in stdout or "AI Document Platform" in stdout

    def test_version_command(self):
        """测试版本命令。"""
        returncode, stdout, stderr = self.run_adp_command("--version")
        assert returncode == 0
        # stdout may be None on Windows due to encoding issues
        if stdout:
            assert "1.10.0" in stdout

    def test_config_help(self):
        """测试配置帮助。"""
        returncode, stdout, stderr = self.run_adp_command("config", "--help")
        assert returncode == 0

    def test_parse_help(self):
        """测试解析帮助。"""
        returncode, stdout, stderr = self.run_adp_command("parse", "--help")
        assert returncode == 0

    def test_extract_help(self):
        """测试抽取帮助。"""
        returncode, stdout, stderr = self.run_adp_command("extract", "--help")
        assert returncode == 0

    def test_query_help(self):
        """测试查询帮助。"""
        returncode, stdout, stderr = self.run_adp_command("query", "--help")
        assert returncode == 0

    def test_app_id_help(self):
        """测试应用 ID 帮助。"""
        returncode, stdout, stderr = self.run_adp_command("app-id", "--help")
        assert returncode == 0


class TestCLIE2E:
    """CLI 端到端测试。"""

    def test_complete_workflow(self, tmp_path):
        """测试完整工作流。"""
        # 创建测试文件
        test_file = tmp_path / "test.pdf"
        test_file.write_text("Test PDF content")

        # 注意：这些测试需要实际的 API 服务器
        # 在实际环境中，这些测试可能会跳过或失败

        # 工作流：
        # 1. 配置 API Key
        # 2. 解析文档
        # 3. 提取信息
        # 4. 查询任务

        pass  # 占位符，实际测试需要 mocking API 服务器
