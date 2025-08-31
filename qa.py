#!/usr/bin/env python3
"""
Quality assurance script for MW Convert.

This script runs all quality checks including tests, linting, and formatting
to ensure the codebase meets all quality standards.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """
    Run a command and return success status.

    Args:
        command: Command to run
        description: Description of what the command does

    Returns:
        True if command succeeded
    """
    print(f"\n🔍 {description}...")
    try:
        subprocess.run(command.split(), capture_output=True, text=True, check=True)
        print(f"✅ {description} passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {command}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        return False


def main() -> None:
    """Run all quality checks."""
    print("🚀 Running MW Convert Quality Assurance")
    print("=" * 50)

    # Change to project directory
    project_dir = Path(__file__).parent
    print(f"📁 Project directory: {project_dir}")

    # Define checks to run
    checks = [
        ("python -m pytest tests/ -v", "Running all tests"),
        (
            "python -m pytest tests/ --cov=main.py --cov=config.py "
            "--cov=utils.py --cov-report=term-missing",
            "Running tests with coverage",
        ),
        (
            "black --check main.py config.py utils.py gui_app.py tests/ qa.py",
            "Checking code formatting with black",
        ),
        (
            "isort --check-only main.py config.py utils.py gui_app.py tests/ qa.py",
            "Checking import sorting with isort",
        ),
        (
            "flake8 main.py config.py utils.py gui_app.py tests/ qa.py",
            "Checking code style with flake8",
        ),
        ("mypy main.py config.py utils.py", "Type checking with mypy"),
    ]

    # Track results
    passed = 0
    failed = 0

    # Run each check
    for command, description in checks:
        if run_command(command, description):
            passed += 1
        else:
            failed += 1

    # Final report
    print("\n" + "=" * 50)
    print("📊 Quality Assurance Report")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success rate: {passed / (passed + failed) * 100:.1f}%")

    if failed == 0:
        print("\n🎉 All quality checks passed! Code is ready for deployment.")
        sys.exit(0)
    else:
        print(
            f"\n⚠️  {failed} quality check(s) failed. "
            "Please fix issues before deployment."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
