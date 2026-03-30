"""
Runtime hook for ADP CLI to ensure encodings module is loaded early.
This fixes the "ModuleNotFoundError: No module named 'encodings'" issue in one-file mode.
"""

import sys
import os

# Force import encodings early
import encodings
import codecs
import locale

# Ensure encodings module is in sys.modules
if 'encodings' not in sys.modules:
    sys.modules['encodings'] = encodings

# This helps PyInstaller detect the encodings dependency
__import__('encodings', {}, {}, ['utf_8', 'ascii', 'latin_1'])
