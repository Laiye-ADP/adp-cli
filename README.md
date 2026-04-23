# ADP CLI - AI Document Platform Command Line Tool

AI Document Platform (ADP) 命令行工具，提供完整的文档处理能力。

## 功能特性

- 文档解析 (Parse)：支持本地文件、URL 和批量处理
- 文档抽取 (Extract)：使用 AI 应用提取文档结构化信息
- **自定义抽取应用 (Custom App)**：直接通过 CLI 创建和管理自定义抽取应用
- 认证管理：基于 API Key 的安全界证，本地加密存储
- 同步/异步处理：灵活的任务执行模式
- 多格式支持：图片、PDF、Office 文档等
- QPS 限制管理：免费用户 1/s，付费用户 2/s
- **国际化支持**：自动根据系统语言显示中文或英文界面
- **并发数控制**：批量处理时支持并发任务数（免费用户最大1，付费用户最大2）

## 安装

### 从源码安装

```bash
pip install -e .
```

### 从 PyPI 安装

```bash
pip install agentic_doc_parse_and_extract
```

## 快速开始

### 1. 配置 API Key

```bash
adp config set --api-key YOUR_API_KEY
```

### 2. 查看可用应用

```bash
adp app-id list
```

### 3. 解析文档

同步解析本地文件：

```bash
adp parse local ./document.pdf
```

异步解析 URL 文件：

```bash
adp parse url https://example.com/document.pdf --async
```

### 4. 提取文档信息

同步提取本地文件：

```bash
adp extract local ./invoice.pdf --app-id APP_ID
```

异步提取并导出结果：

```bash
adp extract url https://example.com/invoice.pdf --app-id APP_ID --async --export result.json
```

### 5. 查询异步任务

```bash
adp query TASK_ID
```

### 6. 创建自定义抽取应用

**方式一：使用 JSON 字符串（推荐 PowerShell）**

```bash
adp custom-app create \
  --app-name "财务票据抽取" \
  --extract-fields '[
    {"field_name":"发票号码","field_type":"文本","field_prompt":"提取发票左上角编号"},
    {"field_name":"开票日期","field_type":"日期","field_prompt":"提取发票开具日期"},
    {"field_name":"商品明细","field_type":"表格"}
  ]' \
  --parse-mode "增强解析" \
  --enable-long-doc true \
  --long-doc-config '[
    {"doc_type":"合同","doc_desc":"多页合同"},
    {"doc_type":"标书","doc_desc":"工程类标书"}
  ]'
```

**方式二：使用 JSON 文件（推荐 Windows CMD）**

创建 `extract-fields.json` 和 `long-doc-config.json` 文件：

```bash
adp custom-app create \
  --app-name "财务票据抽取" \
  --extract-fields extract-fields.json \
  --parse-mode "增强解析" \
  --enable-long-doc true \
  --long-doc-config long-doc-config.json
```

## 命令参考

### 认证配置 (config)

```bash
adp config set --api-key <key>    # 设置/修改 API Key
adp config get                   # 查看当前配置（脱敏）
adp config clear                 # 清除本地配置
```

### 文档解析 (parse)

```bash
adp parse local <path>           # 解析本地文件/文件夹
adp parse url <url>              # 解析 URL 文件
adp parse base64 <b64>...       # 解析 base64 编码内容
adp parse local <path> --async --no-wait   # 异步提交，立即返回 task ID
adp parse local <path> --retry 3          # 失败重试 3 次
```

**parse 命令新选项**：
| 选项 | 说明 |
|------|------|
| `--async` | 异步处理，自动等待任务完成 |
| `--no-wait` | 异步提交后立即返回 task ID（需配合 --async） |
| `--retry N` | 失败任务重试 N 次（指数退避） |
| `--concurrency 2` | 并发数（付费用户最大 2） |

### 文档抽取 (extract)

```bash
adp extract local <path> --app-id <id>           # 抽取本地文件
adp extract url <url> --app-id <id>             # 抽取 URL 文件
adp extract base64 <b64>... --app-id <id>       # 抽取 base64 内容
adp extract local <path> --app-id <id> --async  # 异步抽取
adp extract local <path> --app-id <id> --no-wait --async --export tasks.json  # 批量提交
```

**extract 命令新选项**：
| 选项 | 说明 |
|------|------|
| `--async` | 异步处理，自动等待任务完成 |
| `--no-wait` | 异步提交后立即返回 task ID（需配合 --async） |
| `--retry N` | 失败任务重试 N 次（指数退避） |
| `--concurrency 2` | 并发数（付费用户最大 2） |

### 查询异步结果 (query)

```bash
adp parse query <task-id>              # 查询解析任务状态
adp extract query <task-id>            # 查询抽取任务状态
adp parse query <task-id> --watch      # 监视直到完成
adp parse query <id1> <id2> ...       # 批量查询多个任务
adp extract query --file tasks.json    # 从文件加载任务 ID 批量查询
```

**query 命令新选项**：
| 选项 | 说明 |
|------|------|
| `--watch` | 监视模式，持续查询直到任务完成 |
| `--file <path>` | 从 JSON 文件加载任务 ID |
| `--concurrency 2` | 批量查询时的并发数 |
| `--export <path>` | 导出结果到 JSON 文件 |

### 批量结果导出

批量处理时，每个结果写入独立文件：

```bash
# 批量处理后，导出目录结构：
# output/
#   ├── doc1.json          # 成功结果
#   ├── doc2.json
#   ├── doc3.error.json     # 失败结果
#   └── _summary.json       # 汇总信息
```

### 应用管理 (app-id)

```bash
adp app-id list                  # 列出所有可用应用 ID
```

### 自定义抽取应用 (custom-app)

```bash
adp custom-app create [OPTIONS]          # 创建自定义抽取应用
adp custom-app get-config [OPTIONS]      # 查询应用配置
adp custom-app list-versions [OPTIONS]   # 列出配置版本
adp custom-app delete [OPTIONS]          # 删除应用
adp custom-app delete-version [OPTIONS]  # 删除指定配置版本
adp custom-app ai-generate [OPTIONS]     # AI 生成抽取字段推荐
```

#### custom-app create 参数说明

| 参数 | 说明 | 必填 |
|------|------|------|
| `--app-name` | 应用应用名称（50 字以内） | 是 |
| `--extract-fields` | 字段配置（JSON 格式或文件路径） | 是 |
| `--parse-mode` | 解析模式 | 是 |
| `--enable-long-doc` | 是否开启长文档支持（true/false） | 是 |
| `--long-doc-config` | 长文档配置（JSON 格式或文件路径） | 否 |

**说明**：
- `--extract-fields` 和 `--long-doc-config` 支持两种方式：
  1. 直接传入 JSON 字符串（推荐 PowerShell）
  2. 传入 JSON 文件路径（推荐 Windows CMD，文件会自动读取）

#### custom-app 其他命令参数

| 命令 | 参数说明 |
|------|----------|
| `get-config` | `--app-id`（必填），`--config-version`（可选，默认最新版本) |
| `list-versions` | `--app-id`（必填） |
| `delete` | `--app-id`（必填） |
| `delete-version` | `--app-id`（必填），`--config-version`（必填） |
| `ai-generate` | `--app-id`（必填），`--file-url` 或 `--file-base64`（二选一） |

## 支持的文件格式

- 图片：.jpeg, .jpg, .png, .bmp, .tiff
- 文档：.pdf, .doc, .docx, .xls, .xlsx
- 文件大小限制：最大 50MB

## 配置文件

配置文件保存在：`~/.adp/config.json`

## 国际化支持 (i18n)

CLI 工具支持自动根据系统语言切换界面显示语言：

### 语言检测优先级：

1. `--lang` 命令行参数（最高优先级）
2. `ADP_LANG` 环境变量
3. `LANG` 环境变量
4. `LC_ALL` 环境变量
5. 系统默认语言

### 使用方法：

```bash
# 自动根据系统语言显示帮助（中文系统显示中文，其他显示英文）
adp --help

# 手动指定英文
adp --lang en --help

# 手动指定中文
adp --lang zh --help

# 通过环境变量设置
export ADP_LANG=en
adp --help
```

### 支持的语言：

- `zh` - 中文（简体、繁体都会识别为中文）
- `en` - 英文（所有非中文语言默认使用英文）

## Agent 使用

本 CLI 工具专为 AI Agent 优化，支持结构化错误输出和幂等操作。

### 结构化错误输出

非 TTY 环境下，错误以 JSON 格式输出：

```json
{
  "type": "NETWORK_ERROR",
  "code": 1,
  "message": "Connection timeout after 30 seconds",
  "fix": "Check your network connection and try again.",
  "retryable": true,
  "details": {}
}
```

### 错误类型

| type | 说明 | retryable |
|------|------|-----------|
| `NETWORK_ERROR` | 网络连接错误 | true |
| `API_ERROR` | API 调用错误 | false |
| `AUTH_ERROR` | 认证/权限错误 | false |
| `PARAM_ERROR` | 参数错误 | false |
| `RESOURCE_ERROR` | 资源不存在 | false |
| `SYSTEM_ERROR` | 系统错误 | false |

### 退出码

| 退出码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 参数错误 |
| 3 | 资源不存在 |
| 4 | 权限不足 |
| 5 | 冲突/已存在 |

### Schema 自省

Agent 可通过 schema 命令查询 CLI 能力：

```bash
adp schema                    # 查看完整命令树
adp schema parse local       # 查看特定命令参数
```

### 幂等操作

所有命令均支持幂等执行：

- `config clear --force` - 重复清除不会报错
- `custom-app delete` - 删除不存在的应用返回退出码 3
- `custom-app delete-version` - 删除不存在的版本返回退出码 3

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black src/
isort src/
```

### 类型检查

```bash
mypy src/
```
