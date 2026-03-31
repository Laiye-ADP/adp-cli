"""Extended tests for ConfigManager."""

import pytest
import tempfile
import json
from pathlib import Path
from cryptography.fernet import Fernet

from adp_cli.adp.config import ConfigManager


@pytest.fixture
def temp_config_dir(tmp_path):
    """创建临时配置目录。"""
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


def test_set_api_key_encryption(temp_config_dir):
    """测试 API Key 加密。"""
    manager = ConfigManager()
    api_key = "my-secret-api-key-12345"

    manager.set_api_key(api_key)

    # 读取配置文件，检查 API Key 是否加密
    with open(manager.CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    encrypted_key = config.get("api_key")
    assert encrypted_key is not None
    assert api_key not in encrypted_key  # 原始密钥不应出现在加密数据中


def test_get_api_key_decryption(temp_config_dir):
    """测试 API Key 解密。"""
    manager = ConfigManager()
    api_key = "my-secret-api-key-67890"

    manager.set_api_key(api_key)
    retrieved_key = manager.get_api_key()

    assert retrieved_key == api_key


def test_get_api_key_not_set(temp_config_dir):
    """测试获取未设置的 API Key。"""
    manager = ConfigManager()
    api_key = manager.get_api_key()

    assert api_key is None


def test_get_api_key_masked_short_key(temp_config_dir):
    """测试短密钥的脱敏显示。"""
    manager = ConfigManager()
    api_key = "short"

    manager.set_api_key(api_key)
    masked_key = manager.get_api_key_masked()

    assert masked_key == "****"


def test_get_api_key_masked_none(temp_config_dir):
    """测试未设置密钥时的脱敏显示。"""
    manager = ConfigManager()
    masked_key = manager.get_api_key_masked()

    assert masked_key is None


def test_set_multiple_config_items(temp_config_dir):
    """测试设置多个配置项。"""
    manager = ConfigManager()

    manager.set("api_base_url", "https://api.example.com")
    manager.set("tenant_name", "my_tenant")
    manager.set("timeout", "300")
    manager.set("max_retries", "3")

    assert manager.get("api_base_url") == "https://api.example.com"
    assert manager.get("tenant_name") == "my_tenant"
    assert manager.get("timeout") == "300"
    assert manager.get("max_retries") == "3"


def test_get_nonexistent_key_with_default(temp_config_dir):
    """测试获取不存在的键时返回默认值。"""
    manager = ConfigManager()

    assert manager.get("nonexistent") is None
    assert manager.get("nonexistent", "default") == "default"
    assert manager.get("nonexistent", 123) == 123
    assert manager.get("nonexistent", []) == []


def test_update_existing_config_item(temp_config_dir):
    """测试更新已存在的配置项。"""
    manager = ConfigManager()

    manager.set("key", "value1")
    assert manager.get("key") == "value1"

    manager.set("key", "value2")
    assert manager.get("key") == "value2"


def test_clear_config_removes_files(temp_config_dir):
    """测试清除配置会删除文件。"""
    manager = ConfigManager()

    manager.set_api_key("test-key")
    manager.set("test_key", "test_value")

    assert manager.CONFIG_FILE.exists()
    assert manager.KEY_FILE.exists()

    manager.clear()

    assert not manager.CONFIG_FILE.exists()
    assert not manager.KEY_FILE.exists()


def test_clear_config_when_no_config(temp_config_dir):
    """测试清除不存在的配置不报错。"""
    manager = ConfigManager()
    assert not manager.CONFIG_FILE.exists()

    # Should not raise
    manager.clear()
    assert not manager.CONFIG_FILE.exists()


def test_is_configured_without_api_key(temp_config_dir):
    """测试没有 API Key 时未配置。"""
    manager = ConfigManager()
    manager.set("api_base_url", "https://api.example.com")

    assert manager.is_configured() is False


def test_is_configured_without_api_base_url(temp_config_dir):
    """测试没有 API Base URL 时未配置。"""
    manager = ConfigManager()
    manager.set_api_key("test-key")

    assert manager.is_configured() is False


def test_is_configured_with_empty_api_base_url(temp_config_dir):
    """测试空 API Base URL 时未配置。"""
    manager = ConfigManager()
    manager.set_api_key("test-key")
    manager.set("api_base_url", "   ")

    assert manager.is_configured() is False


def test_is_configured_fully_configured(temp_config_dir):
    """测试完全配置。"""
    manager = ConfigManager()
    manager.set_api_key("test-key")
    manager.set("api_base_url", "https://api.example.com")

    assert manager.is_configured() is True


def test_get_config_summary_without_config(temp_config_dir):
    """测试获取配置摘要（无配置）。"""
    manager = ConfigManager()
    summary = manager.get_config_summary()

    assert summary["configured"] is False
    assert summary["api_key_masked"] is None
    assert summary["api_base_url"] == ""


def test_get_config_summary_with_config(temp_config_dir):
    """测试获取配置摘要（有配置）。"""
    manager = ConfigManager()
    manager.set_api_key("test-api-key-12345")
    manager.set("api_base_url", "https://api.example.com")

    summary = manager.get_config_summary()

    assert summary["configured"] is True
    assert summary["api_key_masked"] is not None
    assert "test" in summary["api_key_masked"]
    assert "345" in summary["api_key_masked"]
    assert summary["api_base_url"] == "https://api.example.com"


def test_multiple_managers_same_config(temp_config_dir):
    """测试多个 ConfigManager 实例共享配置。"""
    manager1 = ConfigManager()
    manager2 = ConfigManager()

    manager1.set_api_key("shared-key")
    manager1.set("test", "value")

    assert manager2.get_api_key() == "shared-key"
    assert manager2.get("test") == "value"


def test_key_file_persistence(temp_config_dir):
    """测试密钥文件持久化。"""
    manager1 = ConfigManager()
    api_key = "persistent-key-123"

    manager1.set_api_key(api_key)

    # 创建新实例
    manager2 = ConfigManager()
    retrieved_key = manager2.get_api_key()

    assert retrieved_key == api_key


def test_config_file_persistence(temp_config_dir):
    """测试配置文件持久化。"""
    manager1 = ConfigManager()

    manager1.set("key1", "value1")
    manager1.set("key2", "value2")

    # 创建新实例
    manager2 = ConfigManager()

    assert manager2.get("key1") == "value1"
    assert manager2.get("key2") == "value2"


def test_config_with_complex_value(temp_config_dir):
    """测试配置复杂值（字典和列表）。"""
    manager = ConfigManager()

    dict_value = {"nested": {"key": "value"}}
    list_value = ["item1", "item2", "item3"]

    manager.set("dict_config", dict_value)
    manager.set("list_config", list_value)

    assert manager.get("dict_config") == dict_value
    assert manager.get("list_config") == list_value


def test_unicode_api_key(temp_config_dir):
    """测试 Unicode API Key。"""
    manager = ConfigManager()
    api_key = "测试-api-key-密钥"

    manager.set_api_key(api_key)
    retrieved_key = manager.get_api_key()

    assert retrieved_key == api_key


def test_special_characters_api_key(temp_config_dir):
    """测试包含特殊字符的 API Key。"""
    manager = ConfigManager()
    api_key = "sk-!@#$%^&*()_+-=[]{}|;':\",./<>?~`"

    manager.set_api_key(api_key)
    retrieved_key = manager.get_api_key()

    assert retrieved_key == api_key


def test_very_long_api_key(temp_config_dir):
    """测试很长的 API Key。"""
    manager = ConfigManager()
    api_key = "x" * 1000

    manager.set_api_key(api_key)
    retrieved_key = manager.get_api_key()

    assert retrieved_key == api_key
    assert len(retrieved_key) == 1000
