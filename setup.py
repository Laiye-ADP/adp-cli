"""Setup script for ADP CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="adp-cli",
    version="1.10.0",
    author="ADP Team",
    author_email="support@adp.ai",
    description="AI Document Platform Command Line Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adp/adp-aiem",
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
        "pygments>=2.14.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
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
        "Bug Reports": "https://github.com/adp/adp-aiem/issues",
        "Source": "https://github.com/adp/adp-aiem",
    },
)
