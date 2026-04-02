# Docker Build Guide for Linux Binaries

This guide explains how to build Linux binaries with compatible GLIBC versions using Docker.

---

## Problem

When building Linux binaries with PyInstaller on your local machine (WSL), the resulting binary links to your system's GLIBC version. If the target environment has an older GLIBC version, the binary will fail to run:

```
version `GLIBC_2.38' not found (required by ./adp)
```

---

## Solution

Build the binary inside a Docker container with a specific Linux distribution that has the desired GLIBC version.

---

## Files Created

### 1. `Dockerfile.build`
Dockerfile for building the binary. Uses Rocky Linux 8 by default (GLIBC 2.28).

### 2. `scripts/build-linux-docker.sh`
Bash script for building on Linux/macOS.

### 3. `scripts/build-linux-docker.bat`
Batch script for building on Windows (using Docker Desktop).

### 4. `scripts`/build-linux-matrix-docker.sh`
Builds binaries for multiple Linux distributions at once.

---

## Usage

### Windows (with Docker Desktop)

```cmd
cd d:\ADP\adp-cli
scripts\build-linux-docker.bat
```

### Linux / macOS / WSL

```bash
cd /path/to/adp-cli
chmod +x scripts/build-linux-docker.sh
./scripts/build-linux-docker.sh
```

---

## Build Multiple Platforms

```bash
# Build for Ubuntu 20.04, Ubuntu 22.04, Rocky 8, Rocky 9
chmod +x scripts/build-linux-matrix-docker.sh
./scripts/build-linux-matrix-docker.sh
```

Output: `dist/docker/adp-ubuntu-20.04`, `dist/docker/adp-ubuntu-22.04`, etc.

---

## Platform GLIBC Versions

| Platform | Docker Image | GLIBC Version |
|---------|---------------|----------------|
| Ubuntu 20.04 | `ubuntu:20.04` | 2.31 |
| Ubuntu 22.04 | `ubuntu:22.04` | 2.35 |
| Rocky/CentOS 8 | `rockylinux:8` | 2.28 |
| Rocky/CentOS 9 | `rockylinux:9` | 2.34 |
| Debian 11 | `debian:11` | 2.31 |

---

## Check GLIBC Version

On the target system:

```bash
ldd --version
# or
strings /lib64/libc.so.6 | grep GLIBC
```

---

## Output

Built binary: `dist/docker/adp`

To verify:

```bash
./dist/docker/adp --version
```

---

## Prerequisites

1. Docker installed and running
2. Docker Desktop (for Windows) or Docker CLI (for Linux/macOS)
3. WSL (on Windows) is already configured if using Docker Desktop

---

## Customizing Base Image

To use a different Linux distribution, modify `Dockerfile.build`:

```dockerfile
FROM ubuntu:20.04  # Change to desired image
```

Or override when building:

```bash
docker build -f Dockerfile.build --build-arg BASE_IMAGE=ubuntu:20.04 -t adp-cli-builder .
```

---

## Troubleshooting

### Docker not found

```
ERROR: Docker is not installed or not running.
```

**Solution:** Install Docker Desktop (Windows/macOS) or Docker Engine (Linux).

### Permission denied (Linux)

```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:** Add your user to the docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Build fails

Check the error message. Common issues:
- Missing dependencies in Dockerfile
- Incorrect file paths
- PyInstaller spec file errors

---

## Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: Build Linux Binary

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build with Docker
        run: |
          docker build -f Dockerfile.build -t adp-cli-builder .
          docker run --rm \
            -v ${{ github.workspace }}:/app \
            -v ${{ github.workspace }}/dist:/output \
            -w /app \
            adp-cli-builder \
            sh -c "pyinstaller --clean adp_cli.spec && cp dist/adp /output/adp"
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: adp-linux-binary
          path: dist/adp
```

---

## References

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Docker Documentation](https://docs.docker.com/)
- [GLIBC Compatibility](https://sourceware.org/glibc/wiki/Testing/Builds)
