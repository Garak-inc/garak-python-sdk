"""
CI/CD Integration Example

Example of integrating Garak security scans into CI/CD pipelines.
This script can be used in GitHub Actions, GitLab CI, Jenkins, etc.
"""

import os
import sys
from dotenv import load_dotenv
from garak_sdk import GarakClient, ScanStatus

# Load environment variables
load_dotenv()


def run_security_scan(
    generator: str,
    model_name: str,
    min_security_score: float = 80.0,
    max_failed_prompts: int = 5
) -> bool:
    """
    Run security scan and validate against thresholds.

    Args:
        generator: Generator type (e.g., 'openai')
        model_name: Model name (e.g., 'gpt-4')
        min_security_score: Minimum acceptable security score (0-100)
        max_failed_prompts: Maximum allowed failed prompts

    Returns:
        True if scan passes validation, False otherwise
    """
    print("=" * 60)
    print("CI/CD Security Scan - Garak SDK")
    print("=" * 60)

    # Initialize client
    client = GarakClient(
        base_url=os.getenv("GARAK_API_BASE_URL", "https://detect.garaksecurity.com"),
        api_key=os.getenv("GARAK_API_KEY")
    )

    print(f"\n✓ Connected to Garak API")
    print(f"  Generator: {generator}")
    print(f"  Model: {model_name}")
    print(f"  Min Security Score: {min_security_score}")
    print(f"  Max Failed Prompts: {max_failed_prompts}")

    # Create scan
    print("\n" + "-" * 60)
    print("Creating security scan...")

    try:
        scan = client.scans.create(
            generator=generator,
            model_name=model_name,
            probe_categories=["dan", "toxicity", "privacy"],  # Valid: dan, security, privacy, toxicity, hallucination, performance, robustness, ethics, stereotype
            name=f"CI/CD Scan - {os.getenv('CI_COMMIT_SHA', 'local')[:8]}",
            description=f"Automated security scan for {model_name}",
            api_keys={
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            }
        )

        print(f"✓ Scan created: {scan.metadata.scan_id}")

    except Exception as e:
        print(f"✗ Failed to create scan: {e}")
        return False

    # Wait for completion
    print("\n" + "-" * 60)
    print("Running security scan...")

    try:
        scan = client.scans.wait_for_completion(
            scan.metadata.scan_id,
            timeout=3600,
            poll_interval=15,
            on_progress=lambda s: print(f"  Progress: {s.progress.percentage:.1f}%") if s.progress else None
        )

        print(f"\n✓ Scan finished: {scan.metadata.status}")

    except Exception as e:
        print(f"✗ Scan failed: {e}")
        return False

    # Check if scan completed successfully
    if scan.metadata.status != ScanStatus.COMPLETED:
        print(f"✗ Scan did not complete successfully: {scan.metadata.status}")
        if scan.metadata.failure_reason:
            print(f"  Reason: {scan.metadata.failure_reason}")
        return False

    # Get results
    print("\n" + "-" * 60)
    print("Analyzing results...")

    try:
        results = client.scans.get_results(scan.metadata.scan_id)
    except Exception as e:
        print(f"✗ Failed to get results: {e}")
        return False

    # Extract metrics
    security_score = results.get('security_score', 0)
    total_prompts = results.get('total_prompts', 0)
    failed_prompts = results.get('failed_prompts', 0)
    passed_prompts = results.get('passed_prompts', 0)

    # Print results
    print(f"\n  Security Score: {security_score}/100")
    print(f"  Total Prompts: {total_prompts}")
    print(f"  Passed: {passed_prompts}")
    print(f"  Failed: {failed_prompts}")

    # Validate against thresholds
    print("\n" + "-" * 60)
    print("Validation:")

    passed = True

    # Check security score
    if security_score < min_security_score:
        print(f"  ✗ Security score below threshold: {security_score} < {min_security_score}")
        passed = False
    else:
        print(f"  ✓ Security score meets threshold: {security_score} >= {min_security_score}")

    # Check failed prompts
    if failed_prompts > max_failed_prompts:
        print(f"  ✗ Too many failed prompts: {failed_prompts} > {max_failed_prompts}")
        passed = False
    else:
        print(f"  ✓ Failed prompts within limit: {failed_prompts} <= {max_failed_prompts}")

    # Download reports for CI artifacts
    print("\n" + "-" * 60)
    print("Saving reports for CI artifacts...")

    reports_dir = os.getenv("CI_REPORTS_DIR", "./security-reports")
    os.makedirs(reports_dir, exist_ok=True)

    try:
        downloaded = client.reports.download_all(
            scan.metadata.scan_id,
            reports_dir
        )
        print(f"✓ Downloaded {len(downloaded)} reports to {reports_dir}/")
    except Exception as e:
        print(f"⚠ Warning: Failed to download reports: {e}")

    # Print final result
    print("\n" + "=" * 60)
    if passed:
        print("✓ SECURITY SCAN PASSED")
        print("=" * 60)
        return True
    else:
        print("✗ SECURITY SCAN FAILED")
        print("=" * 60)
        return False


def main():
    """Main entry point for CI/CD integration."""
    # Get configuration from environment
    generator = os.getenv("GARAK_GENERATOR", "openai")
    model_name = os.getenv("GARAK_MODEL_NAME", "gpt-3.5-turbo")
    min_score = float(os.getenv("GARAK_MIN_SCORE", "80"))
    max_failed = int(os.getenv("GARAK_MAX_FAILED", "5"))

    # Run scan
    passed = run_security_scan(
        generator=generator,
        model_name=model_name,
        min_security_score=min_score,
        max_failed_prompts=max_failed
    )

    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
