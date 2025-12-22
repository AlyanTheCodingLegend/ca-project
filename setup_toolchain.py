#!/usr/bin/env python3
"""
RISC-V Toolchain Setup Script

Downloads and configures the xPack RISC-V toolchain for all platforms.
"""

import os
import sys
import platform
import urllib.request
import zipfile
import tarfile
import shutil
from pathlib import Path


# xPack RISC-V toolchain version
TOOLCHAIN_VERSION = "12.2.0-3"
BASE_URL = "https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download"


def get_platform_info():
    """Detect the current platform and return the appropriate toolchain package."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "win32-x64", "zip"
    elif system == "linux":
        if "aarch64" in machine or "arm64" in machine:
            return "linux-arm64", "tar.gz"
        else:
            return "linux-x64", "tar.gz"
    elif system == "darwin":  # macOS
        if "arm" in machine or "aarch64" in machine:
            return "darwin-arm64", "tar.gz"
        else:
            return "darwin-x64", "tar.gz"
    else:
        raise Exception(f"Unsupported platform: {system}")


def download_file(url, dest_path):
    """Download a file with progress indication."""
    print(f"Downloading from {url}...")

    def show_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '=' * filled + '-' * (bar_length - filled)
        print(f'\r[{bar}] {percent:.1f}%', end='', flush=True)

    # Accept pathlib.Path or string paths
    dest_path = str(dest_path)
    urllib.request.urlretrieve(url, dest_path, show_progress)
    print()  # New line after progress bar


def extract_archive(archive_path, extract_to):
    """Extract a zip, tar.gz or tgz archive."""
    # Accept pathlib.Path as well as strings
    archive_path = str(archive_path)
    print(f"Extracting {archive_path}...")

    if archive_path.endswith('.zip'):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
        with tarfile.open(archive_path, 'r:gz') as tar_ref:
            tar_ref.extractall(extract_to)
    else:
        raise Exception(f"Unknown archive format: {archive_path}")


def setup_toolchain():
    """Main setup function."""
    print("=" * 60)
    print("RISC-V Toolchain Setup")
    print("=" * 60)

    # Check if toolchain already exists
    toolchain_dir = Path("riscv-toolchain")
    toolchain_bin = toolchain_dir / f"xpack-riscv-none-elf-gcc-{TOOLCHAIN_VERSION}" / "bin"

    if toolchain_bin.exists():
        print(f"\n✓ Toolchain already exists at: {toolchain_bin}")
        print("\nTo reinstall, delete the 'riscv-toolchain' folder and run this script again.")
        return 0

    # Get platform information
    try:
        platform_name, archive_ext = get_platform_info()
        print(f"\nDetected platform: {platform_name}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1

    # Construct download URL
    archive_name = f"xpack-riscv-none-elf-gcc-{TOOLCHAIN_VERSION}-{platform_name}.{archive_ext}"
    download_url = f"{BASE_URL}/v{TOOLCHAIN_VERSION}/{archive_name}"

    # Create temporary directory
    temp_dir = Path("temp_toolchain")
    temp_dir.mkdir(exist_ok=True)
    archive_path = temp_dir / archive_name

    try:
        # Download the toolchain
        print(f"\nDownloading toolchain...")
        download_file(download_url, archive_path)

        # Extract the archive
        print(f"\nExtracting toolchain...")
        toolchain_dir.mkdir(exist_ok=True)
        extract_archive(archive_path, toolchain_dir)

        # Verify installation
        if toolchain_bin.exists():
            print(f"\n✓ Toolchain successfully installed at: {toolchain_dir}")
            print(f"\n✓ Binaries available at: {toolchain_bin}")

            # Test the toolchain
            gcc_binary = "riscv-none-elf-gcc.exe" if platform.system() == "Windows" else "riscv-none-elf-gcc"
            gcc_path = toolchain_bin / gcc_binary
            if gcc_path.exists():
                print(f"\n✓ Toolchain is ready to use!")
            else:
                print(f"\n⚠ Warning: Could not find gcc binary at {gcc_path}")
        else:
            print(f"\n✗ Installation failed: binaries not found at {toolchain_bin}")
            return 1

    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        return 1
    finally:
        # Clean up temporary files
        if temp_dir.exists():
            print("\nCleaning up temporary files...")
            shutil.rmtree(temp_dir)

    print("\n" + "=" * 60)
    print("Setup complete! You can now run: python main.py")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(setup_toolchain())
