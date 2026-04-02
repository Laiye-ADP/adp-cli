# GLIBC 兼容性解决方案

## 问题描述

glibc 是 Linux 系统的核心 C 库，具有**向后不兼容**的特性：

```
较新系统上构建 → 链接 glibc 2.35+ → 二进制文件标记需要 GLIBC_2.35
较老系统上运行 → 只有 glibc 2.17     → ❌ version `GLIBC_2.35' not found
```

**典型错误**：
```
./adp: /lib64/libc.so.6: version `GLIBC_2.28' not found
```

## 解决方案

使用 **Docker 多平台构建**，在每个目标平台上分别构建。

### 快速开始

```bash
# 在项目根目录运行
./scripts/build-linux-matrix-docker.sh
```

### 输出文件

构建完成后，在 `dist/docker/` 目录生成：

| 文件 | glibc 版本 | 兼容范围 |
|------|-----------|---------|
| `adp-rockylinux-8` | 2.28 | CentOS 7+, Rocky 8+, Ubuntu 18.04+, Debian 10+ |
| `adp-ubuntu-20.04` | 2.31 | Ubuntu 20.04+, Debian 11+ |
| `adp-ubuntu-22.04` | 2.35 | Ubuntu 22.04+, Debian 12+ |

### 推荐使用

**生产环境推荐使用 `adp-rockylinux-8`**：
- 兼容性最广（glibc 2.28）
- 涵盖大部分企业 Linux 发行版
- 向下兼容 CentOS 7（2014年发布）

## 使用方法

### 1. 下载

```bash
# 根据目标系统选择对应的版本
wget https://your-release-url/adp-rockylinux-8
```

### 2. 安装

```bash
chmod +x adp-rockylinux-8
sudo mv adp-rockylinux-8 /usr/local/bin/adp
```

### 3. 验证

```bash
adp --version
```

## GLIBC 版本对照表

| 发行版 | 版本 | glibc |
|--------|------|-------|
| CentOS 7 | 7.x | 2.17 |
| Rocky Linux 8 | 8.x | 2.28 |
| Ubuntu 18.04 | Bionic | 2.27 |
| Ubuntu 20.04 | Focal | 2.31 |
| Ubuntu 22.04 | Jammy | 2.35 |
| Debian 10 | Buster | 2.28 |
| Debian 11 | Bullseye | 2.31 |
| Debian 12 | Bookworm | 2.35 |

## 兼容性矩阵

| 构建平台 | 可运行平台 |
|---------|-----------|
| Rocky Linux 8 (glibc 2.28) | ✅ CentOS 7+, Rocky 8+, Ubuntu 18.04+, Debian 10+ |
| Ubuntu 20.04 (glibc 2.31) | ✅ Ubuntu 20.04+, Debian 11+ |
| Ubuntu 22.04 (glibc 2.35) | ✅ Ubuntu 22.04+, Debian 12+ |

## 验证 GLIBC 依赖

### 查看二进制文件所需的 glibc 版本

```bash
# 方法1：使用 objdump
objdump -T adp-rockylinux-8 | grep GLIBC | awk '{print $NF}' | sort -u

# 方法2：使用 ldd
ldd adp-rockylinux-8 | grep libc
```

### 查看 Docker 容器内的 glibc 版本

```bash
docker run --rm rockylinux:8 ldd --version | head -1
```

## 故障排除

### 错误：version `GLIBC_2.xx' not found

**原因**：二进制文件需要的 glibc 版本比系统中的新

**解决**：
1. 选择更低 glibc 版本的构建
2. 或升级目标系统

### 错误：permission denied

```bash
chmod +x adp-rockylinux-8
```

### 错误：No such file or directory

确保在正确的架构上运行（x86_64 vs ARM）：
```bash
file adp-rockylinux-8
# 输出：adp-rockylinux-8: ELF 64-bit LSB executable, x86-64, ...
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Build Linux Binaries

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build Linux Matrix
        run: ./scripts/build-linux-matrix-docker.sh

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: linux-binaries
          path: dist/docker/*
```

## 最佳实践

1. **默认选择最兼容版本**：发布时推荐 `adp-rockylinux-8`
2. **提供多个版本**：让用户根据系统选择
3. **文档清晰标注兼容性**：在发布说明中列出支持的系统
4. **自动化验证**：在 CI 中验证 glibc 依赖

## 相关资源

- [GLIBC 版本历史](https://sourceware.org/glibc/wiki/News)
- [Linux 发行版发布日期](https://en.wikipedia.org/wiki/Linux_distribution)
- [PyInstaller Linux 构建](https://pyinstaller.org/en/stable/usage.html#making-gnu-linux-app-executable-across-distributions)
