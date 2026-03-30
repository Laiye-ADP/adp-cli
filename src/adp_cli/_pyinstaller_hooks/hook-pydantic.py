# PyInstaller hook for pydantic
from PyInstaller.utils.hooks import collect_data_files

# Collect pydantic data files
datas = collect_data_files('pydantic')

# Explicitly list pydantic submodules that might be needed
# Using a minimal set to avoid unnecessary bloat
hiddenimports = [
    'pydantic',
    'pydantic.annotated_types',
    'pydantic.dataclasses',
    'pydantic.errors',
    'pydantic.fields',
    'pydantic.functional_validators',
    'pydantic.main',
    'pydantic.networks',
    'pydantic.parse',
    'pydantic.types',
    'pydantic.validators',
    'pydantic.version',
    # pydantic v2 core modules
    'pydantic_core',
    'pydantic_core._pydantic_core',
]
