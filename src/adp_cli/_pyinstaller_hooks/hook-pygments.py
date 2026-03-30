# PyInstaller hook for pygments
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect pygments data files (includes lexers/formatters)
datas = collect_data_files('pygments')

# Collect pygments submodules
hiddenimports = collect_submodules('pygments')
