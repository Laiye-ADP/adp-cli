# ADP CLI 用户使用手册

## 目录

1. [简介](#简介)
2. [系统要求](#系统要求)
3. [安装指南](#安装指南)
4. [快速开始](#快速开始)
5. [命令参考](#命令参考)
6. [配置说明](#配置说明)
7. [文件格式支持](#文件格式支持)
8. [使用示例](#使用示例)
9. [错误处理](#错误处理)
   - [常见错误](#常见错误)
   - [退出码](#退出码)
10. [最佳实践](#最佳实践)
11. [常见问题](#常见问题)
12. [API参考](#api参考)

---

## 简介

**ADP CLI** (AI Document Platform Command Line Tool) 是AI文档平台的官方命令行工具，为Agent和Skill提供了完整的文档处理能力。

**核心功能：**
- **文档解析**：将文档解析为结构化内容
- **文档抽取**：使用AI应用提取文档关键信息
- **自定义应用**：创建和管理自定义抽取应用
- **任务查询**：查询异步任务状态和结果
- **应用管理**：查看和管理可用应用

**主要特性：**
- 支持同步/异步处理模式
- 本地文件和URL处理
- 批量文件处理
- 多格式支持（图片、PDF、Office文档）
- API Key加密存储
- 国际化支持（中英文）
- 跨平台支持（Windows、Linux、macOS）

---

## 系统要求

| 平台 | 最低要求 |
|------|------|
| **Windows** | Windows 10 或更高版本 |
| **Linux** | Ubuntu 18.04+, CentOS 7+, 或主流Linux发行版 |
| **macOS** | macOS 10.14 (Mojave) 或更高版本 |

---

## 安装指南

ADP CLI 提供预编译的可执行文件，无需安装Python环境即可直接使用。

#### Windows 系统安装

**步骤 1：下载可执行文件**

从ADP平台官网下载Windows版本的 `app.exe` 文件。

**步骤 2：运行可执行文件**

 `app.exe` 命令提示符中运行：

```cmd
# 在当前目录运行
app.exe --help

# 或者添加到PATH后直接使用
adp --help
```

**步骤 3：添加到系统PATH（可选）**

为了在任意位置使用 `adp` 命令，可以将文件所在目录添加到系统PATH：

```cmd
# 方式一：临时添加（当前会话窗口）
set PATH=%PATH%;C:\path\to\adp-cli

# 方式二：永久添加（需要管理员权限）
setx PATH "%PATH%;C:\path\to\adp-cli"
```

**步骤 4：验证安装**

```cmd
# 查看版本信息
app.exe --version

# 或如果已添加到PATH
adp --version
```

#### Linux 系统安装

**步骤 1：下载可执行文件**

从ADP平台官网下载Linux版本的 `app` 文件。

**步骤 2：设置可执行权限**

```bash
# 设置可执行权限
chmod +x app

# 运行测试
./app --help
```

**步骤 3：添加到PATH环境变量（推荐）**

为了在任意位置使用 `adp` 命令，推荐以下两种方式之一：

```bash
# 方式一：临时添加（当前会话窗口）
export PATH=$PATH:$(pwd)

# 方式二：永久添加（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export PATH=$PATH:/path/to/app' >> ~/.bashrc
source ~/.bashrc

# 方式三：创建软链接（需要sudo权限）
sudo ln -s $(pwd)/app /usr/local/bin/adp

# 验证
adp --version
```

**步骤 4：验证安装**

```bash
# 使用相对路径
./app --version

# 或者如果已添加到PATH
adp --version
```

#### macOS 系统安装

**步骤 1：下载可执行文件**

从ADP平台官网下载macOS版本的 `app` 文件。

**步骤 2：设置可执行权限**

```bash
# 设置可执行权限
chmod +x app

# 运行测试
./app --help
```

**步骤 3：添加到PATH环境变量（推荐）**

为了在任意位置使用 `adp` 命�令，推荐以下两种方式之一：

```bash
# 方式一：临时添加（当前会话窗口）
export PATH=$PATH:$(pwd)

# 方式二：永久添加（添加到 ~/.zshrc）
echo 'export PATH=$PATH:/path/to/app' >> ~/.zshrc
source ~/.zshrc

# 方式三：创建软链接（需要sudo权限）
sudo ln -s $(pwd)/app /usr/local/bin/adp

# 验证
adp --version
```

**步骤 4：验证安装**

```bash
# 使用相对路径
./app --version

# 或者如果已添加到PATH
adp --version
```

---

## 快速开始

#### 步骤 1：配置 API Key

```bash
# 设置API Key
adp config set --api-key YOUR_API_KEY

# 可选：设置自定义API地址
adp config set --api-base-url https://your-api-url.com
```

#### 步骤 2：查看可用应用

```bash
# 列出所有可用应用
adp app-id list
```

#### 步骤 3：解析文档

```bash
# 同步解析本地文件
adp parse local ./document.pdf --app-id YOUR_APP_ID

# 异步解析URL文件
adp parse url https://example.com/document.pdf --app-id YOUR_APP_ID --async
```

#### 步骤 4：提取文档信息

```bash
# 同步提取本地文件
adp extract local ./invoice.pdf --app-id YOUR_EXTRACT_APP_ID

# 异步提取并导出结果
adp extract url https://example.com/invoice.pdf \
  --app-id YOUR_EXTRACT_APP_ID \
  --async \
  --export result.json
```

#### 步骤 5：查询异步任务

```bash
# 查询解析任务状态
adp parse query TASK_ID

# 查询抽取任务状态
adp extract query TASK_ID

# 监视任务直到完成
adp parse query TASK_ID --watch
adp extract query TASK_ID --watch
```

#### 步骤 6：查询剩余额度

```bash
# 查询剩余额度
adp credit
```

---

## 命令参考

#### 全局选项

| 选项 | 说明 |
|------|------|
| `--json` | 输出为JSON格式（机器可读） |
| `--quiet` | 抑制所有输出（除错误外） |
| `--lang` | 设置语言（en或zh） |
| `--help, -h` | 显示帮助信息 |
| `--version` | 显示版本信息 |

#### 认证配置命令

**配置管理组**

```bash
adp config [COMMAND]
```

| 命令 | 说明 |
|------|------|
| `set` | 设置或更新API Key / API Base URL |
| `get` | 查看当前配置 |
| `clear` | 清除所有本地配置 |

**config set**

```bash
adp config set [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥 | 否 |
| `--api-base-url` | API基础URL | 否 |

```bash
# 示例
adp config set --api-key sk-xxxxxxxxxxxx
adp config set --api-base-url https://adp.laiye.com
```

**config get**

```bash
adp config get
```

**config clear**

```bash
adp config clear
```

#### 文档解析命令

**文档解析组**

```bash
adp parse [COMMAND]
```

| 命令 | 说明 |
|------|------|
| `local` | 解析本地文件或文件夹 |
| `url` | 解析URL文件或URL列表文件 |
| `base64` | 解析Base64编码的文件内容 |
| `query` | 查询解析异步任务状态 |

**parse local**

```bash
adp parse local PATH [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `path` | 文件或文件夹路径 | 是 |
| `--app-id` | 解析应用ID | 是 |
| `--async` | 提交异步任务并等待完成返回结果 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 任务超时时间（秒） | 否 |
| `--concurrency` | 批量处理的并发数（默认：1） | 否 |

```bash
# 示例
adp parse local ./document.pdf --app-id YOUR_APP_ID
adp parse local ./documents/ --app-id YOUR_APP_ID --async
adp parse local ./documents/ --app-id YOUR_APP_ID --async --concurrency 5
adp parse local ./document.pdf --app-id YOUR_APP_ID --export result.json
```

**parse url**

```bash
adp parse url URL [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `url` | 文件URL或URL列表文件路径 | 是 |
| `--app-id` | 解析应用ID | 是 |
| `--async` | 提交异步任务并等待完成返回结果 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 任务超时时间（秒） | 否 |
| `--concurrency` | 批量处理的并发数（默认：1） | 否 |

```bash
# 示例
adp parse url https://example.com/document.pdf --app-id YOUR_APP_ID
adp parse url ./urls.txt --app-id YOUR_APP_ID --async
adp parse url ./urls.txt --app-id YOUR_APP_ID --async --concurrency 5
```

**parse base64**

```bash
adp parse base64 BASE64_STRING [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `file_base64` | Base64编码的文件内容（一个或多个） | 是 |
| `--app-id` | 解析应用ID | 是 |
| `--async` | 提交异步任务并等待完成返回结果 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 任务超时时间（秒） | 否 |
| `--file-name` | Base64内容的基础文件名（默认：document） | 否 |
| `--concurrency` | 批量处理的并发数（默认：1） | 否 |

```bash
# 示例
adp parse base64 SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID
adp parse base64 SGVsbG8gV29ybGQ= SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID --file-name document
```

**parse query**

```bash
adp parse query TASK_ID [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `task-id` | 解析异步任务ID | 是 |
| `--watch` | 监视模式，持续查询直到任务完成 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 监视模式超时时间（秒） | 否 |

```bash
# 示例
adp parse query 12345678-1234-1234-1234-123456789012
adp parse query 12345678-1234-1234-1234-123456789012 --watch
adp parse query 12345678-1234-1234-1234-123456789012 --export result.json
```

#### 文档抽取命令

**文档抽取组**

```bash
adp extract [COMMAND]
```

| 命令 | 说明 |
|------|------|
| `local` | 抽取本地文件或文件夹 |
| `url` | 抽取URL文件或URL列表文件 |
| `base64` | 抽取Base64编码的文件内容 |
| `query` | 查询抽取异步任务状态 |

**extract local**

```bash
adp extract local PATH [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `path` | 文件或文件夹路径 | 是 |
| `--app-id` | 抽取应用ID | 是 |
| `--async` | 提交异步任务并等待完成返回结果 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 任务超时时间（秒） | 否 |
| `--concurrency` | 批量处理的并发数（默认：1） | 否 |

```bash
# 示例
adp extract local ./invoice.pdf --app-id INVOICE_EXTRACTOR
adp extract local ./invoices/ --app-id INVOICE_EXTRACTOR --async
adp extract local ./invoices/ --app-id INVOICE_EXTRACTOR --async --concurrency 5
```

**extract url**

```bash
adp extract url URL [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `url` | 文件URL或URL列表文件路径 | 是 |
| `--app-id` | 抽取应用ID | 是 |
| `--async` | 提交异步任务并等待完成返回结果 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 任务超时时间（秒） | 否 |
| `--concurrency` | 批量处理的并发数（默认：1） | 否 |

```bash
# 示例
adp extract url https://example.com/invoice.pdf \
  --app-id YOUR_EXTRACT_APP_ID \
  --async \
  --export result.json

# 批量处理并发数
adp extract url ./urls.txt \
  --app-id YOUR_EXTRACT_APP_ID \
  --async \
  --concurrency 5
```

**extract base64**

```bash
adp extract base64 BASE64_STRING [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `file_base64` | Base64编码的文件内容（一个或多个） | 是 |
| `--app-id` | 抽取应用ID | 是 |
| `--async` | 提交异步任务并等待完成返回结果 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 任务超时时间（秒） | 否 |
| `--file-name` | Base64内容的基础文件名（默认：document） | 否 |
| `--concurrency` | 批量处理的并发数（默认：1） | 否 |

```bash
# 示例
adp extract base64 SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID
adp extract base64 SGVsbG8gV29ybGQ= SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID --file-name document
```

**extract query**

```bash
adp extract query TASK_ID [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `task-id` | 抽取异步任务ID | 是 |
| `--watch` | 监视模式，持续查询直到任务完成 | 否 |
| `--export` | 导出结果到JSON文件 | 否 |
| `--timeout` | 监视模式超时时间（秒） | 否 |

```bash
# 示例
adp extract query 12345678-1234-1234-1234-123456789012
adp extract query 12345678-1234-1234-1234-123456789012 --watch
adp extract query 12345678-1234-1234-1234-123456789012 --export result.json
```

#### 应用管理命令

**应用管理组**

```bash
adp app-id [COMMAND]
```

| 命令 | 说明 |
|------|------|------|
| `list` | 列出所有可用应用 |

**app-id list**

```bash
adp app-id list [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--app-label` | 按标签过滤应用（可选） | 否 |

```bash
# 示例
adp app-id list
adp app-id list --app-label invoice
```

#### 自定义应用命令

**自定义应用管理组**

```bash
adp custom-app [COMMAND]
```

| 命令 | 说明 |
|------|------|
| `create` | 创建自定义抽取应用 |
| `update` | 更新自定义抽取应用（全量更新） |
| `get-config` | 查询应用配置 |
| `delete` | 删除应用 |
| `delete-version` | 删除指定配置版本 |
| `ai-generate` | AI生成抽取字段推荐 |

**schema**

```bash
adp schema [COMMAND]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `command` | 命令路径（可选），如 `parse local`、`extract url` | 否 |

```bash
# 示例
adp schema              # 显示完整命令树
adp schema parse        # 显示 parse 命令组
adp schema parse local  # 显示 parse local 命令详情
```

**app-id cache**

```bash
adp app-id cache [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--app-label` | 按标签过滤缓存应用（可选） | 否 |

```bash
# 示例
adp app-id cache                    # 列出所有缓存的高频应用
adp app-id cache --app-label invoice # 查询指定标签的缓存应用
```

| 命令 | 说明 |
|------|------|
| `list` | 列出所有可用应用 |
| `cache` | 列出缓存的高频应用（快速，无需网络） |

**custom-app create**

```bash
adp custom-app create [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选，如果已配置则不需要） | 否 |
| `--app-name` | 应用名称（最多50字符） | 是 |
| `--app-label` | 应用标签（最多5个，可选） | 否 |
| `--extract-fields` | 字段配置（JSON格式或文件路径） | 是 |
| `--parse-mode` | 解析模式（standard=标准；advance=增强；agentic=智能体） | 是 |
| `--enable-long-doc` | 启用长文档支持（true/false） | 是 |
| `--long-doc-config` | 可用文档配置 | 否 |

```bash
# 方式一：使用JSON字符串（推荐PowerShell）
adp custom-app create \
  --app-name "财务票据抽取" \
  --app-label "发票,财务" \
  --extract-fields '[
    {"field_name":"发票号码","field_type":"string","field_prompt":"提取发票左上角编号"},
    {"field_name":"开票日期","field_type":"date","field_prompt":"提取发票开具日期"},
    {"field_name":"商品明细","field_type":"table"}
  ]' \
  --parse-mode "advance" \
  --enable-long-doc true

# 方式二：使用JSON文件（推荐Windows CMD）
adp custom-app create \
  --app-name "财务票据抽取" \
  --app-label "发票,财务" \
  --extract-fields extract-fields.json \
  --parse-mode "advance" \
  --enable-long-doc true \
  --long-doc-config long-doc-config.json
```

**custom-app update**

```bash
adp custom-app update [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选，如果已配置则不需要） | 否 |
| `--app-id` | 要更新的应用ID | 是 |
| `--app-name` | 应用名称（最多50字符） | 否 |
| `--app-label` | 应用标签（最多5个，可选） | 否 |
| `--extract-fields` | 字段配置（JSON格式或文件路径） | 是 |
| `--parse-mode` | 解析模式（standard=标准；advance=增强；agentic=智能体） | 是 |
| `--enable-long-doc` | 启用长文档支持（true/false） | 是 |
| `--long-doc-config` | 长文档配置 | 否 |

```bash
# 示例
adp custom-app update \
  --app-id YOUR_APP_ID \
  --app-name "更新的票据抽取" \
  --extract-fields extract-fields.json \
  --parse-mode "advance" \
  --enable-long-doc true
```

**custom-app get-config**

```bash
adp custom-app get-config [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选） | 否 |
| `--app-id` | 应用ID | 是 |
| `--config-version` | 配置版本（可选，默认最新版） | 否 |

**custom-app delete**

```bash
adp custom-app delete [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选） | 否 |
| `--app-id` | 应用ID | 是 |

**custom-app delete-version**

```bash
adp custom-app delete-version [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选） | 否 |
| `--app-id` | 应用ID | 是 |
| `--config-version` | 要删除的配置版本 | 是 |

**custom-app ai-generate**

```bash
adp custom-app ai-generate [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选） | 否 |
| `--app-id` | 应用ID | 是 |
| `--file-url` | 示例文档URL | 否（与--file-local或--base64三选一） |
| `--file-local` | 本地示例文档路径 | 否（与--file-url或--base64三选一） |
| `--base64` | Base64编码的示例文档 | 否（与--file-url或--file-local三选一） |

```bash
# 示例
adp custom-app ai-generate \
  --app-id YOUR_APP_ID \
  --file-url https://example.com/sample.pdf

adp custom-app ai-generate \
  --app-id YOUR_APP_ID \
  --file-local ./sample.pdf
```

#### 额度查询命令

**查询剩余额度**

```bash
adp credit [OPTIONS]
```

| 参数 | 说明 | 必填 |
|------|------|------|
| `--api-key` | API认证密钥（可选，如果已配置则不需要） | 否 |

```bash
# 示例
adp credit
adp credit --api-key sk-xxxxxxxxxxxx
```

---

## 配置说明

#### 配置文件位置

配置文件保存在用户主目录的隐藏文件夹中：

```
~/.adp/
├── config.json      # 配置文件
└── key.enc         # 加密的API Key
```

**不同系统的具体位置：**

| 平台 | 配置目录 |
|------|------|
| **Windows** | `C:\Users\<username>\.adp\` |
| **Linux** | `/home/<username>/.adp/` |
| **macOS** | `/Users/<username>/.adp/` |

#### API Key 加密存储

API Key 使用 Fernet 对称加密算法进行加密存储，确保敏感信息安全。

#### 查看配置

```bash
adp config get
```

---

## 文件格式支持

#### 支持的文件类型

| 类别 | 扩展名 |
|------|------|
| **图片** | .jpg, .jpeg, .png, .bmp, .tiff, .tif |
| **文档** | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx |

#### 文件限制

- **最大文件大小**：50MB
- **批量处理**：支持文件夹递归处理

#### URL列表文件格式

处理多个URL时，可以创建一个文本文件，每行一个URL：

```
https://example.com/document1.pdf
https://example.com/document2.pdf
https://example.com/document3.pdf
```

---

## 使用示例

#### 示例 1：批量处理发票

```bash
# 批量抽取发票信息
adp extract local ./invoices/ --app-id INVOICE_EXTRACTOR --export results.json
```

#### 示例 2：异步处理大型文档

```bash
# 提交异步任务
TASK_ID=$(adp parse local ./large-document.pdf --app-id YOUR_APP_ID --async --json | jq -r '.task_id')

# 监视任务完成
adp query $TASK_ID --watch
```

#### 示例 3：创建自定义应用

```bash
# 先使用AI生成字段推荐
adp custom-app ai-generate \
  --app-id YOUR_APP_ID \
  --file-url https://example.com/sample-invoice.pdf

# 创建自定义应用
adp custom-app create \
  --app-name "Custom Invoice Extractor" \
  --app-label "发票,财务" \
  --extract-fields fields.json \
  --parse-mode "advance" \
  --enable-long-doc true
```

#### 示例 4：错误处理和重试

```bash
# Windows CMD
adp parse local ./document.pdf --app-id YOUR_APP_ID || echo "Parse failed, retrying..."

# Linux/macOS
adp parse local ./document.pdf --app-id YOUR_APP_ID || echo "Parse failed, retrying..."
```

---

## 错误处理

#### 常见错误

| 错误信息 | 原因 | 解决方案 |
|------|------|------|------|
| `API Key not configured` | 未设置API Key | 运行 `adp config set --api-key YOUR_KEY` |
| `File not found` | 文件不存在 | 检查文件路径 |
| `Unsupported file type` | 不支持的文件格式 | 使用支持的文件格式 |
| `File too large` | 文件超过50MB | 压缩或分割文件 |
| `Invalid API Key` | API Key无效 | 检查API Key是否正确 |
| `Network error` | 网络连接失败 | 检查网络连接 |
| `Task timeout` | 任务超时 | 增加超时时间或使用异步模式 |
| `Free users: 1, paid users: 2, other values are invalid` | 无效的并发数 | 免费用户使用1，付费用户使用2 |
| `You are a free user, maximum concurrency is 1` | 免费用户无法使用并发2 | 设置并发为1或升级为付费账户 |

#### 退出码

CLI 返回特定的退出码以区分不同类型的错误，使自动化脚本能够正确处理错误：

| 退出码 | 名称 | 含义 | Agent 应对 |
|--------|------|------|------------|
| 0 | `EXIT_SUCCESS` | 成功 | 继续执行 |
| 1 | `EXIT_GENERAL_ERROR` | 一般错误（API失败、网络错误、运行时异常） | 读取 stderr 诊断问题 |
| 2 | `EXIT_PARAMETER_ERROR` | 参数错误、缺少必需参数、JSON格式错误 | 修正参数后重试 |
| 3 | `EXIT_RESOURCE_NOT_FOUND` | 资源不存在（文件、URL等） | 跳过或创建资源 |
| 4 | `EXIT_PERMISSION_DENIED` | 权限不足 | 提示用户授权 |
| 5 | `EXIT_CONFLICT` | 冲突或已存在 | 跳过或更新 |

**示例 - 使用退出码的脚本处理：**

```bash
# Linux/macOS
adp parse local ./document.pdf --app-id YOUR_APP_ID
case $? in
    0) echo "成功" ;;
    1) echo "一般错误 - 检查 stderr" ;;
    2) echo "参数错误 - 修正后重试" ;;
    3) echo "文件不存在" ;;
    4) echo "权限不足" ;;
    5) echo "资源冲突" ;;
esac
```

#### 结构化错误输出

在非 TTY 环境（脚本、CI、Agent）中，错误以 JSON 格式输出：

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

| 字段 | 说明 | 示例 |
|------|------|------|
| `type` | 机器可读错误类型 | `NETWORK_ERROR`, `API_ERROR`, `PARAM_ERROR` |
| `code` | 退出码 | 1, 2, 3, 4, 5 |
| `message` | 人类可读描述 | "Connection timeout..." |
| `fix` | 修复建议 | "Check your network..." |
| `retryable` | 是否值得重试 | `true` / `false` |
| `details` | 额外上下文 | `{"context": "..."}` |

**错误类型：**

| type | 说明 | retryable |
|------|------|-----------|
| `NETWORK_ERROR` | 网络连接错误 | true |
| `API_ERROR` | API 调用错误 | false |
| `AUTH_ERROR` | 认证/权限错误 | false |
| `PARAM_ERROR` | 参数错误 | false |
| `RESOURCE_ERROR` | 资源不存在 | false |
| `SYSTEM_ERROR` | 系统错误 | false |

---

## 最佳实践

#### 1. API Key 安全管理

- 不要将API Key硬编码在脚本中
- 使用环境变量传递敏感信息
- 定期轮换API Key

```bash
# 好的做法
export ADP_API_KEY="sk-xxxxxxxxxxxx"
adp config set --api-key $ADP_API_KEY

# 避免
adp config set --api-key "sk-xxxxxxxxxxxx"  # 不要在脚本中
```

#### 2. 异步处理大文件

对于大型文件或批量处理，使用异步模式以提高效率：

```bash
# 小文件使用同步模式
adp parse local ./small-file.pdf --app-id YOUR_APP_ID

# 大文件使用异步模式
adp parse local ./large-file.pdf --app-id YOUR_APP_ID --async
```

#### 3. 结果导出和备份

始终导出结果到文件以备后用：

```bash
adp extract local ./document.pdf --app-id YOUR_APP_ID --export results.json
```

#### 4. 错误处理和日志

在脚本中添加适当的错误处理：

```bash
# Linux/macOS
if ! adp parse local ./document.pdf --app-id YOUR_APP_ID; then
    echo "Error: Parse failed"
    exit 1
fi
```

---

## 常见问题

**Q: 如何获取API Key？**

A: 请访问ADP平台官网，在个人中心或开发者页面获取您的API Key。

**Q: 支持哪些操作系统？**

A: 支持Windows、Linux和macOS系统。

**Q: 如何处理超过50MB的文件？**

A: 需要压缩或分割文件后再处理。可以使用异步模式提高处理效率。

**Q: 同步模式和异步模式的区别？**

A: 同步模式会等待任务完成并返回结果，适用于小文件。异步模式立即返回任务ID，适用于大文件或批量处理。

**Q: 如何切换语言？**

A: 使用 `--lang` 选项或设置环境变量 `ADP_LANG`。

```bash
adp --lang en --help
export ADP_LANG=zh
```

---

## API参考

#### API端点

| 功能 | 端点 | 方法 |
|------|------|------|
| 文档解析（同步） | `/v1/app/doc/recognize` | POST |
| 文档解析（异步） | `/v1/app/doc/recognize/create/task` | POST |
| 查询解析任务 | `/v1/app/doc/recognize/query/task/{task_id}` | GET |
| 文档抽取（同步） | `/v1/app/doc/extract` | POST |
| 文档抽取（异步） | `/v1/app/doc/extract/create/task` | POST |
| 查询抽取任务 | `/v1/app/doc/extract/query/task/{task_id}` | GET |
| 应用列表 | `/v1/app-list` | GET |
| 创建自定义应用 | `/v1/app-manage/create` | POST |
| 查询应用配置 | `/v1/app-manage/config` | POST |
| 删除应用 | `/v1/app-manage/delete` | POST |
| AI推荐字段 | `/v1/app-manage/ai-recommend` | POST |

---

## 版本信息

**ADP CLI 版本**: 1.10.0

**最后更新**: 2026-04-05

---

## 许可证

MIT License

---

## 联系支持

- **项目主页**: https://github.com/adp/adp-aiem
- **问题反馈**: https://github.com/adp/adp-aiem/issues
- **文档**: https://github.com/adp/adp-aiem/wiki

---

*本手册由ADP CLI工具自动生成*
*适用于Agent和Skill用户*
