"""Setup script for ADP CLI."""

from pathlib import Path
from setuptools import setup, find_packages

# Load version from __init__.py
_version_py = Path("src/adp_cli/__init__.py").read_text()
version = _version_py.split("__version__")[1].split("=")[1].strip().strip('"').strip("'")

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="agentic_doc_parse_and_extract",
    version=version,
    author="ADP Team",
    author_email="support@adp.ai",
    license="Commercial license required. New users receive 100 free credits monthly to offset usage.",
    description="AI Document Platform Command Line Tool - Document Parse & Extract Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["adp", "cli", "document", "parse", "extract", "ai"],
    url="https://github.com/Laiye-ADP/adp-cli",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "cryptography>=41.0.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "types-requests>=2.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "adp=adp_cli.cli:cli",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Laiye-ADP/adp-cli/issues",
        "Source": "https://github.com/Laiye-ADP/adp-cli",
    },
)
