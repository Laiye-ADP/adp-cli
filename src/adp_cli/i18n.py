"""Internationalization (i18n) support for ADP CLI."""

import locale
import os
import click
from typing import Dict


# Translation dictionaries
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # Main CLI
        "cli_title": "ADP CLI - AI Document Platform Command Line Tool",
        "cli_description": "Command line tool for AI Document Platform, providing complete document processing capabilities. Supports document parsing, content extraction, and async task querying.",
        "quick_start": "Quick Start:",
        "global_options": "Global Options:",
        "get_more_help": "Get More Help:",
        "examples": "Examples:",

        # Global options
        "option_json": "Output in JSON format (for machine-readable results)",
        "option_quiet": "Suppress all output except errors",
        "option_lang": "Set language (en or zh)",

        # Config command
        "config_description": "Authentication configuration management.",
        "config_detail": "Manage API Key and API Base URL configurations. API Key is encrypted and stored locally.",
        "subcommands": "Subcommands:",
        "config_set_desc": "Set or update API Key / API Base URL",
        "config_get_desc": "View current configuration (API Key will be masked)",
        "config_clear_desc": "Clear all local configurations",

        # Config set
        "config_set_title": "Set or update API Key and API Base URL.",
        "config_set_detail": "API Key is encrypted and stored in local configuration file. Each call will override previous configuration items.",
        "config_set_examples": "Examples:",
        "config_get_api_key": "Get API Key:",
        "config_get_api_key_hint": "Please visit the ADP platform website to get your API Key",
        "error_not_configured": "Configuration incomplete. Please run 'adp config set' to configure API Key and API Base URL.",
        "error_api_key_or_url_required": "At least one of --api-key or --api-base-url must be provided",
        "api_key_configured": "API Key configured successfully",
        "api_base_url_configured": "API Base URL configured successfully",

        # Config get
        "config_get_title": "View current configuration.",
        "config_get_detail": "Display current configuration, API Key will be masked (only showing first 4 and last 4 characters).",
        "config_get_example": "Example:",
        "config_get_output_example": "Output Example:",

        # Config clear
        "config_clear_title": "Clear local configuration.",
        "config_clear_detail": "Delete all locally stored configurations, including API Key.",
        "config_clear_warning": "Warning:",
        "config_clear_warning_1": "- This operation cannot be undone",
        "config_clear_warning_2": "- Need to reconfigure API Key after clearing to use CLI tool",
        "confirm_clear_config": "Are you sure you want to clear all configuration?",
        "config_cleared": "Configuration cleared",

        # Parse command
        "parse_description": "Document parsing.",
        "parse_detail": "Parse documents into structured content, supporting multiple file formats. Supports synchronous or asynchronous processing, local files and URLs.",
        "parse_local_desc": "Parse local files or folders (supports batch processing)",
        "parse_url_desc": "Parse URL files or URL list files",
        "parsing_modes": "Parsing Modes:",
        "sync_mode": "Synchronous (default): Wait for processing to complete and return results",
        "async_mode": "Asynchronous (--async): Automatically wait for task completion and return results",
        "supported_formats": "Supported File Formats:",
        "formats_list": "PDF, DOCX, PPTX, XLSX, TXT, HTML, etc.",

        # Parse local
        "parse_local_title": "Parse local files or folders.",
        "parse_local_detail": "Supports single file or folder batch processing. In folder mode, all supported files will be processed recursively.",
        "parse_local_args": "Arguments:",
        "parse_local_path_arg": "path           File or folder path (required)",
        "parse_local_options": "Options:",
        "parse_local_async_option": "--async        Process asynchronously, return task ID immediately",
        "parse_local_export_option": "--export PATH  Export results to JSON file",
        "parse_local_timeout_option": "--timeout SEC  Timeout for (seconds, default: 300)",

        # Parse url
        "parse_url_title": "Parse URL files or URL list files.",
        "parse_url_detail": "The URL parameter can be a single file URL or a local file path containing a list of URLs.",
        "parse_url_arg": "url            File URL or URL list file path (required)",
        "parse_url_format_title": "URL List File Format:",

        # Parse base64
        "parse_base64_title": "Parse base64 encoded file content.",
        "parse_base64_detail": "Parse document from base64 encoded content. Useful when you already have the file in memory or from other sources.",

        # Parse query
        "parse_query_title": "Query parse async task status.",
        "parse_query_detail": "Query the status and result of a document parsing parsing async task created by 'adp parse local/url --async'.",
        "parse_result": "Parse Result",
        "extract_result": "Extract Result",

        # Extract command
        "extract_description": "Document extraction.",
        "extract_detail": "Use AI applications to perform deep content extraction on documents and extract key information. Need to first get available application IDs through 'adp app-id list'.",
        "extract_local_desc": "Extract local files or folders",
        "extract_url_desc": "Extract URL files or URL list files",
        "extraction_modes": "Extraction Modes:",
        "notes": "Notes:",
        "extract_note_1": "- extract operation requires specifying a valid app-id",
        "extract_note_2": "- Use 'adp app-id list' to view all available applications",
        "extract_note_3": "- Each application may have specific extraction rules and output formats",

        # Extract local
        "extract_local_title": "Extract local files or folders.",
        "extract_local_detail": "Use specified AI application to perform deep content extraction on documents and extract key information.",
        "extract_app_id_option": "--app-id ID    Application ID (required, use \"adp app-id list\" to view)",

        # Extract url
        "extract_url_title": "Extract URL files or URL list files.",
        "extract_url_detail": "Use specified AI application to perform deep content extraction on URL documents and extract key information.",

        # Extract base64
        "extract_base64_title": "Extract base64 encoded file content.",
        "extract_base64_detail": "Extract information from base64 encoded document content. Useful when you already have file in memory or from other sources.",

        # Extract query
        "extract_query_title": "Query extract async task status.",
        "extract_query_detail": "Query the status and result of a document extraction async task created by 'adp extract local/url --async'.",

        # Option translations
        "option_api_key": "API Key for authentication (format: sk-xxxxxxxxxxxx)",
        "option_api_base_url": "API Base URL (default: https://adp.laiye.com)",
        "option_app_id_parse": "Application ID for parsing (use \"adp app-id list\" to get available IDs)",
        "option_app_id_extract": "Application ID for extraction (use \"adp app-id list\" to get available IDs)",
        "option_async": "Process asynchronously (return task ID immediately)",
        "option_export": "Export results to JSON file",
        "option_timeout": "Timeout for sync mode (seconds, default: 300)",
        "option_concurrency": "For batch processing, concurrency defaults to 1. Free users max=1, paid users max=2. If other values are entered, concurrency will not take effect. Please wait for processing.",
        "option_file_base64": "Directly pass file content as base64 encoded string (skip file reading)",
        "option_file_name": "File name (default: document)",
        "option_watch": "Watch task until completion (polls until task finishes)",
        "option_watch_timeout": "Timeout for watch mode (seconds, default: 300)",

        # Query command
        "query_description": "Query async task status.",
        "query_arg": "task-id        Async task ID (required)",
        "query_watch_option": "--watch        Watch mode, continuously query until task completes",
        "query_timeout_option": "--timeout SEC  Watch mode timeout (seconds, default: 300)",
        "task_status": "Task Status:",
        "status_pending": "pending      Task waiting to be processed",
        "status_processing": "processing   Task being processed",
        "status_completed": "completed    Task completed",
        "status_failed": "failed       Task failed",
        "workflow": "Workflow:",
        "workflow_step_1": "1. Submit async task with --async to get task ID",
        "workflow_step_2": "2. Use adp query to check task status",
        "workflow_step_3": "3. Or use --watch to continuously monitor until task completes",
        "task_completed": "Task completed",

        # App ID command
        "app_id_description": "Application management.",
        "app_id_detail": "Manage applications available for document extraction.",
        "app_id_list_desc": "List all available application IDs and their descriptions",
        "app_id_list_app_label": "Filter applications by label (optional)",
        "output_example": "Output Example:",

        # Help command
        "help_description": "Display help information and available commands.",
        "help_detail": "Same as `--help` option, provides detailed command descriptions and usage examples.",

        # Credit command
        "credit_description": "Query remaining credits.",
        "credit_detail": "Query the remaining number of credits in your account. If you need to recharge, please visit the ADP portal website.",
        "credit_api_key": "API Key for authentication (optional if already configured)",
        "credit_info": "Credit Information",
        "remaining_credits": "Remaining Credits",
        "recharge_message": "To recharge, please visit",

        # App ID list
        "app_id_list_title": "List all available application IDs and their descriptions.",
        "app_id_list_detail": "This command displays all AI applications available for document extraction and their detailed information.",
        "output_format": "Output Format:",
        "output_format_table": "- Default: Table format (human-readable)",
        "output_format_json": "--json: JSON format (machine-readable)",
        "no_applications_found": "No applications found",
        "available_applications": "Available Applications",

        # Common
        "error": "Error:",
        "no_supported_files": "No supported files found in:",
        "skipped_invalid_files": "Skipped {count} invalid files:",
        "no_valid_files": "No valid files to process",
        "processing_files": "Processing {count} file(s)",
        "failed_to_process": "Failed to process {name}: {error}",
        "successfully_processed": "Successfully processed {count} file(s)",
        "results_exported_to": "Results exported to:",
        "processing_urls": "Processing {count} URL(s) from file",
        "processing_url": "Processing {count} URL",
        "invalid_url_format": "Invalid URL format: {url}. URL must start with http://) or https://",
        "no_valid_urls": "No valid URLs found in file:",
        "successfully_processed_urls": "Successfully processed {count} URL(s)",
        "failed_to_process_url": "Failed to process URL: {url} - {error}",
        "interrupted": "Received interrupt signal, stopping...",
        "cancelled_pending_tasks": "Cancelled {count} pending task(s)",
        "waiting_for_results": "Waiting for all results to complete...",

        # Custom App command
        "custom_app_description": "Custom extraction application management.",
        "custom_app_create_title": "Create a custom extraction application.",
        "custom_app_create_api_key": "API Key for authentication (optional if already configured)",
        "custom_app_create_app_name": "Application name (max 50 characters)",
        "custom_app_create_app_label": "Application labels (max 5 labels, optional, format: JSON array or comma-separated string)",
        "custom_app_create_extract_fields": "Field configuration in JSON format or JSON file path (required). Fields must include: field_name, field_type, field_prompt. field_type: string=text, date=date, table=table. When field_type is table, field_prompt can be empty and must have sub_fields. Sub_fields must include: field_name, field_type, field_prompt. Sub_fields field_type cannot be table, only string or date. See documentation for examples.",
        "custom_app_create_parse_mode": "Parse mode: standard=standard parsing; advance=advanced parsing; agentic=agentic parsing",
        "custom_app_create_enable_long_doc": "Enable long document support (true/false, optional)",
        "custom_app_create_long_doc_config": "Long document configuration in JSON format or JSON file path (optional, only valid when enable-long-doc=true)",
        "custom_app_get_config_title": "Query custom app configuration.",
        "custom_app_get_config_api_key": "API Key for authentication",
        "custom_app_get_config_app_id": "Application ID",
        "custom_app_get_config_config_version": "Configuration version (optional, default: latest)",
        "custom_app_list_versions_title": "List configuration versions.",
        "custom_app_list_versions_api_key": "API Key for authentication",
        "custom_app_list_versions_app_id": "Application ID",
        "custom_app_delete_title": "Delete custom app.",
        "custom_app_delete_api_key": "API Key for authentication",
        "custom_app_delete_app_id": "Application ID",
        "custom_app_delete_version_title": "Delete specified config version.",
        "custom_app_delete_version_api_key": "API Key for authentication",
        "custom_app_delete_version_app_id": "Application ID",
        "custom_app_delete_version_config_version": "Configuration version to delete",
        "custom_app_ai_generate_title": "AI generate extraction field recommendations.",
        "custom_app_ai_generate_api_key": "API Key for authentication",
        "custom_app_ai_generate_app_id": "Application ID",
        "custom_app_ai_generate_file_url": "URL of sample document",
        "custom_app_ai_generate_file_local": "Local of sample document",
        "error_invalid_json_format": "Invalid JSON format: {error}",
        "error_read_json_file": "Failed to read JSON file: {error}",
        "error_file_url_or_local_required": "Either --file-url or --file-local must be provided",
        "error_file_url_local_or_base64_required": "Either --file-url, --file-local or --file-base64 must be provided",
        "app_created": "Custom app created successfully",
        "app_config": "App Configuration",
        "config_versions": "Configuration Versions",
        "app_deleted": "App deleted successfully",
        "version_deleted": "Version deleted successfully",
        "no_versions_found": "No versions found",
        "available_versions": "Available Versions",
        "error_invalid_concurrency": "Free users: 1, paid users: 2, other values are invalid",
        "error_not_paid_user": "You are a free user, maximum concurrency is 1",
    },

    "zh": {
        # Main CLI
        "cli_title": "ADP CLI - AI 文档平台命令行工具",
        "cli_description": "AI 文档平台命令行工具，提供完整的文档处理能力。支持文档解析、内容抽取、异步任务查询等功能。",
        "quick_start": "快速开始:",
        "global_options": "全局选项:",
        "get_more_help": "获取更多帮助:",
        "examples": "示例:",

        # Global options
        "option_json": "输出为 JSON 格式（机器可读）",
        "option_quiet": "除错误外抑制所有输出",
        "option_lang": "设置语言 (en 或 zh)",

        # Config command
        "config_description": "认证配置管理。",
        "config_detail": "管理 API Key 和 API Base URL 等配置信息。API Key 会加密存储在本地。",
        "subcommands": "子命令:",
        "config_set_desc": "设置或更新 API Key / API Base URL",
        "config_get_desc": "查看当前配置 (API Key 会脱敏显示)",
        "config_clear_desc": "清除所有本地配置",

        # Config set
        "config_set_title": "设置或更新 API Key 和 API Base URL。",
        "config_set_detail": "API Key 会被加密存储在本地配置文件中。每次调用都会覆盖之前的配置项。",
        "config_set_examples": "示例:",
        "config_get_api_key": "获取 API Key:",
        "config_get_api_key_hint": "请访问 ADP 平台官网获取您的 API Key",
        "error_not_configured": "配置未完成，请先运行 'adp config set' 配置 API Key 和 API Base URL。",
        "error_api_key_or_url_required": "必须提供 --api-key 或 --api-base-url 中的至少一个",
        "api_key_configured": "API Key 配置成功",
        "api_base_url_configured": "API Base URL 配置成功",

        # Config get
        "config_get_title": "查看当前配置。",
        "config_get_detail": "显示当前配置信息，API Key 会进行脱敏处理(只显示前 4 位和后 4 位)。",
        "config_get_example": "示例:",
        "config_get_output_example": "输出示例:",

        # Config clear
        "config_clear_title": "清除本地配置。",
        "config_clear_detail": "删除所有本地存储的配置信息，包括 API Key。",
        "config_clear_warning": "警告:",
        "config_clear_warning_1": "- 此操作不可撤销",
        "config_clear_warning_2": "- 清除后需要重新配置 API Key 才能使用 CLI 工具",
        "confirm_clear_config": "确定要清除所有配置吗?",
        "config_cleared": "配置已清除",

        # Parse command
        "parse_description": "文档解析。",
        "parse_detail": "将文档解析为结构化内容，支持多种文件格式。可以同步或异步处理，支持本地文件和 URL。",
        "parse_local_desc": "解析本地文件或文件夹 (支持批量处理)",
        "parse_url_desc": "解析 URL 文件或 URL 列表文件",
        "parsing_modes": "解析模式:",
        "sync_mode": "同步模式 (默认): 等待处理完成并返回结果",
        "async_mode": "异步模式 (--async): 自动等待任务完成并返回结果",
        "supported_formats": "支持的文件格式:",
        "formats_list": "PDF, DOCX, PPTX, XLSX, TXT, HTML 等",

        # Parse local
        "parse_local_title": "解析本地文件或文件夹。",
        "parse_local_detail": "支持单个文件或文件夹批量处理。文件夹模式下会递归处理所有支持的文件。",
        "parse_local_args": "参数:",
        "parse_local_path_arg": "path           文件或文件夹路径 (必需)",
        "parse_local_options": "选项:",
        "parse_local_async_option": "--async        异步处理，立即返回任务 ID",
        "parse_local_export_option": "--export PATH  导出结果到 JSON 文件",
        "parse_local_timeout_option": "--timeout SEC  同步模式超时时间 (秒，默认 300)",

        # Parse url
        "parse_url_title": "解析 URL 文件或 URL 列表文件。",
        "parse_url_detail": "URL 参数可以是单个文件 URL，也可以是包含 URL 列表的本地文件路径。",
        "parse_url_arg": "url            文件 URL 或 URL 列表文件路径 (必需)",
        "parse_url_format_title": "URL 列表文件格式:",

        # Parse base64
        "parse_base64_title": "解析 base64 编码的文件内容。",
        "parse_base64_detail": "从 base64 编码的内容解析文档。适用于文件已在内存中或从其他来源获取的情况。",

        # Parse query
        "parse_query_title": "查询解析异步任务状态。",
        "parse_query_detail": "查询由 'adp parse local/url --async' 创建的文档解析异步任务的状态和结果。",
        "parse_result": "解析结果",
        "extract_result": "抽取结果",

        # Extract command
        "extract_description": "文档抽取。",
        "extract_detail": "使用 AI 应用对文档进行深度内容抽取，提取关键信息。需要先通过 'adp app-id list' 获取可用的应用 ID。",
        "extract_local_desc": "抽取本地文件或文件夹",
        "extract_url_desc": "抽取 URL 文件或 URL 列表文件",
        "extraction_modes": "抽取模式:",
        "notes": "注意事项:",
        "extract_note_1": "- extract 操作需要指定有效的 app-id",
        "extract_note_2": "- 使用 'adp app-id list' 查看所有可用应用",
        "extract_note_3": "- 每个应用可能有特定的抽取规则和输出格式",

        # Extract local
        "extract_local_title": "抽取本地文件或文件夹。",
        "extract_local_detail": "使用指定的 AI 应用对文档进行深度内容抽取，提取关键信息。",
        "extract_app_id_option": "--app-id ID    应用 ID (必需，使用 \"adp app-id list list\" 查看)",

        # Extract url
        "extract_url_title": "抽取 URL 文件或 URL 列表文件。",
        "extract_url_detail": "使用指定的 AI 应用对 URL 文档进行深度内容抽取，提取关键信息。",

        # Extract base64
        "extract_base64_title": "抽取 base64 编码的文件内容。",
        "extract_base64_detail": "从 base64 编码的文档内容中抽取信息。适用于文件已在内存中或从其他来源获取的情况。",

        # Extract query
        "extract_query_title": "查询抽取异步任务状态。",
        "extract_query_detail": "查询由 'adp extract local/url --async' 创建的文档抽取异步任务的状态和结果。",

        # Option translations
        "option_api_key": "API 认证密钥（格式: sk-xxxxxxxxxxxx）",
        "option_api_base_url": "API Base URL (默认: https://adp.laiye.com)",
        "option_app_id_parse": "解析的应用 ID (使用 \"adp app-id list\" 获取可用 ID)",
        "option_app_id_extract": "抽取的应用 ID (使用 \"adp app-id list\" 获取可用 ID)",
        "option_async": "异步处理，立即返回任务 ID",
        "option_export": "导出结果到 JSON 文件",
        "option_timeout": "同步模式超时时间（秒，默认 300）",
        "option_concurrency": "批量处理时，并发数默认为 1。免费用户最高为 1，付费用户最高为 2。若输入其他数值，并发将不生效，请等待处理。",
        "option_file_base64": "直接传入文件的 base64 编码内容（跳过文件读取）",
        "option_file_name": "文件名（默认: document）",
        "option_watch": "监视任务直到完成（轮询直到任务结束）",
        "option_watch_timeout": "监视模式超时时间（秒，默认 300）",

        # Query command
        "query_description": "查询异步任务状态。",
        "query_arg": "task-id        异步任务 ID (必需)",
        "query_watch_option": "--watch        监视模式，持续查询直到任务完成",
        "query_timeout_option": "--timeout SEC  监视模式超时时间 (秒，默认 300)",
        "task_status": "任务状态:",
        "status_pending": "pending      任务等待处理",
        "status_processing": "processing   任务处理中",
        "status_completed": "completed    任务完成",
        "status_failed": "failed       任务失败",
        "workflow": "工作流程:",
        "workflow_step_1": "1. 使用 --async 提交异步任务，获取任务 ID",
        "workflow_step_2": "2. 使用 adp query 查询任务状态",
        "workflow_step_3": "3. 或使用 --watch 持续监视直到任务完成",
        "task_completed": "任务完成",

        # App ID command
        "app_id_description": "应用管理。",
        "app_id_detail": "管理可用于文档抽取的应用。",
        "app_id_list_desc": "列出所有可用的应用 ID 及其描述",
        "output_example": "输出示例:",

        # Help command
        "help_description": "显示帮助信息和可用命令。",
        "help_detail": "与 `--help` 选项相同，提供命令的详细说明和使用示例。",

        # Credit command
        "credit_description": "查询剩余资产数。",
        "credit_detail": "查询账户中的剩余资产数。如需充值，请访问 ADP 门户网站。",
        "credit_api_key": "API 认证密钥（可选，如果已配置则不需要）",
        "credit_info": "资产信息",
        "remaining_credits": "剩余资产",
        "recharge_message": "充值请访问",

        # App ID list
        "app_id_list_title": "列出所有可用的应用 ID 及其描述。",
        "app_id_list_detail": "此命令会显示所有可用于文档抽取的 AI 应用及其详细信息。",
        "output_format": "输出格式:",
        "output_format_table": "- 默认: 表格格式 (人类可读)",
        "output_format_json": "--json: JSON 格式 (机器可读)",
        "no_applications_found": "未找到应用",
        "available_applications": "可用应用",

        # Common
        "error": "错误:",
        "error_invalid_concurrency": "并发数无效。批量处理时：免费用户最高为1，付费用户最高为2。若输入其他数值，并发将不生效，请等待处理。",
        "no_supported_files": "未找到支持的文件:",
        "skipped_invalid_files": "跳过 {count} 个无效文件:",
        "no_valid_files": "没有有效的文件需要处理",
        "processing_files": "正在处理 {count} 个文件",
        "failed_to_process": "处理失败 {name}: {error}",
        "successfully_processed": "成功处理 {count} 个文件",
        "results_exported_to": "结果已导出到:",
        "processing_urls": "正在处理文件中的 {count} 个 URL",
        "processing_url": "正在处理 {count} 个 URL",
        "invalid_url_format": "无效的 URL 格式: {url}。URL 必须以 http:// 或 https:// 开头",
        "no_valid_urls": "文件中未找到有效的 URL:",
        "successfully_processed_urls": "成功处理 {count} 个 URL",
        "failed_to_process_url": "处理 URL 失败: {url} - {error}",
        "interrupted": "接收到中断信号，正在停止...",
        "cancelled_pending_tasks": "已取消 {count} 个待处理任务",
        "waiting_for_results": "等待所有结果完成...",

        # Custom App command
        "custom_app_description": "自定义抽取应用管理。",
        "custom_app_create_title": "创建自定义抽取应用。",
        "custom_app_create_api_key": "API 认证密钥（可选，如果已配置则不需要）",
        "custom_app_create_app_name": "应用名称 (最多 50 个字符)",
        "custom_app_create_app_label": "应用标签（最多5个，可选，格式：JSON 数组或逗号分隔字符串）",
        "custom_app_create_extract_fields": "字段配置，JSON 格式或 JSON 文件路径（必需）。字段需要包含 field_name（字段名）、field_type（字段类型）、field_prompt（字段提示词）。field_type 可选值：string（文本）、date（日期）、table（表格）。table 类型时 field_prompt 可为空，需包含 sub_fields（表格子字段）。表格子字段的 field_type 只能为 string 或 date。参见文档查看示例。",
        "custom_app_create_parse_mode": "解析模式：standard=标准解析；advance=增强解析；agentic=智能体解析",
        "custom_app_create_enable_long_doc": "启用长文档支持 (true/false，可选)",
        "custom_app_create_long_doc_config": "长文档配置，JSON 格式或 JSON 文件路径（可选，仅当 enable-long-doc=true 时生效）",
        "custom_app_get_config_title": "查询自定义应用配置。",
        "custom_app_get_config_api_key": "API 认证密钥",
        "custom_app_get_config_app_id": "应用 ID",
        "custom_app_get_config_config_version": "配置版本 (可选，默认: 最新版)",
        "custom_app_list_versions_title": "列出配置版本。",
        "custom_app_list_versions_api_key": "API 认证密钥",
        "custom_app_list_versions_app_id": "应用 ID",
        "custom_app_delete_title": "删除自定义应用。",
        "app_id_list_app_label": "按标签过滤应用（可选）",
        "custom_app_delete_api_key": "API 认证密钥",
        "custom_app_delete_app_id": "应用 ID",
        "custom_app_delete_version_title": "删除指定配置版本。",
        "custom_app_delete_version_api_key": "API 认证密钥",
        "custom_app_delete_version_app_id": "应用 ID",
        "custom_app_delete_version_config_version": "要删除的配置版本",
        "custom_app_ai_generate_title": "AI 生成抽取字段推荐。",
        "custom_app_ai_generate_api_key": "API 认证密钥",
        "custom_app_ai_generate_app_id": "应用 ID",
        "custom_app_ai_generate_file_url": "示例文档 URL",
        "custom_app_ai_generate_file_local": "本地示例文档",
        "error_invalid_json_format": "无效的 JSON 格式: {error}",
        "error_read_json_file": "读取 JSON 文件失败: {error}",
        "error_file_url_or_local_required": "必须提供 --file-url 或 --file-local 中的一个",
        "error_file_url_local_or_base64_required": "必须提供 --file-url、--file-local 或 --file-base64 中的一个",
        "app_created": "自定义应用创建成功",
        "app_config": "应用配置",
        "config_versions": "配置版本",
        "app_deleted": "应用删除成功",
        "version_deleted": "版本删除成功",
        "no_versions_found": "未找到版本",
        "available_versions": "可用版本",
        "error_invalid_concurrency": "免费用户：1，付费用户：2，输入其他值无效",
        "error_not_paid_user": "您是免费用户，最大并发数为1",
    },
}


def get_system_language() -> str:
    """Detect system language and return 'zh' for Chinese, 'en' otherwise."""
    # Try multiple sources for language detection
    lang = (
        os.environ.get('ADP_LANG') or
        os.environ.get('LANG', '').split('.')[0].split('_')[0] or
        os.environ.get('LC_ALL', '').split('.')[0].split('_')[0] or
        locale.getdefaultlocale()[0] or
        'en'
    )

    # Normalize language code
    lang = lang.lower()

    # Return 'zh' for any Chinese variant, otherwise 'en'
    if lang.startswith('zh'):
        return 'zh'
    return 'en'


# Global language setting (can be overridden)
_current_language = get_system_language()


def set_language(lang: str) -> None:
    """Set language explicitly."""
    global _current_language
    if lang not in TRANSLATIONS:
        lang = 'en'
    _current_language = lang


def get_language() -> str:
    """Get current language."""
    return _current_language


def t(key: str, **kwargs) -> str:
    """
    Get translated text for a given key.

    Args:
        key: Translation key
        **kwargs: Format arguments

    Returns:
        Translated text with arguments formatted
    """
    text = TRANSLATIONS.get(_current_language, TRANSLATIONS['en']).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


class I18nHelpFormatter(click.HelpFormatter):
    """Custom HelpFormatter that supports i18n."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write(self, text):
        """Write text with i18n support for specific keys."""
        # Try to translate if text matches a known key pattern
        for key, value in TRANSLATIONS.get(_current_language, {}).items():
            if text.strip() == value.strip():
                text = text.replace(value, t(key))
                break
        super().write(text)


# Global formatter instance
_help_formatter = I18nHelpFormatter()


def get_help_formatter() -> I18nHelpFormatter:
    """Get the global help formatter instance."""
    return _help_formatter


def reset_help_formatter():
    """Reset the help formatter (useful when language changes)."""
    global _help_formatter
    _help_formatter = I18nHelpFormatter()
