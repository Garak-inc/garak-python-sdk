# Publishing Garak SDK to PyPI

This guide walks through publishing the garak-sdk package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts at:
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/

2. **API Tokens**: Generate API tokens for authentication:
   - Test PyPI: https://test.pypi.org/manage/account/token/
   - Production PyPI: https://pypi.org/manage/account/token/

3. **Configure Credentials**: Save tokens in `~/.pypirc`:
   ```ini
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-your-production-token-here

   [testpypi]
   username = __token__
   password = pypi-your-test-token-here
   ```

   **Important**: Set proper permissions:
   ```bash
   chmod 600 ~/.pypirc
   ```

## Current Build Status

✅ **Package built successfully!**

Built files in `dist/`:
- `garak_sdk-1.0.0-py3-none-any.whl` (21 KB)
- `garak_sdk-1.0.0.tar.gz` (35 KB)

✅ **Package validation passed!**
- Twine check: PASSED
- README rendering: OK
- Metadata: Valid

## Publishing Steps

### Step 1: Upload to Test PyPI (Recommended First)

Test the package on Test PyPI before production:

```bash
# Upload to Test PyPI
python3 -m twine upload --repository testpypi dist/*

# Or explicitly specify the repository URL
python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### Step 2: Test Installation from Test PyPI

Verify the package can be installed from Test PyPI:

```bash
# Create a test virtual environment
python3 -m venv test_env
source test_env/bin/activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple garak-sdk

# Test the package
python3 -c "import garak_sdk; print(garak_sdk.__version__)"

# Test basic functionality
python3 -c "from garak_sdk import GarakClient; print('Import successful')"

# Deactivate and clean up
deactivate
rm -rf test_env
```

### Step 3: Upload to Production PyPI

Once verified on Test PyPI, upload to production:

```bash
# Upload to production PyPI
python3 -m twine upload dist/*

# Or explicitly
python3 -m twine upload --repository pypi dist/*
```

### Step 4: Verify Production Installation

Test the live package:

```bash
# Install from production PyPI
pip install garak-sdk

# Verify version
python3 -c "import garak_sdk; print(garak_sdk.__version__)"

# Check all imports work
python3 -c "
from garak_sdk import (
    GarakClient,
    ScanStatus,
    ReportType,
    GarakSDKError,
    AuthenticationError
)
print('✓ All imports successful')
"
```

### Step 5: Create GitHub Release

1. Tag the release:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. Create release on GitHub:
   - Go to https://github.com/garak-security/garak-python-sdk/releases/new
   - Select tag: `v1.0.0`
   - Release title: `v1.0.0 - Initial Release`
   - Description: See template below
   - Upload `dist/*` files as release assets

## Release Notes Template

```markdown
# Garak SDK v1.0.0

Initial release of the Garak Security SDK for Python.

## Features

- 🔒 **Security Scanning** - Run comprehensive security scans against AI models
- 🤖 **Multiple Generators** - Support for OpenAI, Anthropic, HuggingFace, and more
- 🎯 **Probe Categories** - Test for jailbreaks, harmful content, privacy violations
- 📊 **Detailed Reports** - Download JSON, JSONL, and HTML reports
- ⚡ **CI/CD Integration** - Built for automation and continuous integration
- 🔄 **Async Support** - Efficient polling and waiting mechanisms
- 🛡️ **Type Safe** - Full Pydantic model support with mypy type checking

## Installation

```bash
pip install garak-sdk
```

## Quick Start

```python
from garak_sdk import GarakClient
import os

client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

scan = client.scans.create(
    generator="openai",
    model_name="gpt-4",
    probe_categories=["jailbreak", "harmful"]
)

scan = client.scans.wait_for_completion(scan.metadata.scan_id)
results = client.scans.get_results(scan.metadata.scan_id)
```

## Documentation

- [README](https://github.com/garak-security/garak-python-sdk#readme)
- [API Documentation](https://docs.garaksecurity.com)
- [Examples](https://github.com/garak-security/garak-python-sdk/tree/main/examples)

## Requirements

- Python 3.8+
- requests >= 2.31.0
- pydantic >= 2.0.0

## What's Included

- Full SDK implementation (93% test coverage)
- Type-safe with mypy
- Security scanned (bandit, pip-audit)
- Code formatted (black, isort)
- Comprehensive examples
- CI/CD integration examples
```

## Troubleshooting

### Issue: Authentication Error

**Error**: `403 Invalid or non-existent authentication information`

**Solution**:
1. Verify your API token is correct
2. Ensure `~/.pypirc` has correct format
3. Token username must be `__token__`

### Issue: Package Already Exists

**Error**: `400 File already exists`

**Solution**: You cannot re-upload the same version. Options:
1. Bump version in `garak_sdk/__init__.py`
2. Delete the package on PyPI (only for mistakes)

### Issue: README Not Rendering

**Error**: `The description failed to render`

**Solution**:
1. Check README markdown syntax
2. Run `twine check dist/*` to validate
3. Test rendering at https://readme-renderer.readthedocs.io/

### Issue: Missing Dependencies

**Error**: Package installs but imports fail

**Solution**:
1. Verify `pyproject.toml` dependencies are correct
2. Check `setup.py` matches `pyproject.toml`
3. Rebuild: `rm -rf dist/ && python3 -m build`

## Post-Publishing Checklist

- [ ] Package installed successfully from PyPI
- [ ] All imports work correctly
- [ ] Example scripts run without errors
- [ ] GitHub release created with tag
- [ ] Release notes published
- [ ] README badges updated (PyPI version)
- [ ] Documentation updated
- [ ] Announcement posted (Twitter, Discord, etc.)
- [ ] Monitor PyPI download stats

## Updating the Package

For future releases:

1. **Update Version**:
   ```python
   # In garak_sdk/__init__.py
   __version__ = "1.0.1"  # or "1.1.0", "2.0.0"
   ```

2. **Update CHANGELOG** (create if doesn't exist):
   ```markdown
   ## [1.0.1] - 2025-01-15
   ### Fixed
   - Bug fix description
   ### Added
   - New feature description
   ```

3. **Rebuild**:
   ```bash
   rm -rf dist/ build/ *.egg-info
   python3 -m build
   twine check dist/*
   ```

4. **Publish**:
   ```bash
   # Test first
   twine upload --repository testpypi dist/*

   # Then production
   twine upload dist/*
   ```

5. **Tag Release**:
   ```bash
   git tag -a v1.0.1 -m "Release version 1.0.1"
   git push origin v1.0.1
   ```

## Automation with GitHub Actions

The `.github/workflows/publish.yml` workflow automates publishing:

### Manual Trigger (Test PyPI):
```bash
# Go to GitHub Actions → Publish to PyPI → Run workflow
# Check "Publish to Test PyPI"
```

### Automatic (Production PyPI):
- Create a GitHub release
- CI automatically publishes to PyPI
- Requires PyPI API token in GitHub Secrets

### Setup GitHub Secrets:

1. Go to repository Settings → Secrets and variables → Actions
2. Add secrets:
   - `PYPI_API_TOKEN` - Production PyPI token
   - `TEST_PYPI_API_TOKEN` - Test PyPI token

## Package URLs

After publishing:

- **PyPI**: https://pypi.org/project/garak-sdk/
- **Test PyPI**: https://test.pypi.org/project/garak-sdk/
- **Stats**: https://pypistats.org/packages/garak-sdk
- **Libraries.io**: https://libraries.io/pypi/garak-sdk

## Support

Questions? Contact:
- Email: support@garaksecurity.com
- Issues: https://github.com/garak-security/garak-python-sdk/issues
