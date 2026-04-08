"""Main CLI entry point for ADP."""

import sys
import functools
from pathlib import Path
from typing import Optional, Dict, Any

import click
from click.core import F

from adp_cli.adp import (
    ConfigManager,
    APIClient,
    FileHandler,
    OutputFormatter,
    ADPCacheManager,
)
from adp_cli.i18n import t, set_language, reset_help_formatter, get_language

# Set output encoding to UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7 doesn't have reconfigure
        pass


# Global shared formatter
formatter = OutputFormatter()

# Exit codes for CLI
EXIT_SUCCESS = 0
EXIT_GENERAL_ERROR = 1
EXIT_PARAMETER_ERROR = 2
EXIT_RESOURCE_NOT_FOUND = 3
EXIT_PERMISSION_DENIED = 4
EXIT_CONFLICT = 5

# Error types for structured error output
ERROR_TYPE_API = "API_ERROR"
ERROR_TYPE_NETWORK = "NETWORK_ERROR"
ERROR_TYPE_AUTH = "AUTH_ERROR"
ERROR_TYPE_PARAM = "PARAM_ERROR"
ERROR_TYPE_RESOURCE = "RESOURCE_ERROR"
ERROR_TYPE_SYSTEM = "SYSTEM_ERROR"


class CLIError(Exception):
    """Structured CLI error with full context for Agent handling."""

    def __init__(
        self,
        message: str,
        error_type: str,
        exit_code: int,
        fix: str = None,
        retryable: bool = False,
        details: Dict[str, Any] = None
    ):
        """
        Initialize CLI error.

        Args:
            message: Human-readable error description
            error_type: Machine-readable error type (ERROR_TYPE_*)
            exit_code: Exit code (EXIT_*)
            fix: Suggested fix for Agent
            retryable: Whether this error is retryable
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.exit_code = exit_code
        self.fix = fix or ""
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "type": self.error_type,
            "code": self.exit_code,
            "message": self.message,
            "fix": self.fix,
            "retryable": self.retryable,
            "details": self.details
        }


def print_error_and_exit(error: CLIError) -> None:
    """
    Print structured error and exit with appropriate code.

    Args:
        error: CLIError instance
    """
    formatter.print_error(error.to_dict())
    sys.exit(error.exit_code)


def classify_exception(e: Exception, context: str = "") -> CLIError:
    """
    Classify an exception and return appropriate CLIError.

    Args:
        e: The exception to classify
        context: Additional context about where the error occurred

    Returns:
        CLIError with appropriate type, exit code, and fix suggestion
    """
    error_str = str(e).lower()
    message = str(e)

    # 网络相关错误
    if any(keyword in error_str for keyword in ['timeout', 'connection', 'network', 'dns', 'ECONNREFUSED', ' ConnectionError']):
        return CLIError(
            message=f"Network error: {message}",
            error_type=ERROR_TYPE_NETWORK,
            exit_code=EXIT_GENERAL_ERROR,
            fix="Check your network connection and try again. If the issue persists, the API server may be down.",
            retryable=True,
            details={"context": context} if context else {}
        )

    # API 认证错误
    if any(keyword in error_str for keyword in ['401', 'unauthorized', 'auth', 'invalid api key', 'api key']):
        return CLIError(
            message=f"Authentication error: {message}",
            error_type=ERROR_TYPE_AUTH,
            exit_code=EXIT_PERMISSION_DENIED,
            fix="Check your API key is correct. Run 'adp config set --api-key YOUR_KEY' to update.",
            retryable=False,
            details={"context": context} if context else {}
        )

    # 权限不足
    if any(keyword in error_str for keyword in ['403', 'forbidden', 'permission']):
        return CLIError(
            message=f"Permission denied: {message}",
            error_type=ERROR_TYPE_AUTH,
            exit_code=EXIT_PERMISSION_DENIED,
            fix="Your account may not have permission for this operation. Contact support.",
            retryable=False,
            details={"context": context} if context else {}
        )

    # 资源不存在
    if any(keyword in error_str for keyword in ['404', 'not found', 'does not exist', 'version_not_found']):
        return CLIError(
            message=f"Resource not found: {message}",
            error_type=ERROR_TYPE_RESOURCE,
            exit_code=EXIT_RESOURCE_NOT_FOUND,
            fix="Verify the resource exists or check if the ID is correct.",
            retryable=False,
            details={"context": context} if context else {}
        )

    # 文件/路径错误
    if any(keyword in error_str for keyword in ['file not found', 'path not found', 'no such file', 'ENOENT']):
        return CLIError(
            message=f"File not found: {message}",
            error_type=ERROR_TYPE_RESOURCE,
            exit_code=EXIT_RESOURCE_NOT_FOUND,
            fix="Check the file path is correct and the file exists.",
            retryable=False,
            details={"context": context} if context else {}
        )

    # JSON 解析错误
    if any(keyword in error_str for keyword in ['json', 'decode', 'parse']):
        return CLIError(
            message=f"JSON parse error: {message}",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Check the JSON format is valid.",
            retryable=False,
            details={"context": context} if context else {}
        )

    # 路径遍历
    if any(keyword in error_str for keyword in ['path traversal', 'invalid path']):
        return CLIError(
            message=f"Path security error: {message}",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="The path contains invalid characters. Use relative paths without '../'.",
            retryable=False,
            details={"context": context} if context else {}
        )

    # 默认：一般错误
    return CLIError(
        message=f"Error: {message}",
        error_type=ERROR_TYPE_SYSTEM,
        exit_code=EXIT_GENERAL_ERROR,
        fix="Check the error message and try again. If the issue persists, contact support.",
        retryable=False,
        details={"context": context} if context else {}
    )


def check_config(func):
    """Decorator: Check if configuration is complete."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config_manager = ConfigManager()
        if not config_manager.is_configured():
            error = CLIError(
                message=t('error_not_configured'),
                error_type=ERROR_TYPE_PARAM,
                exit_code=EXIT_PARAMETER_ERROR,
                fix="Run 'adp config set --api-key YOUR_KEY --api-base-url YOUR_URL' to configure",
                retryable=False
            )
            print_error_and_exit(error)
        return func(*args, **kwargs)
    return wrapper


def _validate_concurrency(api_client: APIClient, concurrency: int) -> int:
    """
    Validate and adjust concurrency limit based on user payment status.

    Args:
        api_client: APIClient instance
        concurrency: Requested concurrency from user input

    Returns:
        int: Allowed concurrency value based on user's payment level

    Raises:
        ValueError: Only re-raises original ValueError from API
    """
    # 性能优化: 先处理最常见和最限制的分支，最大程度减少外部 API 请求
    if concurrency <= 1:
        return 1

    # 常量定义，便于维护与升级
    FREE_LIMIT = 1
    PAID_LIMIT = 2

    try:
        # 只在需要请求时才访问接口，提高性能
        payment_status = api_client.get_user_payment_status()
        payment_type = payment_status.get("payment_type", "")

        if payment_type == "paid":
            allowed = min(concurrency, PAID_LIMIT)
            if concurrency > PAID_LIMIT:
                formatter.print_warning(f"{t('warning')}: {t('error_invalid_concurrency')}")
            return allowed
        else:
            if concurrency > FREE_LIMIT:
                formatter.print_warning(f"{t('warning')}: {t('error_not_paid_user')}")
            return FREE_LIMIT

    except ValueError:
        # 可预期异常直接抛出，后续上层捕获处理
        raise
    except Exception:
        # 所有其他异常（比如网络、未知API错误），保守降级
        formatter.print_warning(f"{t('warning')}: {t('error_invalid_concurrency')}")
        return FREE_LIMIT


class CLI(click.Group):
    """Custom Click Group class for dynamic i18n support."""

    def format_help(self, ctx, formatter):
        """Format help text with dynamic i18n support."""
        # Update option help texts for current command (including global options)
        if hasattr(self, 'params'):
            for param in self.params:
                if hasattr(param, 'help') and param.help and param.help.startswith("__") and param.help.endswith("__"):
                    key = param.help.strip("_")
                    param.help = t(key)
        super().format_help(ctx, formatter)

    def format_commands(self, ctx, formatter):
        """Format commands section with dynamic i18n support."""
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            if cmd is not None:
                # Get translated help text
                if hasattr(cmd, 'help_key'):
                    help_text = t(cmd.help_key)
                else:
                    help_text = cmd.get_short_help_str()
                commands.append((subcommand, help_text))

        if commands:
            with formatter.section("Commands"):
                formatter.write_dl(commands)

    def get_command(self, ctx, cmd_name):
        """Get command and update its help text."""
        cmd = super().get_command(ctx, cmd_name)
        if cmd:
            # Update command help text
            if hasattr(cmd, 'is_group') and cmd.is_group:
                # For groups, we need to update help text dynamically
                if hasattr(cmd, 'help_key'):
                    cmd.help = t(cmd.help_key)
            else:
                # For commands, update help text dynamically
                if hasattr(cmd, 'help_key'):
                    cmd.help = t(cmd.help_key)
                # Also handle placeholder pattern (e.g., "__key__")
                if cmd.help and cmd.help.startswith("__") and cmd.help.endswith("__"):
                    key = cmd.help.strip("_")
                    cmd.help = t(key)

            # Update option help texts dynamically
            if hasattr(cmd, 'params'):
                for param in cmd.params:
                    if hasattr(param, 'help_key'):
                        param.help = t(param.help_key)
                    # Also handle placeholder pattern (e.g., "__key__")
                    if hasattr(param, 'help') and param.help and param.help.startswith("__") and param.help.endswith("__"):
                        key = param.help.strip("_")
                        param.help = t(key)
        return cmd


def lang_callback(_ctx, _param, value):
    """Callback to set language from --lang option."""
    if value:
        set_language(value)
        reset_help_formatter()
    return value


@click.version_option(version="1.10.0", prog_name="adp")
@click.option('--json', 'json_mode', is_flag=True, help="__option_json__", is_eager=True)
@click.option('--quiet', is_flag=True, help="__option_quiet__", is_eager=True)
@click.option('--lang', help="__option_lang__", is_eager=True, callback=lang_callback)
@click.group(cls=CLI, context_settings={'help_option_names': ['-h', '--help']})
@click.pass_context
def cli(ctx, json_mode, quiet, lang):
    """
    ADP CLI - AI Document Platform Command Line Tool
    """
    # Setup custom help formatter
    ctx.help_formatter_class = reset_help_formatter().__class__

    # Store global options in context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj['json_mode'] = json_mode
    ctx.obj['quiet'] = quiet
    ctx.obj['lang'] = lang

    # Update formatter with global options
    formatter.set_json_mode(json_mode)
    formatter.set_quiet_mode(quiet)


# ==================== Config Commands ====================

@cli.group(help=t('config_description'), cls=CLI)
def config():
    """
    Authentication configuration management.
    """
    pass

# Store help key for dynamic i18n
config.help_key = 'config_description'
config.is_group = True


@config.command(help="__config_set_title__")
@click.option('--api-key', help="__option_api_key__")
@click.option('--api-base-url', help="__option_api_base_url__")
def set(api_key, api_base_url):
    """
    Set or update API Key and API Base URL.
    """
    if not api_key and not api_base_url:
        error = CLIError(
            message=t('error_api_key_or_url_required'),
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Provide at least one of --api-key or --api-base-url",
            retryable=False
        )
        print_error_and_exit(error)

    config_manager = ConfigManager()

    if api_key:
        config_manager.set_api_key(api_key)
        formatter.print_success(t('api_key_configured'))

    if api_base_url:
        config_manager.set("api_base_url", api_base_url)
        formatter.print_success(t('api_base_url_configured'))

set.help_key = 'config_set_title'


@config.command(help=t('config_get_title'))
def get():
    """
    View current configuration.
    """
    config_manager = ConfigManager()
    summary = config_manager.get_config_summary()
    formatter.print_json(summary)

    # if formatter.json_mode:
    #     formatter.print_json(summary)
    # else:
    #     formatter.print_config_summary(summary)

get.help_key = 'config_get_title'


@config.command(help=t('config_clear_title'))
@click.option('--force', '-y', is_flag=True, help="__option_force_clear__")
def clear(force):
    """
    Clear local configuration.
    """
    config_manager = ConfigManager()
    if force or click.confirm(t('confirm_clear_config')):
        config_manager.clear()
        formatter.print_success(t('config_cleared'))

clear.help_key = 'config_clear_title'


# ==================== Parse Commands ====================

@cli.group(help=t('parse_description'), cls=CLI)
def parse():
    """
    Document parsing.
    """
    pass

parse.help_key = 'parse_description'
parse.is_group = True


@parse.command(help="__parse_local_title__")
@click.argument('path', type=click.Path(exists=True))
@click.option('--app-id', required=True, help="__option_app_id_parse__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_timeout__")
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1, help="__option_concurrency__")
@check_config
def local(path, app_id, async_mode, export, timeout, concurrency):
    """
    Parse local files or folders.
    """
    try:
        _process_local_files(path, async_mode, export, timeout, mode="parse", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        print_error_and_exit(classify_exception(e, "parse local"))

local.help_key = 'parse_local_title'


@parse.command(help="__parse_url_title__")
@click.argument('url')
@click.option('--app-id', required=True, help="__option_app_id_parse__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_timeout__")
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1, help="__option_concurrency__")
@check_config
def url(url, app_id, async_mode, export, timeout, concurrency):
    """
    Parse URL files or URL list files.
    """
    try:
        _process_url_file(url, async_mode, export, timeout, mode="parse", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        print_error_and_exit(classify_exception(e))

url.help_key = 'parse_url_title'


@parse.command('base64', help="__parse_base64_title__")
@click.argument('file_base64', nargs=-1, required=True)
@click.option('--app-id', required=True, help="__option_app_id_parse__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_timeout__")
@click.option('--file-name', default="document", help="__option_file_name__")
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1, help="__option_concurrency__")
@check_config
def parse_base64(file_base64, app_id, async_mode, export, timeout, file_name, concurrency):
    """
    Parse base64 encoded file content.
    """
    try:
        _process_base64_files(
            file_base64, app_id, file_name, async_mode,
            export, timeout, mode="parse", concurrency=concurrency
        )
    except Exception as e:
        print_error_and_exit(classify_exception(e))

parse_base64.help_key = 'parse_base64_title'


# ==================== Extract Commands ====================

@cli.group(help=t('extract_description'), cls=CLI)
def extract():
    """
    Document extraction.
    """
    pass

extract.help_key = 'extract_description'
extract.is_group = True


@extract.command(help="__extract_local_title__")
@click.argument('path', type=click.Path(exists=True))
@click.option('--app-id', required=True, help="__option_app_id_extract__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_timeout__")
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1, help="__option_concurrency__")
@check_config
def local(path, app_id, async_mode, export, timeout, concurrency):
    """
    Extract local files or folders.
    """
    try:
        _process_local_files(path, async_mode, export, timeout, mode="extract", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        print_error_and_exit(classify_exception(e))

local.help_key = 'extract_local_title'


@extract.command(help="__extract_url_title__")
@click.argument('url')
@click.option('--app-id', required=True, help="__option_app_id_extract__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_timeout__")
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1, help="__option_concurrency__")
@check_config
def url(url, app_id, async_mode, export, timeout, concurrency):
    """
    Extract URL files or URL list files.
    """
    try:
        _process_url_file(url, async_mode, export, timeout, mode="extract", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        print_error_and_exit(classify_exception(e))

url.help_key = 'extract_url_title'


@extract.command('base64', help="__extract_base64_title__")
@click.argument('file_base64', nargs=-1, required=True)
@click.option('--app-id', required=True, help="__option_app_id_extract__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_timeout__")
@click.option('--file-name', default="document", help="__option_file_name__")
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1, help="__option_concurrency__")
@check_config
def extract_base64(file_base64, app_id, async_mode, export, timeout, file_name, concurrency):
    """
    Extract base64 encoded file content.
    """
    try:
        _process_base64_files(
            file_base64, app_id, file_name, async_mode,
            export, timeout, mode="extract", concurrency=concurrency
        )
    except Exception as e:
        print_error_and_exit(classify_exception(e))

extract_base64.help_key = 'extract_base64_title'


@extract.command('query', help="__extract_query_title__")
@click.argument('task-id')
@click.option('--watch', is_flag=True, help="__option_watch__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_watch_timeout__")
@check_config
def extract_query(task_id, watch, export,timeout):
    """
    Query extract async task status.
    """
    try:
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)

        if watch:
            # Watch mode: wait for task completion
            result = api_client.wait_for_task(
                task_id,
                api_client.query_extract_task,
                timeout=timeout
            )
            formatter.print_success(t('task_completed'))
        else:
            # Single query
            result = api_client.query_extract_task(task_id)
        data = result.get("data",{})
        formatter.print_task_result(task_id, data.get("status", ""), result)
        if export:
            FileHandler.write_json_output(data, Path(export))
            formatter.print_success(f"{t('results_exported_to')} {export}")
            
    except Exception as e:
        print_error_and_exit(classify_exception(e))

extract_query.help_key = 'extract_query_title'


# ==================== Parse Query Command ====================

@parse.command('query', help="__parse_query_title__")
@click.argument('task-id')
@click.option('--watch', is_flag=True, help="__option_watch__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=900, help="__option_watch_timeout__")
@check_config
def parse_query(task_id, watch,export, timeout):
    """
    Query parse async task status.
    """
    try:
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)

        if watch:
            # Watch mode: wait for task completion
            result = api_client.wait_for_task(
                task_id,
                api_client.query_parse_task,
                timeout=timeout
            )
            formatter.print_success(t('task_completed'))
        else:
            # Single query
            result = api_client.query_parse_task(task_id)
        data = result.get("data",{})
        formatter.print_task_result(task_id, data.get("status", ""), result)
        if export:
            FileHandler.write_json_output(data, Path(export))
            formatter.print_success(f"{t('results_exported_to')} {export}")
            

    except Exception as e:
        print_error_and_exit(classify_exception(e))

parse_query.help_key = 'parse_query_title'


# ==================== App ID Command ====================

@cli.group(help=t('app_id_description'), cls=CLI)
def app_id():
    """
    Application management.
    """
    pass

app_id.help_key = 'app_id_description'
app_id.is_group = True


@app_id.command('list', help=t('app_id_list_title'))
@click.option('--app-label', help="__app_id_list_app_label__")
@click.option('--app-type', type=int, help="__app_id_list_app_type__")
@click.option('--limit', type=int, default=120, help="__app_id_list_limit__", callback=lambda ctx, param, value: (_ for _ in ()).throw(click.BadParameter(t('limit_must_be_non_negative'))) if value is not None and value < 0 else value)
@check_config
def list_apps(app_label, app_type, limit):
    """
    List all available application IDs from API.
    """
    try:
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)
        apps = api_client.list_apps(app_type, limit)

        # Save all apps to cache
        cache = ADPCacheManager()
        cache.set_apps(apps)

        # Filter by app_label if provided
        if app_label:
            filtered_apps = []
            for app in apps:
                app_labels = app.get("app_label", [])
                if app_labels:
                    label_str = ", ".join(app_labels) if isinstance(app_labels, list) else str(app_labels)
                    if app_label in label_str:
                        filtered_apps.append(app)
            apps = filtered_apps

        if apps:
            formatter.print_json({"apps": apps})
        else:
            formatter.print_json({"apps": [], "message": t('no_applications_found')})

    except Exception as e:
        print_error_and_exit(classify_exception(e))

list_apps.help_key = 'app_id_list_title'


@app_id.command('cache', help=t('app_id_list_cache_title'))
def list_apps_cache():
    """
    List cached application IDs (fast, no network required).
    """
    cache = ADPCacheManager()
    apps = cache.get_all_apps()
    formatter.print_json({"apps": apps})

list_apps_cache.help_key = 'app_id_list_cache_title'


# ==================== Custom App Commands ====================

def _parse_json_param_value(value: str):
    """
    解析 JSON 参数值（字符串或文件路径）。

    支持两种方式：
    1. 直接传入 JSON 字符串
    2. 传入 JSON 文件路径（自动读取文件内容）

    Args:
        value: 参数值（JSON 字符串或文件路径）

    Returns:
        解析后的 Python 对象
    """
    if value is None:
        return None
    import json
    from pathlib import Path

    # 检查是否为文件路径
    path = Path(value)
    if path.exists() and path.is_file():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                json_str = f.read()
        except Exception as e:
            print_error_and_exit(classify_exception(e, "read JSON file"))
    else:
        json_str = value

    # 去除首尾空白
    json_str = json_str.strip()

    # 剥离外层引号（某些终端可能会包裹引号）
    if (json_str.startswith('"') and json_str.endswith('"')) or \
       (json_str.startswith("'") and json_str.endswith("'")):
        json_str = json_str[1:-1].strip()

    # 尝试解析 JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        error = CLIError(
            message=f"Invalid JSON format: {str(e)}",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Check the JSON syntax is correct. Use a JSON validator if needed.",
            retryable=False
        )
        print_error_and_exit(error)


def parse_bool_param(_ctx, _param, value):
    """
    Click callback: 解析布尔参数。

    Args:
        _ctx: Click 上下文（未使用）
        _param: 参数对象（未使用）
        value: 参数值

    Returns:
        布尔值
    """
    if value is None:
        return None
    if value.lower() in ('true', '1', 'yes'):
        return True
    elif value.lower() in ('false', '0', 'no'):
        return False
    else:
        error = CLIError(
            message=f"Invalid boolean value: {value}",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Use one of: true, false, 1, 0, yes, no",
            retryable=False
        )
        print_error_and_exit(error)


def parse_json_list_param(_ctx, _param, value):
    """
    Click callback: 解析 JSON 列表参数（用于 app-label）。

    Args:
        _ctx: Click 上下文（未使用）
        _param: 参数对象（未使用）
        value: 参数值（JSON 字符串或逗号分隔的字符串）

    Returns:
        列表
    """
    if value is None:
        return None
    import json
    import re

    # 检查是否为 JSON 数组格式
    if value.strip().startswith('['):
        try:
            labels = json.loads(value)
            if isinstance(labels, type([])):
                return labels
            else:
                error = CLIError(
                    message=f"app-label must be a list, got: {value}",
                    error_type=ERROR_TYPE_PARAM,
                    exit_code=EXIT_PARAMETER_ERROR,
                    fix="Provide app-label as a JSON array, e.g., [\"tag1\", \"tag2\"]",
                    retryable=False
                )
                print_error_and_exit(error)
        except json.JSONDecodeError:
            # 不是有效的 JSON，尝试作为逗号分隔的字符串处理
            pass

    # 尝试作为作为逗号分隔的字符串处理
    # 去除可能的引号
    value = re.sub(r'^["\']|["\']$', '', value)
    return [label.strip() for label in value.split(',') if label.strip()]


def validate_create_app_params(app_name, app_label, enable_long_doc, long_doc_config):
    """
    验证创建应用参数。

    Args:
        app_name: 应用名称
        app_label: 标签列表
        enable_long_doc: 是否开启长文档支持
        long_doc_config: 长文档配置
    """
    # 验证 app_name 长度不超过 50 字符
    if len(app_name) > 50:
        error = CLIError(
            message=f"app_name must be 50 characters or less (got {len(app_name)})",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Shorten the app_name to 50 characters or fewer",
            retryable=False
        )
        print_error_and_exit(error)

    # 验证 app_label 最多 5 个
    if app_label and len(app_label) > 5:
        error = CLIError(
            message=f"app_label must have 5 or fewer labels (got {len(app_label)})",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Remove extra labels to keep only 5 or fewer",
            retryable=False
        )
        print_error_and_exit(error)

    # 验证 long_doc_config 仅在 enable_long_doc=true 时生效
    if long_doc_config is not None and not enable_long_doc:
        error = CLIError(
            message="long_doc_config is only valid when enable_long_doc=true",
            error_type=ERROR_TYPE_PARAM,
            exit_code=EXIT_PARAMETER_ERROR,
            fix="Set --enable-long-doc to true when using --long-doc-config",
            retryable=False
        )
        print_error_and_exit(error)
        sys.exit(EXIT_PARAMETER_ERROR)


@cli.group(help=t('custom_app_description'), cls=CLI)
def custom_app():
    """
    Custom extraction application management.
    """
    pass

custom_app.help_key = 'custom_app_description'
custom_app.is_group = True


@custom_app.command(help="__custom_app_create_title__")
@click.option('--api-key', help="__custom_app_create_api_key__")
@click.option('--app-name', required=True, help="__custom_app_create_app_name__")
@click.option('--app-label', callback=parse_json_list_param, help="__custom_app_create_app_label__")
@click.option('--extract-fields', required=True, help="__custom_app_create_extract_fields__")
@click.option('--parse-mode', required=True,
              type=click.Choice(['standard', 'advance', 'agentic'], case_sensitive=False),
              help="__custom_app_create_parse_mode__")
@click.option('--enable-long-doc', callback=parse_bool_param, help="__custom_app_create_enable_long_doc__")
@click.option('--long-doc-config', help="__custom_app_create_long_doc_config__")
@check_config
def create(api_key, app_name, app_label, extract_fields, parse_mode, enable_long_doc, long_doc_config):
    """
    Create a custom extraction application.

    """
    try:
        # 验证参数
        validate_create_app_params(app_name, app_label, enable_long_doc, long_doc_config)

        # 解析 JSON 参数（支持字符串或文件路径）
        extract_fields = _parse_json_param_value(extract_fields)
        if long_doc_config:
            long_doc_config = _parse_json_param_value(long_doc_config)


        # 临时覆盖 API Key（如果提供）
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.create_custom_app(
            app_name=app_name,
            extract_fields=extract_fields,
            parse_mode=parse_mode,
            enable_long_doc=enable_long_doc,
            long_doc_config=long_doc_config,
            app_label=app_label
        )

        formatter.print_success(t('app_created'))
        formatter.print_json(result)

        # 恢复原始 API Key
        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))

create.help_key = 'custom_app_create_title'


@custom_app.command(help="__custom_app_update_title__")
@click.option('--api-key', help="__custom_app_update_api_key__")
@click.option('--app-id', required=True, help="__custom_app_update_app_id__")
@click.option('--app-name', help="__custom_app_update_app_name__")
@click.option('--app-label', callback=parse_json_list_param, help="__custom_app_update_app_label__")
@click.option('--extract-fields', required=True, help="__custom_app_update_extract_fields__")
@click.option('--parse-mode', required=True,
              type=click.Choice(['standard', 'advance', 'agentic'], case_sensitive=False),
              help="__custom_app_update_parse_mode__")
@click.option('--enable-long-doc', 'enable_long_doc', required=True,
              callback=parse_bool_param, help="__custom_app_update_enable_long_doc__")
@click.option('--long-doc-config', help="__custom_app_update_long_doc_config__")
@check_config
def update(api_key, app_id, app_name, app_label, extract_fields,
           parse_mode, enable_long_doc, long_doc_config):
    """
    Update a custom extraction application (full coverage update).
    """
    try:
        # 解析 JSON 参数
        extract_fields = _parse_json_param_value(extract_fields)
        if long_doc_config:
            long_doc_config = _parse_json_param_value(long_doc_config)

        # 临时覆盖 API Key
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.update_custom_app(
            app_id=app_id,
            extract_fields=extract_fields,
            parse_mode=parse_mode,
            enable_long_doc=enable_long_doc,
            app_name=app_name,
            app_label=app_label,
            long_doc_config=long_doc_config,
        )

        formatter.print_success(t('app_updated'))
        formatter.print_json(result)

        # 恢复原始 API Key
        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))

update.help_key = 'custom_app_update_title'


@custom_app.command(help="__custom_app_get_config_title__")
@click.option('--api-key', help="__custom_app_get_config_api_key__")
@click.option('--app-id', required=True, help="__custom_app_get_config_app_id__")
@click.option('--config-version', help="__custom_app_get_config_config_version__")
@check_config
def get_config(api_key, app_id, config_version):
    """
    Query custom app configuration.
    """
    try:
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.get_custom_app_config(app_id, config_version)

        if formatter.json_mode:
            formatter.print_json(result)
        else:
            formatter.print_section(t('app_config'))
            formatter.print_json(result)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))

get_config.help_key = 'custom_app_get_config_title'


@custom_app.command(help="__custom_app_delete_title__")
@click.option('--api-key', help="__custom_app_delete_api_key__")
@click.option('--app-id', required=True, help="__custom_app_delete_app_id__")
@check_config
def delete(api_key, app_id):
    """
    Delete a custom extraction application.
    """
    try:
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.delete_custom_app(app_id)

        # 检查业务级删除结果
        if result.get("code") == "success" and result.get("data", {}).get("success"):
            formatter.print_success(t('app_deleted'))
        else:
            # 删除失败（可能是应用不存在）
            error_msg = result.get("data", {}).get("message", "Failed to delete app")
            error = CLIError(
                message=f"Failed to delete app: {error_msg}",
                error_type=ERROR_TYPE_RESOURCE,
                exit_code=EXIT_RESOURCE_NOT_FOUND,
                fix="Verify the app-id is correct. Run 'adp custom-app get-config --app-id YOUR_APP_ID' to check if the app exists.",
                retryable=False,
                details={"app_id": app_id}
            )
            print_error_and_exit(error)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))

delete.help_key = 'custom_app_delete_title'


@custom_app.command(help="__custom_app_delete_version_title__")
@click.option('--api-key', help="__custom_app_delete_version_api_key__")
@click.option('--app-id', required=True, help="__custom_app_delete_version_app_id__")
@click.option('--config-version', required=True, help="__custom_app_delete_version_config_version__")
@check_config
def delete_version(api_key, app_id, config_version):
    """
    Delete a specific configuration version of a custom app.
    """
    try:
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.delete_custom_app_version(app_id, config_version)

        # 检查业务级删除结果
        if result.get("code") == "success":
            formatter.print_success(t('version_deleted'))
        else:
            # 删除失败（可能是版本不存在）
            error_msg = result.get("message", "Failed to delete version")
            error = CLIError(
                message=f"Failed to delete version: {error_msg}",
                error_type=ERROR_TYPE_RESOURCE,
                exit_code=EXIT_RESOURCE_NOT_FOUND,
                fix="Verify the app-id and config-version are correct.",
                retryable=False,
                details={"app_id": app_id, "config_version": config_version}
            )
            print_error_and_exit(error)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))

delete_version.help_key = 'custom_app_delete_version_title'


@custom_app.command(help="__custom_app_ai_generate_title__")
@click.option('--api-key', help="__custom_app_ai_generate_api_key__")
@click.option('--app-id', required=True, help="__custom_app_ai_generate_app_id__")
@click.option('--file-url', help="__custom_app_ai_generate_file_url__")
@click.option('--file-local', help="__custom_app_ai_generate_file_local__")
@click.option('--base64', 'file_base64', help="__custom_app_ai_generate_file_base64__")
@check_config
def ai_generate(api_key, app_id, file_url, file_local, file_base64):
    """
    AI generate extraction field recommendations.
    """
    try:
        if not file_url and not file_local and not file_base64:
            error = CLIError(
                message="One of --file-url, --file-local, or --base64 must be provided",
                error_type=ERROR_TYPE_PARAM,
                exit_code=EXIT_PARAMETER_ERROR,
                fix="Provide at least one of: --file-url, --file-local, or --base64",
                retryable=False
            )
            print_error_and_exit(error)

        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.ai_generate_fields(app_id, file_url, file_local, file_base64)

        formatter.print_section(t('custom_app_ai_generate_title'))
        formatter.print_json(result)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))

ai_generate.help_key = 'custom_app_ai_generate_title'


# ==================== Credit Command ====================

@cli.command(help=t('credit_description'))
@click.option('--api-key', help="__credit_api_key__")
@check_config
def credit(api_key):
    """
    Query remaining credits.
    """
    try:
        # Temporarily override API Key (if provided)
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.get_user_payment_status()

        # Get credit from response
        credit = result.get("remaining_credits", 0)

        # Get portal URL based on language
        lang = get_language()
        if lang == 'zh':
            portal_url = "https://adp.laiye.com"
        else:
            portal_url = "https://adp-global.laiye.com"

        # Display result
        if formatter.json_mode:
            formatter.print_json({
                "credit": credit,
                "portal_url": portal_url
            })
        else:
            formatter.print_section(t('credit_info'))
            formatter.print_info(f"{t('remaining_credits')}: {credit}")
            formatter.print_info(f"{t('recharge_message')}: {portal_url}")

        # Restore original API Key
        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        print_error_and_exit(classify_exception(e))


# ==================== Help Command ====================

@cli.command(help=t('help_description'))
@click.pass_context
def help(ctx):
    """
    Display help information and available commands.
    """
    click.echo(ctx.parent.get_help())
    return

help.help_key = 'help_description'


# ==================== Schema Command ====================

@cli.command(help="__schema_description__")
@click.argument('command', required=False, nargs=-1)
def schema(command):
    """
    Display command schema for Agent introspection.

    Use this command to query the CLI's capabilities and parameter definitions.

    Examples:
        adp schema              # Show full command tree
        adp schema parse       # Show parse command group
        adp schema parse local # Show parse local command details
    """
    if command:
        # command is a tuple of parts, e.g. ('parse', 'local')
        # Navigate through the command tree
        cmd = cli
        cmd_name_parts = []
        for part in command:
            next_cmd = cmd.get_command(None, part) if hasattr(cmd, 'get_command') else None
            if next_cmd is None:
                full_path = " ".join(command[:len(cmd_name_parts) + 1])
                error = CLIError(
                    message=f"Command not found: {full_path}",
                    error_type=ERROR_TYPE_RESOURCE,
                    exit_code=EXIT_RESOURCE_NOT_FOUND,
                    fix=f"Run 'adp schema' to see available commands",
                    retryable=False,
                    details={"requested_command": full_path}
                )
                print_error_and_exit(error)
            cmd = next_cmd
            cmd_name_parts.append(part)

        full_command_name = " ".join(command)
        schema_data = _get_command_schema(full_command_name, cmd)
    else:
        # 输出完整命令树
        schema_data = _get_full_schema()

    formatter.print_json(schema_data)

schema.help_key = 'schema_description'


def _get_command_schema(command_name: str, cmd) -> Dict[str, Any]:
    """
    获取单个命令的 schema。

    Args:
        command_name: 命令名称
        cmd: Click 命令对象

    Returns:
        命令 schema 字典
    """
    schema = {
        "name": command_name,
        "help": cmd.help or "",
        "type": "group" if hasattr(cmd, 'is_group') and cmd.is_group else "command",
        "options": [],
        "arguments": [],
        "subcommands": {}
    }

    # 如果是命令组，获取子命令列表
    if hasattr(cmd, 'list_commands'):
        for sub_name in cmd.list_commands({}):
            sub_cmd = cmd.get_command({}, sub_name)
            if sub_cmd:
                schema["subcommands"][sub_name] = {
                    "help": sub_cmd.help or ""
                }

    # 如果是具体命令，获取参数和选项
    if hasattr(cmd, 'params'):
        for param in cmd.params:
            if param.param_type_name == 'argument':
                schema["arguments"].append({
                    "name": param.name,
                    "required": param.required,
                    "help": getattr(param, 'help', '') or ""
                })
            elif param.param_type_name == 'option':
                option_info = {
                    "name": param.name,
                    "required": param.required,
                    "help": getattr(param, 'help', '') or "",
                    "flags": param.opts
                }
                if hasattr(param, 'default') and param.default is not None:
                    # 过滤不可 JSON 序列化的值（如 Sentinel 对象）
                    try:
                        import json
                        json.dumps(param.default)
                        option_info["default"] = param.default
                    except (TypeError, ValueError):
                        pass
                if hasattr(param, 'choices') and param.choices:
                    option_info["choices"] = list(param.choices)
                schema["options"].append(option_info)

    return schema


def _get_full_schema() -> Dict[str, Any]:
    """
    获取完整命令树 schema。

    Returns:
        完整命令树 schema
    """
    schema = {
        "version": "1.10.0",
        "commands": {}
    }

    for subcommand_name in cli.list_commands(None):
        subcommand = cli.get_command(None, subcommand_name)
        if subcommand:
            schema["commands"][subcommand_name] = {
                "help": subcommand.help or "",
                "is_group": hasattr(subcommand, 'is_group') and subcommand.is_group,
                "subcommands": {}
            }
            # 如果是命令组，获取子命令
            if hasattr(subcommand, 'list_commands'):
                for sub_name in subcommand.list_commands({}):
                    sub_cmd = subcommand.get_command({}, sub_name)
                    if sub_cmd:
                        schema["commands"][subcommand_name]["subcommands"][sub_name] = {
                            "help": sub_cmd.help or ""
                        }

    return schema


# ==================== Batch Processor Classes ====================

from typing import Tuple, List, Any, Dict, Optional


class BatchProcessor:
    """批量处理器基类，处理通用流程."""

    def __init__(self, mode: str, app_id: str, async_mode: bool,
                 export_path: Optional[str], timeout: int, concurrency: int):
        self.mode = mode
        self.app_id = app_id
        self.async_mode = async_mode
        self.export_path = export_path
        self.timeout = timeout
        self.concurrency = concurrency
        self.config_manager = ConfigManager()
        self.api_client = APIClient(self.config_manager)

    def run(self, items: List) -> None:
        """执行处理流程."""
        # 1. 验证并发
        try:
            self.concurrency = _validate_concurrency(self.api_client, self.concurrency)
        except ValueError as e:
            error = CLIError(
                message=str(e),
                error_type=ERROR_TYPE_PARAM,
                exit_code=EXIT_PARAMETER_ERROR,
                fix="Set concurrency to 1 (free users) or 2 (paid users)",
                retryable=False
            )
            print_error_and_exit(error)

        # 2. 获取有效项目
        valid_items, invalid_items = self._validate_items(items)

        # 3. 输出无效项目警告
        self._display_invalid_items(invalid_items)

        if not valid_items:
            error = CLIError(
                message="No valid files to process",
                error_type=ERROR_TYPE_RESOURCE,
                exit_code=EXIT_RESOURCE_NOT_FOUND,
                fix="Check the file path is correct and files are supported formats (PDF, DOCX, XLSX, PPTX, images)",
                retryable=False
            )
            print_error_and_exit(error)

        formatter.print_section(self._get_section_title(valid_items))

        # 4. 处理项目（并发或串行）
        if len(valid_items) > 1 and self.concurrency > 1:
            results = self._process_concurrent(valid_items)
        else:
            results = self._process_sequential(valid_items)

        # 5. 排序并输出结果
        results = _sort_and_clean_results(results)
        OutputFormatter.print_results(results, valid_items, self.mode, formatter, t)

        # 6. 导出
        self._export_if_needed(results, valid_items)

    # --- 子类必须实现的方法 ---

    def _validate_items(self, items: List) -> Tuple[List, List]:
        """验证项目，返回 (有效列表, 无效列表)."""
        raise NotImplementedError

    def _process_single(self, item: Any, index: int, total: int) -> Dict[str, Any]:
        """处理单个项目."""
        raise NotImplementedError

    def _get_item_name(self, item: Any) -> str:
        """获取项目显示名称."""
        raise NotImplementedError

    def _get_section_title(self, items: List) -> str:
        """获取section标题."""
        raise NotImplementedError

    # --- 可选覆盖的方法 ---

    def _display_invalid_items(self, invalid_items: List) -> None:
        """显示无效项目警告，默认实现."""
        if invalid_items:
            formatter.print_warning(t('skipped_invalid_files', count=len(invalid_items)))
            for item, error in invalid_items:
                formatter.print(f"  - {item}: {error}", style="dim")

    def _get_error_message_key(self) -> str:
        """获取错误消息的i18n key."""
        return 'failed_to_process'

    # --- 内部辅助方法 ---

    def _process_concurrent(self, items: List) -> List[Dict[str, Any]]:
        """并发处理."""
        return _process_items_concurrently(
            items, self._process_single,
            self.concurrency,
            self._display_submit, self._display_result, t
        )

    def _process_sequential(self, items: List) -> List[Dict[str, Any]]:
        """串行处理."""
        results = []
        for i, item in enumerate(items, 1):
            result = self._process_single(item, i, len(items))
            if "error" not in result:
                results.append(result)
            if "task_id" in result:
                formatter.print_progress(i, len(items), f"{self._get_item_name(item)} - Task_ID: {result['task_id']} - Completed")
            elif not self.async_mode:
                formatter.print_progress(i, len(items), f"{self._get_item_name(item)}")
        return results

    def _display_submit(self, index: int, item: Any, total: int) -> None:
        """显示提交信息."""
        print(f"[{index}/{total}] Submitted: {self._get_item_name(item)}")

    def _display_result(self, result: Dict[str, Any]) -> None:
        """显示结果信息."""
        item = result.get("file") or result.get("url") or result
        item_name = self._get_item_name(item) if not isinstance(item, str) else item
        if "error" in result:
            print(f"✗ Failed: {item_name} - {result['error']}")
        elif "task_id" in result:
            print(f"✓ Completed: {item_name} - Task_ID: {result['task_id']}")
        else:
            print(f"✓ Completed: {item_name}")

    def _export_if_needed(self, results: List[Dict], valid_items: List) -> None:
        """导出结果."""
        if not self.export_path:
            return
        data = results[0]["result"] if len(results) == 1 else {"results": results}
        FileHandler.write_json_output(data, Path(self.export_path))
        formatter.print_success(f"{t('results_exported_to')} {self.export_path}")

    def _call_api(self, item: Any, file_name: str, index: int) -> Dict[str, Any]:
        """调用API处理单个项目."""
        try:
            if self.mode == "parse":
                if self.async_mode:
                    task_id = self.api_client.parse_async(None, self.app_id, file_path=item)
                    result = self.api_client.wait_for_task(
                        task_id, self.api_client.query_parse_task, timeout=self.timeout
                    )
                    return {"file": str(item), "task_id": task_id, "result": result, "index": index}
                else:
                    result = self.api_client.parse_sync(None, self.app_id, file_path=item)
                    return {"file": str(item), "result": result, "index": index}
            else:  # extract
                if self.async_mode:
                    task_id = self.api_client.extract_async(None, self.app_id, file_path=item)
                    result = self.api_client.wait_for_task(
                        task_id, self.api_client.query_extract_task, timeout=self.timeout
                    )
                    return {"file": str(item), "task_id": task_id, "result": result, "index": index}
                else:
                    result = self.api_client.extract_sync(None, self.app_id, file_path=item)
                    return {"file": str(item), "result": result, "index": index}
        except Exception as e:
            formatter.print_error(t(self._get_error_message_key(), name=str(item), error=str(e)))
            return {"file": str(item), "error": str(e), "index": index}


class LocalFileProcessor(BatchProcessor):
    """本地文件批量处理器."""

    def _validate_items(self, items: List) -> Tuple[List, List]:
        """验证文件项目."""
        # items[0] is path string, get all files from this path
        path = Path(items[0])
        files = FileHandler.get_files_from_path(path)
        return FileHandler.validate_files(files)

    def _process_single(self, file_path: Path, index: int, total: int) -> Dict[str, Any]:
        """处理单个文件."""
        return self._call_api(file_path, file_path.name, index)

    def _get_item_name(self, item: Any) -> str:
        """获取文件显示名称."""
        return Path(item).name

    def _get_section_title(self, items: List) -> str:
        """获取section标题."""
        return t('processing_files', count=len(items))


class UrlProcessor(BatchProcessor):
    """URL批量处理器."""

    def __init__(self, mode: str, app_id: str, async_mode: bool,
                 export_path: Optional[str], timeout: int, concurrency: int,
                 source_file: Optional[str] = None):
        super().__init__(mode, app_id, async_mode, export_path, timeout, concurrency)
        self.source_file = source_file  # Optional: if URLs were read from a file

    def _validate_items(self, items: List) -> Tuple[List, List]:
        """验证URL项目."""
        valid_urls = []
        invalid_urls = []

        for url in items:
            if _is_valid_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append((url, t('invalid_url_format', url=url)))

        return valid_urls, invalid_urls

    def _process_single(self, url: str, index: int, total: int) -> Dict[str, Any]:
        """处理单个URL."""
        try:
            if self.mode == "parse":
                if self.async_mode:
                    task_id = self.api_client.parse_async(url, self.app_id)
                    result = self.api_client.wait_for_task(
                        task_id, self.api_client.query_parse_task, timeout=self.timeout
                    )
                    return {"url": url, "task_id": task_id, "result": result, "index": index}
                else:
                    result = self.api_client.parse_sync(url, self.app_id)
                    return {"url": url, "result": result, "index": index}
            else:  # extract
                if self.async_mode:
                    task_id = self.api_client.extract_async(url, self.app_id)
                    result = self.api_client.wait_for_task(
                        task_id, self.api_client.query_extract_task, timeout=self.timeout
                    )
                    return {"url": url, "task_id": task_id, "result": result, "index": index}
                else:
                    result = self.api_client.extract_sync(url, self.app_id)
                    return {"url": url, "result": result, "index": index}
        except Exception as e:
            formatter.print_error(t('failed_to_process_url', url=url, error=str(e)))
            return {"url": url, "error": str(e), "index": index}

    def _get_item_name(self, item: Any) -> str:
        """获取URL显示名称（截断处理）."""
        url = str(item)
        return url[:80] + ('...' if len(url) > 80 else '')

    def _get_section_title(self, items: List) -> str:
        """获取section标题."""
        if len(items) == 1 and not self.source_file:
            return t('processing_url', count=1, url=items[0])
        elif self.source_file:
            return t('processing_urls', count=len(items), file=self.source_file)
        return t('processing_urls', count=len(items), file='')

    def _display_submit(self, index: int, item: Any, total: int) -> None:
        """显示提交信息."""
        url = str(item)
        url_display = url[:80] + ('...' if len(url) > 80 else '')
        print(f"[{index}/{total}] Submitted: {url_display}")

    def _display_result(self, result: Dict[str, Any]) -> None:
        """显示结果信息."""
        url = result.get("url", "")
        url_display = url[:60] + ('...' if len(url) > 60 else '')
        if "error" in result:
            print(f"✗ Failed: {url_display} - {result['error']}")
        elif "task_id" in result:
            print(f"✓ Completed: {url_display} - Task_ID: {result['task_id']}")
        else:
            print(f"✓ Completed: {url_display}")

    def _get_error_message_key(self) -> str:
        """获取错误消息的i18n key."""
        return 'failed_to_process_url'


class Base64Processor(BatchProcessor):
    """Base64批量处理器."""

    def __init__(self, mode: str, app_id: str, async_mode: bool,
                 export_path: Optional[str], timeout: int, concurrency: int,
                 file_name: str = "document"):
        super().__init__(mode, app_id, async_mode, export_path, timeout, concurrency)
        self.file_name = file_name

    def _validate_items(self, items: List) -> Tuple[List, List]:
        """Base64不需要验证，直接返回."""
        return items, []

    def _process_single(self, b64_str: str, index: int, total: int) -> Dict[str, Any]:
        """处理单个base64字符串."""
        current_file_name = self.file_name if total == 1 else f"{self.file_name}_{index}"
        try:
            if self.mode == "parse":
                if self.async_mode:
                    task_id = self.api_client.parse_async(None, self.app_id, file_base64=b64_str, file_name=current_file_name)
                    result = self.api_client.wait_for_task(
                        task_id, self.api_client.query_parse_task, timeout=self.timeout
                    )
                    return {"index": index, "task_id": task_id, "result": result}
                else:
                    result = self.api_client.parse_sync(None, self.app_id, file_base64=b64_str, file_name=current_file_name)
                    return {"index": index, "result": result}
            else:  # extract
                if self.async_mode:
                    task_id = self.api_client.extract_async(None, self.app_id, file_base64=b64_str, file_name=current_file_name)
                    result = self.api_client.wait_for_task(
                        task_id, self.api_client.query_extract_task, timeout=self.timeout
                    )
                    return {"index": index, "task_id": task_id, "result": result}
                else:
                    result = self.api_client.extract_sync(None, self.app_id, file_base64=b64_str, file_name=current_file_name)
                    return {"index": index, "result": result}
        except Exception as e:
            formatter.print_error(t('failed_to_process', name=f"base64_{index}", error=str(e)))
            return {"index": index, "error": str(e)}

    def _get_item_name(self, item: Any) -> str:
        """获取显示名称."""
        return f"base64_{item}" if isinstance(item, int) else "base64"

    def _get_section_title(self, items: List) -> str:
        """获取section标题."""
        return t('processing_files', count=len(items))

    def _display_submit(self, index: int, item: Any, total: int) -> None:
        """显示提交信息."""
        print(f"[{index}/{total}] Submitted base64_{index}")

    def _display_result(self, result: Dict[str, Any]) -> None:
        """显示结果信息."""
        if "error" in result:
            print(f"✗ Failed: base64_{result['index']} - {result['error']}")
        elif "task_id" in result:
            print(f"✓ Completed: base64_{result['index']} - Task_ID: {result['task_id']}")
        else:
            print(f"✓ Completed: base64_{result['index']}")

    def _export_if_needed(self, results: List[Dict], valid_items: List) -> None:
        """导出结果（使用index作为标识）."""
        if not self.export_path:
            return
        # Reconstruct results with base64 index for display
        display_results = []
        for r in results:
            display_results.append({
                "base64_index": r.get("index"),
                "result": r.get("result"),
                "task_id": r.get("task_id")
            })
        data = display_results[0] if len(display_results) == 1 else {"results": display_results}
        FileHandler.write_json_output(data, Path(self.export_path))
        formatter.print_success(f"{t('results_exported_to')} {self.export_path}")


# ==================== Helper Functions ====================

def _sort_and_clean_results(results):
    """
    对结果按index排序并移除index字段。

    Args:
        results: 结果列表，每个结果包含'index'字段

    Returns:
        排序并清理后的结果列表
    """
    results.sort(key=lambda x: x["index"])
    for result in results:
        result.pop("index", None)
    return results


def _process_items_concurrently(items, process_func, concurrency, display_submit_func, display_result_func, t):
    """
    并发处理多个项目，支持键盘中断。

    Args:
        items: 要处理的项目列表
        process_func: 处理函数，签名为 func(item, index, total) -> dict
        concurrency: 并发数
        display_submit_func: 显示提交信息的函数，签名为 func(index, item, total) -> str
        display_result_func: 显示完成信息的函数，签名为 func(result) -> str
        t: 国际化函数

    Returns:
        处理结果列表
    """
    import concurrent.futures
    results = []

    print(f"Processing {len(items)} items with {concurrency} workers (batch mode)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all tasks and show submission info
        future_to_item = {}
        for i, item in enumerate(items, 1):
            future = executor.submit(process_func, item, i, len(items))
            future_to_item[future] = item
            # Show task submission
            display_submit_func(i, item, len(items))

        # Show waiting message
        print(t('waiting_for_results'))

        # Collect results as they complete
        try:
            for future in concurrent.futures.as_completed(future_to_item):
                result = future.result()
                if "error" not in result:
                    results.append(result)
                    display_result_func(result)
                else:
                    display_result_func(result)
        except KeyboardInterrupt:
            print(t('interrupted'))
            # Cancel all pending tasks
            cancelled = 0
            for future in future_to_item:
                if future.cancel():
                    cancelled += 1
            if cancelled > 0:
                print(t('cancelled_pending_tasks', count=cancelled))
            # Shutdown executor immediately
            executor.shutdown(wait=False)
            raise

    return results


def _process_local_files(
    path_str: str,
    async_mode: bool,
    export_path: Optional[str],
    timeout: int,
    mode: str,
    app_id: Optional[str] = None,
    concurrency: int = 1
) -> None:
    """
    Process local files (supports batch processing).

    Args:
        path_str: File/folder path
        async_mode: Whether to process asynchronously
        export_path: Export path
        timeout: Timeout
        mode:: Mode (parse or extract)
        app_id: Application ID (required for extract mode)
        concurrency: Number of concurrent tasks (only effective for batch processing)
    """
    processor = LocalFileProcessor(mode, app_id, async_mode, export_path, timeout, concurrency)
    processor.run([path_str])


def _is_valid_url(url: str) -> bool:
    """
    Validate if URL format is valid and safe.

    Args:
        url: URL string

    Returns:
        Whether it is a valid URL
    """
    # 只允许 http:// 和 https://
    if not url.startswith(("http://", "https://")):
        return False

    # 拒绝危险的协议
    dangerous_schemes = ("javascript:", "file:", "data:", "vbscript:", "mailto:")
    lower_url = url.lower()
    for scheme in dangerous_schemes:
        if lower_url.startswith(scheme):
            return False

    # 拒绝嵌入凭据的URL (user:password@host)
    if "@" in url and "://" in url:
        # 检查 @ 是否在 path 中而非 authority 中
        scheme_end = url.index("://") + 3
        authority_end = url.find("/", scheme_end)
        if authority_end == -1:
            authority_end = len(url)
        authority = url[scheme_end:authority_end]
        if "@" in authority:
            return False

    return True


def _process_url_file(
    url: str,
    async_mode: bool,
    export_path: Optional[str],
    timeout: int,
    mode: str,
    app_id: Optional[str] = None,
    concurrency: int = 1
) -> None:
    """
    Process URL file or URL list file.

    Args:
        url: File URL or file path containing URL list
        async_mode: Whether to process asynchronously
        export_path: Export path
        timeout: Timeout
        mode: Mode (parse or extract)
        app_id: Application ID (required for extract mode)
        concurrency: Number of concurrent tasks (only effective for batch processing)
    """
    # Determine if url parameter is a file path or a single URL
    input_path = Path(url)
    is_file_path = input_path.exists() and input_path.is_file()
    source_file = None

    if is_file_path:
        # Read URL list from file
        try:
            urls = FileHandler.read_url_list_file(input_path)
        except Exception as e:
            print_error_and_exit(classify_exception(e, "read URL list file"))

        if not urls:
            error = CLIError(
                message=f"No valid URLs found in file: {input_path}",
                error_type=ERROR_TYPE_RESOURCE,
                exit_code=EXIT_RESOURCE_NOT_FOUND,
                fix="Check the file contains valid URLs (one per line, starting with http:// or https://)",
                retryable=False,
                details={"file": str(input_path)}
            )
            print_error_and_exit(error)

        source_file = str(input_path)
    else:
        # Single URL - validate URL format
        if not _is_valid_url(url):
            error = CLIError(
                message=f"Invalid URL format: {url}. URL must start with http:// or https://",
                error_type=ERROR_TYPE_PARAM,
                exit_code=EXIT_RESOURCE_NOT_FOUND,
                fix="Provide a valid URL starting with http:// or https://",
                retryable=False,
                details={"url": url}
            )
            print_error_and_exit(error)

        urls = [url]

    # Use UrlProcessor to handle the URLs
    processor = UrlProcessor(mode, app_id, async_mode, export_path, timeout, concurrency, source_file=source_file)
    processor.run(urls)


def _process_base64_files(
    base64_strings: list,
    app_id: str,
    file_name: str,
    async_mode: bool,
    export_path: Optional[str],
    timeout: int,
    mode: str,
    concurrency: int = 1
) -> None:
    """
    Process base64 encoded files (supports batch processing).

    Args:
        base64_strings: List of base64 encoded strings
        app_id: Application ID
        file_name: Base file name
        async_mode: Whether to process asynchronously
        export_path: Export path
        timeout: Timeout
        mode: Mode (parse or extract)
        concurrency: Number of concurrent tasks (only effective for batch processing)
    """
    processor = Base64Processor(mode, app_id, async_mode, export_path, timeout, concurrency, file_name=file_name)
    processor.run(base64_strings)


if __name__ == "__main__":
    cli()
