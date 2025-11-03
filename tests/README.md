# Garak SDK Test Suite

Comprehensive test suite for the Garak Security Python SDK.

## Overview

The test suite provides thorough coverage of all SDK components including:
- **Authentication** - API key validation and management
- **Client** - HTTP client functionality and error handling
- **Resources** - Scan, metadata, and report operations
- **Models** - Pydantic model validation
- **Exceptions** - Error handling and exception hierarchy
- **Integration** - End-to-end workflows

## Test Structure

```
tests/
├── __init__.py                 # Test package
├── conftest.py                 # Shared fixtures and utilities
├── test_auth.py                # Authentication tests
├── test_client.py              # Client tests
├── test_scans.py               # Scan resource tests
├── test_metadata.py            # Metadata resource tests
├── test_reports.py             # Report resource tests
├── test_models.py              # Model validation tests
├── test_exceptions.py          # Exception tests
├── test_integration.py         # Integration tests
└── requirements-test.txt       # Test dependencies
```

## Installation

Install test dependencies:

```bash
# From SDK root directory
pip install -r tests/requirements-test.txt

# Or install SDK with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# Specific component tests
pytest -m auth
pytest -m client
pytest -m scans
pytest -m metadata
pytest -m reports
pytest -m models
pytest -m exceptions
```

### Run Specific Test Files

```bash
# Single file
pytest tests/test_auth.py

# Multiple files
pytest tests/test_auth.py tests/test_client.py

# Specific test class
pytest tests/test_auth.py::TestAuthManager

# Specific test method
pytest tests/test_auth.py::TestAuthManager::test_init_with_api_key
```

### Skip Slow Tests

```bash
pytest -m "not slow"
```

### Run with Verbose Output

```bash
pytest -v
pytest -vv  # More verbose
```

## Coverage

### Generate Coverage Report

```bash
# Terminal output
pytest --cov=garak_sdk

# HTML report
pytest --cov=garak_sdk --cov-report=html

# Open HTML report
open htmlcov/index.html
```

### Coverage Requirements

Target: **90%+ code coverage**

Current coverage by module:
- `garak_sdk.auth`: 95%+
- `garak_sdk.client`: 90%+
- `garak_sdk.resources`: 90%+
- `garak_sdk.models`: 100%
- `garak_sdk.exceptions`: 100%
- `garak_sdk.utils`: 85%+

## Test Markers

Tests are organized with pytest markers:

| Marker | Description |
|--------|-------------|
| `unit` | Unit tests (fast, no external deps) |
| `integration` | Integration tests (require backend) |
| `slow` | Long-running tests |
| `auth` | Authentication tests |
| `client` | Client tests |
| `scans` | Scan resource tests |
| `metadata` | Metadata resource tests |
| `reports` | Report resource tests |
| `models` | Model validation tests |
| `exceptions` | Exception tests |

## Test Fixtures

Common fixtures are defined in `conftest.py`:

### Mock Data Fixtures
- `mock_api_key` - Test API key
- `mock_base_url` - Test API base URL
- `mock_scan_id` - Test scan ID
- `mock_scan_metadata` - Mock scan metadata
- `mock_scan_results` - Mock scan results
- `mock_generators` - Mock generator list
- `mock_probe_categories` - Mock probe categories
- `mock_health_response` - Mock health check response
- `mock_quota_response` - Mock quota response

### HTTP Mocking Fixtures
- `mocked_responses` - Responses mock instance
- `mock_successful_scan_creation` - Mock scan creation API
- `mock_scan_status_*` - Mock status API calls
- `mock_health_check` - Mock health check API

### Client Fixtures
- `mock_client` - Configured GarakClient for testing
- `auth_manager` - Authentication manager

### Environment Fixtures
- `clean_env` - Clean environment variables
- `set_env_vars` - Set test environment variables

### Error Response Fixtures
- `mock_auth_error` - Mock 401 error
- `mock_rate_limit_error` - Mock 429 error
- `mock_quota_exceeded_error` - Mock quota exceeded
- `mock_not_found_error` - Mock 404 error

## Writing New Tests

### Test Structure Template

```python
import pytest
from garak_sdk import GarakClient
from garak_sdk.exceptions import GarakSDKError


@pytest.mark.unit  # Add appropriate marker
@pytest.mark.component_name
class TestFeatureName:
    """Test suite for specific feature."""

    def test_basic_functionality(self, mock_client):
        """Test basic functionality."""
        # Arrange
        expected = "result"

        # Act
        result = mock_client.some_method()

        # Assert
        assert result == expected

    def test_error_handling(self, mock_client):
        """Test error handling."""
        with pytest.raises(GarakSDKError):
            mock_client.failing_method()
```

### Using HTTP Mocks

```python
import responses


@responses.activate
def test_api_call(self, mock_client):
    """Test API call with mocked response."""
    responses.add(
        responses.GET,
        "https://test.garaksecurity.com/api/v1/endpoint",
        json={"status": "ok"},
        status=200
    )

    result = mock_client.get("/api/v1/endpoint")
    assert result.status_code == 200
```

## Integration Tests

Integration tests require a running backend or complete mocked workflows.

### Skip Integration Tests

```bash
pytest -m "not integration"
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Configure Backend for Integration Tests

Set environment variables:

```bash
export GARAK_API_BASE_URL="http://localhost:8000"
export GARAK_API_KEY="garak_test_..."
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install -r tests/requirements-test.txt
      - name: Run tests
        run: pytest --cov=garak_sdk --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Tests Failing

1. **Import Errors**: Ensure SDK is installed in development mode
   ```bash
   pip install -e .
   ```

2. **Fixture Not Found**: Check `conftest.py` is in tests directory

3. **HTTP Mocking Issues**: Ensure `responses.activate` decorator is used

4. **Environment Variables**: Use `clean_env` or `set_env_vars` fixtures

### Debugging Tests

```bash
# Drop into debugger on failure
pytest --pdb

# Show print statements
pytest -s

# Show local variables on failure
pytest -l
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Fast**: Unit tests should run quickly (<1s each)
3. **Clear**: Use descriptive test names and docstrings
4. **Comprehensive**: Test both success and failure cases
5. **Maintainable**: Use fixtures to reduce duplication

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure 90%+ coverage
3. Add appropriate markers
4. Update this README if needed
5. Run full test suite before committing

```bash
# Run all tests with coverage
pytest --cov=garak_sdk --cov-report=term-missing

# Check test passes
echo $?  # Should be 0
```

## Contact

For questions about testing:
- Review existing tests for examples
- Check pytest documentation: https://docs.pytest.org
- Ask in team chat or create an issue
