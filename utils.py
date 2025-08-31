"""
Utility functions for the MW Convert application.

This module provides common utility functions used across the application,
including file operations, validation helpers, and UI utilities.
"""

import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Relative path to the resource

    Returns:
        Absolute path to the resource
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS  # type: ignore
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.

    Args:
        directory_path: Path to the directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False


def is_file_readable(file_path: str) -> bool:
    """
    Check if a file exists and is readable.

    Args:
        file_path: Path to the file

    Returns:
        True if file is readable
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and os.access(path, os.R_OK)
    except (PermissionError, OSError):
        return False


def get_file_size_mb(file_path: str) -> Optional[float]:
    """
    Get file size in megabytes.

    Args:
        file_path: Path to the file

    Returns:
        File size in MB, or None if file doesn't exist
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except (FileNotFoundError, OSError):
        return None


def open_file_with_default_app(file_path: str) -> bool:
    """
    Open a file with the system's default application.

    Args:
        file_path: Path to the file to open

    Returns:
        True if file was opened successfully
    """
    try:
        if platform.system() == "Windows":
            os.startfile(file_path)  # type: ignore
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        else:  # Linux and other Unix-like systems
            subprocess.run(["xdg-open", file_path], check=True)

        logger.info(f"Opened file with default application: {file_path}")
        return True
    except (subprocess.CalledProcessError, AttributeError, FileNotFoundError) as e:
        logger.error(f"Failed to open file {file_path}: {e}")
        return False


def open_directory_in_explorer(directory_path: str) -> bool:
    """
    Open a directory in the system's file explorer.

    Args:
        directory_path: Path to the directory to open

    Returns:
        True if directory was opened successfully
    """
    try:
        if platform.system() == "Windows":
            subprocess.run(["explorer", directory_path], check=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", directory_path], check=True)
        else:  # Linux and other Unix-like systems
            subprocess.run(["xdg-open", directory_path], check=True)

        logger.info(f"Opened directory in explorer: {directory_path}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Failed to open directory {directory_path}: {e}")
        return False


def validate_file_extension(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Validate that a file has one of the allowed extensions.

    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed extensions (with dots)

    Returns:
        True if file has an allowed extension
    """
    file_ext = Path(file_path).suffix.lower()
    return file_ext in [ext.lower() for ext in allowed_extensions]


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for the file system
    """
    # Characters not allowed in filenames on Windows
    invalid_chars = '<>:"/\\|?*'

    # Replace invalid characters with underscore
    sanitized = filename
    for char in invalid_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"

    return sanitized


def get_system_info() -> dict:
    """
    Get system information for debugging purposes.

    Returns:
        Dictionary containing system information
    """
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": sys.version,
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
        "machine": platform.machine(),
    }


def log_system_info() -> None:
    """Log system information for debugging."""
    info = get_system_info()
    logger.info("System Information:")
    for key, value in info.items():
        logger.info(f"  {key}: {value}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_pandoc_available() -> bool:
    """
    Check if Pandoc is available in the system PATH.

    Returns:
        True if Pandoc is available
    """
    try:
        result = subprocess.run(
            ["pandoc", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return False


def get_pandoc_version() -> Optional[str]:
    """
    Get the installed Pandoc version.

    Returns:
        Pandoc version string, or None if not available
    """
    try:
        result = subprocess.run(
            ["pandoc", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # Extract version from first line
            first_line = result.stdout.split("\n")[0]
            if "pandoc" in first_line.lower():
                return first_line.strip()
        return None
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return None


def validate_pandoc_installation() -> tuple[bool, str]:
    """
    Validate Pandoc installation and return status with message.

    Returns:
        Tuple of (is_available, message)
    """
    if not is_pandoc_available():
        return False, (
            "Pandoc no está instalado o no está disponible en el PATH del sistema. "
            "Por favor, instale Pandoc desde https://pandoc.org/installing.html"
        )

    version = get_pandoc_version()
    if version:
        return True, f"Pandoc está disponible: {version}"
    else:
        return True, "Pandoc está disponible pero no se pudo obtener la versión"


def create_backup_filename(original_path: str) -> str:
    """
    Create a backup filename by appending timestamp.

    Args:
        original_path: Original file path

    Returns:
        Backup filename with timestamp
    """
    from datetime import datetime

    path = Path(original_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_backup_{timestamp}{path.suffix}"

    return str(path.parent / backup_name)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
