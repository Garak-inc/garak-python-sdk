"""
Basic Scan Example

Simple example of running a security scan using the Garak SDK.
"""

import os
from dotenv import load_dotenv
from garak_sdk import GarakClient

# Load environment variables
load_dotenv()


def main():
    """Run a basic security scan."""
    print("=" * 60)
    print("Garak Security SDK - Basic Scan Example")
    print("=" * 60)

    # Initialize client
    client = GarakClient(
        base_url=os.getenv("GARAK_API_BASE_URL", "https://detect.garaksecurity.com"),
        api_key=os.getenv("GARAK_API_KEY")
    )

    print(f"\n✓ Connected to: {client.base_url}")
    print(f"  API Key: {client.auth.get_key_prefix()}")

    # Check API health
    print("\n" + "-" * 60)
    print("Checking API health...")
    health = client.health_check()
    print(f"✓ API Status: {health['status']}")

    # Check quota
    print("\n" + "-" * 60)
    print("Checking scan quota...")
    quota = client.scans.get_quota()
    print(f"✓ Free scans remaining: {quota.quota_status.remaining_free_scans}/{quota.quota_status.free_scans_limit}")
    print(f"  Total scans used: {quota.quota_status.total_scans_used}/{quota.quota_status.total_scans_limit}")

    # List available generators
    print("\n" + "-" * 60)
    print("Available generators:")
    generators = client.metadata.list_generators()
    for gen in generators[:5]:  # Show first 5
        print(f"  - {gen.name}: {gen.description}")

    # Create a scan
    print("\n" + "-" * 60)
    print("Creating security scan...")

    scan = client.scans.create(
        generator="openai",
        model_name="gpt-3.5-turbo",
        probe_categories=["dan", "toxicity"],  # Valid: dan, security, privacy, toxicity, hallucination, performance, robustness, ethics, stereotype
        name="Example Security Scan",
        description="Basic scan example from SDK",
        api_keys={
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
        }
    )

    print(f"✓ Scan created: {scan.metadata.scan_id}")
    print(f"  Status: {scan.metadata.status}")
    print(f"  Generator: {scan.metadata.generator}")
    print(f"  Model: {scan.metadata.model_name}")

    # Wait for completion
    print("\n" + "-" * 60)
    print("Waiting for scan to complete...")
    print("(This may take several minutes)")

    def on_progress(status):
        if status.progress:
            print(f"  Progress: {status.progress.percentage:.1f}% - {status.progress.message}")

    scan = client.scans.wait_for_completion(
        scan.metadata.scan_id,
        timeout=3600,  # 1 hour
        poll_interval=10,  # Check every 10 seconds
        on_progress=on_progress
    )

    print(f"\n✓ Scan completed: {scan.metadata.status}")

    # Get results
    if scan.metadata.status == "completed":
        print("\n" + "-" * 60)
        print("Scan Results:")

        results = client.scans.get_results(scan.metadata.scan_id)

        print(f"  Security Score: {results.get('security_score', 'N/A')}/100")
        print(f"  Total Prompts: {results.get('total_prompts', 0)}")
        print(f"  Passed: {results.get('passed_prompts', 0)}")
        print(f"  Failed: {results.get('failed_prompts', 0)}")

        # Download reports
        print("\n" + "-" * 60)
        print("Downloading reports...")

        reports_dir = "./security-reports"
        os.makedirs(reports_dir, exist_ok=True)

        downloaded = client.reports.download_all(
            scan.metadata.scan_id,
            reports_dir
        )

        print(f"✓ Downloaded {len(downloaded)} reports to {reports_dir}/")
        for path in downloaded:
            print(f"  - {os.path.basename(path)}")

    print("\n" + "=" * 60)
    print("Scan complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
