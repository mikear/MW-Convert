# 🚀 Development Guide for MW Convert

This guide provides comprehensive information for developers working on the MW Convert project.

## 📋 Table of Contents

- [Project Structure](#-project-structure)
- [Development Setup](#-development-setup)
- [Code Quality](#-code-quality)
- [Testing](#-testing)
- [Architecture](#-architecture)
- [Contributing](#-contributing)

## 📁 Project Structure

```
MW-Convert/
├── main.py                    # Core conversion module (refactored)
├── gui_app.py                # GUI application (refactored)
├── config.py                 # Configuration management
├── utils.py                  # Utility functions
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── pyproject.toml           # Tool configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
├── .flake8                  # Flake8 configuration
├── qa.py                    # Quality assurance script
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_main_improved.py
│   ├── test_config.py
│   └── test_utils.py
├── icons/                   # Application icons
├── templates/              # DOCX templates
├── examples/               # Example files
└── markdowns/             # Test markdown files
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.9 or higher
- Pandoc installed and in PATH
- Git for version control

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mikear/MW-Convert.git
   cd MW-Convert
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks (optional):**
   ```bash
   pre-commit install
   ```

## ⚡ Quick Start

### Run the Application
```bash
python gui_app.py
```

### Run Tests
```bash
python -m pytest tests/ -v
```

### Run Quality Checks
```bash
python qa.py
```

## 🔍 Code Quality

This project maintains high code quality standards using multiple tools:

### Formatting
- **Black**: Code formatting
- **isort**: Import sorting

### Linting
- **flake8**: Style guide enforcement
- **mypy**: Type checking

### Quality Assurance Script

Run all quality checks at once:
```bash
python qa.py
```

This script runs:
- All tests with coverage
- Code formatting checks
- Import sorting validation
- Style guide compliance
- Type checking

### Manual Quality Checks

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 .

# Type checking
mypy main.py config.py utils.py

# Run tests with coverage
pytest tests/ --cov=main.py --cov=config.py --cov=utils.py --cov-report=term-missing
```

## 🧪 Testing

### Test Structure

- **test_main_improved.py**: Tests for core conversion functionality
- **test_config.py**: Tests for configuration management
- **test_utils.py**: Tests for utility functions

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_main_improved.py -v

# Run tests matching pattern
pytest tests/ -k "test_validation"
```

### Test Coverage

Current test coverage:
- **main.py**: 69% coverage
- **config.py**: 92% coverage
- **utils.py**: 82% coverage
- **Total**: 64 tests passing

## 🏗️ Architecture

### Core Modules

#### main.py
- **Purpose**: Core conversion functionality
- **Features**: Type hints, logging, validation, error handling
- **Key Functions**: `convert_md_to_docx()`, validation functions

#### gui_app.py
- **Purpose**: Graphical user interface
- **Features**: Modern Qt interface, threading, drag-and-drop
- **Key Classes**: `MarkdownConverterApp`, `ConversionWorker`, `StyleManager`

#### config.py
- **Purpose**: Centralized configuration management
- **Features**: Application settings, file paths, validation
- **Key Class**: `AppConfig`

#### utils.py
- **Purpose**: Reusable utility functions
- **Features**: File operations, system integration, validation
- **Key Functions**: File handling, system operations, validation helpers

### Design Patterns

- **Separation of Concerns**: Clear separation between GUI, logic, and configuration
- **Factory Pattern**: Configuration management
- **Observer Pattern**: Qt signals and slots for GUI
- **Strategy Pattern**: Different validation strategies

## 🔄 Contributing

### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Run quality checks:**
   ```bash
   python qa.py
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   ```

6. **Push and create a pull request**

### Coding Standards

- **Type Hints**: All functions must have type hints
- **Docstrings**: All public functions must have docstrings
- **Error Handling**: Proper exception handling with custom exceptions
- **Logging**: Use the logging module instead of print statements
- **Testing**: New features must include tests

### Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## 📊 Code Metrics

### Quality Metrics
- ✅ 100% of files pass linting (flake8)
- ✅ 100% of files pass formatting (black)
- ✅ 100% of files pass import sorting (isort)
- ✅ 100% of files pass type checking (mypy)
- ✅ 64 tests passing
- ✅ High test coverage on core modules

### Performance Metrics
- Fast startup time
- Responsive GUI with threading
- Efficient file processing
- Memory-conscious operations

## 🛡️ Security Considerations

- Input validation for all file paths
- Sanitization of user inputs
- Secure file operations
- No execution of user-provided code
- Validation of file types and extensions

## 📚 Additional Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Pandoc Documentation](https://pandoc.org/MANUAL.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)

## 🆘 Troubleshooting

### Common Issues

1. **Pandoc not found**: Install Pandoc and ensure it's in your PATH
2. **Qt display issues**: Set `QT_QPA_PLATFORM=offscreen` for headless environments
3. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements-dev.txt`

### Getting Help

- Check the test files for usage examples
- Review the docstrings for function documentation
- Run `python qa.py` to identify code quality issues
- Check the logs in `mw_convert.log` for runtime issues

---

**Last Updated**: 2025-08-31  
**Version**: 1.3  
**Maintainer**: Diego A. Rábalo