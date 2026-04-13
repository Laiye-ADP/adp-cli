"""API client for ADP backend."""

import re
import time
import mimetypes
import uuid
from typing import Optional, Dict, Any, List
from pathlib import Path
from click.core import F
import requests
from requests.exceptions import RequestException

from .config import ConfigManager


class TaskStatus:
    """任务状态常量。"""

    PENDING = 0
    RUNNING = 2
    SUCCESS = 4
    FAILED = 5
    CANCELLED = 6
    


class APIClient:
    """ADP API 客户端，处理所有与后端的通信。"""

    def __init__(self, config_manager: ConfigManager):
        """
        初始化 API 客户端。

        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.api_base_url = self._get_api_base_url()

    def _get_api_base_url(self) -> str:
        """获取 API 基础 URL。"""
        return self.config_manager.get("api_base_url", "")

    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头（包含 API Key）。

        Returns:
            请求头字典
        """
        api_key = self.config_manager.get_api_key()

        if not api_key:
            raise ValueError("API Key not configured. Run 'adp config set' first.")

        return {
            "Content-Type": "application/json",
            "X-API-Source" : "CLI",
            "X-Api-key": api_key,
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送 HTTP 请求。

        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据

        Returns:
            响应数据

        Raises:
            RequestException: 请求失败
        """

        url = f"{self.api_base_url}{endpoint}"
        headers = self._get_headers()

        try:
            response = requests.request(method, url, headers=headers, json=data, timeout=300)
            return response.json()
        except RequestException as e:
            # 尝试获取响应内容以提供更多调试信息
            error_msg = f"API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    response_text = e.response.text
                    if response_text:
                        error_msg += f"\nResponse: {response_text}"
                except:
                    pass
            raise RequestException(error_msg)


    def _encode_file_to_base64(self, file_path: Path) -> str:
        """
        将文件编码为 base64。

        Args:
            file_path: 文件路径

        Returns:
            base64 编码的文件内容
        """
        import base64

        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def _get_mime_type(self, file_path: Path) -> str:
        """
        获取文件的 MIME 类型。

        Args:
            file_path: 文件路径

        Returns:
            MIME 类型字符串
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"

    # ==================== Parse (Document Recognition) APIs ====================

    def parse_sync(self, file_url: str, app_id: str, file_path: Optional[Path] = None, file_base64: Optional[str] = None, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        同步解析文档。

        Args:
            file_url: 文件 URL（如果 file_path 或 file_base6464 提供，则忽略此参数）
            app_id: 应用 ID
            file_path: 本地文件路径（可选）
            file_base64: Base64 编码的文件内容（可选，如果提供则跳过文件读取）
            file_name: 文件名（可选，默认为 "document"）

        Returns:
            解析结果
        """
        data = {
            "app_id": app_id,
            "file_name": file_name if file_name else (file_path.name if file_path else "document"),
        }

        if file_base64:
            data["file_base64"] = file_base64
        elif file_path:
            data["file_base64"] = self._encode_file_to_base64(file_path)
        else:
            data["file_url"] = file_url

        tenant_name = self.config_manager.get("tenant_name", "laiye")
        return self._request("POST", f"/open/agentic_doc_processor/{tenant_name}/v1/app/doc/recognize", data)

    def parse_async(self, file_url: str, app_id: str, file_path: Optional[Path] = None, file_base64: Optional[str] = None, file_name: Optional[str] = None) -> str:
        """
        异步创建文档解析任务。

        Args:
            file_url: 文件 URL 或 base64 编码（如果 file_path 或 file_base64 提供，则忽略此参数）
            app_id: 应用 ID
            file_path: 本地文件路径（可选）
            file_base64: Base64 编码的文件内容（可选，如果提供则跳过文件读取）
            file_name: 文件名（可选，默认为 "document"）

        Returns:
            任务 ID
        """
        data = {
            "app_id": app_id,
            "file_name": file_name if file_name else (file_path.name if file_path else "document"),
        }

        if file_base64:
            data["file_base64"] = file_base64
        elif file_path:
            data["file_base64"] = self._encode_file_to_base64(file_path)
        else:
            data["file_url"] = file_url

        tenant_name = self.config_manager.get("tenant_name", "laiye")
        response = self._request("POST", f"/open/agentic_doc_processor/{tenant_name}/v1/app/doc/recognize/create/task", data)
        data = response.get("data", {})
        return data.get("task_id", "")

    def query_parse_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询文档解析任务状态。

        Args:
            task_id: 任务 ID

        Returns:
            任务状态和结果
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        response = self._request("GET", f"/open/agentic_doc_processor/{tenant_name}/v1/app/doc/recognize/query/task/{task_id}")
        # 确保返回的结构兼容 wait_for_task 的期望
        data = response.get("data", response)
        if data:
            # 合并 data 和 response 的其他字段
            result = {"data": data, **{k: v for k, v in response.items() if k != "data"}}
            return result
        return response

    # ==================== Extract APIs ====================

    def extract_sync(
        self,
        file_url: str,
        app_id: str,
        file_path: Optional[Path] = None,
        extract_config: Optional[Dict[str, Any]] = None,
        file_base64: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        同步执行文档抽取。

        Args:
            file_url: 文件 URL（如果 file_path 或 file_base64 提供，则忽略此参数）
            app_id: 应用 ID
            file_path: 本地文件路径（可选）
            extract_config: 抽取配置（可选）
            file_base64: Base64 编码的文件内容（可选，如果提供则跳过文件读取）
            file_name: 文件名（可选，默认为 "document"）

        Returns:
            抽取结果
        """
        data = {
            "app_id": app_id,
            "file_name": file_name if file_name else (file_path.name if file_path else "document"),
            "with_rec_result": False
        }

        if file_base64:
            data["file_base64"] = file_base64
        elif file_path:
            data["file_base64"] = self._encode_file_to_base64(file_path)
        else:
            data["file_url"] = file_url

        if extract_config:
            data["extract_config"] = extract_config

        tenant_name = self.config_manager.get("tenant_name", "laiye")
        return self._request("POST", f"/open/agentic_doc_processor/{tenant_name}/v1/app/doc/extract", data)

    def extract_async(
        self,
        file_url: str,
        app_id: str,
        file_path: Optional[Path] = None,
        extract_config: Optional[Dict[str, Any]] = None,
        file_base64: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> str:
        """
        异步创建文档抽取任务。

        Args:
            file_url: 文件 URL 或 base64 编码
            app_id: 应用 ID
            file_path: 本地文件路径（可选）
            extract_config: 抽取配置（可选）
            file_base64: Base64 编码的文件内容（可选，如果提供则跳过文件读取）
            file_name: 文件名（可选，默认为 "document"）

        Returns:
            任务 ID
        """
        data = {
            "app_id": app_id,
            "file_name": file_name if file_name else (file_path.name if file_path else "document"),
            "with_rec_result": False
        }

        if file_base64:
            data["file_base64"] = file_base64
        elif file_path:
            data["file_base64"] = self._encode_file_to_base64(file_path)
        else:
            data["file_url"] = file_url

        if extract_config:
            data["extract_config"] = extract_config

        tenant_name = self.config_manager.get("tenant_name", "laiye")
        response = self._request("POST", f"/open/agentic_doc_processor/{tenant_name}/v1/app/doc/extract/create/task", data)
        data = response.get("data", {})
        return data.get("task_id", "")

    def query_extract_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询文档抽取任务状态。

        Args:
            task_id: 任务 ID

        Returns:
            任务状态和结果
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        response = self._request("GET", f"/open/agentic_doc_processor/{tenant_name}/v1/app/doc/extract/query/task/{task_id}")
        # 确保返回的结构兼容 wait_for_task 的期望
        data = response.get("data", response)
        if data:
            # 合并 data 和 response 的其他字段
            result = {"data": data, **{k: v for k, v in response.items() if k != "data"}}
            return result
        return response

    # ==================== App Management APIs ====================

    def list_apps(self, app_type: int = None, limit: int = 120) -> List[Dict[str, Any]]:
        """
        获取当前租户下的所有可用应用（App）。

        该方法会向 API 发送 GET 请求，获取应用列表。返回的每个应用包含 app_id、app_name 和 description 等信息。

        Args:
            app_type: 应用类型过滤，1=自定义应用，0=系统预设
            limit: 返回应用数量限制

        Returns:
            应用列表，每个元素为 dict，包含 app_id、app_name、description 字段。
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-list"
        query_parts = []
        if app_type is not None:
            query_parts.append(f"app_type={app_type}")
        if limit is not None:
            query_parts.append(f"limit={limit}")
        if query_parts:
            endpoint = f"{endpoint}?{'&'.join(query_parts)}"
        try:
            response = self._request("GET", endpoint)
            apps_list = []
            if (
                isinstance(response, dict)
                and "data" in response
                and "list" in response["data"]
            ):
                for item in response["data"]["list"]:
                    app = {
                        "app_id": item.get("id", ""),
                        "app_name": item.get("app_name", ""),
                        "app_label": item.get("app_label", ""),
                        "app_type": item.get("app_type", 0)
                    }
                    apps_list.append(app)
            return apps_list
        except Exception:
            # 直接抛出错误
            raise

    # ==================== Utility Methods ====================

    def wait_for_task(
        self, task_id: str, query_func: callable, timeout: int = 300, interval: int = 2
    ) -> Dict[str, Any]:
        """
        等待任务完成。

        Args:
            task_id: 任务 ID
            query_func: 查询任务状态的函数
            timeout: 超时时间（秒）
            interval: 轮询间隔（秒）

        Returns:
            任务结果

        Raises:
            TimeoutError: 任务超时
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = query_func(task_id)
            data = result.get("data",{})
            status = data.get("status", "")

            if status == TaskStatus.SUCCESS:
                return result
            elif status == TaskStatus.FAILED:
                raise ValueError(f"Task failed with status: {status}, Failed Message: {data.get('message', '')}")
            elif status == TaskStatus.CANCELLED:
                raise ValueError(f"Task cancelled")

            time.sleep(interval)

        raise TimeoutError(f"Task timeout after {timeout} seconds")

    def health_check(self) -> bool:
        """
        检查 API 服务健康状态。

        Returns:
            服务是否健康
        """
        try:
            # 尝试访问一个简单的端点
            self._request("GET", "/health")
            return True
        except RequestException:
            return False

    # ==================== Custom App Management APIs ====================

    def create_custom_app(
        self,
        app_name: str,
        extract_fields: List[Dict[str, Any]],
        parse_mode: str,
        enable_long_doc: Optional[bool] = None,
        long_doc_config: Optional[List[Dict[str, Any]]] = None,
        app_label: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        创建自定义抽取应用。

        Args:
            app: 应用名称（50字以内）
            extract_fields: 字段配置列表
            parse_mode: 解析模式
            enable_long_doc: 是否开启长文档支持（可选）
            long_doc_config: 长文档配置（可选）
            app_label: 标签列表（最多5个，可选）

        Returns:
            创建结果，包含 app_id 和 config_vision
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-manage/create"

        data = {
            "app_name": app_name,
            "extract_fields": extract_fields,
            "parse_mode": parse_mode
        }

        if app_label is not None:
            data["app_label"] = app_label

        if enable_long_doc is not None:
            data["enable_long_doc"] = enable_long_doc

        # 只有共有 enable_long_doc 为 True 时，long_doc_config 才能生效且不应为空
        if enable_long_doc is True:
            if long_doc_config:
                data["long_doc_config"] = long_doc_config
            else:
                raise ValueError("long_doc_config must be provided and non-empty when enable_long_doc is True")

        return self._request("POST", endpoint, data)

    def get_custom_app_config(
        self,
        app_id: str,
        config_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        查询自定义抽取应用配置。

        Args:
            app_id: 应用唯一标识
            config_version: 配置版本号（可选，不填返回最新版本）

        Returns:
            应用配置信息
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-manage/config"

        data = {"app_id": app_id}
        if config_version:
            data["config_version"] = config_version

        return self._request("POST", endpoint, data)

    def update_custom_app(
        self,
        app_id: str,
        extract_fields: List[Dict[str, Any]],
        parse_mode: str,
        enable_long_doc: bool,
        app_name: Optional[str] = None,
        app_label: Optional[List[str]] = None,
        long_doc_config: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        更新自定义抽取应用（覆盖更新）。

        Args:
            app_id: 应用ID（必填）
            extract_fields: 抽取字段配置（必填）
            parse_mode: 解析模式（必填）
            enable_long_doc: 是否启用长文档（必填）
            app_name: 应用名称（选填）
            app_label: 应用标签（选填）
            long_doc_config: 长文档配置（仅 enable_long_doc=true 时生效）

        Returns:
            更新结果，包含 config_version
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-manage/update"

        data = {
            "app_id": app_id,
            "extract_fields": extract_fields,
            "parse_mode": parse_mode,
            "enable_long_doc": enable_long_doc,
        }

        if app_name is not None:
            data["app_name"] = app_name
        if app_label is not None:
            data["app_label"] = app_label
        if enable_long_doc is True and long_doc_config is not None:
            data["long_doc_config"] = long_doc_config

        return self._request("POST", endpoint, data)

    def delete_custom_app(self, app_id: str) -> Dict[str, Any]:
        """
        删除自定义抽取应用。

        Args:
            app_id: 应用唯一标识

        Returns:
            删除结果
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-manage/delete"

        data = {"app_id": app_id}
        return self._request("POST", endpoint, data)

    def delete_custom_app_version(
        self,
        app_id: str,
        config_version: str
    ) -> Dict[str, Any]:
        """
        删除自定义抽取应用的指定配置版本。

        Args:
            app_id: 应用唯一标识
            config_version:: 配置版本号

        Returns:
            删除结果
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-manage/version/delete"

        data = {
            "app_id": app_id,
            "config_version": config_version
        }
        return self._request("POST", endpoint, data)

    def ai_generate_fields(
        self,
        app_id: str,
        file_url: Optional[str] = None,
        file_local: Optional[str] = None,
        file_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AI 生成抽取字段与提示词推荐。

        Args:
            app_id: 应用 ID
            file_url: 示例文档地址（可选）
            file_local: 示例文档本地文件（可选）
            file_base64: Base64 编码的文件内容（可选，如果提供则跳过文件读取）

        Returns:
            AI 生成的字段推荐结果

        Raises:
            ValueError: 当 file_url、file_local 和 file_base64 都未提供时
        """
        if not file_url and not file_local and not file_base64:
            raise ValueError("Either file_url or file_local or file_base64 must be provided")

        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/v1/app-manage/ai-recommend"

        data = {"app_id": app_id}
        if file_base64:
            data["file_base64"] = file_base64
        elif file_url:
            data["file_url"] = file_url
        elif file_local:
            data["file_base64"] = self._encode_file_to_base64(file_local)

        return self._request("POST", endpoint, data)

    def get_user_payment_status(self) -> Dict[str, Any]:
        """
        获取用户付费状态。

        Returns:
            用户付费状态信息

        Raises:
            RequestException: 请求失败
        """
        tenant_name = self.config_manager.get("tenant_name", "laiye")
        endpoint = f"/open/agentic_doc_processor/{tenant_name}/user/payment"
        return self._request("GET", endpoint)
