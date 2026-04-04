# ADP CLI User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Quick Start](#quick-start)
5. [Command Reference](#command-reference)
6. [Configuration Guide](#configuration-guide)
7. [Supported File Formats](#supported-file-formats)
8. [Usage Examples](#usage-examples)
9. [Error Handling](#error-handling)
   - [Common Errors](#common-errors)
   - [Exit Codes](#exit-codes)
10. [Best Practices](#best-practices)
11. [FAQ](#faq)
12. [API Reference](#api-reference)

---

## Introduction

**ADP CLI** (AI Document Platform Command Line Tool) is the official command-line tool for the AI Document Platform, providing complete document processing capabilities for Agents and Skills.

**Core Features:**
- **Document Parsing**: Parse documents into structured content
- **Document Extraction**: Extract key information from documents using AI applications
- **Custom Applications**: Create and manage custom extraction applications
- **Task Query**: Query asynchronous task status and results
- **Application Management**: View and manage available applications

**Main Features:**
- Support for synchronous/asynchronous processing modes
- Local file and URL processing
- Batch file processing
- Multi-format support (images, PDFs, Office documents)
- Encrypted API Key storage
- Internationalization support (Chinese/English)
- Cross-platform support (Windows, Linux, macOS)

---

## System Requirements

| Platform | Minimum Requirements |
|----------|---------------------|
| **Windows** | Windows 10 or higher |
| **Linux** | Ubuntu 18.04+, CentOS 7+, or mainstream Linux distributions |
| **macOS** | macOS 10.14 (Mojave) or higher |

---

## Installation Guide

ADP CLI provides precompiled executable files that can be used directly without installing a Python environment.

#### Windows Installation

**Step 1: Download Executable File**

Download the Windows version of the `app.exe` file from the ADP Platform official website.

**Step 2: Run Executable File**

Run `app.exe` in the command prompt:

```cmd
# Run in current directory
app.exe --help

# Or use directly after adding to PATH
adp --help
```

**Step 3: Add to System PATH (Optional)**

To use the `adp` command from any location, add the directory containing the file to the system PATH:

```cmd
# Method 1: Temporary addition (current session window)
set PATH=%PATH%;C:\path\to\adp-cli

# Method 2: Permanent addition (requires administrator privileges)
setx PATH "%PATH%;C:\path\to\adp-cli"
```

**Step 4: Verify Installation**

```cmd
# View version information
app.exe --version

# Or if added to PATH
adp --version
```

#### Linux Installation

**Step 1: Download Executable File**

Download the Linux version of the `app` file from the ADP Platform official website.

**Step 2: Set Executable Permissions**

```bash
# Set executable permissions
chmod +x app

# Run test
./app --help
```

**Step 3: Add to PATH Environment Variable (Recommended)**

To use the `adp` command from any location, one of the following two methods is recommended:

```bash
# Method 1: Temporary addition (current session window)
export PATH=$PATH:$(pwd)

# Method 2: Permanent addition (add to ~/.bashrc or ~/.zshrc)
echo 'export PATH=$PATH:/path/to/app' >> ~/.bashrc
source ~/.bashrc

# Method 3: Create symbolic link (requires sudo privileges)
sudo ln -s $(pwd)/app /usr/local/bin/adp

# Verify
adp --version
```

**Step 4: Verify Installation**

```bash
# Use relative path
./app --version

# Or if added to PATH
adp --version
```

#### macOS Installation

**Step 1: Download Executable File**

Download the macOS version of the `app` file from the ADP Platform official website.

**Step 2: Set Executable Permissions**

```bash
# Set executable permissions
chmod +x app

# Run test
./app --help
```

**Step 3: Add to PATH Environment Variable (Recommended)**

To use the `adp` command from any location, one of the following two methods is recommended:

```bash
# Method 1: Temporary addition (current session window)
export PATH=$PATH:$(pwd)

# Method 2: Permanent addition (add to ~/.zshrc)
echo 'export PATH=$PATH:/path/to/app' >> ~/.zshrc
source ~/.zshrc

# Method 3: Create symbolic link (requires sudo privileges)
sudo ln -s $(pwd)/app /usr/local/bin/adp

# Verify
adp --version
```

**Step 4: Verify Installation**

```bash
# Use relative path
./app --version

# Or if added to PATH
adp --version
```

---

## Quick Start

#### Step 1: Configure API Key

```bash
# Set API Key
adp config set --api-key YOUR_API_KEY

# Optional: Set custom API URL
adp config set --api-base-url https://your-api-url.com
```

#### Step 2: View Available Applications

```bash
# List all available applications
adp app-id list
```

#### Step 3: Parse Document

```bash
# Synchronous parsing of local file
adp parse local ./document.pdf --app-id YOUR_APP_ID

# Asynchronous parsing of URL file
adp parse url https://example.com/document.pdf --app-id YOUR_APP_ID --async
```

#### Step 4: Extract Document Information

```bash
# Synchronous extraction of local file
adp extract local ./invoice.pdf --app-id YOUR_EXTRACT_APP_ID

# Asynchronous extraction with result export
adp extract url https://example.com/invoice.pdf \
  --app-id YOUR_EXTRACT_APP_ID \
  --async \
  --export result.json
```

#### Step 5: Query Asynchronous Task

```bash
# Query parse task status
adp parse query TASK_ID

# Query extract task status
adp extract query TASK_ID

# Watch task until completion
adp parse query TASK_ID --watch
adp extract query TASK_ID --watch
```

#### Step 6: Query Remaining Credits

```bash
# Query remaining credits
adp credit
```

---

## Command Reference

#### Global Options

| Option | Description |
|--------|-------------|
| `--json` | Output in JSON format (machine-readable) |
| `--quiet` | Suppress all output (except errors) |
| `--lang` | Set language (en or zh) |
| `--help, -h` | Display help information |
| `--version` | Display version information |

#### Authentication Configuration Commands

**Configuration Management Group**

```bash
adp config [COMMAND]
```

| Command | Description |
|---------|-------------|
| `set` | Set or update API Key / API Base URL |
| `get` | View current configuration |
| `clear` | Clear all local configuration |

**config set**

```bash
adp config set [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key | No |
| `--api-base-url` | API base URL | No |

```bash
# Example
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

#### Document Parsing Commands

**Document Parsing Group**

```bash
adp parse [COMMAND]
```

| Command | Description |
|---------|-------------|
| `local` | Parse local file or folder |
| `url` | Parse URL file or URL list file |
| `base64` | Parse base64 encoded file content |
| `query` | Query parse async task status |

**parse local**

```bash
adp parse local PATH [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `path` | File or folder path | Yes |
| `--app-id` | Parsing application ID | Yes |
| `--async` | Submit async task and wait for completion with results | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Task timeout (seconds) | No |
| `--concurrency` | Concurrent tasks count for batch processing (default: 1, max: 1 for free users, 2 for paid users) | No |

```bash
# Example
adp parse local ./document.pdf --app-id YOUR_APP_ID
adp parse local ./documents/ --app-id YOUR_APP_ID --async
adp parse local ./documents/ --app-id YOUR_APP_ID --async --concurrency 5
adp parse local ./document.pdf --app-id YOUR_APP_ID --export result.json
```

**parse url**

```bash
adp parse url URL [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `url` | File URL or URL list file path | Yes |
| `--app-id` | Parsing application ID | Yes |
| `--async` | Submit async task and wait for completion with results | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Task timeout (seconds) | No |
| `--concurrency` | Concurrent tasks count for batch processing (default: 1, max: 1 for free users, 2 for paid users) | No |

```bash
# Example
adp parse url https://example.com/document.pdf --app-id YOUR_APP_ID
adp parse url ./urls.txt --app-id YOUR_APP_ID --async
adp parse url ./urls.txt --app-id YOUR_APP_ID --async --concurrency 5
```

**parse base64**

```bash
adp parse base64 BASE64_STRING [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `file_base64` | Base64 encoded file content (one or more) | Yes |
| `--app-id` | Parsing application ID | Yes |
| `--async` | Submit async task and wait for completion with results | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Task timeout (seconds) | No |
| `--file-name` | Base file name for the base64 content (default: document) | No |
| `--concurrency` | Concurrent tasks count for batch processing (default: 1) | No |

```bash
# Example
adp parse base64 SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID
adp parse base64 SGVsbG8gV29ybGQ= SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID --file-name document
```

**parse query**

```bash
adp parse query TASK_ID [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `task-id` | Parse async task ID | Yes |
| `--watch` | Watch mode, continuously query until task completes | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Watch mode timeout (seconds) | No |

```bash
# Example
adp parse query 12345678-1234-1234-1234-123456789012
adp parse query 12345678-1234-1234-1234-123456789012 --watch
adp parse query 12345678-1234-1234-1234-123456789012 --export result.json
```

#### Document Extraction Commands

**Document Extraction Group**

```bash
adp extract [COMMAND]
```

| Command | Description |
|---------|-------------|
| `local` | Extract local file or folder |
| `url` | Extract URL file or URL list file |
| `base64` | Extract base64 encoded file content |
| `query` | Query extract async task status |

**extract local**

```bash
adp extract local PATH [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `path` | File or folder path | Yes |
| `--app-id` | Extraction application ID | Yes |
| `--async` | Submit async task and wait for completion with results | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Task timeout (seconds) | No |
| `--concurrency` | Concurrent tasks count for batch processing (default: 1, max: 1 for free users, 2 for paid users) | No |

```bash
# Example
adp extract local ./invoice.pdf --app-id INVOICE_EXTRACTOR
adp extract local ./invoices/ --app-id INVOICE_EXTRACTOR --async
adp extract local ./invoices/ --app-id INVOICE_EXTRACTOR --async --concurrency 5
```

**extract url**

```bash
adp extract url URL [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `url` | File URL or URL list file path | Yes |
| `--app-id` | Extraction application ID | Yes |
| `--async` | Submit async task and wait for completion with results | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Task timeout (seconds) | No |
| `--concurrency` | Concurrent tasks count for batch processing (default: 1, max: 1 for free users, 2 for paid users) | No |

```bash
# Example
adp extract url https://example.com/invoice.pdf \
  --app-id YOUR_EXTRACT_APP_ID \
  --async \
  --export result.json

# Batch processing with concurrency
adp extract url ./urls.txt \
  --app-id YOUR_EXTRACT_APP_ID \
  --async \
  --concurrency 5
```

**extract base64**

```bash
adp extract base64 BASE64_STRING [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `file_base64` | Base64 encoded file content (one or more) | Yes |
| `--app-id` | Extraction application ID | Yes |
| `--async` | Submit async task and wait for completion with results | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Task timeout (seconds) | No |
| `--file-name` | Base file name for the base64 content (default: document) | No |
| `--concurrency` | Concurrent tasks count for batch processing (default: 1) | No |

```bash
# Example
adp extract base64 SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID
adp extract base64 SGVsbG8gV29ybGQ= SGVsbG8gV29ybGQ= --app-id YOUR_APP_ID --file-name document
```

**extract query**

```bash
adp extract query TASK_ID [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `task-id` | Extract async task ID | Yes |
| `--watch` | Watch mode, continuously query until task completes | No |
| `--export` | Export results to JSON file | No |
| `--timeout` | Watch mode timeout (seconds) | No |

```bash
# Example
adp extract query 12345678-1234-1234-1234-123456789012
adp extract query 12345678-1234-1234-1234-123456789012 --watch
adp extract query 12345678-1234-1234-1234-123456789012 --export result.json
```

#### Application Management Commands

**Application Management Group**

```bash
adp app-id [COMMAND]
```

| Command | Description |
|---------|-------------|
| `list` | List all available applications |

**app-id list**

```bash
adp app-id list [OPTIONS]
```

| Parameter | Description | Required |
|`-----------|-------------|----------|
| `--app-label` | Filter applications by label (optional) | No |

```bash
# Example
adp app-id list
adp app-id list --app-label invoice
```

#### Custom Application Commands

**Custom Application Management Group**

```bash
adp custom-app [COMMAND]
```

| Command | Description |
|---------|-------------|
| `create` | Create custom extraction application |
| `update` | Update custom extraction application (full coverage update) |
| `get-config` | Query application configuration |
| `delete` | Delete application |
| `delete-version` | Delete specified configuration version |
| `ai-generate` | AI generate extraction field recommendations |

**custom-app create**

```bash
adp custom-app create [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional if already configured) | No |
| `--app-name` | Application name (max 50 characters) | Yes |
| `--app-label` | Application labels (max 5 labels, optional) | No |
| `--extract-fields` | Field configuration (JSON format or file path) | Yes |
| `--parse-mode` | Parsing mode (standard=standard; advance=advanced; agentic=agentic) | Yes |
| `--enable-long-doc` | Enable long document support (true/false) | Yes` |
| `--long-doc-config` | Available document configuration | No |

```bash
# Method 1: Using JSON string (recommended for PowerShell)
adp custom-app create \
  --app-name "Financial Invoice Extraction" \
  --app-label "invoice,finance" \
  --extract-fields '[
    {"field_name":"Invoice Number","field_type":"string","field_prompt":"Extract invoice number from top left"},
    {"field_name":"Invoice Date","field_type":"date","field_prompt":"Extract invoice date"},
    {"field_name":"Item Details","field_type":"table"}
  ]' \
  --parse-mode "advance" \
  --enable-long-doc true

# Method 2: Using JSON file (recommended for Windows CMD)
adp custom-app create \
  --app-name "Financial Invoice Extraction" \
  --app-label "invoice,finance" \
  --extract-fields extract-fields.json \
  --parse-mode "advance" \
  --enable-long-doc true \
  --long-doc-config long-doc-config.json
```

**custom-app update**

```bash
adp custom-app update [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional if already configured) | No |
| `--app-id` | Application ID to update | Yes |
| `--app-name` | Application name (max 50 characters) | No |
| `--app-label` | Application labels (max 5 labels, optional) | No |
| `--extract-fields` | Field configuration (JSON format or file path) | Yes |
| `--parse-mode` | Parsing mode (standard=standard; advance=advanced; agentic=agentic) | Yes |
| `--enable-long-doc` | Enable long document support (true/false) | Yes |
| `--long-doc-config` | Long document configuration | No |

```bash
# Example
adp custom-app update \
  --app-id YOUR_APP_ID \
  --app-name "Updated Invoice Extraction" \
  --extract-fields extract-fields.json \
  --parse-mode "advance" \
  --enable-long-doc true
```

**custom-app get-config**

```bash
adp custom-app get-config [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional) | No |
| `--app-id` | Application ID | Yes |
| `--config-version` | Configuration version (optional, default: latest) | No |

**custom-app delete**

```bash
adp custom-app delete [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional) | No |
| `--app-id` | Application ID | Yes |

**custom-app delete-version**

```bash
adp custom-app delete-version [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional) | No |
| `--app-id` | Application ID | Yes |
| `--config-version` | Configuration version to delete | Yes |

**custom-app ai-generate**

```bash
adp custom-app ai-generate [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional) | No |
| `--app-id` | Application ID | Yes |
| `--file-url` | URL of sample document | No (either --file-url or --file-local required) |
| `--file-local` | Local path of sample document | No (either --file-url or --file-local required) |

```bash
# Example
adp custom-app ai-generate \
  --app-id YOUR_APP_ID \
  --file-url https://example.com/sample.pdf

adp custom-app ai-generate \
  --app-id YOUR_APP_ID \
  --file-local ./sample.pdf
```

#### Credit Query Commands

**Query remaining credits**

```bash
adp credit [OPTIONS]
```

| Parameter | Description | Required |
|-----------|-------------|----------|
| `--api-key` | API authentication key (optional if already configured) | No |

```bash
# Example
adp credit
adp credit --api-key sk-xxxxxxxxxxxx
```

---

## Configuration Guide

#### Configuration File Location

Configuration files are saved in a hidden folder in the user's home directory:

```
~/.adp/
├── config.json      # Configuration file
└── key.enc         # Encrypted API Key
```

**Specific locations for different systems:**

| Platform | Configuration Directory |
|----------|------------------------|
| **Windows** | `C:\Users\<username>\.adp\` |
| **Linux** | `/home/<username>/.adp/` |
| **macOS** | `/Users/<username>/.adp/` |

#### API Key Encrypted Storage

API Key is encrypted and stored using the Fernet symmetric encryption algorithm to ensure sensitive information security.

#### View Configuration

```bash
adp config get
```

---

## Supported File Formats

#### Supported File Types

| Category | Extensions |
|----------|------------|
| **Images** | .jpg, .jpeg, .png, .bmp, .tiff, .tif |
| **Documents** | .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx |

#### File Limitations

- **Maximum file size**: 50MB
- **Batch processing**: Supports recursive folder processing

#### URL List File Format

When processing multiple URLs, you can create a text file with one URL per line:

```
https://example.com/document1.pdf
https://example.com/document2.pdf
https://example.com/document3.pdf
```

---

## Usage Examples

#### Example 1: Batch Process Invoices

```bash
# Batch extract invoice information
adp extract local ./invoices/ --app-id INVOICE_EXTRACTOR --export results.json
```

#### Example 2: Asynchronous Processing of Large Documents

```bash
# Submit asynchronous task
TASK_ID=$(adp parse local ./large-document.pdf --app-id YOUR_APP_ID --async --json | jq -r '.task_id')

# Monitor task completion
adp query $TASK_ID --watch
```

#### Example 3: Create Custom Application

```bash
# First use AI to generate field recommendations
adp custom-app ai-generate \
  --app-id YOUR_APP_ID \
  --file-url` https://example.com/sample-invoice.pdf

# Create custom application
adp custom-app create \
  --app-name "Custom Invoice Extractor" \
  --app-label "invoice,finance" \
  --extract-fields fields.json \
  --parse-mode "advance" \
  --enable-long-doc true
```

#### Example 4: Error Handling and Retry

```bash
# Windows CMD
adp parse local ./document.pdf --app-id YOUR_APP_ID || echo "Parse failed, retrying..."

# Linux/macOS
adp parse local ./document.pdf --app-id YOUR_APP_ID || echo "Parse failed, retrying..."
```

---

## Error Handling

#### Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `API Key not configured` | API Key not set | Run `adp config set --api-key YOUR_KEY` |
| `File not found` | File does not exist | Check file path |
| `Unsupported file type` | Unsupported file format | Use supported file format |
| `File too large` | File exceeds 50MB | Compress or split file |
| `Invalid API Key` | Invalid API Key | Check if API Key is correct |
| `Network error` | Network connection failed | Check network connection |
| `Task timeout` | Task timeout | Increase timeout or use async mode |
| `Free users: 1, paid users: 2, other values are invalid` | Invalid concurrency value | Use 1 for free users, or 2 for paid users |
| `You are a free user, maximum concurrency is 1` | Free user cannot use concurrency 2 | Set concurrency to 1 or upgrade to paid account |

#### Exit Codes

The CLI returns specific exit codes for different error types, enabling automated scripts to handle errors appropriately:

| Exit Code | Name | Meaning | Agent Response |
|-----------|------|---------|----------------|
| 0 | `EXIT_SUCCESS` | Success | Continue execution |
| 1 | `EXIT_GENERAL_ERROR` | General errors (API failures, network errors, runtime exceptions) | Read stderr to diagnose |
| 2 | `EXIT_PARAMETER_ERROR` | Invalid parameters, missing required arguments, JSON format errors | Fix parameters and retry |
| 3 | `EXIT_RESOURCE_NOT_FOUND` | Resource not found (file, URL, etc.) | Skip or create resource |
| 4 | `EXIT_PERMISSION_DENIED` | Permission denied | Prompt user for authorization |
| 5 | `EXIT_CONFLICT` | Conflict or already exists | Skip or update |

**Example - Script with Exit Code Handling:**

```bash
# Linux/macOS
adp parse local ./document.pdf --app-id YOUR_APP_ID
case $? in
    0) echo "Success" ;;
    1) echo "General error - check stderr" ;;
    2) echo "Invalid parameters - fix and retry" ;;
    3) echo "File not found" ;;
    4) echo "Permission denied" ;;
    5) echo "Resource conflict" ;;
esac
```

#### Structured Error Output

In non-TTY environments (scripts, CI, Agent), errors are output as JSON:

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

| Field | Description | Example |
|-------|-------------|---------|
| `type` | Machine-readable error type | `NETWORK_ERROR`, `API_ERROR`, `PARAM_ERROR` |
| `code` | Exit code | 1, 2, 3, 4, 5 |
| `message` | Human-readable description | "Connection timeout..." |
| `fix` | Fix suggestion | "Check your network..." |
| `retryable` | Whether retry is worthwhile | `true` / `false` |
| `details` | Additional context | `{"context": "..."}` |

**Error Types:**

| type | Description | retryable |
|------|-------------|-----------|
| `NETWORK_ERROR` | Network connection error | true |
| `API_ERROR` | API call error | false |
| `AUTH_ERROR` | Authentication/permission error | false |
| `PARAM_ERROR` | Parameter error | false |
| `RESOURCE_ERROR` | Resource not found | false |
| `SYSTEM_ERROR` | System error | false |

---

## Best Practices

#### 1. API Key Security Management

- Do not hardcode API Key in scripts
- Use environment variables to pass sensitive information
- Regularly rotate API Key

```bash
# Good practice
export ADP_API_KEY="sk-xxxxxxxxxxxx"
adp config set --api-key $ADP_API_KEY

# Avoid
adp config set --api-key "sk-xxxxxxxxxxxx"  # Don't do in scripts
```

#### 2. Asynchronous Processing for Large Files

For large files or batch processing, use asynchronous mode to improve efficiency:

```bash
# Small files use synchronous mode
adp parse local ./small-file.pdf --app-id YOUR_APP_ID

# Large files use asynchronous mode
adp parse local ./large-file.pdf --app-id YOUR_APP_ID --async
```

#### 3. Result Export and Backup

Always export results to files for future use:

```bash
adp extract local ./document.pdf --app-id YOUR_APP_ID --export results.json
```

#### 4. Error Handling and Logging

Add appropriate error handling in scripts:

```bash
# Linux/macOS
if ! adp parse local ./document.pdf --app-id YOUR_APP_ID; then
    echo "Error: Parse failed"
    exit 1
fi
```

---

## FAQ

**Q: How do I get an API Key?**

A: Please visit the ADP Platform official website and get your API Key in the personal center or developer page.

**Q: Which operating systems are supported?**

A: Windows, Linux, and macOS systems are supported.

**Q: How do I handle files larger than 50MB?**

A: You need to compress or split the files before processing. You can use asynchronous mode to improve processing efficiency.

**Q: What's the difference between synchronous and asynchronous modes?**

A: Synchronous mode waits for the task to complete and returns results, suitable for small files. Asynchronous mode returns a task ID immediately, suitable for large files or batch processing.

**Q: How do I switch languages?**

A: Use the `--lang` option or set the environment variable `ADP_LANG`.

```bash
adp --lang en --help
export ADP_LANG=zh
```

**Q: What is the maximum concurrency limit?**

A: The concurrency limit depends on your account type:
- Free users: Maximum concurrency is 1
- Paid users: Maximum concurrency is 2

If you try to use concurrency 2 as a free user, you will receive an error message: "You are a free user, maximum concurrency is 1" (or the Chinese equivalent: "您是免费用户，最大并发数为1").

---

## API Reference

#### API Endpoints

| Function | Endpoint | Method |
|----------|----------|--------|
| Document Parsing (Sync) | `/v1/app/doc/recognize` | POST |
| Document Parsing (Async) | `/v1/app/doc/recognize/create/task` | POST |
| Query Parse Task | `/v1/app/doc/recognize/query/task/{task_id}` | GET |
| Document Extraction (Sync) | `/v1/app/doc/extract` | POST |
| Document Extraction (Async) | `/v1/app/doc/extract/create/task` | POST |
| Query Extract Task | `/v1/app/doc/extract/query/task/{task_id}` | GET |
| Application List | `/v1/app-list` | GET |
| Create Custom Application | `/v1/app-manage/create` | POST |
| Query Application Configuration | `/v1/app-manage/config` | POST |
| Delete Application | `/v1/app-manage/delete` | POST |
| AI Recommend Fields | `/v1/app-manage/ai-recommend` | POST |

---

## Version Information

**ADP CLI Version**: 1.10.0

**Last Updated**: 2026-04-03

---

## License

MIT License

---

## Contact Support

- **Project Homepage**: https://github.com/adp/adp-aiem
- **Issue Tracker**: https://github.com/adp/adp-aiem/issues
- **Documentation**: https://github.com/adp/adp-aiem/wiki

---

*This manual is automatically generated by the ADP CLI tool*
*For Agent and Skill users*
