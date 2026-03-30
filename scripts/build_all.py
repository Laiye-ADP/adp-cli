#!/usr/bin/env python3
"""
Cross-platform build helper for ADP CLI.

This script helps build executables for different platforms using Docker or
direct building on the current platform.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, cwd=None):
    """Run a command and return its exit code."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.resolve()


def build_current_platform():
    """Build executable for the current platform."""
    project_root = get_project_root()

    print_header("Building for Current Platform")

    # Detect platform
    if sys.platform == "win32":
        script = project_root / "scripts" / "build.bat"
        return run_command(["cmd", "/c", str(script)])
    else:
        script = project_root / "scripts" / "build.sh"
        os.chmod(script, 0o755)
        return run_command([str(script)])


def build_linux_with_docker():
    """Build Linux executable using Docker."""
    project_root = get_project_root()

    print_header("Building Linux Executable with Docker")

    # Check if Docker is available
    try:
        subprocess.run(
            ["docker", "--version"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Docker not found or not accessible.")
        print("Please install Docker to use cross-platform builds.")
        return 1

    # Build using Docker
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{project_root}:/app",
        "-w", "/app",
        "python:3.11-slim",
        "bash", "-c",
        "pip install --upgrade pip && "
        "pip install pyinstaller && "
        "pip install -r requirements.txt && "
        "pyinstaller adp_cli.spec --clean --noconfirm"
    ]

    return run_command(docker_cmd)


def archive_executable(platform_name, binary_name, archive_name):
    """Archive the built executable."""
    project_root = get_project_root()
    dist_dir = project_root / "dist"
    binary_path = dist_dir / binary_name
    archive_path = dist_dir / archive_name

    if not binary_path.exists():
        print(f"Error: {binary_path} not found.")
        return 1

    print_header(f"Creating archive: {archive_name}")

    if sys.platform == "win32":
        # Windows: use PowerShell Compress-Archive
        powershell_cmd = [
            "powershell",
            "-Command",
            f"Compress-Archive -Path '{binary_path}' -DestinationPath '{archive_path}'"
        ]
        return run_command(powershell_cmd)
    else:
        # Linux/macOS: use tar
        tar_cmd = ["tar", "-czf", str(archive_path), "-C", str(dist_dir), binary_name]
        return run_command(tar_cmd)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Build ADP CLI for different platforms"
    )
    parser.add_argument(
        "platform",
        nargs="?",
        choices=["current", "linux", "all"],
        default="current",
        help="Platform to build for (default: current)"
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Create compressed archive after build"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for builds (default: dist/)"
    )

    args = parser.parse_args()

    project_root = get_project_root()

    print_header(f"ADP CLI Build Helper - Platform: {args.platform}")

    # Build for requested platform
    if args.platform == "current":
        result = build_current_platform()
        if args.archive:
            if sys.platform == "win32":
                archive_result = archive_executable(
                    "Windows", "adp.exe", "adp-cli-windows-x64.zip"
                )
            else:
                archive_result = archive_executable(
                    "macOS" if sys.platform == "darwin" else "Linux",
                    "adp",
                    f"adp-cli-{'macos' if sys.platform == 'darwin' else 'linux'}-x64.tar.gz"
                )
            result = result or archive_result

    elif args.platform == "linux":
        if sys.platform == "win32" or sys.platform == "darwin":
            print("Note: Building for Linux using Docker...")
            result = build_linux_with_docker()
        else:
            print("You're already on Linux, using current platform build.")
            result = build_current_platform()

        if args.archive and result == 0:
            archive_result = archive_executable(
                "Linux", "adp", "adp-cli-linux-x64.tar.gz"
            )
            result = archive_result

    elif args.platform == "all":
        print("Building for 'all' requires:")
        print("1. Running on each platform separately, OR")
        print("2. Using GitHub Actions (.github/workflows/build.yml)")
        print("\nFor automated multi-platform builds, push a release tag:")
        print("  git tag v1.10.0 && git push --tags")
        return 1

    # Report result
    print_header("Build Complete")
    print(f"Output directory: {project_root / 'dist'}")
    print("\nBuilt files:")
    dist_dir = project_root / "dist"
    for file in dist_dir.iterdir():
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  {file.name:40s} {size_mb:.2f} MB")

    return result


if __name__ == "__main__":
    sys.exit(main())
