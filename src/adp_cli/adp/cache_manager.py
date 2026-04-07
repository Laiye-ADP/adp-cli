"""Cache management for ADP CLI - Application ID caching."""

import json
from pathlib import Path
from typing import List, Dict, Any


class ADPCacheManager:
    """管理 ADP CLI 的应用ID缓存。"""

    CACHE_DIR = Path.home() / ".adp"
    CACHE_FILE = CACHE_DIR / "app_cache.json"

    def __init__(self):
        """初始化缓存管理器。"""
        self._ensure_cache_dir()
        self._load_cache()

    def _ensure_cache_dir(self) -> None:
        """确保缓存目录存在。"""
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_cache(self) -> None:
        """加载缓存文件。"""
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._cache = {"apps": []}
        else:
            self._cache = {"apps": []}

    def _save_cache(self) -> None:
        """保存缓存文件。"""
        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def set_apps(self, apps: List[Dict[str, Any]]) -> None:
        """
        设置完整的应用列表到缓存。

        Args:
            apps: 应用列表，与 list API 返回格式一致
        """
        self._cache = {"apps": apps}
        self._save_cache()

    def get_all_apps(self) -> List[Dict[str, Any]]:
        """
        获取所有缓存的应用（与 list API 返回格式一致）。

        Returns:
            应用列表
        """
        return self._cache.get("apps", [])