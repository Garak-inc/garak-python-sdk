#!/usr/bin/env python3
"""
End-to-End User Flow Example

This example demonstrates the complete workflow for scanning an LLM model
with the Garak SDK, from initial setup through result analysis.

User Flow:
1. Initialize the SDK client
2. Discover available options (generators, probes)
3. Create a security scan
4. Monitor scan progress
5. Retrieve and analyze results
6. Download reports

This example is interactive and educational - perfect for first-time users.
"""

import os
import time
from garak_sdk import GarakClient
from garak_sdk.models import ScanStatus


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Complete end-to-end user flow."""

    print_section("STEP 1: Initialize Garak SDK Client")

    # Get API key from environment
    api_key = os.getenv('GARAK_API_KEY')

    if not api_key:
        print("❌ Error: GARAK_API_KEY environment variable not set")
        print("\nTo get started:")
        print("1. Sign up at https://detect.garaksecurity.com")
        print("2. Generate an API key in the dashboard")
        print("3. Set the environment variable:")
        print("   export GARAK_API_KEY=gsk_your_api_key_here")
        return

    # Initialize client
    client = GarakClient(api_key=api_key)
    print(f"✅ Connected to Garak API")
    print(f"   Base URL: {client.base_url}")

    # Check API health
    health = client.health_check()
    print(f"   API Status: {health.get('status', 'unknown')}")

    # -------------------------------------------------------------------
    print_section("STEP 2: Discover Available Options")

    # List available generators
    print("Available Generators:")
    generators = client.metadata.list_generators()
    for gen in generators[:5]:  # Show first 5
        print(f"  • {gen.name} - {gen.display_name}")
    print(f"  ... and {len(generators) - 5} more\n" if len(generators) > 5 else "")

    # List probe categories
    print("Available Probe Categories:")
    categories = client.metadata.list_probe_categories()
    for category in categories[:5]:  # Show first 5
        print(f"  • {category}")
    print(f"  ... and {len(categories) - 5} more" if len(categories) > 5 else "")

    # Check quota
    print("\nChecking Quota...")
    quota = client.scans.get_quota()
    print(f"  Total Scans: {quota.quota_status.total_scans_used}/{quota.quota_status.total_scans_limit}")
    print(f"  Remaining: {quota.quota_status.remaining_total_scans}")

    if quota.quota_status.remaining_total_scans <= 0:
        print("\n❌ No remaining quota. Please upgrade your subscription.")
        return

    # -------------------------------------------------------------------
    print_section("STEP 3: Create Security Scan")

    # Configuration
    generator = "openai"
    model_name = "gpt-3.5-turbo"
    probe_categories = ["dan", "toxicity"]  # Valid: dan, security, privacy, toxicity, hallucination, performance, robustness, ethics, stereotype

    print(f"Scan Configuration:")
    print(f"  Generator: {generator}")
    print(f"  Model: {model_name}")
    print(f"  Probe Categories: {', '.join(probe_categories)}")

    # Get model-specific API key
    generator_api_keys = {}
    if generator == "openai":
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            generator_api_keys['OPENAI_API_KEY'] = openai_key
            print(f"  Using OpenAI API key: {openai_key[:8]}...")
        else:
            print("  Using free tier (no OpenAI API key provided)")

    # Create scan
    print("\nCreating scan...")
    scan = client.scans.create(
        generator=generator,
        model_name=model_name,
        probe_categories=probe_categories,
        name="End-to-End Example Scan",
        description="Example scan from SDK tutorial",
        api_keys=generator_api_keys,
        use_free_tier=not bool(generator_api_keys)
    )

    scan_id = scan.metadata.scan_id
    print(f"✅ Scan created successfully!")
    print(f"   Scan ID: {scan_id}")
    print(f"   Status: {scan.metadata.status.value}")

    # -------------------------------------------------------------------
    print_section("STEP 4: Monitor Scan Progress")

    print("Waiting for scan to complete...")
    print("(This may take several minutes)\n")

    # Progress tracking variables
    last_percentage = -1
    start_time = time.time()

    def progress_callback(status):
        """Display progress updates."""
        nonlocal last_percentage

        if status.progress and status.progress.percentage != last_percentage:
            percentage = status.progress.percentage
            current = status.progress.current
            total = status.progress.total

            # Draw progress bar
            bar_length = 40
            filled = int(bar_length * percentage / 100)
            bar = "█" * filled + "░" * (bar_length - filled)

            elapsed = time.time() - start_time
            print(f"\r  [{bar}] {percentage:.1f}% ({current}/{total}) - {elapsed:.1f}s", end="", flush=True)

            last_percentage = percentage

    # Wait for completion with progress monitoring
    try:
        final_scan = client.scans.wait_for_completion(
            scan_id,
            timeout=3600,  # 1 hour timeout
            poll_interval=10,  # Check every 10 seconds
            on_progress=progress_callback
        )

        print()  # New line after progress bar
        elapsed = time.time() - start_time
        print(f"\n✅ Scan completed in {elapsed:.1f} seconds")
        print(f"   Final Status: {final_scan.metadata.status.value}")

    except Exception as e:
        print(f"\n❌ Error during scan: {e}")
        return

    # -------------------------------------------------------------------
    print_section("STEP 5: Retrieve and Analyze Results")

    # Get detailed results
    print("Fetching results...")
    results = client.scans.get_results(scan_id)

    # Display results
    security_score = results.get('security_score', 0)
    total_prompts = results.get('total_prompts', 0)
    passed_prompts = results.get('passed_prompts', 0)
    failed_prompts = results.get('failed_prompts', 0)

    print(f"\n📊 Security Analysis Results:")
    print(f"   Security Score: {security_score:.1f}/100")
    print(f"   Total Prompts Tested: {total_prompts}")
    print(f"   ✅ Passed: {passed_prompts} ({passed_prompts/total_prompts*100:.1f}%)")
    print(f"   ❌ Failed: {failed_prompts} ({failed_prompts/total_prompts*100:.1f}%)")

    # Interpret results
    if security_score >= 90:
        print(f"\n🎉 Excellent! Your model has a high security score.")
    elif security_score >= 75:
        print(f"\n✅ Good! Your model has a decent security score.")
    elif security_score >= 50:
        print(f"\n⚠️  Warning! Your model has moderate security concerns.")
    else:
        print(f"\n❌ Critical! Your model has serious security vulnerabilities.")

    # -------------------------------------------------------------------
    print_section("STEP 6: Download Reports")

    print("Listing available reports...")
    report_list = client.reports.list(scan_id)

    print(f"Found {len(report_list)} reports:")
    for report in report_list:
        print(f"  • {report.type.value.upper()}")
        if report.file_size:
            size_kb = report.file_size / 1024
            print(f"    Size: {size_kb:.1f} KB")

    # Download all reports
    print("\nDownloading reports to ./reports/...")
    downloaded = client.reports.download_all(scan_id, "./reports", overwrite=True)

    print(f"✅ Downloaded {len(downloaded)} reports:")
    for path in downloaded:
        print(f"   {path}")

    # -------------------------------------------------------------------
    print_section("🎊 Complete!")

    print("Summary:")
    print(f"  • Scan ID: {scan_id}")
    print(f"  • Security Score: {security_score:.1f}/100")
    print(f"  • Total Tests: {total_prompts}")
    print(f"  • Reports: {len(downloaded)} files downloaded")
    print()
    print("Next Steps:")
    print("  1. Review the downloaded reports for detailed findings")
    print("  2. Address any security vulnerabilities identified")
    print("  3. Re-scan after implementing fixes")
    print("  4. Integrate this into your CI/CD pipeline")
    print()
    print("Learn more: https://docs.garaksecurity.com")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        raise
