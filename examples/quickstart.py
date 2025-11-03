#!/usr/bin/env python3
"""
Quick Start Example

The fastest way to get started with the Garak SDK.
Scan your LLM in just a few lines of code!

Prerequisites:
1. Install the SDK: pip install garak-sdk
2. Get your API key from https://detect.garaksecurity.com
3. Set environment variable: export GARAK_API_KEY=garak_your_key_here
"""

import os
from garak_sdk import GarakClient


def main():
    """Run the quickstart example."""
    # Initialize client (uses GARAK_API_KEY from environment)
    client = GarakClient()

    # Create a security scan
    print("Creating security scan...")
    scan = client.scans.create(
        generator="openai",
        model_name="gpt-3.5-turbo",
        probe_categories=["dan", "toxicity"],  # Valid categories: dan, security, privacy, toxicity, hallucination, performance, robustness, ethics, stereotype
        use_free_tier=True  # Use platform's free tier
    )

    print(f"✓ Scan created: {scan.metadata.scan_id}")

    # Wait for completion
    print("Waiting for scan to complete...")
    final_scan = client.scans.wait_for_completion(
        scan.metadata.scan_id,
        timeout=3600
    )

    print(f"✓ Scan completed: {final_scan.metadata.status.value}")

    # Get results
    results = client.scans.get_results(scan.metadata.scan_id)

    print(f"\n📊 Results:")
    print(f"   Security Score: {results['security_score']:.1f}/100")
    print(f"   Total Tests: {results['total_prompts']}")
    print(f"   Passed: {results['passed_prompts']}")
    print(f"   Failed: {results['failed_prompts']}")

    # Download reports
    print("\nDownloading reports...")
    downloaded = client.reports.download_all(scan.metadata.scan_id, "./reports")
    print(f"✓ Downloaded {len(downloaded)} reports to ./reports/")

    print("\n✅ Done! Check ./reports/ for detailed results.")


if __name__ == '__main__':
    main()
