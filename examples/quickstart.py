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
        generator="rest",
        model_name="https://api.example.com/v1/chat/completions",
        probe_categories=["dan", "toxicity"],
        name="rest-example-scan",
        description="Security scan of REST API endpoint",
        rest_config={
            "uri": "https://api.example.com/v1/chat/completions",
            "method": "post",
            "req_template_json_object": {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "user",
                        "content": "$INPUT"  # Put $INPUT where your API expects the prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 256
            },
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer fake-api-key-12345"  # Replace with your actual auth header
            },
            "response_json": True,  # Set to True if your API returns JSON
            "response_json_field": "$.choices[0].message.content",  # JSONPath to extract the response text
            "verify_ssl": True  # Set to False to disable SSL verification (not recommended for production)
        }
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
