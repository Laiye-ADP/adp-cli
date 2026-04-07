"""Cache management for ADP CLI - Application ID caching."""

import json
import os
from pathlib import Path
from typing import Optional, Dict


# 默认应用ID缓存（7个高频应用）
DEFAULT_APP_CACHE: Dict[str, str] = {
    "采购订单": "ootb_m9n2p5q8r1t4v7w0x3y6z9a2b5",
    "发票/收据": "ootb_a3f8h1j5k9n2p7q4w6x0y3b5c8d1",
    "身份证": "ootb_b7k2m5n8p1q4r7t0v3w6x9y2z5",
    "营业执照": "ootb_g8k2n5p1q4r7t0v3w6x9y2z5a8b",
    "组织机构代码证": "ootb_k8m2n5p1q4r7t0w3w6x9y2z5a8b4",
    "驾驶证": "ootb_f2m5n8p1q4r7t0v3w6x9y2z5a8b",
    "行驶证": "ootb_j2k5n8p1q4r7t0v3w6x9y2z5a8b1",
}


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
                self._cache = {}
        else:
            self._cache = {}
            self._init_default_cache()

    def _init_default_cache(self) -> None:
        """初始化默认缓存。"""
        self._cache = DEFAULT_APP_CACHE.copy()
        self._save_cache()

    def _save_cache(self) -> None:
        """保存缓存文件。"""
        with open(self.CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def get_app_id(self, app_name: str, fuzzy: bool = True) -> Optional[str]:
        """
        从缓存获取应用ID。

        Args:
            app_name: 应用名称（如"采购订单"、"发票/收据"等）
            fuzzy: 是否启用模糊匹配（默认True）。精确匹配优先。

        Returns:
            应用ID字符串，如果不存在返回None
        """
        # 精确匹配
        if app_name in self._cache:
            return self._cache[app_name]

        # 模糊匹配
        if fuzzy:
            app_name_lower = app_name.lower()
            for name, app_id in self._cache.items():
                if app_name_lower in name.lower():
                    return app_id

        return None

    def set_app_id(self, app_name: str, app_id: str) -> None:
        """
        设置应用ID到缓存。

        Args:
            app_name: 应用名称
            app_id: 应用ID
        """
        self._cache[app_name] = app_id
        self._save_cache()

    def get_all_app_ids(self) -> Dict[str, str]:
        """
        获取所有缓存的应用ID。

        Returns:
            应用名称到ID的映射字典
        """
        return self._cache.copy()

    def clear_cache(self) -> None:
        """清除缓存并重新初始化默认缓存。"""
        self._init_default_cache()

    def refresh_cache(self) -> None:
        """刷新缓存为默认缓存。"""
        self._cache = DEFAULT_APP_CACHE.copy()
        self._save_cache()
