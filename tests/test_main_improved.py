"""
Unit tests for the improved main module.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Import the module to test
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_improved import (  # noqa: E402
    ConversionError,
    ValidationError,
    convert_md_to_docx,
    create_output_directory,
    setup_logging,
    validate_input_file,
    validate_template_file,
)


class TestValidateInputFile:
    """Test cases for input file validation."""

    def test_valid_markdown_file(self, tmp_path):
        """Test validation of a valid markdown file."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test content")

        result = validate_input_file(md_file)
        assert result == md_file

    def test_nonexistent_file(self, tmp_path):
        """Test validation fails for non-existent file."""
        md_file = tmp_path / "nonexistent.md"

        with pytest.raises(ValidationError, match="does not exist"):
            validate_input_file(md_file)

    def test_empty_file(self, tmp_path):
        """Test validation fails for empty file."""
        md_file = tmp_path / "empty.md"
        md_file.touch()

        with pytest.raises(ValidationError, match="empty"):
            validate_input_file(md_file)

    def test_directory_instead_of_file(self, tmp_path):
        """Test validation fails when path is a directory."""
        md_dir = tmp_path / "test.md"
        md_dir.mkdir()

        with pytest.raises(ValidationError, match="not a file"):
            validate_input_file(md_dir)

    def test_non_md_extension_warning(self, tmp_path, caplog):
        """Test warning for non-.md extension."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("content")

        with caplog.at_level("WARNING"):
            validate_input_file(txt_file)

        assert "does not have .md extension" in caplog.text


class TestValidateTemplateFile:
    """Test cases for template file validation."""

    def test_valid_docx_template(self, tmp_path):
        """Test validation of a valid DOCX template."""
        docx_file = tmp_path / "template.docx"
        docx_file.write_text("fake docx content")

        result = validate_template_file(docx_file)
        assert result == docx_file

    def test_nonexistent_template(self, tmp_path):
        """Test validation fails for non-existent template."""
        docx_file = tmp_path / "nonexistent.docx"

        with pytest.raises(ValidationError, match="does not exist"):
            validate_template_file(docx_file)

    def test_non_docx_extension(self, tmp_path):
        """Test validation fails for non-.docx extension."""
        txt_file = tmp_path / "template.txt"
        txt_file.write_text("content")

        with pytest.raises(ValidationError, match="must be a .docx file"):
            validate_template_file(txt_file)


class TestCreateOutputDirectory:
    """Test cases for output directory creation."""

    def test_create_new_directory(self, tmp_path):
        """Test creation of a new directory."""
        new_dir = tmp_path / "output"

        result = create_output_directory(new_dir)
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_existing_directory(self, tmp_path):
        """Test with existing directory."""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()

        result = create_output_directory(existing_dir)
        assert result == existing_dir
        assert existing_dir.exists()

    def test_nested_directory_creation(self, tmp_path):
        """Test creation of nested directories."""
        nested_dir = tmp_path / "level1" / "level2" / "output"

        result = create_output_directory(nested_dir)
        assert result == nested_dir
        assert nested_dir.exists()


class TestConvertMdToDocx:
    """Test cases for the main conversion function."""

    def test_successful_conversion(self, tmp_path):
        """Test successful markdown to DOCX conversion."""
        # Create test input file
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nThis is a test.")

        output_dir = tmp_path / "output"

        # Mock pypandoc.convert_file to avoid actual conversion
        with patch("main_improved.pypandoc.convert_file") as mock_convert:
            # Create expected output file
            expected_output = output_dir / "test.docx"
            output_dir.mkdir()
            expected_output.write_text("fake docx")

            result = convert_md_to_docx(md_file, output_dir)

            assert result == expected_output
            mock_convert.assert_called_once()

    def test_conversion_with_template(self, tmp_path):
        """Test conversion with a DOCX template."""
        # Create test files
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test\n\nThis is a test.")

        template_file = tmp_path / "template.docx"
        template_file.write_text("fake template")

        output_dir = tmp_path / "output"

        with patch("main_improved.pypandoc.convert_file") as mock_convert:
            expected_output = output_dir / "test.docx"
            output_dir.mkdir()
            expected_output.write_text("fake docx")

            result = convert_md_to_docx(md_file, output_dir, template_file)

            assert result == expected_output
            # Check that template was passed to pypandoc
            call_args = mock_convert.call_args
            assert "--reference-doc" in call_args[1]["extra_args"]

    def test_conversion_invalid_input(self, tmp_path):
        """Test conversion with invalid input file."""
        nonexistent_file = tmp_path / "nonexistent.md"

        with pytest.raises(ValidationError):
            convert_md_to_docx(nonexistent_file)

    def test_pypandoc_error_handling(self, tmp_path):
        """Test handling of pypandoc errors."""
        md_file = tmp_path / "test.md"
        md_file.write_text("# Test")

        with patch("main_improved.pypandoc.convert_file") as mock_convert:
            mock_convert.side_effect = Exception("Pypandoc error")

            with pytest.raises(ConversionError, match="Conversion failed"):
                convert_md_to_docx(md_file)


class TestSetupLogging:
    """Test cases for logging setup."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()
        # Just ensure it doesn't raise an exception
        # More detailed testing would require checking logger configuration

    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        import logging

        setup_logging(logging.DEBUG)
        # Just ensure it doesn't raise an exception


# Integration tests
class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_complete_workflow(self, tmp_path):
        """Test the complete conversion workflow."""
        # Create a real markdown file
        md_content = """# Test Document

This is a **test** document with:

1. Ordered list
2. Another item

- Unordered list
- Another item

## Code block

```python
def hello():
    print("Hello, World!")
```

[Link](https://example.com)
"""

        md_file = tmp_path / "integration_test.md"
        md_file.write_text(md_content)

        output_dir = tmp_path / "output"

        # Run actual conversion (with real pypandoc)
        result = convert_md_to_docx(md_file, output_dir)

        # Verify output
        assert result is not None
        assert result.exists()
        assert result.suffix == ".docx"
        assert result.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__])
