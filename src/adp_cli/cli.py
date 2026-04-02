"""Main CLI entry point for ADP."""

import sys
import functools
from pathlib import Path
from typing import Optional

import click
from click.core import F

from adp_cli.adp import (
    ConfigManager,
    APIClient,
    FileHandler,
    OutputFormatter,
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


def check_config(func):
    """Decorator: Check if configuration is complete."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config_manager = ConfigManager()
        if not config_manager.is_configured():
            formatter.print_error(t('error_not_configured'))
            sys.exit(1)
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
        formatter.print_error(t('error_api_key_or_url_required'))
        sys.exit(1)

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

    if formatter.json_mode:
        formatter.print_json(summary)
    else:
        formatter.print_config_summary(summary)

get.help_key = 'config_get_title'


@config.command(help=t('config_clear_title'))
def clear():
    """
    Clear local configuration.
    """
    config_manager = ConfigManager()
    if click.confirm(t('confirm_clear_config')):
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
@click.option('--timeout', type=int, default=300, help="__option_timeout__")
@click.option('--concurrency', type=int, default=1, help="__option_concurrency__")
@check_config
def local(path, app_id, async_mode, export, timeout, concurrency):
    """
    Parse local files or folders.
    """
    try:
        _process_local_files(path, async_mode, export, timeout, mode="parse", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

local.help_key = 'parse_local_title'


@parse.command(help="__parse_url_title__")
@click.argument('url')
@click.option('--app-id', required=True, help="__option_app_id_parse__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=int, default=300, help="__option_timeout__")
@click.option('--concurrency', type=int, default=1, help="__option_concurrency__")
@check_config
def url(url, app_id, async_mode, export, timeout, concurrency):
    """
    Parse URL files or URL list files.
    """
    try:
        _process_url_file(url, async_mode, export, timeout, mode="parse", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

url.help_key = 'parse_url_title'


@parse.command('base64', help="__parse_base64_title__")
@click.argument('file_base64', nargs=-1, required=True)
@click.option('--app-id', required=True, help="__option_app_id_parse__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=int, default=300, help="__option_timeout__")
@click.option('--file-name', default="document", help="__option_file_name__")
@click.option('--concurrency', type=int, default=1, help="__option_concurrency__")
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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

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
@click.option('--timeout', type=int, default=300, help="__option_timeout__")
@click.option('--concurrency', type=int, default=1, help="__option_concurrency__")
@check_config
def local(path, app_id, async_mode, export, timeout, concurrency):
    """
    Extract local files or folders.
    """
    try:
        _process_local_files(path, async_mode, export, timeout, mode="extract", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

local.help_key = 'extract_local_title'


@extract.command(help="__extract_url_title__")
@click.argument('url')
@click.option('--app-id', required=True, help="__option_app_id_extract__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=int, default=300, help="__option_timeout__")
@click.option('--concurrency', type=int, default=1, help="__option_concurrency__")
@check_config
def url(url, app_id, async_mode, export, timeout, concurrency):
    """
    Extract URL files or URL list files.
    """
    try:
        _process_url_file(url, async_mode, export, timeout, mode="extract", app_id=app_id, concurrency=concurrency)
    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

url.help_key = 'extract_url_title'


@extract.command('base64', help="__extract_base64_title__")
@click.argument('file_base64', nargs=-1, required=True)
@click.option('--app-id', required=True, help="__option_app_id_extract__")
@click.option('--async', 'async_mode', is_flag=True, help="__option_async__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=int, default=300, help="__option_timeout__")
@click.option('--file-name', default="document", help="__option_file_name__")
@click.option('--concurrency', type=int, default=1, help="__option_concurrency__")
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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

extract_base64.help_key = 'extract_base64_title'


@extract.command('query', help="__extract_query_title__")
@click.argument('task-id')
@click.option('--watch', is_flag=True, help="__option_watch__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=int, default=300, help="__option_watch_timeout__")
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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

extract_query.help_key = 'extract_query_title'


# ==================== Parse Query Command ====================

@parse.command('query', help="__parse_query_title__")
@click.argument('task-id')
@click.option('--watch', is_flag=True, help="__option_watch__")
@click.option('--export', type=click.Path(), help="__option_export__")
@click.option('--timeout', type=int, default=300, help="__option_watch_timeout__")
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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

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
@check_config
def list_apps(app_label):
    """
    List all available application IDs and their descriptions.
    """
    try:
        config_manager = ConfigManager()
        api_client = APIClient(config_manager)

        apps = api_client.list_apps()

        # Filter by app_label if provided (fuzzy matching)
        if app_label:
            filtered_apps = []
            for app in apps:
                app_labels = app.get("app_label", [])
                if app_labels:
                    # Check if app_label input is contained in any of the app's labels
                    label_str = ", ".join(app_labels) if isinstance(app_labels, list) else str(app_labels)
                    if app_label in label_str:
                        filtered_apps.append(app)
            apps = filtered_apps

        if formatter.json_mode:
            formatter.print_json({"apps": apps})
        elif apps:
            table_data = []
            for app in apps:
                app_label_value = app.get("app_label", "")
                # Convert app_label to string if it's a list
                if isinstance(app_label_value, type([])):
                    app_label_value = ", ".join(app_label_value)
                table_data.append([
                    app.get("app_id", ""),
                    app.get("app_name", ""),
                    app_label_value,
                ])
            formatter.print_table(
                ["App ID", "App Name", "App Label"],
                table_data,
                title=t('available_applications')
            )
        else:
            formatter.print_info(f"applist:{apps} {t('no_applications_found')}")

    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

list_apps.help_key = 'app_id_list_title'


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
            formatter.print_error(t('error_read_json_file', error=str(e)))
            sys.exit(1)
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
        formatter.print_error(t('error_invalid_json_format', error=str(e)))
        sys.exit(1)


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
        formatter.print_error(t('error_invalid_json_format', error=f"Invalid boolean value: {value}"))
        sys.exit(1)


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
                formatter.print_error(t('error_invalid_json_format', error=f"app-label must be a list: {value}"))
                sys.exit(1)
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
        formatter.print_error(t('error_invalid_json_format', error=f"app_name must be 50 characters or less (got {len(app_name)})"))
        sys.exit(1)

    # 验证 app_label 最多 5 个
    if app_label and len(app_label) > 5:
        formatter.print_error(t('error_invalid_json_format', error=f"app_label must have 5 or fewer labels (got {len(app_label)})"))
        sys.exit(1)

    # 验证 long_doc_config 仅在 enable_long_doc=true 时生效
    if long_doc_config is not None and not enable_long_doc:
        formatter.print_error(t('error_invalid_json_format', error="long_doc_config is only valid when enable_long_doc=true"))
        sys.exit(1)


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
@click.option('--parse-mode', required=True, help="__custom_app_create_parse_mode__")
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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

create.help_key = 'custom_app_create_title'


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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

get_config.help_key = 'custom_app_get_config_title'


@custom_app.command(help="__custom_app_list_versions_title__")
@click.option('--api-key', help="__custom_app_list_versions_api_key__")
@click.option('--app-id', required=True, help="__custom_app_list_versions_app_id__")
@check_config
def list_versions(api_key, app_id):
    """
    List configuration versions of a custom app.
    """
    try:
        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        versions = api_client.list_custom_app_versions(app_id)

        if formatter.json_mode:
            formatter.print_json({"versions": versions})
        elif versions:
            table_data = []
            for version in versions:
                # 提取版本信息（根据实际返回结构调整）
                version_str = str(version.get("version", version.get("config_version", "N/A")))
                table_data.append([version_str])
            formatter.print_table(
                ["Version"],
                table_data,
                title=t('available_versions')
            )
        else:
            formatter.print_info(t('no_versions_found'))

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

list_versions.help_key = 'custom_app_list_versions_title'


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

        formatter.print_success(t('app_deleted'))
        formatter.print_json(result)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

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

        formatter.print_success(t('version_deleted'))
        formatter.print_json(result)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

delete_version.help_key = 'custom_app_delete_version_title'


@custom_app.command(help="__custom_app_ai_generate_title__")
@click.option('--api-key', help="__custom_app_ai_generate_api_key__")
@click.option('--app-id', required=True, help="__custom_app_ai_generate_app_id__")
@click.option('--file-url', help="__custom_app_ai_generate_file_url__")
@click.option('--file-local', help="__custom_app_ai_generate_file_local__")
@check_config
def ai_generate(api_key, app_id, file_url, file_local):
    """
    AI generate extraction field recommendations.
    """
    try:
        if not file_url and not file_local:
            formatter.print_error(t('error_file_url_or_local_required'))
            sys.exit(1)

        if api_key:
            config_manager = ConfigManager()
            original_key = config_manager.get_api_key()
            config_manager.set_api_key(api_key)
        else:
            config_manager = ConfigManager()

        api_client = APIClient(config_manager)

        result = api_client.ai_generate_fields(app_id, file_url, file_local)

        formatter.print_section(t('custom_app_ai_generate_title'))
        formatter.print_json(result)

        if api_key:
            if original_key:
                config_manager.set_api_key(original_key)

    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

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
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)


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
    import concurrent.futures

    path = Path(path_str)
    config_manager = ConfigManager()
    api_client = APIClient(config_manager)

    # Validate and adjust concurrency based on payment status
    try:
        concurrency = _validate_concurrency(api_client, concurrency)
    except ValueError as e:
        formatter.print_error(str(e))
        sys.exit(1)

    # Get file list
    files = FileHandler.get_files_from_path(path)

    if not files:
        formatter.print_error(f"{t('no_supported_files')} {path}")
        return

    # Validate files
    valid_files, invalid_files = FileHandler.validate_files(files)

    if invalid_files:
        formatter.print_warning(t('skipped_invalid_files', count=len(invalid_files)))
        for file_path, error in invalid_files:
            formatter.print(f"  - {file_path}: {error}", style="dim")

    if not valid_files:
        formatter.print_error(t('no_valid_files'))
        return

    formatter.print_section(t('processing_files', count=len(valid_files)))

    def process_file(file_path, index, total):
        """Process a single file."""
        try:
            if mode == "parse":
                if async_mode:
                    task_id = api_client.parse_async(None, app_id, file_path)
                    # Query task and wait for completion
                    result = api_client.wait_for_task(
                        task_id,
                        api_client.query_parse_task,
                        timeout=timeout
                    )
                    return {"file": str(file_path), "task_id": task_id, "result": result, "index": index}
                else:
                    result = api_client.parse_sync(None, app_id, file_path)
                    return {"file": str(file_path), "result": result, "index": index}
            elif mode == "extract":
                if async_mode:
                    task_id = api_client.extract_async(None, app_id, file_path)
                    # Query task and wait for completion
                    result = api_client.wait_for_task(
                        task_id,
                        api_client.query_extract_task,
                        timeout=timeout
                    )
                    return {"file": str(file_path), "task_id": task_id, "result": result, "index": index}
                else:
                    result = api_client.extract_sync(None, app_id, file_path)
                    return {"file": str(file_path), "result": result, "index": index}
        except Exception as e:
            formatter.print_error(t('failed_to_process', name=file_path.name, error=str(e)))
            return {"file": str(file_path), "error": str(e), "index": index}

    # Display functions for concurrent processing
    def display_file_submit(index, file_path, total):
        print(f"[{index}/{total}] Submitted: {file_path.name}")

    def display_file_result(result):
        if "error" in result:
            print(f"✗ Failed: {Path(result['file']).name} - {result['error']}")
        else:
            file_path = Path(result["file"])
            if "task_id" in result:
                print(f"✓ Completed: {file_path.name} - Task_ID: {result['task_id']}")
            else:
                print(f"✓ Completed: {file_path.name}")

    # Check if batch processing (more than 1 file)
    is_batch = len(valid_files) > 1

    if is_batch and concurrency > 1:
        # Concurrent processing for batch
        results = _process_items_concurrently(
            valid_files, process_file, concurrency,
            display_file_submit, display_file_result, t
        )
    else:
        # Sequential processing (single file or sync mode or concurrency=1)
        results = []
        print(f"valid_files:{len(valid_files)}")
        for i, file_path in enumerate(valid_files, 1):
            result = process_file(file_path, i, len(valid_files))
            if "error" not in result:
                results.append(result)
                # Show progress for each file
                if "task_id" in result:
                    formatter.print_progress(i, len(valid_files), f"Processing: {file_path.name} - Task_ID: {result['task_id']} - Completed")
                elif not async_mode:
                    formatter.print_progress(i, len(valid_files), f"Processing: {file_path.name}")

    # Sort results by index and remove index
    results = _sort_and_clean_results(results)

    # Output results
    OutputFormatter.print_results(results, valid_files, mode, formatter, t)

    if export_path:
        data = results[0]["result"] if len(results) == 1 else {"results": results}
        FileHandler.write_json_output(data, Path(export_path))
        formatter.print_success(f"{t('results_exported_to')} {export_path}")


def _is_valid_url(url: str) -> bool:
    """
    Validate if URL format is valid.

    Args:
        url: URL string

    Returns:
        Whether it is a valid URL
    """
    return url.startswith(("http://", "https://"))


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
    config_manager = ConfigManager()
    api_client = APIClient(config_manager)

    # Validate and adjust concurrency based on payment status
    try:
        concurrency = _validate_concurrency(api_client, concurrency)
    except ValueError as e:
        formatter.print_error(str(e))
        sys.exit(1)

    # Determine if url parameter is a file path or a single URL
    input_path = Path(url)
    is_file_path = input_path.exists() and input_path.is_file()

    if is_file_path:
        # Read URL list from file
        try:
            urls = FileHandler.read_url_list_file(input_path)
        except Exception as e:
            formatter.print_error(f"{t('error')} {str(e)}")
            raise

        if not urls:
            formatter.print_error(f"{t('no_valid_urls')} {input_path}")
            return

        formatter.print_section(t('processing_urls', count=len(urls), file=input_path))
    else:
        # Single URL - validate URL format
        if not _is_valid_url(url):
            formatter.print_error(t('invalid_url_format', url=url))
            return

        urls = [url]
        formatter.print_section(t('processing_url', count=1, url=url))

    def process_url(current_url, index, total):
        """Process a single URL."""
        try:
            if mode == "parse":
                if async_mode:
                    task_id = api_client.parse_async(current_url, app_id)
                    # Query task and wait for completion
                    result = api_client.wait_for_task(
                        task_id,
                        api_client.query_parse_task,
                        timeout=timeout
                    )
                    return {"url": current_url, "task_id": task_id, "result": result, "index": index}
                else:
                    result = api_client.parse_sync(current_url, app_id)
                    return {"url": current_url, "result": result, "index": index}
            elif mode == "extract":
                if async_mode:
                    task_id = api_client.extract_async(current_url, app_id)
                    # Query task and wait for completion
                    result = api_client.wait_for_task(
                        task_id,
                        api_client.query_extract_task,
                        timeout=timeout
                    )
                    return {"url": current_url, "task_id": task_id, "result": result, "index": index}
                else:
                    result = api_client.extract_sync(current_url, app_id)
                    return {"url": current_url, "result": result, "index": index}
        except Exception as e:
            formatter.print_error(t('failed_to_process_url', url=current_url, error=str(e)))
            return {"url": current_url, "error": str(e), "index": index}

    # Display functions for concurrent processing
    def display_url_submit(index, url, total):
        url_display = url[:80] + ('...' if len(url) > 80 else '')
        print(f"[{index}/{total}] Submitted: {url_display}")

    def display_url_result(result):
        url_display = result['url'][:60] + ('...' if len(result['url']) > 60 else '')
        if "error" in result:
            print(f"✗ Failed: {url_display} - {result['error']}")
        elif "task_id" in result:
            print(f"✓ Completed: {url_display} - Task_ID: {result['task_id']}")
        else:
            print(f"✓ Completed: {url_display}")

    # Check if batch processing (more than 1 URL)
    is_batch = len(urls) > 1

    if is_batch and concurrency > 1:
        # Concurrent processing for batch mode
        results = _process_items_concurrently(
            urls, process_url, concurrency,
            display_url_submit, display_url_result, t
        )
    else:
        # Sequential processing (single URL or sync mode or concurrency=1)
        results = []
        for i, current_url in enumerate(urls, 1):
            result = process_url(current_url, i, len(urls))
            if "error" not in result:
                results.append(result)
                # Show progress for each URL
                if "task_id" in result:
                    formatter.print_progress(i, len(urls), f"Processing: {current_url} - Task_ID: {result['task_id']} - Completed")
                elif not async_mode:
                    formatter.print_progress(i, len(urls), f"Processing: {current_url}")

    # Sort results by index and remove index
    results = _sort_and_clean_results(results)

    # Output results
    OutputFormatter.print_results(results, urls, mode, formatter, t)

    if export_path:
        data = results[0]["result"] if len(results) == 1 else {"results": results}
        FileHandler.write_json_output(data, Path(export_path))
        formatter.print_success(f"{t('results_exported_to')} {export_path}")


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
    import concurrent.futures

    config_manager = ConfigManager()
    api_client = APIClient(config_manager)

    # Validate and adjust concurrency based on payment status
    try:
        concurrency = _validate_concurrency(api_client, concurrency)
    except ValueError as e:
        formatter.print_error(str(e))
        sys.exit(1)

    # Check if batch processing (multiple base64 strings)
    is_batch = len(base64_strings) > 1

    formatter.print_section(t('processing_files', count=len(base64_strings)))

    def process_base64(b64_str, index, total):
        """Process a single base64 string."""
        try:
            current_file_name = file_name if len(base64_strings) == 1 else f"{file_name}_{index}"
            if mode == "parse":
                if async_mode:
                    task_id = api_client.parse_async(None, app_id, file_base64=b64_str, file_name=current_file_name)
                    # Query task and wait for completion
                    result = api_client.wait_for_task(
                        task_id,
                        api_client.query_parse_task,
                        timeout=timeout
                    )
                    return {"index": index, "task_id": task_id, "result": result}
                else:
                    result = api_client.parse_sync(None, app_id, file_base64=b64_str, file_name=current_file_name)
                    return {"index": index, "result": result}
            elif mode == "extract":
                if async_mode:
                    task_id = api_client.extract_async(None, app_id, file_base64=b64_str, file_name=current_file_name)
                    # Query task and wait for completion
                    result = api_client.wait_for_task(
                        task_id,
                        api_client.query_extract_task,
                        timeout=timeout
                    )
                    return {"index": index, "task_id": task_id, "result": result}
                else:
                    result = api_client.extract_sync(None, app_id, file_base64=b64_str, file_name=current_file_name)
                    return {"index": index, "result": result}
        except Exception as e:
            formatter.print_error(t('failed_to_process', name=f"base64_{index}", error=str(e)))
            return {"index": index, "error": str(e)}

    # Display functions for concurrent processing
    def display_submit(index, b64_str, total):
        print(f"[{index}/{total}] Submitted base64_{index}")

    def display_result(result):
        if "error" in result:
            print(f"✗ Failed: base64_{result['index']} - {result['error']}")
        else:
            if "task_id" in result:
                print(f"✓ Completed: base64_{result['index']} - Task_ID: {result['task_id']}")
            else:
                print(f"✓ Completed: base64_{result['index']}")

    # Check if batch processing (more than 1 base64 string)
    is_batch = len(base64_strings) > 1

    if is_batch and concurrency > 1:
        # Concurrent processing for batch
        results = _process_items_concurrently(
            base64_strings, process_base64, concurrency,
            display_submit, display_result, t
        )
    else:
        # Sequential processing (single base64 or sync mode or concurrency=1)
        results = []
        for i, b64_str in enumerate(base64_strings, 1):
            result = process_base64(b64_str, i, len(base64_strings))
            if "error" not in result:
                results.append(result)
                # Show progress for each base64 string
                if "task_id" in result:
                    formatter.print_progress(i, len(base64_strings), f"Processing: base64_{i} - Task_ID: {result['task_id']} - Completed")
                elif not async_mode:
                    formatter.print_progress(i, len(base64_strings), f"Processing: base64_{i}")

    # Sort results by index and remove index
    results = _sort_and_clean_results(results)

    # Output results
    OutputFormatter.print_results(results, base64_strings, mode, formatter, t)

    if export_path:
        data = results[0]["result"] if len(results) == 1 else {"results": results}
        FileHandler.write_json_output(data, Path(export_path))
        formatter.print_success(f"{t('results_exported_to')} {export_path}")


if __name__ == "__main__":
    cli()
