# ADP CLI 用户指南

## 目录

1. [安装](#安装)
2. [快速开始](#快速开始)
3. [命令详解](#命令详解)
4. [最佳实践](#最佳实践)
5. [故障排除](#故障排除)

## 安装

### 从源码安装

```bash
cd cli-anything
pip install -e .
```

### 验证安装

```bash
adp --help
```

应该看到完整的命令列表。

## 快速开始

### 1. 配置 API Key

```bash
adp config set --api-key YOUR_API_KEY
```

### 2. 解析文档

```bash
adp parse local ./document.pdf
```

### 3. 提取文档信息

```bash
adp extract local ./invoice.pdf --app-id INVOICE_PROCESSOR
```

## 命令详解

### 认证配置 (config)

#### 设置 API Key

```bash
adp config set --api-key YOUR_API_KEY
```

- API Key 会加密存储在 `~/.adp/config.json`
- 每次设置都会覆盖之前的密钥

#### 查看配置

```bash
adp config get
```

输出示例：
```
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key            ┃ Value                       ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ configured     │ True                        │
│ api_key_masked │ sk-xx...yy                  │
│ api_base_url   │ http://127.0.0.1:8000        │
└────────────────┴──────────────────────────────┘
```

#### 清除配置

```bash
adp config clear
```

### 文档解析 (parse)

#### 解析本地文件

同步模式：
```bash
adp parse local ./document.pdf
```

异步模式：
```bash
adp parse local ./document.pdf --async
```

#### 解析文件夹（批量处理）

```bash
adp parse local ./documents/
```

会自动识别支持的文件类型并批量处理。

#### 解析 URL 文件

```bash
adp parse url https://example.com/document.pdf
```

#### 导出结果

```bash
adp parse local ./document.pdf --export result.json
```

### 文档抽取 (extract)

#### 抽取本地文件

```bash
adp extract local ./invoice.pdf --app-id INVOICE_PROCESSOR
```

#### 抽取 URL 文件

```bash
adp extract url https://example.com/invoice.pdf --app-id INVOICE_PROCESSOR
```

#### 异步抽取

```bash
adp extract local ./invoice.pdf --app-id INVOICE_PROCESSOR --async
```

#### 批量抽取

```bash
adp extract local ./invoices/ --app-id INVOICE_PROCESSOR
```

#### 导出结果

```bash
adp extract local ./invoice.pdf --app-id INVOICE_PROCESSOR --export result.json
```

### 查询异步任务 (query)

#### 查询任务状态

```bash
adp query TASK_ID
```

#### 监视任务直到完成

```bash
adp query TASK_ID --watch
```

### 应用管理 (app-id)

#### 列出所有应用

```bash
adp app-id list
```

输出示例：
```
                        Available Applications
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ App ID          ┃ App Name        ┃ Description                 ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ INVOICE_PROC    │ Invoice Processor│ Extract invoice data       │
│ RECEIPT_PROC    │ Receipt Processor│ Extract receipt data      │
│ CONTRACT_PROC   │ Contract Processor│ Extract contract data    │
└──────────────────┴─────────────────┴──────────────────────────────┘
```

## 最佳实践

### 1. 批量处理

使用文件夹路径进行批量处理：
```bash
adp extract local ./documents/ --app-id APP_ID
```

### 2. 异步处理

对于大文件或批量处理，使用异步模式：
```bash
adp extract local ./large-file.pdf --app-id APP_ID --async
```

### 3. 导出结果

始终导出结果以便后续处理：
```bash
adp extract local ./file.pdf --app-id APP_ID --export result.json
```

### 4. 错误处理

CLI 会跳过无效文件并继续处理其他文件。

### 5. 性能优化

- 使用异步模式处理大文件
- 批量处理时考虑 QPS 限制
- 使用 `--export` �导出结果避免重复处理

## 故障排除

### 1. API Key 未配置

错误信息：
```
✗ API Key not configured. Run 'adp config set --api-key YOUR_KEY' first.
```

解决方法：
```bash
adp config set --api-key YOUR_API_KEY
```

### 2. 文件不支持

错误信息：
```
✗ Unsupported file type: .txt. Supported types: .jpg, .jpeg, ...
```

解决方法：确保文件类型在支持列表中。

### 3. 文件过大

错误信息：
```
✗ File too large: 60.00MB. Maximum size: 50MB
```

解决方法：压缩文件或分批处理。

### 4. API 请求失败

错误信息：
```
✗ API request failed: Connection refused
```

解决方法：
- 检查网络连接
- 检查 API 服务器状态
- 验证 API Key 是否正确

### 5. QPS 限制超限

CLI 会自动处理 QPS 限制，无需手动干预。

## 支持的文件格式

- 图片：.jpeg, .jpg, .png, .bmp, .tiff
- 文档：.pdf, .doc, .docx, .xls, .xlsx
- 文件大小限制：最大 50MB

## 配置文件

配置文件位置：`~/.adp/config.json`

示例配置：
```json
{
  "api_base_url": "http://127.0.0.1:8000",
  "free_qps": 1,
  "paid_qps": 2,
  "is_paid_user": false
}
```

## JSON 模式

使用 `--json` 标志输出纯 JSON 格式：

```bash
adp config get --json
```

输出：
```json
{
  "configured": true,
  "api_key_masked": "sk-xx...yy",
  "api_base_url": "http://127.0.0.1:8000"
}
```

## 静默模式

使用 `--quiet` 标志抑制所有输出（除错误外）：

```bash
adp parse local ./file.pdf --quiet
```
