"""
Tests for the configuration module.
"""

import pytest
from pathlib import Path

from config import AppConfig, config


class TestAppConfig:
    """Test cases for AppConfig class."""

    def test_version_info(self):
        """Test version information is properly set."""
        assert AppConfig.VERSION == "1.3"
        assert AppConfig.YEAR == "2025"
        assert AppConfig.APP_NAME == "MW Convert"
        assert AppConfig.AUTHOR == "Diego A. Rábalo"

    def test_file_extensions(self):
        """Test file extension configurations."""
        assert ".md" in AppConfig.SUPPORTED_INPUT_EXTENSIONS
        assert ".markdown" in AppConfig.SUPPORTED_INPUT_EXTENSIONS
        assert ".docx" in AppConfig.SUPPORTED_TEMPLATE_EXTENSIONS
        assert AppConfig.OUTPUT_EXTENSION == ".docx"

    def test_get_icon_path(self):
        """Test icon path retrieval."""
        app_icon = AppConfig.get_icon_path("app")
        assert app_icon == "icons/app_icon.ico"
        
        search_icon = AppConfig.get_icon_path("search")
        assert search_icon == "icons/search.png"

    def test_get_icon_path_invalid(self):
        """Test icon path with invalid name."""
        with pytest.raises(KeyError, match="Icon 'invalid' not found"):
            AppConfig.get_icon_path("invalid")

    def test_get_app_info(self):
        """Test application information dictionary."""
        info = AppConfig.get_app_info()
        
        assert info["name"] == "MW Convert"
        assert info["version"] == "1.3"
        assert info["author"] == "Diego A. Rábalo"
        assert "contact" in info
        assert "linkedin" in info["contact"]

    def test_get_window_geometry(self):
        """Test window geometry configuration."""
        x, y, width, height = AppConfig.get_window_geometry()
        
        assert x == 100
        assert y == 100
        assert width == 400
        assert height == 450

    def test_validate_input_file(self):
        """Test input file validation."""
        assert AppConfig.validate_input_file("test.md") is True
        assert AppConfig.validate_input_file("test.markdown") is True
        assert AppConfig.validate_input_file("test.txt") is False
        assert AppConfig.validate_input_file("test.docx") is False

    def test_validate_template_file(self):
        """Test template file validation."""
        assert AppConfig.validate_template_file("template.docx") is True
        assert AppConfig.validate_template_file("template.md") is False
        assert AppConfig.validate_template_file("template.txt") is False

    def test_get_output_filename(self):
        """Test output filename generation."""
        output = AppConfig.get_output_filename("test.md")
        assert output == "test.docx"
        
        output = AppConfig.get_output_filename("path/to/document.markdown")
        assert output == "document.docx"

    def test_get_full_app_name(self):
        """Test full application name."""
        full_name = AppConfig.get_full_app_name()
        assert full_name == "MW Convert v1.3 (2025)"

    def test_get_linkedin_share_text(self):
        """Test LinkedIn share text."""
        text = AppConfig.get_linkedin_share_text()
        assert "Markdown" in text
        assert "DOCX" in text
        assert "🚀" in text

    def test_global_config_instance(self):
        """Test global configuration instance."""
        assert config.APP_NAME == "MW Convert"
        assert config.VERSION == "1.3"


class TestConfigurationIntegration:
    """Integration tests for configuration usage."""

    def test_config_consistency(self):
        """Test that configuration values are consistent."""
        # Check that all required icons are defined
        required_icons = ["app", "search", "docx", "convert", "folder"]
        for icon in required_icons:
            assert icon in AppConfig.ICONS

        # Check contact information completeness
        assert "linkedin" in AppConfig.CONTACT
        assert "github" in AppConfig.CONTACT
        assert "email" in AppConfig.CONTACT
        assert "paypal" in AppConfig.CONTACT

    def test_pandoc_format(self):
        """Test Pandoc format configuration."""
        assert AppConfig.PANDOC_FORMAT == "gfm+smart"
        assert "gfm" in AppConfig.PANDOC_FORMAT
        assert "smart" in AppConfig.PANDOC_FORMAT


if __name__ == "__main__":
    pytest.main([__file__])