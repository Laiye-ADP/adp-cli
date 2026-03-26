============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.2, pluggy-1.6.0 -- D:\ADP\adp-cli\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: d:\ADP\adp-cli
configfile: pyproject.toml
plugins: cov-7.1.0
collecting ... collected 147 items

tests/test_api_client.py::test_api_client_initialization PASSED          [  0%]
tests/test_api_client.py::test_get_api_base_url_default PASSED           [  1%]
tests/test_api_client.py::test_get_api_base_url_custom PASSED            [  2%]
tests/test_api_client.py::test_get_headers PASSED                        [  2%]
tests/test_api_client.py::test_get_headers_no_api_key PASSED             [  3%]
tests/test_api_client.py::test_encode_file_to_base64 PASSED              [  4%]
tests/test_api_client.py::test_get_mime_type PASSED                      [  4%]
tests/test_api_client.py::test_parse_sync_with_url PASSED                [  5%]
tests/test_api_client.py::test_parse_async_with_url PASSED               [  6%]
tests/test_api_client.py::test_extract_sync PASSED                       [  6%]
tests/test_api_client.py::test_extract_async PASSED                      [  7%]
tests/test_api_client.py::test_query_extract_task PASSED                 [  8%]
tests/test_api_client.py::test_list_apps PASSED                          [  8%]
tests/test_api_client.py::test_create_custom_app PASSED                  [  9%]
tests/test_api_client.py::test_create_custom_app_long_doc_config_validation PASSED [ 10%]
tests/test_api_client.py::test_get_custom_app_config PASSED              [ 10%]
tests/test_api_client.py::test_list_custom_app_versions PASSED           [ 11%]
tests/test_api_client.py::test_delete_custom_app PASSED                  [ 12%]
tests/test_api_client.py::test_delete_custom_app_version PASSED          [ 12%]
tests/test_api_client.py::test_ai_generate_fields_with_url PASSED        [ 13%]
tests/test_api_client.py::test_ai_generate_fields_no_file PASSED         [ 14%]
tests/test_api_client.py::test_wait_for_task_success PASSED              [ 14%]
tests/test_api_client.py::test_wait_for_task_failed PASSED               [ 15%]
tests/test_api_client.py::test_wait_for_task_timeout PASSED              [ 16%]
tests/test_api_client.py::test_health_check_success PASSED               [ 17%]
tests/test_api_client.py::test_health_check_failure PASSED               [ 17%]
tests/test_api_client.py::test_task_status_constants PASSED              [ 18%]
tests/test_cli_commands.py::test_cli_help PASSED                         [ 19%]
tests/test_cli_commands.py::test_cli_version PASSED                      [ 19%]
tests/test_cli_commands.py::test_cli_custom_help_command PASSED          [ 20%]
tests/test_cli_commands.py::test_config_help PASSED                      [ 21%]
tests/test_cli_commands.py::test_config_set_api_key PASSED               [ 21%]
tests/test_cli_commands.py::test_config_set_api_base_url PASSED          [ 22%]
tests/test_cli_commands.py::test_config_set_no_args PASSED               [ 23%]
tests/test_cli_commands.py::test_config_get PASSED                       [ 23%]
tests/test_cli_commands.py::test_config_clear_with_confirmation PASSED   [ 24%]
tests/test_cli_commands.py::test_parse_help PASSED                       [ 25%]
tests/test_cli_commands.py::test_parse_local_help PASSED                 [ 25%]
tests/test_cli_commands.py::test_parse_url_help PASSED                   [ 26%]
tests/test_cli_commands.py::test_parse_local_no_config PASSED            [ 27%]
tests/test_cli_commands.py::test_extract_help PASSED                     [ 27%]
tests/test_cli_commands.py::test_extract_local_help PASSED               [ 28%]
tests/test_cli_commands.py::test_extract_url_help PASSED                 [ 29%]
tests/test_cli_commands.py::test_extract_local_no_config PASSED          [ 29%]
tests/test_cli_commands.py::test_query_help PASSED                       [ 30%]
tests/test_cli_commands.py::test_query_no_config PASSED                  [ 31%]
tests/test_cli_commands.py::test_app_id_help PASSED                      [ 31%]
tests/test_cli_commands.py::test_app_id_list_help PASSED                 [ 32%]
tests/test_cli_commands.py::test_app_id_list_no_config PASSED            [ 33%]
tests/test_cli_commands.py::test_custom_app_help PASSED                  [ 34%]
tests/test_cli_commands.py::test_custom_app_create_help PASSED           [ 34%]
tests/test_cli_commands.py::test_custom_app_get_config_help PASSED       [ 35%]
tests/test_cli_commands.py::test_custom_app_list_versions_help PASSED    [ 36%]
tests/test_cli_commands.py::test_custom_app_delete_help PASSED           [ 36%]
tests/test_cli_commands.py::test_custom_app_delete_version_help PASSED   [ 37%]
tests/test_cli_commands.py::test_custom_app_ai_generate_help PASSED      [ 38%]
tests/test_cli_commands.py::test_json_mode_flag PASSED                   [ 38%]
tests/test_cli_commands.py::test_lang_flag PASSED                        [ 39%]
tests/test_cli_commands.py::test_invalid_command PASSED                  [ 40%]
tests/test_cli_commands.py::test_parse_json_param_value_string PASSED    [ 40%]
tests/test_cli_commands.py::test_parse_json_param_value_file PASSED      [ 41%]
tests/test_cli_commands.py::test_parse_json_param_value_none PASSED      [ 42%]
tests/test_cli_commands.py::test_parse_json_param_value_with_quotes PASSED [ 42%]
tests/test_cli_commands.py::test_parse_bool_param_true PASSED            [ 43%]
tests/test_cli_commands.py::test_parse_bool_param_false PASSED           [ 44%]
tests/test_cli_commands.py::test_parse_bool_param_none PASSED            [ 44%]
tests/test_cli_commands.py::test_parse_json_list_param_json_array PASSED [ 45%]
tests/test_cli_commands.py::test_parse_json_list_param_comma_separated PASSED [ 46%]
tests/test_cli_commands.py::test_parse_json_list_param_with_quotes PASSED [ 46%]
tests/test_cli_commands.py::test_parse_json_list_param_none PASSED       [ 47%]
tests/test_cli_commands.py::test_parse_json_list_param_with_spaces PASSED [ 48%]
tests/test_cli_commands.py::test_validate_create_app_params_valid PASSED [ 48%]
tests/test_cli_commands.py::test_validate_create_app_params_app_name_too_long PASSED [ 49%]
tests/test_cli_commands.py::test_validate_create_app_params_app_label_too_many PASSED [ 50%]
tests/test_cli_commands.py::test_validate_create_app_params_long_doc_config_without_enable PASSED [ 51%]
tests/test_cli_commands.py::test_parse_local_file PASSED                 [ 51%]
tests/test_cli_commands.py::test_extract_local_file PASSED               [ 52%]
tests/test_cli_integration.py::TestCLIIntegration::test_help_command PASSED [ 53%]
tests/test_cli_integration.py::TestCLIIntegration::test_version_command PASSED [ 53%]
tests/test_cli_integration.py::TestCLIIntegration::test_config_help PASSED [ 54%]
tests/test_cli_integration.py::TestCLIIntegration::test_parse_help PASSED [ 55%]
tests/test_cli_integration.py::TestCLIIntegration::test_extract_help PASSED [ 55%]
tests/test_cli_integration.py::TestCLIIntegration::test_query_help PASSED [ 56%]
tests/test_cli_integration.py::TestCLIIntegration::test_app_id_help PASSED [ 57%]
tests/test_cli_integration.py::TestCLIE2E::test_complete_workflow PASSED [ 57%]
tests/test_config.py::test_config_manager_init PASSED                    [ 58%]
tests/test_config.py::test_set_and_get_api_key PASSED                    [ 59%]
tests/test_config.py::test_get_api_key_masked PASSED                     [ 59%]
tests/test_config.py::test_set_and_get_config PASSED                     [ 60%]
tests/test_config.py::test_get_default_value PASSED                      [ 61%]
tests/test_config.py::test_clear_config PASSED                           [ 61%]
tests/test_config.py::test_is_configured PASSED                          [ 62%]
tests/test_config.py::test_get_config_summary PASSED                     [ 63%]
tests/test_file_handler.py::test_is_supported_file PASSED                [ 63%]
tests/test_file_handler.py::test_is_valid_size PASSED                    [ 64%]
tests/test_file_handler.py::test_validate_file PASSED                    [ 65%]
tests/test_file_handler.py::test_get_files_from_path_file PASSED         [ 65%]
tests/test_file_handler.py::test_get_files_from_path_directory PASSED    [ 66%]
tests/test_file_handler.py::test_validate_files PASSED                   [ 67%]
tests/test_file_handler.py::test_format_file_size PASSED                 [ 68%]
tests/test_file_handler.py::test_batch_process PASSED                    [ 68%]
tests/test_i18n.py::test_get_system_language PASSED                      [ 69%]
tests/test_i18n.py::test_set_language_english PASSED                     [ 70%]
tests/test_i18n.py::test_set_language_chinese PASSED                     [ 70%]
tests/test_i18n.py::test_set_language_invalid PASSED                     [ 71%]
tests/test_i18n.py::test_translate_english PASSED                        [ 72%]
tests/test_i18n.py::test_translate_chinese PASSED                        [ 72%]
tests/test_i18n.py::test_translate_with_formatting PASSED                [ 73%]
tests/test_i18n.py::test_translate_nonexistent_key PASSED                [ 74%]
tests/test_i18n.py::test_translate_all_keys PASSED                       [ 74%]
tests/test_i18n.py::test_help_formatter_initialization PASSED            [ 75%]
tests/test_i18n.py::test_get_help_formatter PASSED                       [ 76%]
tests/test_i18n.py::test_reset_help_formatter PASSED                     [ 76%]
tests/test_i18n.py::test_environment_variable_language PASSED            [ 77%]
tests/test_i18n.py::test_chinese_locale_variants PASSED                  [ 78%]
tests/test_i18n.py::test_language_persistence PASSED                     [ 78%]
tests/test_i18n.py::test_empty_formatting PASSED                         [ 79%]
tests/test_output_formatter.py::test_formatter_initialization PASSED     [ 80%]
tests/test_output_formatter.py::test_set_json_mode PASSED                [ 80%]
tests/test_output_formatter.py::test_set_quiet_mode PASSED               [ 81%]
tests/test_output_formatter.py::test_print PASSED                        [ 82%]
tests/test_output_formatter.py::test_print_quiet_mode PASSED             [ 82%]
tests/test_output_formatter.py::test_print_success PASSED                [ 83%]
tests/test_output_formatter.py::test_print_error PASSED                  [ 84%]
tests/test_output_formatter.py::test_print_warning PASSED                [ 85%]
tests/test_output_formatter.py::test_print_info PASSED                   [ 85%]
tests/test_output_formatter.py::test_print_json_normal_mode PASSED       [ 86%]
tests/test_output_formatter.py::test_print_json_with_complex_data PASSED [ 87%]
tests/test_output_formatter.py::test_print_json_mode PASSED              [ 87%]
tests/test_output_formatter.py::test_print_table PASSED                  [ 88%]
tests/test_output_formatter.py::test_print_table_with_title PASSED       [ 89%]
tests/test_output_formatter.py::test_print_panel PASSED                  [ 89%]
tests/test_output_formatter.py::test_print_task_result PASSED            [ 90%]
tests/test_output_formatter.py::test_print_task_result_without_result PASSED [ 91%]
tests/test_output_formatter.py::test_print_file_list PASSED              [ 91%]
tests/test_output_formatter.py::test_print_file_list_without_size PASSED [ 92%]
tests/test_output_formatter.py::test_print_config_summary PASSED         [ 93%]
tests/test_output_formatter.py::test_print_progress PASSED               [ 93%]
tests/test_output_formatter.py::test_print_progress_zero_total PASSED    [ 94%]
tests/test_output_formatter.py::test_print_section PASSED                [ 95%]
tests/test_output_formatter.py::test_formatter_with_direct_console_initialization PASSED [ 95%]
tests/test_output_formatter.py::test_print_json_with_list PASSED         [ 96%]
tests/test_output_formatter.py::test_print_json_with_unicode PASSED      [ 97%]
tests/test_output_formatter.py::test_print_json_with_special_characters PASSED [ 97%]
tests/test_output_formatter.py::test_print_empty_table PASSED            [ 98%]
tests/test_output_formatter.py::test_print_multiple_sections PASSED      [ 99%]
tests/test_output_formatter.py::test_print_task_result_with_large_data PASSED [100%]

============================== warnings summary ===============================
src\adp_cli\i18n.py:416
tests/test_i18n.py::test_get_system_language
  D:\ADP\adp-cli\src\adp_cli\i18n.py:416: DeprecationWarning: 'locale.getdefaultlocale' is deprecated and slated for removal in Python 3.15. Use setlocale(), getencoding() and getlocale() instead.
    locale.getdefaultlocale()[0] or

tests/test_cli_integration.py::TestCLIIntegration::test_help_command
  D:\ADP\adp-cli\.venv\Lib\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-1 (_readerthread)
  
  Traceback (most recent call last):
    File "D:\Programs\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
      self.run()
    File "D:\Programs\Python312\Lib\threading.py", line 1012, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Programs\Python312\Lib\subprocess.py", line 1599, in _readerthread
      buffer.append(fh.read())
                    ^^^^^^^^^
  UnicodeDecodeError: 'gbk' codec can't decode byte 0xad in position 147: illegal multibyte sequence
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

tests/test_cli_integration.py::TestCLIIntegration::test_config_help
  D:\ADP\adp-cli\.venv\Lib\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-5 (_readerthread)
  
  Traceback (most recent call last):
    File "D:\Programs\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
      self.run()
    File "D:\Programs\Python312\Lib\threading.py", line 1012, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Programs\Python312\Lib\subprocess.py", line 1599, in _readerthread
      buffer.append(fh.read())
                    ^^^^^^^^^
  UnicodeDecodeError: 'gbk' codec can't decode byte 0x82 in position 89: illegal multibyte sequence
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

tests/test_cli_integration.py::TestCLIIntegration::test_parse_help
  D:\ADP\adp-cli\.venv\Lib\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-7 (_readerthread)
  
  Traceback (most recent call last):
    File "D:\Programs\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
      self.run()
    File "D:\Programs\Python312\Lib\threading.py", line 1012, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Programs\Python312\Lib\subprocess.py", line 1599, in _readerthread
      buffer.append(fh.read())
                    ^^^^^^^^^
  UnicodeDecodeError: 'gbk' codec can't decode byte 0x82 in position 82: illegal multibyte sequence
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

tests/test_cli_integration.py::TestCLIIntegration::test_extract_help
  D:\ADP\adp-cli\.venv\Lib\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-9 (_readerthread)
  
  Traceback (most recent call last):
    File "D:\Programs\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
      self.run()
    File "D:\Programs\Python312\Lib\threading.py", line 1012, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Programs\Python312\Lib\subprocess.py", line 1599, in _readerthread
      buffer.append(fh.read())
                    ^^^^^^^^^
  UnicodeDecodeError: 'gbk' codec can't decode byte 0x82 in position 84: illegal multibyte sequence
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

tests/test_cli_integration.py::TestCLIIntegration::test_query_help
  D:\ADP\adp-cli\.venv\Lib\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-11 (_readerthread)
  
  Traceback (most recent call last):
    File "D:\Programs\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
      self.run()
    File "D:\Programs\Python312\Lib\threading.py", line 1012, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Programs\Python312\Lib\subprocess.py", line 1599, in _readerthread
      buffer.append(fh.read())
                    ^^^^^^^^^
  UnicodeDecodeError: 'gbk' codec can't decode byte 0xaf in position 62: illegal multibyte sequence
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

tests/test_cli_integration.py::TestCLIIntegration::test_app_id_help
  D:\ADP\adp-cli\.venv\Lib\site-packages\_pytest\threadexception.py:58: PytestUnhandledThreadExceptionWarning: Exception in thread Thread-13 (_readerthread)
  
  Traceback (most recent call last):
    File "D:\Programs\Python312\Lib\threading.py", line 1075, in _bootstrap_inner
      self.run()
    File "D:\Programs\Python312\Lib\threading.py", line 1012, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Programs\Python312\Lib\subprocess.py", line 1599, in _readerthread
      buffer.append(fh.read())
                    ^^^^^^^^^
  UnicodeDecodeError: 'gbk' codec can't decode byte 0x82 in position 83: illegal multibyte sequence
  
  Enable tracemalloc to get traceback where the object was allocated.
  See https://docs.pytest.org/en/stable/how-to/capture-warnings.html#resource-warnings for more info.
    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=============================== tests coverage ================================
______________ coverage: platform win32, python 3.12.10-final-0 _______________

Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
src\adp_cli\__init__.py                   1      0   100%
src\adp_cli\adp\__init__.py               5      0   100%
src\adp_cli\adp\api_client.py           163     21    87%   134, 152-153, 161, 179, 209, 214, 244, 249, 296-298, 384, 392, 418, 437, 442-447, 519
src\adp_cli\adp\config.py                73      5    93%   65-66, 79, 115-116
src\adp_cli\adp\file_handler.py          83     19    77%   65, 72-73, 89, 101, 137-147, 158-161, 174-175
src\adp_cli\adp\output_formatter.py      81      0   100%
src\adp_cli\cli.py                      553    244    56%   24-26, 68, 90-91, 97, 184, 230-232, 248-252, 283-285, 301-305, 321-341, 366-401, 433-435, 450-452, 474-475, 502-506, 565-604, 618-642, 655-689, 702-723, 737-758, 773-798, 846-847, 853-855, 858-859, 871-873, 880-882, 888-890, 900-901, 914, 936-1003, 1007
src\adp_cli\i18n.py                      37      5    86%   472-476
-------------------------------------------------------------------
TOTAL                                   996    294    70%
======================= 147 passed, 8 warnings in 6.91s =======================
