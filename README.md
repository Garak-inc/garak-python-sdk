# Garak Security SDK

> Python client library for the Garak AI Security Platform

[![PyPI version](https://badge.fury.io/py/garak-sdk.svg)](https://badge.fury.io/py/garak-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/garak-sdk.svg)](https://pypi.org/project/garak-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The Garak SDK provides programmatic access to the Garak AI Security Platform for running security scans against AI models, discovering vulnerabilities, and integrating security testing into your CI/CD pipelines.

## Features

- 🔒 **Security Scanning** - Run comprehensive security scans against AI models
- 🤖 **Multiple Generators** - Support for OpenAI, Anthropic, HuggingFace, and more
- 🎯 **Probe Categories** - Test for jailbreaks, harmful content, privacy violations, and more
- 📊 **Detailed Reports** - Download JSON, JSONL, and HTML reports
- ⚡ **CI/CD Integration** - Built for automation and continuous integration
- 🔄 **Async Support** - Efficient polling and waiting mechanisms
- 🛡️ **Type Safe** - Full Pydantic model support

## Installation

```bash
pip install garak-sdk
```

For development with `.env` file support:

```bash
pip install garak-sdk[dotenv]
```

## Quick Start

```python
from garak_sdk import GarakClient
import os

# Initialize client
client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

# Create a security scan
scan = client.scans.create(
    generator="openai",
    model_name="gpt-4",
    probe_categories=["jailbreak", "harmful"],
    api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
)

scan_id = scan['metadata']['scan_id']

# Wait for completion
scan = client.scans.wait_for_completion(scan_id)

# Get results
results = client.scans.get_results(scan_id)

# Calculate security score
overall_score = results['overallMetrics']['overallScore']
security_score = overall_score * 100
print(f"Security Score: {security_score:.1f}/100")
```

## Authentication

The Garak SDK supports two authentication methods:
1. **Firebase JWT** - For web users (interactive access)
2. **API Keys** - For CI/CD automation (programmatic access)

### API Keys for CI/CD

API keys are the recommended method for automation, CI/CD pipelines, and programmatic access.

#### Creating Your First API Key

1. **Log in to the dashboard** at [scans.garaksecurity.com](https://scans.garaksecurity.com)
2. **Navigate to** Settings → API Keys
3. **Click "Create API Key"**
4. **Configure your key:**
   - Name: Descriptive name (e.g., "GitHub Actions - Production")
   - Description: Purpose of the key
   - Rate Limit: Requests per minute (default: 100, max: 200)
   - Expiration: Days until expiration (default: 90, max: 365)
5. **Save the key securely** - it will only be shown once!

#### Security Requirements

To create API keys, your account must meet these requirements:
- ✅ Email address verified
- ✅ Account at least 24 hours old
- ✅ Maximum 5 active keys per account
- ✅ Maximum 20 total keys (including revoked)

#### API Key Permissions

User-created API keys have the following permissions:
- ✅ **Read**: List scans, get results, download reports
- ✅ **Write**: Create scans, update scan metadata
- ❌ **Admin**: Cannot create more API keys (prevents privilege escalation)

### Environment Variables

Set your API key as an environment variable:

```bash
export GARAK_API_KEY="garak_abc123..."
```

Or use a `.env` file:

```bash
# .env
GARAK_API_KEY=garak_abc123...
GARAK_API_BASE_URL=https://scans.garaksecurity.com

# Model API keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Creating a Scan

```python
scan = client.scans.create(
    generator="openai",
    model_name="gpt-4",
    probe_categories=["jailbreak", "harmful", "privacy"],
    name="Production Security Scan",
    description="Weekly security audit",
    api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
)
```

### Listing Scans

```python
from garak_sdk import ScanStatus

# List all scans
scans = client.scans.list(page=1, per_page=20)

# Filter by status
completed = client.scans.list(status=ScanStatus.COMPLETED)

# Search scans
results = client.scans.list(search="production")
```

### Monitoring Progress

```python
def on_progress(status):
    if status.get('progress'):
        print(f"Progress: {status['progress']['progress_percent']}%")

scan = client.scans.wait_for_completion(
    scan_id,
    timeout=3600,  # 1 hour
    poll_interval=10,  # Check every 10 seconds
    on_progress=on_progress
)
```

### Downloading Reports

```python
# Download a specific report
client.reports.download(
    scan_id,
    report_type="jsonl",
    output_path="./scan_report.jsonl"
)

# Download all reports
client.reports.download_all(
    scan_id,
    output_dir="./security-reports/"
)
```

### Discovering Generators and Probes

```python
# List available generators
generators = client.metadata.list_generators()
for gen in generators:
    print(f"{gen.name}: {gen.description}")

# List available models for a generator
models = client.metadata.list_models("openai")
print(f"OpenAI models: {models}")

# List probe categories
categories = client.metadata.list_probe_categories()
for cat in categories:
    print(f"{cat.name}: {len(cat.probes)} probes")
```

## CI/CD Integration

### Setting Up API Keys for CI/CD

#### Step 1: Create Dedicated API Keys

Create separate API keys for each environment and pipeline:

```bash
# Example key naming convention:
- "GitHub Actions - Production" (for main branch deployments)
- "GitHub Actions - Staging" (for staging branch)
- "Jenkins - Integration Tests" (for integration testing)
- "Local Development - John" (for local testing)
```

#### Step 2: Store Keys Securely

**GitHub Actions:**
1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `GARAK_API_KEY`
4. Value: Your API key (`garak_...`)
5. Click "Add secret"

**GitLab CI:**
1. Go to Project Settings → CI/CD → Variables
2. Add variable: `GARAK_API_KEY`
3. Check "Protect variable" and "Mask variable"
4. Save variable

**Jenkins:**
1. Go to Manage Jenkins → Manage Credentials
2. Add Credentials → Secret text
3. Secret: Your API key
4. ID: `garak-api-key`

**CircleCI:**
1. Project Settings → Environment Variables
2. Add Variable: `GARAK_API_KEY`

### GitHub Actions

#### Basic Security Scan

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Garak SDK
        run: pip install garak-sdk

      - name: Run Security Scan
        env:
          GARAK_API_KEY: ${{ secrets.GARAK_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GARAK_MIN_SCORE: 80
        run: |
          python - <<'EOF'
          from garak_sdk import GarakClient
          import os
          import sys

          client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

          # Create scan
          scan = client.scans.create(
              name=f"GitHub Actions - {os.getenv('GITHUB_REF_NAME', 'unknown')}",
              description=f"Security scan for commit {os.getenv('GITHUB_SHA', '')[:8]}",
              generator="openai",
              model_name="gpt-4",
              probe_categories=["jailbreak", "harmful"],
              api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
          )

          scan_id = scan['metadata']['scan_id']
          print(f"Created scan: {scan_id}")

          # Wait for completion
          scan = client.scans.wait_for_completion(
              scan_id,
              timeout=3600,
              poll_interval=10
          )

          # Get results
          results = client.scans.get_results(scan_id)

          # Check threshold
          min_score = float(os.getenv("GARAK_MIN_SCORE", "80"))
          overall_score = results['overallMetrics']['overallScore']
          actual_score = overall_score * 100

          print(f"\n{'='*60}")
          print(f"Security Score: {actual_score}/100")
          print(f"Threshold: {min_score}/100")
          print(f"{'='*60}\n")

          if actual_score < min_score:
              print(f"❌ FAILED: Security score {actual_score} below threshold {min_score}")
              sys.exit(1)

          print(f"✅ PASSED: Security scan passed with score {actual_score}/100")
          EOF

      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: ./security-reports/
```

#### Advanced: Matrix Testing Multiple Models

```yaml
name: Multi-Model Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  security-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        model:
          - generator: openai
            model_name: gpt-4
            probe_categories: jailbreak,harmful,privacy
          - generator: anthropic
            model_name: claude-3-opus-20240229
            probe_categories: jailbreak,harmful
          - generator: openai
            model_name: gpt-3.5-turbo
            probe_categories: jailbreak
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Garak SDK
        run: pip install garak-sdk

      - name: Run Security Scan - ${{ matrix.model.generator }}/${{ matrix.model.model_name }}
        env:
          GARAK_API_KEY: ${{ secrets.GARAK_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python - <<EOF
          from garak_sdk import GarakClient
          import os
          import json

          client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

          # Create scan
          scan = client.scans.create(
              name="${{ matrix.model.generator }}/${{ matrix.model.model_name }}",
              generator="${{ matrix.model.generator }}",
              model_name="${{ matrix.model.model_name }}",
              probe_categories="${{ matrix.model.probe_categories }}".split(','),
              api_keys={
                  "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                  "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
              }
          )

          scan_id = scan['metadata']['scan_id']

          # Wait and get results
          scan = client.scans.wait_for_completion(scan_id)
          results = client.scans.get_results(scan_id)

          # Save results
          with open("scan_results.json", "w") as f:
              json.dump(results, f, indent=2)

          overall_score = results.get('overallMetrics', {}).get('overallScore', 0)
          security_score = overall_score * 100
          print(f"Security Score: {security_score:.1f}/100")
          EOF

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: scan-results-${{ matrix.model.generator }}-${{ matrix.model.model_name }}
          path: scan_results.json

### GitLab CI

```yaml
# .gitlab-ci.yml
security_scan:
  stage: test
  image: python:3.11-slim
  before_script:
    - pip install garak-sdk
  script:
    - |
      python - <<'EOF'
      from garak_sdk import GarakClient
      import os
      import sys

      client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

      scan = client.scans.create(
          name=f"GitLab CI - {os.getenv('CI_COMMIT_REF_NAME')}",
          description=f"Commit {os.getenv('CI_COMMIT_SHORT_SHA')}",
          generator="openai",
          model_name="gpt-4",
          probe_categories=["jailbreak", "harmful"],
          api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
      )

      scan_id = scan['metadata']['scan_id']
      scan = client.scans.wait_for_completion(scan_id)
      results = client.scans.get_results(scan_id)

      overall_score = results['overallMetrics']['overallScore']
      security_score = overall_score * 100

      if security_score < 80:
          sys.exit(1)
      EOF
  artifacts:
    paths:
      - security-reports/
    when: always
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        GARAK_API_KEY = credentials('garak-api-key')
        OPENAI_API_KEY = credentials('openai-api-key')
    }

    stages {
        stage('Install') {
            steps {
                sh 'pip install garak-sdk'
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    python - <<'EOF'
                    from garak_sdk import GarakClient
                    import os
                    import sys

                    client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

                    scan = client.scans.create(
                        name=f"Jenkins - {os.getenv('BRANCH_NAME')}",
                        generator="openai",
                        model_name="gpt-4",
                        probe_categories=["jailbreak", "harmful"],
                        api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
                    )

                    scan_id = scan['metadata']['scan_id']
                    scan = client.scans.wait_for_completion(scan_id)
                    results = client.scans.get_results(scan_id)

                    overall_score = results.get('overallMetrics', {}).get('overallScore', 0)
                    score = overall_score * 100
                    print(f"Security Score: {score:.1f}/100")

                    if score < 80:
                        print("Security scan failed!")
                        sys.exit(1)
                    EOF
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'security-reports/**', allowEmptyArchive: true
        }
    }
}
```

### Python Script Examples

#### Basic CI/CD Script

```python
#!/usr/bin/env python3
"""
Basic CI/CD security scan script.
Usage: python cicd_scan.py
"""
from garak_sdk import GarakClient
import os
import sys

# Initialize client
client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

# Create and run scan
print("Creating security scan...")
scan = client.scans.create(
    generator="openai",
    model_name="gpt-4",
    probe_categories=["jailbreak", "harmful"],
    api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
)

scan_id = scan['metadata']['scan_id']
print(f"Scan created: {scan_id}")
print("Waiting for completion...")

# Wait for completion with progress
def on_progress(status):
    if status.get('progress'):
        print(f"Progress: {status['progress']['progress_percent']}%")

scan = client.scans.wait_for_completion(
    scan_id,
    timeout=3600,
    poll_interval=10,
    on_progress=on_progress
)

# Get results
results = client.scans.get_results(scan_id)

# Download reports
print("\nDownloading reports...")
client.reports.download_all(scan_id, output_dir="./security-reports/")

# Check threshold
min_score = float(os.getenv("GARAK_MIN_SCORE", "80"))
overall_score = results.get('overallMetrics', {}).get('overallScore', 0)
actual_score = overall_score * 100

print(f"\n{'='*60}")
print(f"Security Score: {actual_score}/100")
print(f"Threshold: {min_score}/100")
print(f"{'='*60}\n")

if actual_score < min_score:
    print(f"❌ FAILED: Security score {actual_score} below threshold {min_score}")
    sys.exit(1)

print(f"✅ PASSED: Security scan passed with score {actual_score}/100")
```

#### Advanced: Parallel Batch Scanning

```python
#!/usr/bin/env python3
"""
Advanced CI/CD script with parallel scanning of multiple models.
"""
from garak_sdk import GarakClient
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_scan(client, config):
    """Run a single scan and return results."""
    print(f"Starting scan: {config['name']}")

    scan = client.scans.create(**config)
    scan = client.scans.wait_for_completion(scan.metadata.scan_id, timeout=3600)
    results = client.scans.get_results(scan.metadata.scan_id)

    return {
        'name': config['name'],
        'scan_id': scan.metadata.scan_id,
        'score': results.get('security_score', 0),
        'results': results
    }

# Initialize client
client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

# Define scan configurations
scan_configs = [
    {
        'name': 'GPT-4 Security Scan',
        'generator': 'openai',
        'model_name': 'gpt-4',
        'probe_categories': ['jailbreak', 'harmful', 'privacy'],
        'api_keys': {'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')}
    },
    {
        'name': 'GPT-3.5 Security Scan',
        'generator': 'openai',
        'model_name': 'gpt-3.5-turbo',
        'probe_categories': ['jailbreak', 'harmful'],
        'api_keys': {'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')}
    },
    {
        'name': 'Claude Security Scan',
        'generator': 'anthropic',
        'model_name': 'claude-3-opus-20240229',
        'probe_categories': ['jailbreak', 'harmful'],
        'api_keys': {'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')}
    },
]

# Run scans in parallel
print(f"Running {len(scan_configs)} scans in parallel...")
results = []

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(run_scan, client, config) for config in scan_configs]

    for future in as_completed(futures):
        try:
            result = future.result()
            results.append(result)
            print(f"✓ Completed: {result['name']} - Score: {result['score']}/100")
        except Exception as e:
            print(f"✗ Failed: {e}")

# Check if all scans passed
min_score = float(os.getenv("GARAK_MIN_SCORE", "80"))
failed_scans = [r for r in results if r['score'] < min_score]

print(f"\n{'='*60}")
print(f"Results Summary:")
for result in results:
    status = "✅ PASS" if result['score'] >= min_score else "❌ FAIL"
    print(f"{status} {result['name']}: {result['score']}/100")
print(f"{'='*60}\n")

if failed_scans:
    print(f"❌ {len(failed_scans)} scan(s) failed!")
    sys.exit(1)

print(f"✅ All scans passed!")
```

## API Key Security Best Practices

### ✅ DO:

- **Create separate keys for each use case**
  - One key per CI/CD pipeline
  - One key per environment (prod, staging, dev)
  - One key per team member for local development

- **Use descriptive names**
  - ✅ "GitHub Actions - Production Pipeline"
  - ✅ "Jenkins - Integration Tests"
  - ✅ "Local Development - John Doe"
  - ❌ "my-key" or "test-key"

- **Rotate keys regularly**
  - Set expiration dates (default: 90 days)
  - Use the key rotation endpoint to update without downtime
  - Remove old keys after rotation

- **Store keys in secret managers**
  - GitHub Secrets
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
  - Google Secret Manager

- **Set appropriate rate limits**
  - Production: 100-200 requests/minute
  - Development: 50-100 requests/minute
  - Testing: 20-50 requests/minute

- **Monitor usage in the dashboard**
  - Check the "API Keys" page regularly
  - Review "Last Used" timestamps
  - Look for unusual IP addresses

- **Revoke keys immediately when:**
  - Key is compromised or leaked
  - Team member leaves
  - Pipeline is decommissioned
  - Suspicious activity is detected

### ❌ DON'T:

- **Don't share keys between people**
  - Each person should create their own key
  - Sharing makes it impossible to track who did what

- **Don't commit keys to git repositories**
  - Keys in git history are permanently exposed
  - Use `.env` files and add them to `.gitignore`

- **Don't use keys with overly broad permissions**
  - User keys are limited to read+write (good!)
  - Never share admin keys

- **Don't reuse keys across environments**
  - Production keys ≠ Staging keys ≠ Development keys
  - Environment isolation prevents accidents

- **Don't leave keys active indefinitely**
  - Always set an expiration date
  - Review and renew keys periodically

- **Don't ignore security alerts**
  - Check your email for security notifications
  - Review the dashboard for warnings

### 🚨 If Your Key Is Compromised:

1. **Immediately revoke the key**
   ```bash
   # Via dashboard: Settings → API Keys → Revoke
   # Or via API:
   curl -X POST https://scans.garaksecurity.com/api/v1/keys/{key_id}/revoke \
     -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
   ```

2. **Create a new key**
   - Log into dashboard
   - Create replacement key with a new name
   - Update your CI/CD secrets

3. **Review audit logs**
   - Check "Last Used" timestamp
   - Look for suspicious IP addresses
   - Review recent scans created with the key

4. **Rotate all other keys as a precaution**
   - If one key was compromised, others might be too
   - Use the rotation endpoint for zero-downtime updates

### Key Rotation Example

```python
from garak_sdk import GarakClient
import os

client = GarakClient(api_key=os.getenv("GARAK_API_KEY"))

# Rotate your key programmatically
new_key_response = client.keys.rotate(
    key_id=123,
    name="GitHub Actions - Production (Rotated)",
    expires_days=90
)

# Save the new key securely
new_key = new_key_response['new_api_key']
print(f"New key created: {new_key}")
print(f"Old key revoked: {new_key_response['old_key_id']}")

# Update your CI/CD secrets with the new key
```

## Examples

See the [`examples/`](examples/) directory for complete examples:

- [`basic_scan.py`](examples/basic_scan.py) - Simple security scan
- [`cicd_integration.py`](examples/cicd_integration.py) - CI/CD pipeline integration
- [`batch_scanning.py`](examples/batch_scanning.py) - Parallel batch scanning

## API Reference

### Client

```python
GarakClient(
    base_url: str = "https://scans.garaksecurity.com",
    api_key: str = None,
    timeout: int = 30,
    verify_ssl: bool = True
)
```

### Scans

- `client.scans.create()` - Create a new scan
- `client.scans.list()` - List scans with pagination
- `client.scans.get(scan_id)` - Get scan details
- `client.scans.get_status(scan_id)` - Get scan status
- `client.scans.wait_for_completion(scan_id)` - Wait for scan to complete
- `client.scans.update(scan_id)` - Update scan metadata
- `client.scans.cancel(scan_id)` - Cancel a running scan
- `client.scans.get_results(scan_id)` - Get scan results
- `client.scans.get_quota()` - Get quota information

### Metadata

- `client.metadata.list_generators()` - List available generators
- `client.metadata.get_generator(name)` - Get generator details
- `client.metadata.list_models(generator)` - List models for generator
- `client.metadata.list_probe_categories()` - List probe categories
- `client.metadata.list_probes(category)` - List probes in category
- `client.metadata.health_check()` - Check API health
- `client.metadata.get_api_info()` - Get API information

### Reports

- `client.reports.list(scan_id)` - List available reports
- `client.reports.download(scan_id, report_type, output_path)` - Download a report
- `client.reports.download_all(scan_id, output_dir)` - Download all reports

## Error Handling

```python
from garak_sdk import (
    GarakSDKError,
    AuthenticationError,
    QuotaExceededError,
    ScanNotFoundError,
    ScanTimeoutError
)

try:
    scan = client.scans.create(...)
except AuthenticationError:
    print("Invalid API key")
except QuotaExceededError:
    print("Quota exceeded, please upgrade")
except ScanTimeoutError:
    print("Scan timed out")
except GarakSDKError as e:
    print(f"Error: {e}")
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/Garak-inc/garak-python-sdk.git
cd garak-python-sdk

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black garak_sdk/
isort garak_sdk/

# Type checking
mypy garak_sdk/
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=garak_sdk --cov-report=html

# Run specific test
pytest tests/test_client.py
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@getgarak.com

## Links

- [Garak Dashboard](https://scans.garaksecurity.com)
- [GitHub Repository](https://github.com/Garak-inc/garak-python-sdk)
- [PyPI Package](https://pypi.org/project/garak-sdk/)

---

Made with ❤️ by [Garak Security](https://garaksecurity.com)
