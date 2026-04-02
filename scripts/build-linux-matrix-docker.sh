#!/bin/bash
# Build Linux binaries for multiple distributions using Docker
# 解决 glibc 兼容性问题：在最老系统上构建，确保向下兼容

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Target distributions (base_image:platform_name)
# 按构建顺序排列：老系统在前，新系统在后
# ⚠️ 重要：老系统上构建的二进制可以在新系统上运行，反之不行
declare -A PLATFORMS=(
    ["python:3.8-buster"]="rockylinux-8"        # glibc 2.28 - 推荐，兼容 CentOS 7+, Rocky 8+, Ubuntu 18.04+
    # ["python:3.8-bullseye"]="ubuntu-20.04"     #    glibc 2.31 - 兼容 Ubuntu 20.04+, Debian 11+
    # ["python:3.8-bookworm"]="ubuntu-22.04"     #    glibc 2.35 - 仅兼容最新系统
)

# glibc 版本对照表
declare -A GLIBC_VERSIONS=(
    ["rockylinux-8"]="2.28"
    ["ubuntu-20.04"]="2.31"
    ["ubuntu-22.04"]="2.35"
)

# 兼容性说明
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ADP CLI Linux Binary Build - glibc Compatibility Matrix       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  glibc 向后不兼容原则："
echo "    • 在老系统上构建 → 可在新系统运行"
echo "    • 在新系统上构建 → ❌ 不能在老系统运行"
echo ""
echo "📋 构建计划："
for image in "${!PLATFORMS[@]}"; do
    platform="${PLATFORMS[$image]}"
    glibc="${GLIBC_VERSIONS[$platform]}"
    echo "    • $platform (glibc $glibc)"
done
echo ""

cd "$PROJECT_DIR"
mkdir -p dist/docker

for image in "${!PLATFORMS[@]}"; do
    platform="${PLATFORMS[$image]}"
    glibc="${GLIBC_VERSIONS[$platform]}"

    echo ""
    echo "────────────────────────────────────────────────────────────────"
    echo "Building for: $platform"
    echo "Base image:   $image"
    echo "glibc version: $glibc"
    echo "────────────────────────────────────────────────────────────────"

    # Build image
    echo "[1/2] Building Docker image..."
    docker build -f Dockerfile.build --build-arg BASE_IMAGE=$image -t adp-cli-builder:$platform .

    # Build binary
    echo "[2/2] Building binary..."
    docker run --rm \
        -v "$PROJECT_DIR":/app \
        -v "$PROJECT_DIR/dist/docker":/output \
        -w /app \
        adp-cli-builder:$platform \
        bash -c "
            python3 -m PyInstaller --clean --noconfirm adp_cli.spec && \
            cp dist/adp /output/adp-$platform && \
            chmod +x /output/adp-$platform && \
            echo 'Build complete: dist/adp-$platform'
        "

    if [ -f "$PROJECT_DIR/dist/docker/adp-$platform" ]; then
        echo "✅ Success: dist/docker/adp-$platform"
    else
        echo "❌ Failed: $platform build error!"
        exit 1
    fi
done

echo ""
echo "══════════════════════════════════════════════════════════════════"
echo "Build Summary"
echo "══════════════════════════════════════════════════════════════════"
echo ""
echo "📦 Output files:"
ls -lh "$PROJECT_DIR/dist/docker/" | grep "adp-"

echo ""
echo "🔍 GLIBC dependency check:"
echo ""
for each in "${PLATFORMS[@]}"; do
    if [ -f "$PROJECT_DIR/dist/docker/adp-$each" ]; then
        echo "  $each:"
        echo "    Required glibc:"
        docker run --rm -v "$PROJECT_DIR/dist/docker":/bin rockylinux:8 \
            objdump -T /bin/adp-$each 2>/dev/null | grep GLIBC | awk '{print $NF}' | sort -u | sed 's/^/      - /'
    fi
done

echo ""
echo "══════════════════════════════════════════════════════════════════"
echo "Compatibility Guide"
echo "══════════════════════════════════════════════════════════════════"
echo ""
echo "推荐使用："
echo "  • adp-rockylinux-8  →  兼容 CentOS 7+, Rocky 8+, Ubuntu 18.04+, Debian 10+"
echo "  • adp-ubuntu-20.04  →  兼容 Ubuntu 20.04+, Debian 11+"
echo "  • adp-ubuntu-22.04  →  仅 Ubuntu 22.04+, Debian 12+"
echo ""
echo "安装方法："
echo "  wget https://your-release-url/adp-rockylinux-8"
echo "  chmod +x adp-rockylinux-8"
echo "  mv adp-rockylinux-8 /usr/local/bin/adp"
echo ""
echo "验证安装："
echo "  adp --version"
echo ""
