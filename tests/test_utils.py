"""
Tests for the utilities module.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils import (
    get_resource_path,
    ensure_directory_exists,
    is_file_readable,
    get_file_size_mb,
    validate_file_extension,
    sanitize_filename,
    get_system_info,
    format_file_size,
    is_pandoc_available,
    get_pandoc_version,
    validate_pandoc_installation,
    create_backup_filename,
    truncate_text,
)


class TestResourcePath:
    """Test resource path functions."""

    def test_get_resource_path_normal(self):
        """Test resource path in normal mode."""
        path = get_resource_path("test.txt")
        assert "test.txt" in path

    @patch("utils.sys")
    def test_get_resource_path_pyinstaller(self, mock_sys):
        """Test resource path in PyInstaller mode."""
        mock_sys._MEIPASS = "/tmp/meipass"
        path = get_resource_path("test.txt")
        assert path == "/tmp/meipass/test.txt"


class TestDirectoryOperations:
    """Test directory operation functions."""

    def test_ensure_directory_exists_new(self, tmp_path):
        """Test creating a new directory."""
        new_dir = tmp_path / "new_directory"
        assert ensure_directory_exists(str(new_dir)) is True
        assert new_dir.exists()

    def test_ensure_directory_exists_existing(self, tmp_path):
        """Test with existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        assert ensure_directory_exists(str(existing_dir)) is True

    def test_ensure_directory_exists_nested(self, tmp_path):
        """Test creating nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "level3"
        assert ensure_directory_exists(str(nested_dir)) is True
        assert nested_dir.exists()


class TestFileOperations:
    """Test file operation functions."""

    def test_is_file_readable_existing(self, tmp_path):
        """Test with readable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        assert is_file_readable(str(test_file)) is True

    def test_is_file_readable_nonexistent(self, tmp_path):
        """Test with non-existent file."""
        test_file = tmp_path / "nonexistent.txt"
        assert is_file_readable(str(test_file)) is False

    def test_is_file_readable_directory(self, tmp_path):
        """Test with directory instead of file."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        assert is_file_readable(str(test_dir)) is False

    def test_get_file_size_mb_existing(self, tmp_path):
        """Test file size calculation."""
        test_file = tmp_path / "test.txt"
        content = "A" * 1024 * 1024  # 1 MB
        test_file.write_text(content)
        
        size = get_file_size_mb(str(test_file))
        assert size is not None
        assert abs(size - 1.0) < 0.1  # Should be approximately 1 MB

    def test_get_file_size_mb_nonexistent(self, tmp_path):
        """Test file size with non-existent file."""
        test_file = tmp_path / "nonexistent.txt"
        assert get_file_size_mb(str(test_file)) is None


class TestFileValidation:
    """Test file validation functions."""

    def test_validate_file_extension_valid(self):
        """Test with valid file extension."""
        assert validate_file_extension("test.md", [".md", ".txt"]) is True
        assert validate_file_extension("test.TXT", [".md", ".txt"]) is True

    def test_validate_file_extension_invalid(self):
        """Test with invalid file extension."""
        assert validate_file_extension("test.pdf", [".md", ".txt"]) is False
        assert validate_file_extension("test", [".md", ".txt"]) is False

    def test_validate_file_extension_case_insensitive(self):
        """Test case insensitive extension validation."""
        assert validate_file_extension("test.MD", [".md"]) is True
        assert validate_file_extension("test.md", [".MD"]) is True


class TestFilenameSanitization:
    """Test filename sanitization."""

    def test_sanitize_filename_normal(self):
        """Test sanitizing normal filename."""
        result = sanitize_filename("normal_file.txt")
        assert result == "normal_file.txt"

    def test_sanitize_filename_invalid_chars(self):
        """Test sanitizing filename with invalid characters."""
        result = sanitize_filename("file<>:\"/\\|?*.txt")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert result.endswith(".txt")

    def test_sanitize_filename_empty(self):
        """Test sanitizing empty filename."""
        result = sanitize_filename("")
        assert result == "unnamed_file"

    def test_sanitize_filename_dots_spaces(self):
        """Test sanitizing filename with leading/trailing dots and spaces."""
        result = sanitize_filename("  ..filename..  ")
        assert not result.startswith(" ")
        assert not result.endswith(" ")
        assert not result.startswith(".")


class TestSystemInfo:
    """Test system information functions."""

    def test_get_system_info(self):
        """Test getting system information."""
        info = get_system_info()
        assert "platform" in info
        assert "python_version" in info
        assert "architecture" in info
        assert isinstance(info, dict)

    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(512) == "512 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_format_file_size_edge_cases(self):
        """Test file size formatting edge cases."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1) == "1 B"
        assert "KB" in format_file_size(1500)


class TestPandocValidation:
    """Test Pandoc validation functions."""

    @patch("utils.subprocess.run")
    def test_is_pandoc_available_true(self, mock_run):
        """Test Pandoc availability when installed."""
        mock_run.return_value = MagicMock(returncode=0)
        assert is_pandoc_available() is True

    @patch("utils.subprocess.run")
    def test_is_pandoc_available_false(self, mock_run):
        """Test Pandoc availability when not installed."""
        mock_run.side_effect = FileNotFoundError()
        assert is_pandoc_available() is False

    @patch("utils.subprocess.run")
    def test_get_pandoc_version_success(self, mock_run):
        """Test getting Pandoc version successfully."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="pandoc 2.19.2\nCompiled with pandoc-types...\n"
        )
        version = get_pandoc_version()
        assert version == "pandoc 2.19.2"

    @patch("utils.subprocess.run")
    def test_get_pandoc_version_failure(self, mock_run):
        """Test getting Pandoc version when not available."""
        mock_run.side_effect = FileNotFoundError()
        version = get_pandoc_version()
        assert version is None

    @patch("utils.is_pandoc_available")
    @patch("utils.get_pandoc_version")
    def test_validate_pandoc_installation_success(self, mock_version, mock_available):
        """Test Pandoc installation validation success."""
        mock_available.return_value = True
        mock_version.return_value = "pandoc 2.19.2"
        
        is_available, message = validate_pandoc_installation()
        assert is_available is True
        assert "pandoc 2.19.2" in message

    @patch("utils.is_pandoc_available")
    def test_validate_pandoc_installation_failure(self, mock_available):
        """Test Pandoc installation validation failure."""
        mock_available.return_value = False
        
        is_available, message = validate_pandoc_installation()
        assert is_available is False
        assert "no está instalado" in message


class TestUtilityFunctions:
    """Test miscellaneous utility functions."""

    def test_create_backup_filename(self):
        """Test backup filename creation."""
        original = "/path/to/file.txt"
        backup = create_backup_filename(original)
        
        assert "backup" in backup
        assert backup.endswith(".txt")
        assert "/path/to/" in backup

    def test_truncate_text_no_truncation(self):
        """Test text truncation when not needed."""
        text = "Short text"
        result = truncate_text(text, 20)
        assert result == text

    def test_truncate_text_with_truncation(self):
        """Test text truncation when needed."""
        text = "This is a very long text that needs truncation"
        result = truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_text_custom_suffix(self):
        """Test text truncation with custom suffix."""
        text = "This is a long text"
        result = truncate_text(text, 10, suffix="...")
        assert result.endswith("...")
        assert len(result) == 10


class TestSystemOperations:
    """Test system operation functions (mocked)."""

    @patch("utils.platform.system")
    @patch("utils.subprocess.run")
    def test_open_file_linux(self, mock_run, mock_system):
        """Test opening file on Linux."""
        mock_system.return_value = "Linux"
        
        from utils import open_file_with_default_app
        result = open_file_with_default_app("test.txt")
        
        mock_run.assert_called_once_with(["xdg-open", "test.txt"], check=True)

    @patch("utils.platform.system")
    @patch("utils.subprocess.run")
    def test_open_directory_linux(self, mock_run, mock_system):
        """Test opening directory on Linux."""
        mock_system.return_value = "Linux"
        
        from utils import open_directory_in_explorer
        result = open_directory_in_explorer("/path/to/dir")
        
        mock_run.assert_called_once_with(["xdg-open", "/path/to/dir"], check=True)


if __name__ == "__main__":
    pytest.main([__file__])