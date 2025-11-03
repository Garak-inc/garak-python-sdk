# Garak SDK Examples

Comprehensive examples demonstrating how to use the Garak SDK for LLM security scanning in various scenarios.

## 📚 Available Examples

### 1. **Quick Start** (`quickstart.py`) ⭐ NEW
The fastest way to get started - scan your LLM in just a few lines of code!

**Use when:** You want to quickly test the SDK or run a simple scan.

```bash
python quickstart.py
```

**Features:**
- Minimal code (< 50 lines)
- Uses free tier
- Automatic result retrieval
- Report downloading

---

### 2. **End-to-End User Flow** (`end_to_end_flow.py`) ⭐ NEW
Interactive example with step-by-step guidance through the complete scanning workflow.

**Use when:** You're learning the SDK for the first time.

```bash
python end_to_end_flow.py
```

**Features:**
- Step-by-step guidance with progress bars
- Quota checking and option discovery
- Result analysis and interpretation
- Interactive and educational

---

### 3. **Complete CI/CD Integration** (`complete_cicd_integration.py`) ⭐ NEW
Production-ready CI/CD pipeline integration with comprehensive error handling.

**Use when:** Integrating security scans into your CI/CD pipeline.

```bash
python complete_cicd_integration.py
```

**Features:**
- Environment-based configuration
- Pre-scan validation and quota checking
- Real-time progress monitoring with logging
- Security threshold validation
- Automated report generation
- Exit codes for CI/CD control (0 = pass, 1 = fail)
- Production-ready error handling

**Environment Variables:**
```bash
# Required
export GARAK_API_KEY=gsk_your_api_key_here

# Optional - Model Configuration
export MODEL_GENERATOR=openai          # Default: openai
export MODEL_NAME=gpt-4                # Default: gpt-3.5-turbo
export PROBE_CATEGORIES=jailbreak,harmful  # Default: jailbreak,harmful

# Optional - Security Configuration
export SECURITY_THRESHOLD=80.0         # Default: 80.0 (0-100)
export SCAN_TIMEOUT=3600               # Default: 3600 seconds

# Optional - Report Configuration
export DOWNLOAD_REPORTS=true           # Default: true
export REPORT_DIR=./reports            # Default: ./reports
```

**CI/CD Examples:**

**GitHub Actions:**
```yaml
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install SDK
        run: pip install garak-sdk
      - name: Run Security Scan
        env:
          GARAK_API_KEY: ${{ secrets.GARAK_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          SECURITY_THRESHOLD: 80.0
        run: python examples/complete_cicd_integration.py
      - name: Upload Reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: reports/
```

**GitLab CI:**
```yaml
security_scan:
  stage: test
  image: python:3.10
  script:
    - pip install garak-sdk
    - python examples/complete_cicd_integration.py
  variables:
    SECURITY_THRESHOLD: "80.0"
  artifacts:
    paths: [reports/]
    when: always
```

**Jenkins:**
```groovy
pipeline {
    agent any
    environment {
        GARAK_API_KEY = credentials('garak-api-key')
        OPENAI_API_KEY = credentials('openai-api-key')
        SECURITY_THRESHOLD = '80.0'
    }
    stages {
        stage('Security Scan') {
            steps {
                sh 'pip install garak-sdk'
                sh 'python examples/complete_cicd_integration.py'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**'
        }
    }
}
```

---

### 4. **Error Handling** (`error_handling.py`) ⭐ NEW
Comprehensive error handling patterns for production use.

**Use when:** Building production applications or handling edge cases.

```bash
python error_handling.py
```

**Features:**
- Safe client initialization
- Quota management
- Rate limit handling with retry
- Network error recovery
- Scan error handling
- Context manager usage
- Production-ready patterns

**Covered Errors:**
- `AuthenticationError`, `QuotaExceededError`, `ScanNotFoundError`
- `ScanTimeoutError`, `RateLimitError`, `NetworkError`
- `InvalidConfigurationError`

---

### 5. **Basic Scan** (`basic_scan.py`)
Simple security scan example with progress tracking.

```bash
python basic_scan.py
```

**Features:**
- Health check and quota verification
- Create and run security scan
- Wait for completion with progress updates
- Download and analyze results

---

### 6. **CI/CD Integration** (`cicd_integration.py`)
Original CI/CD example with threshold validation.

```bash
export GARAK_API_KEY="gsk_..."
export OPENAI_API_KEY="sk-..."
export GARAK_MIN_SCORE=80
python cicd_integration.py
```

**Features:**
- Configurable thresholds
- Exit codes for pass/fail
- Report generation
- Environment-based config

---

### 7. **Batch Scanning** (`batch_scanning.py`)
Parallel scanning of multiple models.

```bash
python batch_scanning.py
```

**Features:**
- Parallel scan execution
- Multiple model configurations
- Performance comparison
- Batch result analysis

---

## 🚀 Getting Started

### Prerequisites

1. **Install the SDK:**
```bash
pip install garak-sdk
# Or from source
pip install -e ..
```

2. **Get API Key:**
- Sign up at https://detect.garaksecurity.com
- Navigate to Settings → API Keys
- Generate a new API key

3. **Set Environment:**
```bash
export GARAK_API_KEY=gsk_your_api_key_here
# Optional: Model-specific keys
export OPENAI_API_KEY=sk_your_openai_key
export ANTHROPIC_API_KEY=sk_your_anthropic_key
```

### Running Examples

```bash
# Quick test
python quickstart.py

# Learn the SDK
python end_to_end_flow.py

# CI/CD integration
python complete_cicd_integration.py

# Error handling
python error_handling.py
```

---

## 🎯 Complete User Flow

Step-by-step workflow from start to finish:

### 1. Setup
```bash
pip install garak-sdk
export GARAK_API_KEY=gsk_your_key
```

### 2. Initialize
```python
from garak_sdk import GarakClient
client = GarakClient()
```

### 3. Check Quota
```python
quota = client.scans.get_quota()
print(f"Remaining: {quota.quota_status.remaining_total_scans}")
```

### 4. Discover Options
```python
generators = client.metadata.list_generators()
categories = client.metadata.list_probe_categories()
```

### 5. Create Scan
```python
scan = client.scans.create(
    generator="openai",
    model_name="gpt-4",
    probe_categories=["jailbreak", "harmful"],
    api_keys={"OPENAI_API_KEY": "sk_..."}
)
scan_id = scan.metadata.scan_id
```

### 6. Monitor Progress
```python
def on_progress(status):
    print(f"Progress: {status.progress.percentage:.1f}%")

final_scan = client.scans.wait_for_completion(
    scan_id, timeout=3600, on_progress=on_progress
)
```

### 7. Get Results
```python
results = client.scans.get_results(scan_id)
print(f"Score: {results['security_score']:.1f}/100")
```

### 8. Download Reports
```python
reports = client.reports.download_all(scan_id, "./reports")
```

### 9. Validate (CI/CD)
```python
if results['security_score'] >= 80:
    sys.exit(0)  # Pass
else:
    sys.exit(1)  # Fail
```

---

## 📊 Exit Codes (CI/CD)

| Code | Meaning |
|------|---------|
| 0 | Success - meets threshold |
| 1 | Failure - below threshold or error |

---

## 🐛 Troubleshooting

### "No API key provided"
```bash
export GARAK_API_KEY=gsk_your_key
```

### "Authentication failed"
- Verify API key is correct
- Check account is active
- Ensure key hasn't been revoked

### "Quota exceeded"
- Check quota at dashboard
- Upgrade subscription
- Wait for quota reset

### "Scan timeout"
- Increase timeout parameter
- Check scan status manually
- Verify scan didn't fail

### "Network error"
- Check internet connection
- Verify firewall settings
- Try again later

---

## 📚 Resources

- **Documentation:** https://docs.garaksecurity.com
- **Dashboard:** https://detect.garaksecurity.com
- **SDK Reference:** ../README.md
- **Support:** support@garaksecurity.com

---

## 💡 Best Practices

1. **Always check quota** before running scans
2. **Use context managers** for automatic cleanup
3. **Implement retry logic** for network errors
4. **Set appropriate timeouts** based on scan size
5. **Store reports** as CI/CD artifacts
6. **Use environment variables** (never hardcode keys)
7. **Monitor progress** to detect stuck scans
8. **Validate results** against thresholds

---

## 🤝 Contributing

Have a useful example? Submit a PR!

1. Create example file
2. Add documentation
3. Update this README
4. Test thoroughly
5. Submit PR
