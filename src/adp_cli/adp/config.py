"""Configuration management for ADP CLI."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64


class ConfigManager:
    """管理 ADP CLI 的配置，包括 API Key 的加密存储。"""

    CONFIG_DIR = Path.home() / ".adp"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    KEY_FILE = CONFIG_DIR / "key.enc"

    def __init__(self):
        """初始化配置管理器。"""
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """确保配置目录存在。"""
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _get_cipher(self) -> Fernet:
        """获取加密/解密器。"""
        if not self.KEY_FILE.exists():
            # 生成新的密钥
            key = Fernet.generate_key()
            self.KEY_FILE.write_bytes(key)
        else:
            key = self.KEY_FILE.read_bytes()
        return Fernet(key)

    def set_api_key(self, api_key: str) -> None:
        """
        设置 API Key（加密存储）。

        Args:
            api_key: API Key 字符串
        """
        cipher = self._get_cipher()
        encrypted_key = cipher.encrypt(api_key.encode())
        config = self._load_config()
        config["api_key"] = encrypted_key.decode()
        self._save_config(config)

    def get_api_key(self) -> Optional[str]:
        """
        获取 API Key（解密）。

        Returns:
            API Key 字符串，如果不存在返回 None
        """
        config = self._load_config()
        if "api_key" not in config:
            return None

        try:
            cipher = self._get_cipher()
            encrypted_key = config["api_key"].encode()
            decrypted = cipher.decrypt(encrypted_key)
            return decrypted.decode()
        except Exception:
            return None

    def get_api_key_masked(self) -> Optional[str]:
        """
        获取脱敏的 API Key（用于显示）。

        Returns:
            脱敏的 API Key，例如：sk-xxx...xxx
        """
        api_key = self.get_api_key()
        if not api_key:
            return None
        if len(api_key) <= 8:
            return "****"
        return f"{api_key[:4]}...{api_key[-4:]}"

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项。

        Args:
            key: 配置键
            value: 配置值
        """
        config = self._load_config()
        config[key] = value
        self._save_config(config)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项。

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值
        """
        config = self._load_config()
        return config.get(key, default)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件。"""
        if not self.CONFIG_FILE.exists():
            return {}
        try:
            with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置文件。"""
        with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def clear(self) -> None:
        """清除所有配置。"""
        if self.CONFIG_FILE.exists():
            self.CONFIG_FILE.unlink()
        if self.KEY_FILE.exists():
            self.KEY_FILE.unlink()

    def is_configured(self) -> bool:
        """检查是否已配置 API Key。"""
        return self.get_api_key() is not None

    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要（不包含敏感信息）。"""
        config = self._load_config()
        summary = {
            "configured": self.is_configured(),
            "api_key_masked": self.get_api_key_masked(),
            "api_base_url": config.get("api_base_url", "https://adp.laiye.com"),
        }
        return summary
