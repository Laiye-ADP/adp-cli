# ADP CLI Agent 优化方案

本文档记录 ADP CLI 为支持 Agent（AI Agent）使用场景所做的所有优化。

---

## 1. 退出码标准化

### 问题
原代码中所有错误都使用 `sys.exit(1)`，无法区分错误类型，Agent 难以针对性处理。

### 解决方案
定义专用退出码常量：

```python
# Exit codes for CLI
EXIT_SUCCESS = 0              # 成功
EXIT_GENERAL_ERROR = 1        # 一般错误（API失败、网络错误、运行时异常）
EXIT_PARAMETER_ERROR = 2     # 参数错误、缺少必需参数、JSON格式错误
EXIT_RESOURCE_NOT_FOUND = 3  # 资源不存在（文件、URL等）
EXIT_PERMISSION_DENIED = 4   # 权限不足
EXIT_CONFLICT = 5            # 冲突或已存在
```

### 退出码映射表

| 退出码 | 名称 | 含义 | Agent 应对 |
|--------|------|------|------------|
| 0 | `EXIT_SUCCESS` | 成功 | 继续执行 |
| 1 | `EXIT_GENERAL_ERROR` | 一般错误 | 读取 stderr 诊断 |
| 2 | `EXIT_PARAMETER_ERROR` | 参数错误 | 修正参数后重试 |
| 3 | `EXIT_RESOURCE_NOT_FOUND` | 资源不存在 | 跳过或创建 |
| 4 | `EXIT_PERMISSION_DENIED` | 权限不足 | 提示用户授权 |
| 5 | `EXIT_CONFLICT` | 冲突/已存在 | 跳过或更新 |

### 使用场景

| 退出码 | 使用场景 |
|--------|----------|
| `EXIT_PARAMETER_ERROR (2)` | API Key 未配置、缺少必要参数、JSON 格式错误、参数验证失败 |
| `EXIT_GENERAL_ERROR (1)` | API 调用异常、文件处理异常、网络错误、路径遍历检测 |
| `EXIT_RESOURCE_NOT_FOUND (3)` | 文件不存在、无效 URL 格式、无有效文件、无有效 URL |

---

## 2. 非 TTY 环境输出优化

### 问题
- 非 TTY 环境（脚本/CI/Agent）默认输出 Rich 彩色格式，机器难以解析
- Agent 需要额外加 `--json` 才能获得机器可读输出

### 解决方案
自动检测 TTY，非 TTY 环境输出纯文本：

```python
def print_success(self, message: str) -> None:
    if self.is_tty:
        self.print(f"✓ {message}", style="green")
    else:
        self.print(message)  # 无颜色纯文本
```

### 行为对比

| 环境 | `print_success` 输出 | `print_json` 输出 |
|------|---------------------|------------------|
| TTY | `✓ Success` (绿色) | 语法高亮 JSON |
| 非 TTY | `Success` (纯文本) | 纯 JSON |

### Agent 影响
- **不需要**加 `--json` 选项
- 非 TTY 环境自动获得纯文本/JSON 输出

---

## 3. 资源不存在时正确退出码

### 问题
部分场景下命令静默失败（return），退出码为 0，Agent 误以为成功。

### 修复场景

| 位置 | 修复前 | 修复后 |
|------|--------|--------|
| 无有效文件 | `return` | `sys.exit(EXIT_RESOURCE_NOT_FOUND)` |
| 无有效 URL | `return` | `sys.exit(EXIT_RESOURCE_NOT_FOUND)` |
| 无效 URL 格式 | `return` | `sys.exit(EXIT_RESOURCE_NOT_FOUND)` |

---

## 4. config clear 强制选项

### 问题
`click.confirm()` 在非 TTY 环境下返回 `False`，导致 `adp config clear` 无法执行。

### 解决方案
添加 `--force` / `-y` 选项：

```python
@config.command(help=t('config_clear_title'))
@click.option('--force', '-y', is_flag=True, help="__option_force_clear__")
def clear(force):
    if force or click.confirm(t('confirm_clear_config')):
        config_manager.clear()
```

### ⚠️ Agent 必须使用 --force

**原因**：
- Agent 环境通常无 TTY（无交互式终端）
- `click.confirm()` 在非 TTY 下返回 `False`
- 不加 `--force` 会静默退出，什么都不做

### Agent 用法
```bash
# ❌ 错误 - Agent 环境无法执行（静默退出）
adp config clear

# ✅ 正确 - 使用 --force 强制清除
adp config clear --force

# ✅ 正确 - 使用简写 -y
adp config clear -y
```

---

## 5. URL 协议严格验证

### 问题
原代码只检查 `http://` 或 `https://` 前缀，可能存在安全隐患。

### 解决方案
拒绝危险的协议和恶意 URL：

```python
def _is_valid_url(url: str) -> bool:
    # 只允许 http:// 和 https://
    if not url.startswith(("http://", "https://")):
        return False

    # 拒绝危险的协议
    dangerous_schemes = ("javascript:", "file:", "data:", "vbscript:", "mailto:")
    for scheme in dangerous_schemes:
        if url.lower().startswith(scheme):
            return False

    # 拒绝嵌入凭据的 URL (user:password@host)
    if "@" in url and "://" in url:
        # ... 验证逻辑
```

### 拒绝的 URL 类型

| 类型 | 示例 | 原因 |
|------|------|------|
| `javascript:` | `javascript:alert(1)` | XSS 攻击 |
| `file:` | `file:///etc/passwd` | 本地文件访问 |
| `data:` | `data:text/html,<script>alert(1)</script>` | XSS 攻击 |
| 嵌入凭据 | `https://user:pass@evil.com/` | 凭据泄露 |

---

## 6. 敏感目录写入防护

### 问题
导出路径可能被滥用来写入系统敏感目录。

### 解决方案
检测并拒绝写入敏感目录：

```python
def is_path_traversal(cls, path: Path) -> bool:
    # 敏感目录列表
    sensitive_dirs = [
        "/etc", "/root", "/home",
        "/.ssh", "/.gnupg", "/.aws",
        "/.config", "/.local/share"
    ]
    # Windows 敏感目录
    if sys.platform == "win32":
        user_home = os.path.expanduser("~")
        sensitive_dirs.extend([
            os.path.join(user_home, ".ssh"),
            os.path.join(user_home, ".gnupg"),
            os.path.join(user_home, ".aws"),
        ])

    for sensitive in sensitive_dirs:
        if resolved_str.startswith(sensitive):
            return True
```

### 拒绝的路径

| 目录 | 平台 | 风险 |
|------|------|------|
| `~/.ssh/` | Linux/macOS/Windows | SSH 私钥 |
| `~/.gnupg/` | Linux/macOS/Windows | GPG 密钥 |
| `~/.aws/` | Linux/macOS/Windows | AWS 凭据 |
| `/etc` | Linux | 系统配置 |
| `/root` | Linux | root 目录 |

---

## 7. Schema 自省命令

### 问题
Agent 需要查询 CLI 的能力和参数定义，但缺乏标准化方式。

### 解决方案
添加 `adp schema` 命令：

```python
@cli.command(help="__schema_description__")
@click.argument('command', required=False)
def schema(command):
    """Display command schema for Agent introspection."""
    if command:
        schema_data = _get_command_schema(command, cmd)
    else:
        schema_data = _get_full_schema()
    formatter.print_json(schema_data)
```

### 用法

```bash
# 查看完整命令树
adp schema

# 查看特定命令的参数
adp schema parse local
adp schema custom-app create
```

### 输出示例

```bash
$ adp schema parse
{
  "name": "parse",
  "help": "文档解析。",
  "type": "group",
  "options": [],
  "arguments": [],
  "subcommands": {
    "base64": { "help": "解析 base64 编码的文件内容。" },
    "local": { "help": "解析本地文件或文件夹。" },
    "query": { "help": "查询解析异步任务状态。" },
    "url": { "help": "解析 URL 文件或 URL 列表文件。" }
  }
}

$ adp schema parse local
{
  "name": "parse local",
  "help": "解析本地文件或文件夹。",
  "type": "command",
  "options": [
    { "name": "app_id", "required": true, "help": "解析的应用 ID", "flags": ["--app-id"] },
    { "name": "async_mode", "required": false, "help": "异步处理", "flags": ["--async"], "default": false },
    { "name": "export", "required": false, "help": "导出结果到 JSON 文件", "flags": ["--export"] },
    { "name": "timeout", "required": false, "help": "超时时间（秒）", "flags": ["--timeout"], "default": 300 },
    { "name": "concurrency", "required": false, "help": "并发数", "flags": ["--concurrency"], "default": 1 }
  ],
  "arguments": [ { "name": "path", "required": true, "help": "" } ],
  "subcommands": {}
}
```

---

## 8. 枚举约束

### 问题
部分参数接受自由文本，Agent 可能传入无效值。

### 解决方案
使用 Click 的 `Choice` 类型约束：

```python
# parse-mode 枚举
@click.option('--parse-mode', required=True,
              type=click.Choice(['standard', 'advance', 'agentic'], case_sensitive=False),
              help="__custom_app_create_parse_mode__")
```

### 受约束的参数

| 参数 | 有效值 | 错误提示 |
|------|--------|----------|
| `--parse-mode` | `standard`, `advance`, `agentic` | Invalid value... is not one of... |

---

## 9. 数值范围限制

### 问题
数值参数（如 timeout）没有范围限制，可能传入极端值。

### 解决方案
使用 Click 的 `IntRange` 类型约束：

```python
# timeout: 30秒 - 1小时
@click.option('--timeout', type=click.IntRange(min=30, max=3600), default=300)

# concurrency: 1 - 2
@click.option('--concurrency', type=click.IntRange(min=1, max=2), default=1)
```

### 范围约束

| 参数 | 范围 | 默认值 | 说明 |
|------|------|--------|------|
| `--timeout` | 30-3600 | 300 | 秒 |
| `--concurrency` | 1-2 | 1 | 并发数 |

---

## 10. Agent 使用最佳实践

### 推荐用法

```bash
# 单文件处理 - 直接获得 JSON 结果
adp parse local ./document.pdf --app-id YOUR_APP_ID

# 批量处理 - 通过 export 导出结果
adp parse local ./folder --app-id YOUR_APP_ID --export results.json

# 强制清除配置（Agent 必须用 --force）
adp config clear --force

# 查询 Agent 支持的命令
adp schema

# 查询特定命令的参数
adp schema extract local
```

### 错误处理模式

```bash
# Agent 错误处理示例
adp parse local ./file.pdf --app-id xxx
case $? in
    0) echo "Success" ;;
    1) echo "General error - check stderr" ;;
    2) echo "Parameter error - fix and retry" ;;
    3) echo "Resource not found - skipping" ;;
    4) echo "Permission denied" ;;
    5) echo "Resource conflict" ;;
esac
```

### 结构化错误输出

CLI 输出包含四个要素的错误信息：

```json
{
  "type": "NETWORK_ERROR",
  "code": 1,
  "message": "Connection timeout after 30 seconds",
  "fix": "Check your network connection and try again. If the issue persists, the API server may be down.",
  "retryable": true,
  "details": {"context": "parse local"}
}
```

| 字段 | 说明 | 示例 |
|------|------|------|
| `type` | 机器可读错误类型 | `NETWORK_ERROR`, `API_ERROR`, `PARAM_ERROR` |
| `code` | 退出码 | 1, 2, 3, 4, 5 |
| `message` | 人类可读错误描述 | "Connection timeout..." |
| `fix` | 修复建议 | "Check your network..." |
| `retryable` | 是否可重试 | `true` / `false` |
| `details` | 额外上下文 | `{"context": "..."}` |

#### 错误类型

| type | 说明 | retryable |
|------|------|-----------|
| `NETWORK_ERROR` | 网络连接错误 | true |
| `API_ERROR` | API 调用错误 | false |
| `AUTH_ERROR` | 认证/权限错误 | false |
| `PARAM_ERROR` | 参数错误 | false |
| `RESOURCE_ERROR` | 资源不存在 | false |
| `SYSTEM_ERROR` | 系统错误 | false |

#### TTY vs 非TTY 输出

```bash
# TTY 环境 - 人类可读
✗ Error: Connection timeout after 30 seconds
  Fix: Check your network connection and try again.
  Retryable: Yes

# 非TTY环境 - JSON格式
{
  "type": "NETWORK_ERROR",
  "code": 1,
  "message": "Connection timeout after 30 seconds",
  "fix": "Check your network connection and try again.",
  "retryable": true,
  "details": {}
}
```

### 按需查询 Schema

```bash
# Agent 在执行命令前查询参数定义
SCHEMA=$(adp schema parse local)
# 解析 SCHEMA 获取必需参数 app_id 和可选参数

# 执行命令
adp parse local ./file.pdf --app-id xxx
```

---

## 11. CLIError 类

### 问题
异常处理分散在各处，错误信息格式不统一。

### 解决方案
定义统一的 `CLIError` 类和 `classify_exception()` 函数：

```python
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
        self.message = message
        self.error_type = error_type
        self.exit_code = exit_code
        self.fix = fix or ""
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.error_type,
            "code": self.exit_code,
            "message": self.message,
            "fix": self.fix,
            "retryable": self.retryable,
            "details": self.details
        }
```

### classify_exception() 函数

自动分类异常类型：

```python
def classify_exception(e: Exception, context: str = "") -> CLIError:
    error_str = str(e).lower()

    # 网络错误
    if any(k in error_str for k in ['timeout', 'connection', 'network']):
        return CLIError(
            message=f"Network error: {e}",
            error_type=ERROR_TYPE_NETWORK,
            exit_code=EXIT_GENERAL_ERROR,
            fix="Check network connection...",
            retryable=True
        )

    # 认证错误
    if any(k in error_str for k in ['401', 'unauthorized', 'api key']):
        return CLIError(...)

    # 更多分类...
```

---

### 结构化错误输出覆盖的命令

所有以下错误场景都已更新为结构化输出：

| 错误场景 | 错误类型 | 修复建议 |
|---------|---------|---------|
| JSON 格式错误 | `PARAM_ERROR` | 检查 JSON 语法是否正确 |
| 布尔值无效 | `PARAM_ERROR` | 使用: true, false, 1, 0, yes, no |
| app-label 格式错误 | `PARAM_ERROR` | 提供 JSON 数组格式 |
| app_name 长度超限 | `PARAM_ERROR` | 缩短到 50 字符以内 |
| app_label 数量超限 | `PARAM_ERROR` | 保持 5 个或更少 |
| 缺少文件参数 | `PARAM_ERROR` | 提供 --file-url、--file-local 或 --base64 |
| schema 命令不存在 | `RESOURCE_ERROR` | 运行 `adp schema` 查看可用命令 |
| 无有效文件 | `RESOURCE_ERROR` | 检查文件路径和格式是否支持 |
| 并发数无效 | `PARAM_ERROR` | 设置 concurrency 为 1（免费）或 2（付费） |
| URL 格式无效 | `PARAM_ERROR` | 提供以 http:// 或 https:// 开头的有效 URL |
| 无有效 URL | `RESOURCE_ERROR` | 检查文件包含有效 URL（每行一个） |
| 删除应用失败 | `RESOURCE_ERROR` | 验证 app-id 是否正确 |
| 删除版本失败 | `RESOURCE_ERROR` | 验证 app-id 和 config-version 是否正确 |

---

## 12. 幂等性

### 问题
删除不存在的资源会报错，影响 Agent 重试。

### 解决方案
检测业务返回结果，区分"删除成功"和"资源不存在"：

```python
result = api_client.delete_custom_app(app_id)

if result.get("code") == "success" and result.get("data", {}).get("success"):
    formatter.print_success(t('app_deleted'))
else:
    error = CLIError(
        message=f"Failed to delete app: {error_msg}",
        error_type=ERROR_TYPE_RESOURCE,
        exit_code=EXIT_RESOURCE_NOT_FOUND,
        fix="Verify the app-id is correct...",
        retryable=False
    )
    print_error_and_exit(error)
```

### 幂等命令

| 命令 | 幂等性 |
|------|--------|
| `config clear --force` | ✅ 重复清除不报错 |
| `custom-app delete` | ✅ 不存在返回退出码 3 |
| `custom-app delete-version` | ✅ 不存在返回退出码 3 |
| `custom-app create` | ✅ API 允许同名 |

---

## 13. 文档更新

| 文件 | 更新内容 |
|------|----------|
| `docs/ADP-CLI-USER-MANUAL.md` | 添加 Exit Codes 和结构化错误输出章节 |
| `docs/ADP-CLI-USER-MANUAL-zh.md` | 添加退出码和结构化错误输出章节（中文） |
| `README.md` | 添加 Agent 使用章节 |
| `test_data/test.sh` | Agent 测试脚本 |

---

## 变更摘要

| 优化项 | 文件 | 状态 |
|--------|------|------|
| 退出码标准化 | `cli.py` | ✅ |
| 非 TTY 输出优化 | `output_formatter.py` | ✅ |
| 资源不存在退出码 | `cli.py` | ✅ |
| config clear --force | `cli.py`, `i18n.py` | ✅ |
| URL 协议验证 | `cli.py` | ✅ |
| 敏感目录防护 | `file_handler.py` | ✅ |
| Schema 自省命令 | `cli.py`, `i18n.py` | ✅ |
| parse-mode 枚举 | `cli.py` | ✅ |
| timeout 范围 | `cli.py` | ✅ |
| concurrency 范围 | `cli.py` | ✅ |
| CLIError 类 | `cli.py` | ✅ |
| classify_exception | `cli.py` | ✅ |
| 幂等性 | `cli.py` | ✅ |
| 结构化错误输出（14+场景） | `cli.py`, `output_formatter.py` | ✅ |

---

*文档版本: 1.10.0*
*最后更新: 2026-04-04*
