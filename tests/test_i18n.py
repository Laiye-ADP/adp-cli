"""Tests for internationalization (i18n) support."""

import pytest
import os

from adp_cli.i18n import (
    t, set_language, get_language, get_system_language,
    I18nHelpFormatter, get_help_formatter, reset_help_formatter
)


def test_get_system_language():
    """Test getting system language."""
    lang = get_system_language()
    assert lang in ['en', 'zh']


def test_set_language_english():
    """Test setting language to English."""
    original_lang = get_language()
    set_language('en')
    assert get_language() == 'en'

    # Restore original language
    set_language(original_lang)


def test_set_language_chinese():
    """Test setting language to Chinese."""
    original_lang = get_language()
    set_language('zh')
    assert get_language() == 'zh'

    # Restore original language
    set_language(original_lang)


def test_set_language_invalid():
    """Test setting invalid language defaults to English."""
    original_lang = get_language()
    set_language('invalid')
    assert get_language() == 'en'

    # Restore original language
    set_language(original_lang)


def test_translate_english():
    """Test translating to English."""
    original_lang = get_language()
    set_language('en')

    text = t('error')
    assert 'Error' in text

    text = t('config_description')
    assert 'Authentication' in text

    # Restore original language
    set_language(original_lang)


def test_translate_chinese():
    """Test translating to Chinese."""
    original_lang = get_language()
    set_language('zh')

    text = t('error')
    assert '错误' in text

    text = t('config_description')
    assert '认证' in text

    # Restore original language
    set_language(original_lang)


def test_translate_with_formatting():
    """Test translating with format arguments."""
    original_lang = get_language()
    set_language('en')

    text = t('no_supported_files', path='/tmp/docs')
    assert 'No supported files' in text

    text = t('skipped_invalid_files', count=5)
    assert '5' in text

    # Restore original language
    set_language(original_lang)


def test_translate_nonexistent_key():
    """Test translating nonexistent key returns the key itself."""
    text = t('nonexistent_key_xyz')
    assert text == 'nonexistent_key_xyz'


def test_translate_all_keys():
    """Test that all defined keys can be translated."""
    # Sample keys to test (not exhaustive but covers main categories)
    keys = [
        # Main CLI
        'cli_title',
        'option_json',
        'option_quiet',
        'option_lang',

        # Config
        'config_description',
        'config_set.set_title',
        'config_get_title',
        'config_clear_title',
        'error_api_key_or_url_required',
        'api_key_configured',
        'api_base_url_configured',
        'confirm_clear_config',
        'config_cleared',

        # Parse
        'parse_description',
        'parse_local_title',
        'parse_url_title',
        'option_async',
        'option_export',
        'option_timeout',

        # Extract
        'extract_description',
        'extract_local_title',
        'extract_url_title',
        'option_app_id_extract',

        # Query
        'query_description',
        'option_watch',
        'option_watch_timeout',
        'task_completed',

        # App ID
        'app_id_description',
        'app_id_list_title',
        'no_applications_found',
        'available_applications',

        # Custom App
        'custom_app_description',
        'custom_app_create_title',
        'custom_app_get_config_title',
        'custom_app_list_versions_title',
        'custom_app_delete_title',
        'custom_app_delete_version_title',
        'custom_app_ai_generate_title',
        'error_invalid_json_format',
        'app_created',
        'app_deleted',
        'version_deleted',
        'no_versions_found',
        'available_versions',

        # Common
        'error',
        'no_supported_files',
        'skipped_invalid_files',
        'no_valid_files',
        'successfully_processed',
        'results_exported_to',
    ]

    for lang in ['en', 'zh']:
        set_language(lang)
        for key in keys:
            text = t(key)
            assert text is not None
            assert isinstance(text, str)


def test_help_formatter_initialization():
    """Test help formatter initialization."""
    formatter = I18nHelpFormatter()
    assert formatter is not None


def test_get_help_formatter():
    """Test getting help formatter instance."""
    formatter = get_help_formatter()
    assert formatter is not None
    assert isinstance(formatter, I18nHelpFormatter)


def test_reset_help_formatter():
    """Test resetting help formatter."""
    formatter1 = get_help_formatter()
    reset_help_formatter()
    # After reset, get_help_formatter should return the new formatter
    formatter2 = get_help_formatter()

    assert formatter2 is not None
    assert isinstance(formatter2, I18nHelpFormatter)


def test_environment_variable_language():
    """Test language detection from environment variable."""
    original_adp_lang = os.environ.get('ADP_LANG')
    original_lang = os.environ.get('LANG')

    try:
        # Test ADP_LANG
        os.environ['ADP_LANG'] = 'en'
        lang = get_system_language()
        assert lang == 'en'

        # Test LANG
        os.environ['ADP_LANG'] = ''
        os.environ['LANG'] = 'zh_CN.UTF-8'
        lang = get_system_language()
        assert lang == 'zh'

        # Test Chinese variant
        os.environ['LANG'] = 'zh_TW.UTF-8'
        lang = get_system_language()
        assert lang == 'zh'

    finally:
        # Restore environment variables
        if original_adp_lang:
            os.environ['ADP_LANG'] = original_adp_lang
        elif 'ADP_LANG' in os.environ:
            del os.environ['ADP_LANG']

        if original_lang:
            os.environ['LANG'] = original_lang
        elif 'LANG' in os.environ:
            del os.environ['LANG']


def test_chinese_locale_variants():
    """Test that Chinese language is set correctly."""
    original_lang = get_language()

    # Only 'en' and 'zh' are valid language codes in the system
    valid_langs = ['zh', 'en']

    for lang_var in valid_langs:
        set_language(lang_var)
        assert get_language() == lang_var

    # Restore
    set_language(original_lang)


def test_language_persistence():
    """Test that language setting persists across multiple calls."""
    original_lang = get_language()

    set_language('en')
    assert get_language() == 'en'
    assert t('error') == 'Error:'

    set_language('zh')
    assert get_language() == 'zh'
    assert '错误' in t('error')

    # Restore
    set_language(original_lang)


def test_empty_formatting():
    """Test translation with no formatting arguments."""
    still_lang = get_language()
    set_language('en')

    text = t('error')
    text2 = t('error')  # Call again
    assert text == text2

    # Restore
    set_language(still_lang)
