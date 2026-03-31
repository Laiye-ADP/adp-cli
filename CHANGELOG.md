# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Concurrency control for batch processing (`--concurrency` option)
- User payment status validation (API endpoint: `/open/agentic_doc_processor/{tenant_name}/user/payment`)
- Maximum concurrency limits: 1 for free users, 2 for paid users
- Internationalized error messages for concurrency validation

## [1.0.0] - 2026-03-19

### Added
- Initial release of ADP CLI tool
- Document parsing (Parse) with support for local files, URLs, and batch processing
- Document extraction (Extract) using AI applications for structured information
- Authentication management with API Key support and local encrypted storage
- Synchronous and asynchronous task execution modes
- Multiple file format support (images, PDF, Office documents)
- QPS limit management (1/s for free users, 2/s for paid users)
- Project initialization
- Basic CLI structure and configuration
- Core command groups: config, parse, extract, query, app-id
