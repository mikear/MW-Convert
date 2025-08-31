"""
Configuration module for MW Convert application.

This module provides centralized configuration management for the application,
including version information, file paths, and application settings.
"""

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class AppConfig:
    """Application configuration manager."""

    # Version information
    VERSION = "1.3"
    YEAR = "2025"
    APP_NAME = "MW Convert"
    AUTHOR = "Diego A. Rábalo"

    # File and directory settings
    DEFAULT_OUTPUT_DIR = "output"
    LOG_FILE = "mw_convert.log"
    MANUAL_FILE = "manual.html"

    # Supported file extensions
    SUPPORTED_INPUT_EXTENSIONS = [".md", ".markdown"]
    SUPPORTED_TEMPLATE_EXTENSIONS = [".docx"]
    OUTPUT_EXTENSION = ".docx"

    # GUI settings
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 450
    WINDOW_X = 100
    WINDOW_Y = 100

    # Icon paths
    ICONS = {
        "app": "icons/app_icon.ico",
        "search": "icons/search.png",
        "docx": "icons/docx.ico",
        "clear": "icons/clear.png",
        "convert": "icons/convert_about.png",
        "folder": "icons/folder_open.png",
        "linkedin": "icons/linkedin.ico",
        "new_project": "icons/new_project.png",
    }

    # Contact information
    CONTACT = {
        "linkedin": "https://www.linkedin.com/in/rabalo",
        "github": "https://github.com/mikear",
        "email": "diego_rabalo@hotmail.com",
        "paypal": "https://paypal.me/diegorabalo",
    }

    # Pandoc settings
    PANDOC_FORMAT = "gfm+smart"  # GitHub-Flavored Markdown with smart typography

    @classmethod
    def get_icon_path(cls, icon_name: str) -> str:
        """
        Get the full path to an icon file.

        Args:
            icon_name: Name of the icon (key from ICONS dict)

        Returns:
            Full path to the icon file

        Raises:
            KeyError: If icon name is not found
        """
        if icon_name not in cls.ICONS:
            available = ", ".join(cls.ICONS.keys())
            raise KeyError(f"Icon '{icon_name}' not found. Available: {available}")

        return cls.ICONS[icon_name]

    @classmethod
    def get_app_info(cls) -> Dict[str, Any]:
        """
        Get application information as a dictionary.

        Returns:
            Dictionary containing app information
        """
        return {
            "name": cls.APP_NAME,
            "version": cls.VERSION,
            "year": cls.YEAR,
            "author": cls.AUTHOR,
            "contact": cls.CONTACT.copy(),
        }

    @classmethod
    def get_window_geometry(cls) -> tuple[int, int, int, int]:
        """
        Get default window geometry.

        Returns:
            Tuple of (x, y, width, height)
        """
        return (cls.WINDOW_X, cls.WINDOW_Y, cls.WINDOW_WIDTH, cls.WINDOW_HEIGHT)

    @classmethod
    def validate_input_file(cls, file_path: str) -> bool:
        """
        Check if a file has a supported input extension.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file extension is supported
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in cls.SUPPORTED_INPUT_EXTENSIONS

    @classmethod
    def validate_template_file(cls, file_path: str) -> bool:
        """
        Check if a file has a supported template extension.

        Args:
            file_path: Path to the file to check

        Returns:
            True if the file extension is supported
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in cls.SUPPORTED_TEMPLATE_EXTENSIONS

    @classmethod
    def get_output_filename(cls, input_path: str) -> str:
        """
        Generate output filename from input path.

        Args:
            input_path: Path to the input file

        Returns:
            Output filename with correct extension
        """
        input_file = Path(input_path)
        return input_file.stem + cls.OUTPUT_EXTENSION

    @classmethod
    def get_full_app_name(cls) -> str:
        """
        Get the full application name with version.

        Returns:
            Full application name string
        """
        return f"{cls.APP_NAME} v{cls.VERSION} ({cls.YEAR})"

    @classmethod
    def get_linkedin_share_text(cls) -> str:
        """
        Get pre-formatted text for LinkedIn sharing.

        Returns:
            LinkedIn share text
        """
        return (
            "🚀 ¡Acabo de usar una increíble app para convertir Markdown a DOCX! "
            "📄✨ Permite estilos personalizados con plantillas DOCX. "
            "¡Súper útil para documentos profesionales y académicos! "
            "#Markdown #DOCX #Productividad #Pandoc"
        )

    @classmethod
    def log_config_info(cls) -> None:
        """Log current configuration information."""
        logger.info(f"Application: {cls.get_full_app_name()}")
        logger.info(f"Author: {cls.AUTHOR}")
        logger.info(f"Default output directory: {cls.DEFAULT_OUTPUT_DIR}")
        logger.info(f"Supported input formats: {cls.SUPPORTED_INPUT_EXTENSIONS}")
        logger.info(f"Supported template formats: {cls.SUPPORTED_TEMPLATE_EXTENSIONS}")


# Global configuration instance
config = AppConfig()

# Export commonly used configuration values
APP_NAME = config.APP_NAME
VERSION = config.VERSION
AUTHOR = config.AUTHOR
DEFAULT_OUTPUT_DIR = config.DEFAULT_OUTPUT_DIR
