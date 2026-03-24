"""Tests for ConfigManager."""

import pytest
import tempfile
import json
from pathlib import Path

from adp_cli.adp.config import ConfigManager


@pytest.fixture
def temp_config_dir(tmp_path):
    """创建临时配置目录。"""
    config_dir = tmp_path / ".adp"
    config_dir.mkdir()

    # 临时替换 ConfigManager 的配置目录
    original_dir = ConfigManager.CONFIG_DIR
    ConfigManager.CONFIG_DIR = config_dir
    ConfigManager.CONFIG_FILE = config_dir / "config.json"
    ConfigManager.KEY_FILE = config_dir / "key.enc"

    yield config_dir

    # 恢复原始配置目录
    ConfigManager.CONFIG_DIR = original_dir
    ConfigManager.CONFIG_FILE = original_dir / "config.json"
    ConfigManager.KEY_FILE = original_dir / "key.enc"


def test_config_manager_init(temp_config_dir):
    """测试配置管理器初始化。"""
    manager = ConfigManager()
    assert temp_config_dir.exists()


def test_set_and_get_api_key(temp_config_dir):
    """测试设置和获取 API Key。"""
    manager = ConfigManager()
    api_key = "test-api-key-12345"

    manager.set_api_key(api_key)
    retrieved_key = manager.get_api_key()

    assert retrieved_key == api_key


def test_get_api_key_masked(temp_config_dir):
    """测试获取脱敏的 API Key。"""
    manager = ConfigManager()
    api_key = "test-api-key-12345"

    manager.set_api_key(api_key)
    masked_key = manager.get_api_key_masked()

    assert masked_key is not None
    assert "test" in masked_key
    assert "345" in masked_key
    assert api_key not in masked_key  # 确保完整密钥不在脱敏字符串中


def test_set_and_get_config(temp_config_dir):
    """测试设置和获取配置项。"""
    manager = ConfigManager()

    manager.set("test_key", "test_value")
    value = manager.get("test_key")

    assert value == "test_value"


def test_get_default_value(temp_config_dir):
    """测试获取配置项的默认值。"""
    manager = ConfigManager()
    value = manager.get("nonexistent_key", "default_value")

    assert value == "default_value"


def test_clear_config(temp_config_dir):
    """测试清除配置。"""
    manager = ConfigManager()

    manager.set_api_key("test-key")
    manager.set("test_key", "test_value")

    assert manager.is_configured() is True

    manager.clear()

    assert manager.is_configured() is False
    assert manager.get("test_key") is None


def test_is_configured(temp_config_dir):
    """测试是否已配置。"""
    manager = ConfigManager()

    assert manager.is_configured() is False

    manager.set_api_key("test-key")

    assert manager.is_configured() is True


def test_get_config_summary(temp_config_dir):
    """测试获取配置摘要。"""
    manager = ConfigManager()

    summary = manager.get_config_summary()

    assert "configured" in summary
    assert "api_key_masked" in summary
    assert "api_base_url" in summary

    assert summary["configured"] is False
