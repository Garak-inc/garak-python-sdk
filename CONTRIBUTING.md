# Contributing to Garak SDK

Thank you for your interest in contributing to the Garak SDK! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Development Setup

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/garak-python-sdk.git
   cd garak-python-sdk
   ```

3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/garak-security/garak-python-sdk.git
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   pip install types-requests
   ```

5. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test improvements

### 2. Make Changes

- Write clear, concise code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=garak_sdk --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### 4. Check Code Quality

```bash
# Format code
black garak_sdk/ tests/
isort garak_sdk/ tests/

# Type checking
mypy garak_sdk/

# Linting
flake8 garak_sdk/ tests/

# Security scan
bandit -r garak_sdk/
```

Or use pre-commit to run all checks:
```bash
pre-commit run --all-files
```

### 5. Commit Changes

Write clear commit messages following [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add support for new probe category"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Build/tooling changes

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub:
- Use a clear, descriptive title
- Reference any related issues
- Describe what changed and why
- Include examples if applicable

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all function signatures
- Maximum line length: 100 characters (enforced by Black)
- Use descriptive variable names

### Documentation

- Add docstrings to all public functions, classes, and modules
- Use Google-style docstrings:
  ```python
  def function(arg1: str, arg2: int) -> bool:
      """
      Brief description of function.

      Args:
          arg1: Description of arg1
          arg2: Description of arg2

      Returns:
          Description of return value

      Raises:
          ValueError: When something is wrong

      Example:
          >>> function("test", 42)
          True
      """
  ```

### Testing

- Write tests for all new functionality
- Aim for >90% code coverage
- Use descriptive test names: `test_function_name_expected_behavior`
- Include edge cases and error conditions

## Pull Request Process

1. **Update Documentation**: Update README.md and docstrings as needed
2. **Add Tests**: Ensure new code is tested
3. **Pass CI**: All CI checks must pass
4. **Code Review**: Address review feedback
5. **Squash Commits**: Clean up commit history before merge

## Reporting Issues

### Bug Reports

Include:
- Python version
- SDK version
- Minimal reproduction code
- Expected vs actual behavior
- Error messages/stack traces

### Feature Requests

Include:
- Use case description
- Proposed API/interface
- Examples of usage
- Alternatives considered

## Development Tips

### Running Tests Locally

```bash
# Quick test run
pytest -x  # Stop on first failure

# Test specific module
pytest tests/test_scans.py

# Test with verbose output
pytest -v

# Test with coverage
pytest --cov=garak_sdk --cov-report=term-missing
```

### Debugging

```bash
# Run with debugging
pytest --pdb  # Drop into debugger on failure

# Print output
pytest -s  # Show print statements
```

### Type Checking

```bash
# Check all files
mypy garak_sdk/

# Check specific file
mypy garak_sdk/client.py

# Show error codes
mypy --show-error-codes garak_sdk/
```

## Release Process

Releases are handled by maintainers:

1. Update version in `garak_sdk/__init__.py`
2. Update CHANGELOG.md
3. Create GitHub release with tag (e.g., `v1.0.0`)
4. CI automatically publishes to PyPI

## Questions?

- 📧 Email: support@garaksecurity.com
- 💬 Discord: https://discord.gg/garak-security
- 🐛 Issues: https://github.com/garak-security/garak-python-sdk/issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Garak SDK!
