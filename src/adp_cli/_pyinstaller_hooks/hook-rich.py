# PyInstaller hook for rich
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect rich data files (includes themes)
datas = collect_data_files('rich')

# Collect rich submodules
hiddenimports = collect_submodules('rich')
