# CLAUDE.md – ADP CLI Operating Instructions

You are **Claude Code** operating in this repository for **ADP CLI** (AI Document Platform Command Line Tool).

---

## 0) Project Overview

**ADP CLI** is a Python-based command-line tool that provides document processing capabilities for the AI Document Platform.

### Key Features
- Document parsing (parse local/URL files)
- Document extraction (extract structured information using AI apps)
- Custom application management (create/configure/delete extraction apps)
- Task query (sync/async task monitoring)
- Authentication management (encrypted API key storage)
- Internationalization (English/Chinese)
- Cross-platform support (Windows/Linux/macOS)

### Project Structure
```
adp-cli/
├── src/adp_cli/          # Main source code
│   ├── cli.py            # CLI entry point (Click framework)
│   ├── i18n.py           # Internationalization
│   └── adp/             # Core modules
│       ├── api_client.py  # API communication
│       ├── config.py      # Configuration management
│       ├── file_handler.py # File operations
│       └── output_formatter.py # Output formatting
├── tests/                # Test suite
├── docs/                 # Documentation
└── scripts/              # Build scripts
```

### Technology Stack
- **Python**: 3.8+
- **CLI Framework**: Click
- **HTTP Client**: Requests
- **Cryptography**: Fernet (API key encryption)
- **Output Formatting**: Rich, Pygments
- **Testing**: Pytest
- **Packaging**: PyInstaller (for standalone executables)

---

## 1) Development Workflow

### 1.1 Setting Up Development Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -e ".[dev]"
```

### 1.2 Code Style and Quality

**Before committing changes**:
```bash
# Format code
black src/
isort src/

# Type checking
mypy src/

# Run tests
pytest tests/
```

### 1.3 Adding New Features

When adding new CLI commands or features:

1. **Define command structure** in [cli.py](src/adp_cli/cli.py)
   - Use Click decorators for command definition
   - Follow existing naming conventions
   - Add internationalization keys for all user-facing strings

2. **Implement core logic** in appropriate module:
   - API calls → `api_client.py`
   - File operations → `file_handler.py`
   - Configuration → `config.py`

3. **Add internationalization** in [i18n.py](src/adp_cli/i18n.py):
   - Add English and Chinese translations for new messages
   - Use `t()` function for translatable strings

4. **Write tests** in `tests/`:
   - Unit tests for individual functions
   - Integration tests for command behavior

---

### 2) CLI Command Structure

### 2.1 Command Groups

The CLI is organized into groups:

| Group | Purpose |
|-------|---------|
| `config` | Authentication and configuration |
| `parse` | Document parsing operations |
| `extract` | Document extraction operations |
| `app-id` | Application list management |
| `custom-app` | Custom application management |
| `query` | Async task status queries |

### 2.2 Global Options

- `--json`: Output in JSON format (machine-readable)
- `--quiet`: Suppress all output except errors
- `--lang`: Set language (en/zh)
- `--help, -h`: Display help
- `--version`: Display version

### 2.3 Adding a New Command

Pattern for adding new commands:

```python
@cli.command(help="__new_command_title__")
@click.option('--required-option', required=True, help="__option_description__")
@click.option('--optional-option', help="__option_description__")
@check_config  # If command requires authentication
def new_command(required_option, optional_option):
    """
    Command description.
    """
    try:
        # Implementation here
        formatter.print_success(t('success_message'))
    except Exception as e:
        formatter.print_error(f"{t('error')} {str(e)}")
        sys.exit(1)

new_command.help_key = 'new_command_title'
```

---

## 3) Core Components

### 3.1 APIClient ([api_client.py](src/adp_cli/adp/api_client.py))

Handles all API communication with the ADP platform.

**Key Methods**:
- `parse_sync()`, `parse_async()`: Document parsing
- `extract_sync()`, `extract_async()`: Document extraction
- `query_extract_task()`: Query task status
- `wait_for_task()`: Wait for async task completion
- `list_apps()`: Get available applications
- `create_custom_app()`: Create custom extraction app
- `get_custom_app_config()`: Query app configuration
- `delete_custom_app()`: Delete custom app

### 3.2 ConfigManager ([config.py](src/adp_cli/adp/config.py))

Manages local configuration and API key storage.

**Key Methods**:
- `set_api_key()`: Store encrypted API key
- `get_api_key()`: Retrieve decrypted API key
- `set()`, `get()`: Generic config operations
- `is_configured()`: Check if config is complete
- `clear()`: Clear all configuration

**Config Location**: `~/.adp/`

### 3.3 FileHandler ([file_handler.py](src/adp_cli/adp/file_handler.py))

Handles file operations and validation.

**Key Methods**:
- `get_files_from_path()`: Recursively get files
- `validate_files()`: Validate file format and size
- `read_url_list_file()`: Parse URL list files
- `write_json_output()`: Export results to file

**Supported Formats**:
- Images: .jpg, .jpeg, .png, .bmp, .tiff
- Documents: .pdf, .doc, .docx, .xls, .xlsx, .ppt, .pptx
- Max size: 50MB

### 3.4 OutputFormatter ([output_formatter.py](src/adp_cli/adp/output_formatter.py))

Handles formatted output to console.

**Key Methods**:
- `print_success()`, `print_error()`, `print_warning()`, `print_info()`
- `print_table()`: Display tabular data
- `print_json()`: Output JSON (respects --json flag)
- `print_progress()`: Show progress during batch operations

---

## 4) Internationalization (i18n)

### 4.1 Adding Translations

When adding new user-facing text:

1. **Add to translations dictionary** in [i18n.py](src/adp_cli/i18n.py):

```python
translations = {
    "en": {
        # ... existing keys
        "new_message": "New message",
    },
    "zh": {
        # ... existing keys
        "new_message": "新消息",
    },
}
```

2. **Use in code**:

```python
formatter.print_info(t('new_message'))
```

### 4.2 Language Detection Priority

1. `--lang` command-line option (highest)
2. `ADP_LANG` environment variable
3. `LANG` environment variable
4. `LC_ALL` environment variable
5. System default language

---

## 5) Testing

### 5.1 Test Structure

```
tests/
├── test_cli_integration.py  # CLI command integration tests
├── test_config.py           # Configuration management tests
├── test_file_handler.py     # File operations tests
└── test_qps_limiter.py      # Rate limiting tests
```

### 5.2 Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=src/adp_cli tests/

# Run with verbose output
pytest -v tests/
```

### 5.3 Writing Tests

Pattern for writing tests:

```python
import pytest
from pathlib import Path
from adp_cli.adp import FileHandler

def test_function_name():
    # Setup
    test_file = Path("test.txt")

    # Execute
    result = FileHandler.method(test_file)

    # Assert
    assert result is not None
    assert result["status"] == "success"
```

---

## 6) Building Executables

### 6.1 Build Process

ADP CLI can be packaged as standalone executables using PyInstaller.

**Quick Build**:
```bash
# Windows
scripts\build.bat

# Linux/macOS
./scripts/build.sh
```

**Output**: `dist/adp.exe` (Windows) or `dist/adp` (Linux/macOS)

### 6.2 Build Configuration

PyInstaller spec file: `build/adp_cli.spec`

Key settings:
- Single-file executable
- Console enabled
- UPX compression enabled
- Excludes unnecessary packages for size reduction

See [BUILD.md](docs/BUILD.md) for detailed build instructions.

---

## 7) Common Tasks

### 7.1 Adding a New CLI Command

1. Add command function to [cli.py](src/adp_cli/cli.py)
2. Add i18n keys to [i18n.py](src/adp_cli/i18n.py)
3. Add core logic to appropriate module
4. Write tests in `tests/`

### 7.2 Modifying API Behavior

1. Update [api_client.py](src/adp_cli/adp/api_client.py)
2. Update error handling and messages
3. Write/update integration tests
4. Update documentation

### 7.3 Adding New File Format Support

1. Update `SUPPORTED_EXTENSIONS` in [file_handler.py](src/adp_cli/adp/file_handler.py)
2. Update validation logic if needed
3. Add test cases for new format
4. Update documentation

### 7.4 Updating Documentation

- **User Manual**: [docs/ADP-CLI-USER-MANUAL.md](docs/ADP-CLI-USER-MANUAL.md)
- **Build Guide**: [docs/BUILD.md](docs/BUILD.md)
- **Developer Guide**: [docs/CLI-DEVELOPER-GUIDE.md](docs/CLI-DEVELOPER-GUIDE.md)
- **README**: [README.md](README.md)

---

## 8) Error Handling

### 8.1 User-Facing Errors

Always use the formatter for error messages:

```python
try:
    # Operation
    pass
except APIError as e:
    formatter.print_error(f"{t('error')} {str(e)}")
    sys.exit(1)
except ValueError as e:
    formatter.print_error(t('invalid_input', error=str(e)))
    sys.exit(1)
```

### 8.2 Common Error Patterns

- **API Key not configured**: Use `check_config` decorator
- **File not found**: Validate file path before processing
- **Invalid file type**: Use `FileHandler.validate_files()`
- **Network errors**: Catch and display user-friendly messages
- **Timeout errors**: Suggest using async mode or increasing timeout

---

## 9) Release Process

### 9.1 Version Update

1. Update version in:
   - `setup.py`
   - [cli.py](src/adp_cli/cli.py) (version_option decorator)
   - Documentation files

2. Update CHANGELOG.md

### 9.2 Testing Before Release

```bash
# Run full test suite
pytest tests/

# Build executables for all platforms
# (on each platform) ./scripts/build.sh

# Test built executables
./dist/adp --version
./dist/adp config set --api-key test_key
```

### 9.3 Publishing

```bash
# Build Python package
python setup.py sdist bdist_wheel

# Upload to PyPI (test first)
twine upload --repository testpypi dist/*
twine upload dist/*
```

---

## 10) Best Practices

### 10.1 Code Style
- Follow PEP 8
- Use Black for formatting
- Use isort for import sorting
- Add type hints where appropriate

### 10.2 API Key Security
- Never log or print API keys
- Always encrypt before storage
- Use environment variables for test keys

### 10.3 User Experience
- Provide clear error messages
- Show progress for long operations
- Support `--quiet` and `--json` modes
- Maintain backward compatibility

### 10.4 Testing
- Write tests for new features
- Maintain high test coverage
- Test both success and error cases

---

## 11) Troubleshooting

### Common Issues

**Import errors after installation**:
```bash
pip install -e . --force-reinstall --no-deps
pip install -r requirements.txt
```

**Build fails with PyInstaller**:
- Check for missing modules in `hiddenimports`
- Ensure all dependencies are installed
- Review `build/adp_cli.spec` configuration

**Encoding issues on Windows**:
- The CLI automatically configures UTF-8 output
- Ensure terminal supports UTF-8 characters

---

## 12) Resources

- **Project Homepage**: https://github.com/adp/adp-aiem
- **Issue Tracker**: https://github.com/adp/adp-aiem/issues
- **User Manual**: [docs/ADP-CLI-USER-MANUAL.md](docs/ADP-CLI-USER-MANUAL.md)
- **Build Guide**: [docs/BUILD.md](docs/BUILD.md)
- **Click Documentation**: https://click.palletsprojects.com/
- **PyInstaller Documentation**: https://pyinstaller.org/
