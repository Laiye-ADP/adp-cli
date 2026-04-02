#!/bin/bash
set -e

echo "=================================================="
echo "ADP CLI PyPI Publish Script"
echo "=================================================="
echo ""

# 清理旧的Python构建产物
echo "[1/3] Cleaning old Python builds..."
rm -rf build/ *.egg-info src/*.egg-info
rm -f dist/*.whl dist/*.tar.gz
echo "✓ Cleaned build artifacts"

# 构建新的Python包
echo ""
echo "[2/3] Building Python packages..."
python setup.py sdist bdist_wheel
echo "✓ Built source distribution and wheel"

# 上传到PyPI
echo ""
echo "[3/3] Uploading to PyPI..."
echo "Packages to upload:"
ls -lh dist/*.whl dist/*.tar.gz
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

twine upload dist/*.whl dist/*.tar.gz

echo ""
echo "=================================================="
echo "✓ Published successfully!"
echo "=================================================="
echo ""
echo "Users can update with: pip install agentic_doc_parse_and_extract --upgrade"
