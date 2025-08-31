"""
Core module for Markdown to DOCX conversion using pypandoc.

This module provides the main conversion functionality for the MW Convert application.
It includes proper logging, error handling, input validation, and type hints.
"""

import logging
from pathlib import Path
from typing import Optional, Union

import pypandoc


# Configure logging
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Custom exception for conversion-related errors."""

    pass


class ValidationError(Exception):
    """Custom exception for input validation errors."""

    pass


def setup_logging(level: int = logging.INFO) -> None:
    """
    Set up logging configuration for the application.

    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("mw_convert.log")],
    )


def validate_input_file(input_path: Union[str, Path]) -> Path:
    """
    Validate the input Markdown file.

    Args:
        input_path: Path to the input Markdown file

    Returns:
        Validated Path object

    Raises:
        ValidationError: If the file is invalid
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise ValidationError(f"Input file does not exist: {input_path}")

    if not input_path.is_file():
        raise ValidationError(f"Input path is not a file: {input_path}")

    if input_path.suffix.lower() != ".md":
        logger.warning(f"Input file does not have .md extension: {input_path}")

    if input_path.stat().st_size == 0:
        raise ValidationError(f"Input file is empty: {input_path}")

    return input_path


def validate_template_file(template_path: Union[str, Path]) -> Path:
    """
    Validate the DOCX template file.

    Args:
        template_path: Path to the DOCX template file

    Returns:
        Validated Path object

    Raises:
        ValidationError: If the template is invalid
    """
    template_path = Path(template_path)

    if not template_path.exists():
        raise ValidationError(f"Template file does not exist: {template_path}")

    if not template_path.is_file():
        raise ValidationError(f"Template path is not a file: {template_path}")

    if template_path.suffix.lower() != ".docx":
        raise ValidationError(f"Template file must be a .docx file: {template_path}")

    return template_path


def create_output_directory(output_dir: Union[str, Path]) -> Path:
    """
    Create and validate the output directory.

    Args:
        output_dir: Path to the output directory

    Returns:
        Path object for the output directory

    Raises:
        ValidationError: If the directory cannot be created
    """
    output_dir = Path(output_dir)

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ready: {output_dir}")
        return output_dir
    except PermissionError as e:
        raise ValidationError(f"Permission denied creating output directory: {e}")
    except OSError as e:
        raise ValidationError(f"Error creating output directory: {e}")


def convert_md_to_docx(
    input_md_path: Union[str, Path],
    output_dir: Union[str, Path] = "output",
    reference_docx_path: Optional[Union[str, Path]] = None,
) -> Optional[Path]:
    """
    Convert a Markdown file to DOCX using pypandoc with comprehensive error handling.

    Args:
        input_md_path: Path to the input Markdown file
        output_dir: Directory for output files (default: "output")
        reference_docx_path: Optional path to a DOCX template file

    Returns:
        Path to the generated DOCX file, or None if conversion fails

    Raises:
        ValidationError: If input validation fails
        ConversionError: If the conversion process fails
    """
    try:
        # Validate inputs
        input_path = validate_input_file(input_md_path)
        logger.info(f"Converting file: {input_path}")

        # Create output directory
        output_path = create_output_directory(output_dir)

        # Validate template if provided
        if reference_docx_path:
            validate_template_file(reference_docx_path)
            logger.info(f"Using template: {reference_docx_path}")

        # Generate output file path
        output_filename = input_path.stem + ".docx"
        output_docx_path = output_path / output_filename

        # Prepare conversion arguments
        extra_args = []
        if reference_docx_path:
            extra_args.extend(["--reference-doc", str(reference_docx_path)])

        # Perform conversion
        logger.info("Starting conversion process...")
        pypandoc.convert_file(
            str(input_path),
            "docx",
            format="gfm+smart",  # GitHub-Flavored Markdown with smart typography
            outputfile=str(output_docx_path),
            extra_args=extra_args,
        )

        # Verify output file was created
        if not output_docx_path.exists():
            raise ConversionError("Output file was not created successfully")

        logger.info(f"Conversion successful: {output_docx_path}")
        return output_docx_path

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except Exception as e:
        error_msg = f"Conversion failed: {e}"
        logger.error(error_msg)
        raise ConversionError(error_msg) from e


def main() -> None:
    """Main function for testing and demonstration purposes."""
    setup_logging()

    logger.info("Starting MW Convert test")

    # Create test Markdown content
    dummy_md_content = """# Documento de Prueba

Este es un archivo markdown de prueba.

**Listas:**

**Lista Ordenada:**
1. Primer elemento
2. Segundo elemento
   1. Sub-elemento 2.1
   2. Sub-elemento 2.2
3. Tercer elemento

**Lista Desordenada:**
* Elemento A
* Elemento B
  * Sub-elemento B.1
  * Sub-elemento B.2
* Elemento C

## Código

```python
def hello_world():
    print("Hello, World!")
```

## Enlaces y énfasis

Este es un [enlace](https://example.com) y esto es **texto en negrita** 
y esto es *texto en cursiva*.

---

Fin del documento de prueba.
"""

    test_md_path = Path("test_input.md")

    try:
        # Write test file
        test_md_path.write_text(dummy_md_content, encoding="utf-8")
        logger.info(f"Created test file: {test_md_path}")

        # Perform conversion
        converted_file = convert_md_to_docx(test_md_path)

        if converted_file:
            logger.info(f"Test conversion successful: {converted_file}")
            print(f"✅ Convertido exitosamente a: {converted_file}")
        else:
            print("❌ La conversión falló.")

    except (ValidationError, ConversionError) as e:
        print(f"❌ Error durante la conversión: {e}")
        logger.error(f"Test failed: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        logger.error(f"Unexpected error in test: {e}")
    finally:
        # Clean up test file
        if test_md_path.exists():
            test_md_path.unlink()
            logger.info("Cleaned up test file")


if __name__ == "__main__":
    main()
