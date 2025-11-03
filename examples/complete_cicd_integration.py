#!/usr/bin/env python3
"""
Complete CI/CD Integration Example

This example demonstrates a full CI/CD pipeline integration for LLM security scanning.
It shows best practices for production use including:
- Environment-based configuration
- Pre-scan validation
- Progress monitoring with logging
- Result validation with security thresholds
- Report generation and artifact storage
- Exit codes for CI/CD pipeline control

Use Case: Run this script in your GitHub Actions, GitLab CI, or Jenkins pipeline
to validate your LLM before deployment.
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any

from garak_sdk import GarakClient
from garak_sdk.models import ScanStatus
from garak_sdk.exceptions import (
    GarakSDKError,
    QuotaExceededError,
    ScanTimeoutError,
    AuthenticationError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CICDSecurityScanner:
    """CI/CD Security Scanner for LLM models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        security_threshold: float = 80.0,
        timeout: int = 3600
    ):
        """
        Initialize CI/CD Scanner.

        Args:
            api_key: Garak API key (defaults to GARAK_API_KEY env var)
            base_url: API base URL (defaults to production)
            security_threshold: Minimum acceptable security score (0-100)
            timeout: Maximum time to wait for scan completion (seconds)
        """
        self.security_threshold = security_threshold
        self.timeout = timeout

        # Initialize client
        try:
            self.client = GarakClient(
                api_key=api_key,
                base_url=base_url,
                timeout=30
            )
            logger.info(f"✓ Connected to Garak API at {self.client.base_url}")
        except AuthenticationError as e:
            logger.error(f"✗ Authentication failed: {e}")
            sys.exit(1)

    def check_quota(self) -> bool:
        """
        Check if quota is available before starting scan.

        Returns:
            True if quota available, False otherwise
        """
        try:
            quota = self.client.scans.get_quota()

            logger.info("\n=== Quota Status ===")
            logger.info(f"Total scans: {quota.quota_status.total_scans_used}/{quota.quota_status.total_scans_limit}")
            logger.info(f"Remaining: {quota.quota_status.remaining_total_scans}")

            if quota.quota_status.remaining_total_scans <= 0:
                logger.error("✗ No remaining scan quota!")
                return False

            logger.info("✓ Quota available")
            return True

        except Exception as e:
            logger.warning(f"Could not check quota: {e}")
            return True  # Continue anyway

    def discover_available_options(self) -> Dict[str, Any]:
        """
        Discover available generators, models, and probes.

        Returns:
            Dictionary with available options
        """
        try:
            logger.info("\n=== Discovering Available Options ===")

            # Get generators
            generators = self.client.metadata.list_generators()
            logger.info(f"✓ Found {len(generators)} generators")

            # Get probe categories
            categories = self.client.metadata.list_probe_categories()
            logger.info(f"✓ Found {len(categories)} probe categories")

            return {
                'generators': [g.name for g in generators],
                'probe_categories': categories
            }

        except Exception as e:
            logger.warning(f"Could not discover options: {e}")
            return {}

    def create_scan(
        self,
        generator: str,
        model_name: str,
        probe_categories: list,
        scan_name: Optional[str] = None
    ) -> str:
        """
        Create a new security scan.

        Args:
            generator: Generator type (e.g., 'openai', 'anthropic')
            model_name: Model name to scan
            probe_categories: List of probe categories to run
            scan_name: Optional scan name

        Returns:
            Scan ID

        Raises:
            QuotaExceededError: If quota is exceeded
        """
        try:
            logger.info("\n=== Creating Security Scan ===")
            logger.info(f"Generator: {generator}")
            logger.info(f"Model: {model_name}")
            logger.info(f"Probe Categories: {', '.join(probe_categories)}")

            # Get API keys from environment
            api_keys = {}
            if generator == 'openai':
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    api_keys['OPENAI_API_KEY'] = api_key
                    logger.info("✓ Using OpenAI API key from environment")
            elif generator == 'anthropic':
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    api_keys['ANTHROPIC_API_KEY'] = api_key
                    logger.info("✓ Using Anthropic API key from environment")

            # Create scan
            scan = self.client.scans.create(
                generator=generator,
                model_name=model_name,
                probe_categories=probe_categories,
                name=scan_name or f"CI/CD Scan - {model_name}",
                description=f"Automated security scan for {model_name} in CI/CD pipeline",
                api_keys=api_keys,
                use_free_tier=not bool(api_keys)  # Use free tier if no API keys provided
            )

            scan_id = scan.metadata.scan_id
            logger.info(f"✓ Scan created successfully: {scan_id}")
            return scan_id

        except QuotaExceededError:
            logger.error("✗ Quota exceeded. Please upgrade your subscription.")
            raise
        except Exception as e:
            logger.error(f"✗ Failed to create scan: {e}")
            raise

    def monitor_progress(self, scan_id: str) -> Dict[str, Any]:
        """
        Monitor scan progress with real-time updates.

        Args:
            scan_id: Scan ID to monitor

        Returns:
            Final scan results
        """
        logger.info("\n=== Monitoring Scan Progress ===")
        logger.info(f"Scan ID: {scan_id}")
        logger.info(f"Timeout: {self.timeout} seconds")
        logger.info("Waiting for completion...")

        start_time = time.time()
        last_progress = -1

        def on_progress(status):
            """Progress callback for real-time updates."""
            nonlocal last_progress

            if status.progress and status.progress.percentage != last_progress:
                elapsed = time.time() - start_time
                logger.info(
                    f"⏳ Progress: {status.progress.percentage:.1f}% "
                    f"({status.progress.current}/{status.progress.total}) "
                    f"- Elapsed: {elapsed:.1f}s"
                )
                last_progress = status.progress.percentage

        try:
            # Wait for completion with progress monitoring
            scan = self.client.scans.wait_for_completion(
                scan_id,
                timeout=self.timeout,
                poll_interval=10,
                on_progress=on_progress
            )

            elapsed = time.time() - start_time
            logger.info(f"✓ Scan completed in {elapsed:.1f} seconds")
            logger.info(f"Status: {scan.metadata.status.value}")

            # Get detailed results
            results = self.client.scans.get_results(scan_id)

            return results

        except ScanTimeoutError:
            logger.error(f"✗ Scan timed out after {self.timeout} seconds")
            raise
        except Exception as e:
            logger.error(f"✗ Error during scan: {e}")
            raise

    def validate_results(self, results: Dict[str, Any]) -> bool:
        """
        Validate scan results against security thresholds.

        Args:
            results: Scan results dictionary

        Returns:
            True if results meet threshold, False otherwise
        """
        logger.info("\n=== Security Results ===")

        security_score = results.get('security_score', 0)
        total_prompts = results.get('total_prompts', 0)
        passed_prompts = results.get('passed_prompts', 0)
        failed_prompts = results.get('failed_prompts', 0)

        logger.info(f"Security Score: {security_score:.1f}/100")
        logger.info(f"Total Prompts: {total_prompts}")
        logger.info(f"Passed: {passed_prompts} ({passed_prompts/total_prompts*100:.1f}%)")
        logger.info(f"Failed: {failed_prompts} ({failed_prompts/total_prompts*100:.1f}%)")
        logger.info(f"Threshold: {self.security_threshold}/100")

        # Check threshold
        if security_score >= self.security_threshold:
            logger.info(f"✓ PASSED: Security score meets threshold!")
            return True
        else:
            logger.error(f"✗ FAILED: Security score below threshold!")
            logger.error(f"   Score: {security_score:.1f} < Threshold: {self.security_threshold}")
            return False

    def download_reports(self, scan_id: str, output_dir: str = "./reports") -> list:
        """
        Download all scan reports for archival.

        Args:
            scan_id: Scan ID
            output_dir: Output directory for reports

        Returns:
            List of downloaded report paths
        """
        logger.info("\n=== Downloading Reports ===")

        try:
            # Create output directory
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Download all reports
            downloaded = self.client.reports.download_all(
                scan_id,
                output_dir,
                overwrite=True
            )

            logger.info(f"✓ Downloaded {len(downloaded)} reports to {output_dir}")
            for path in downloaded:
                logger.info(f"  - {path}")

            return downloaded

        except Exception as e:
            logger.warning(f"Could not download reports: {e}")
            return []

    def run_pipeline(
        self,
        generator: str,
        model_name: str,
        probe_categories: list,
        scan_name: Optional[str] = None,
        download_reports: bool = True,
        output_dir: str = "./reports"
    ) -> int:
        """
        Run complete CI/CD security pipeline.

        Args:
            generator: Generator type
            model_name: Model name
            probe_categories: Probe categories to run
            scan_name: Optional scan name
            download_reports: Whether to download reports
            output_dir: Output directory for reports

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        try:
            logger.info("=" * 70)
            logger.info("CI/CD SECURITY SCAN PIPELINE")
            logger.info("=" * 70)

            # Step 1: Check API health
            logger.info("\n=== Health Check ===")
            health = self.client.health_check()
            logger.info(f"✓ API Status: {health.get('status', 'unknown')}")

            # Step 2: Check quota
            if not self.check_quota():
                return 1

            # Step 3: Discover options (optional)
            self.discover_available_options()

            # Step 4: Create scan
            scan_id = self.create_scan(
                generator=generator,
                model_name=model_name,
                probe_categories=probe_categories,
                scan_name=scan_name
            )

            # Step 5: Monitor progress
            results = self.monitor_progress(scan_id)

            # Step 6: Validate results
            passed = self.validate_results(results)

            # Step 7: Download reports
            if download_reports:
                self.download_reports(scan_id, output_dir)

            # Final summary
            logger.info("\n" + "=" * 70)
            if passed:
                logger.info("✓ PIPELINE PASSED: Model meets security requirements")
                logger.info("=" * 70)
                return 0
            else:
                logger.error("✗ PIPELINE FAILED: Model does not meet security requirements")
                logger.error("=" * 70)
                return 1

        except QuotaExceededError:
            logger.error("\n✗ PIPELINE FAILED: Quota exceeded")
            return 1
        except ScanTimeoutError:
            logger.error("\n✗ PIPELINE FAILED: Scan timeout")
            return 1
        except GarakSDKError as e:
            logger.error(f"\n✗ PIPELINE FAILED: {e}")
            return 1
        except Exception as e:
            logger.error(f"\n✗ PIPELINE FAILED: Unexpected error: {e}")
            return 1


def main():
    """Main entry point for CI/CD integration."""

    # Configuration from environment variables
    GARAK_API_KEY = os.getenv('GARAK_API_KEY')
    GARAK_BASE_URL = os.getenv('GARAK_BASE_URL')  # Optional

    # Model configuration
    GENERATOR = os.getenv('MODEL_GENERATOR', 'openai')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
    PROBE_CATEGORIES = os.getenv('PROBE_CATEGORIES', 'dan,toxicity').split(',')  # Valid: dan,security,privacy,toxicity,hallucination,performance,robustness,ethics,stereotype

    # Security configuration
    SECURITY_THRESHOLD = float(os.getenv('SECURITY_THRESHOLD', '80.0'))
    SCAN_TIMEOUT = int(os.getenv('SCAN_TIMEOUT', '3600'))

    # Report configuration
    DOWNLOAD_REPORTS = os.getenv('DOWNLOAD_REPORTS', 'true').lower() == 'true'
    REPORT_DIR = os.getenv('REPORT_DIR', './reports')

    # Validate required configuration
    if not GARAK_API_KEY:
        logger.error("ERROR: GARAK_API_KEY environment variable is required")
        logger.error("Set it with: export GARAK_API_KEY=gsk_your_api_key_here")
        sys.exit(1)

    # Initialize scanner
    scanner = CICDSecurityScanner(
        api_key=GARAK_API_KEY,
        base_url=GARAK_BASE_URL,
        security_threshold=SECURITY_THRESHOLD,
        timeout=SCAN_TIMEOUT
    )

    # Run pipeline
    exit_code = scanner.run_pipeline(
        generator=GENERATOR,
        model_name=MODEL_NAME,
        probe_categories=PROBE_CATEGORIES,
        scan_name=os.getenv('SCAN_NAME'),
        download_reports=DOWNLOAD_REPORTS,
        output_dir=REPORT_DIR
    )

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
