# ADP CLI 开发者指南

## 目录

1. [项目结构](#项目结构)
2. [开发环境设置](#开发环境设置)
3. [核心组件](#核心组件)
4. [测试](#测试)
5. [代码规范](#代码规范)
6. [发布流程](#发布流程)

## 项目结构

```
cli-anything/
├── src/cli_anything/
│   ├── __init__.py
│   ├── cli.py              # 主 CLI 入口
│   └── adp/
│       ├── __init__.py
│       ├── config.py       # 配置管理
│       ├── api_client.py   # API 客户端
│       ├── file_handler.py  # 文件处理
│       ├── output_formatter.py  # 输出格式化
│       └── qps_limiter.py  # QPS 限制
├── tests/
│   ├── test_config.py
│   ├── test_file_handler.py
│   └── test_qps_limiter.py
├── docs/
├── setup.py
├── pyproject.toml
└── requirements.txt
```

## 开发环境设置

### 1. 克隆仓库

```bash
git clone <repository-url>
cd adp-aiem/cli-anything
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -e ".[dev]"
```

### 4. 验证安装

```bash
adp --help
```

## 核心组件

### ConfigManager

负责配置管理，包括 API Key 的加密存储。

```python
from cli_anything.adp import ConfigManager

config = ConfigManager()

# 设置 API Key
config.set_api_key("your-api-key")

# 获取 API Key
api_key = config.get_api_key()

# 获取脱敏的 API Key
masked_key = config.get_api_key_masked()
```

### APIClient

处理所有与后端的通信。

```python
from cli_anything.adp import ConfigManager, APIClient

config = ConfigManager()
api_client = APIClient(config)

# 同步解析
result = api_client.parse_sync(file_url)

# 异步解析
task_id = api_client.parse_async(file_url)

# 查询任务
task_result = api_client.query_parse_task(task_id)

# 同步抽取
result = api_client.extract_sync(file_url, app_id)

# 异步抽取
task_id = api_client.extract_async(file_url, app_id)

# 查询抽取任务
task_result = api_client.query_extract_task(task_id)
```

### FileHandler

文件处理工具，支持文件验证、批量处理等。

```python
from cli_anything.adp import FileHandler
from pathlib import Path

# 验证文件
is_valid, error = FileHandler.validate_file(Path("document.pdf"))

# 获取文件列表
files = FileHandler.get_files_from_path(Path("./documents/"))

# 验证多个文件
valid_files, invalid_files = FileHandler.validate_files(files)

# 写入 JSON 输出
FileHandler.write_json_output(data, Path("output.json"))
```

### OutputFormatter

输出格式化工具，支持控制台和 JSON 输出。

```python
from cli_anything.adp import OutputFormatter

formatter = OutputFormatter()

# 打印消息
formatter.print("Hello, World!")
formatter.print_success("Operation successful")
formatter.print_error("Operation failed")
formatter.print_warning("Warning message")
formatter.print_info("Info message")

# 打印 JSON
formatter.print_json({"key": "value"})

# 打印表格
formatter.print_table(
    ["Name", "Age"],
    [["Alice", "25"], ["Bob", "30"]]
)

# 打印面板
formatter.print_panel("Content", "Title")
```

### QPSLimiter

QPS 限制器，控制 API 请求速率。

```python
from cli_anything.adp import QPSLimiter

limiter = QPSLimiter()

# 获取当前 QPS 限制
qps = limiter.get_current_qps()

# 获取请求许可（会自动处理速率限制）
limiter.acquire()

# 设置用户类型
limiter.set_paid_user(True)
```

## 测试

### 运行所有测试

```bash
pytest tests/
```

### 运行特定测试文件

```bash
pytest tests/test_config.py
```

### 运行特定测试用例

```bash
pytest tests/test_config.py::test_set_and_get_api_key
```

### 生成覆盖率报告

```bash
pytest tests/ --cov=cli_anything --cov-report=html
```

覆盖率报告会生成在 `htmlcov/` 目录。

### 测试结构

```python
import pytest
from cli_anything.adp.config import ConfigManager

@pytest.fixture
def temp_config_dir(tmp_path):
    """创建临时配置目录。"""
    # 设置代码...
    yield config_dir
    # 清理代码...

def test_some_function(temp_config_dir):
    """测试函数。"""
    # 测试代码...
    assert result == expected
```

## 代码规范

### Python 版本

支持 Python 3.8+

### 代码格式化

使用 Black 进行代码格式化：

```bash
black src/ tests/
```

### Import 排序

使用 isort 进行 import 排序：

```bash
isort src/ tests/
```

### 类型检查

使用 mypy 进行类型检查：

```bash
mypy src/
```

### 代码风格

- 遵循 PEP 8 规范
- 使用类型注解
- 编写文档字符串
- 保持函数简洁（单一职责）

## 发布流程

### 1. 更新版本号

在 `setup.py` 中更新版本号：

```python
version="1.0.1",  # 递增版本号
```

### 2. 更新 CHANGELOG.md

记录变更内容。

### 3. 运行测试

```bash
pytest tests/
```

### 4. 构建包

```bash
python -m build
```

### 5. 发布到 PyPI

```bash
twine upload dist/*
```

### 6. 创建 Git tag

```bash
git tag v1.0.1
git push origin v1.0.1
```

## 添加新命令

### 1. 在 `cli.py` 中添加命令

```python
@cli.command()
@click.argument('name')
@click.option('--option', help='Some option')
def new_command(name, option):
    """新命令的描述。"""
    # 实现代码...
```

### 2. 添加测试

在 `tests/` 目录中创建对应的测试文件。

### 3. 更新文档

在 `docs/` 目录中更新用户指南和开发者指南。

## 扩展功能

### 添加新的文件类型支持

在 `FileHandler.SUPPORTED_EXTENSIONS` 中添加新的扩展名：

```python
SUPPORTED_EXTENSIONS = {
    # 现有扩展名...
    ".newtype",  # 新的文件类型
}
```

### 添加新的 API 端点

在 `APIClient` 类中添加新的方法：

```python
def new_api_call(self, param: str) -> Dict[str, Any]:
    """
    新的 API 调用。

    Args:
        param: 参数说明

    Returns:
        返回值说明
    """
    data = {"param": param}
    return self._request("POST", "/v1/new/endpoint", data)
```

## 最佳实践

1. **错误处理**：始终捕获并处理异常
2. **类型注解**：使用类型注解提高代码可读性
3. **文档字符串**：为所有公共函数编写文档字符串
4. **测试覆盖**：保持高测试覆盖率
5. **代码审查**：所有变更都应经过代码审查

## 调试

### 启用详细日志

```bash
adp --verbose command
```

### 使用 pdb 调试

在代码中添加断点：

```python
import pdb; pdb.set_trace()
```

### 使用 print 语句（临时）

```python
print(f"Debug: {variable}")
```

## 贡献

1. Fork 仓库
2. 创建功能分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License
