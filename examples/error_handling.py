#!/usr/bin/env python3
"""
Error Handling Example

Demonstrates proper error handling patterns for production use.
Shows how to handle common errors gracefully and implement retry logic.
"""

import os
import time
from garak_sdk import GarakClient
from garak_sdk.exceptions import (
    GarakSDKError,
    AuthenticationError,
    QuotaExceededError,
    ScanNotFoundError,
    ScanTimeoutError,
    RateLimitError,
    NetworkError,
    InvalidConfigurationError
)


def initialize_client_with_error_handling():
    """Example 1: Safe client initialization."""
    print("=" * 60)
    print("Example 1: Client Initialization with Error Handling")
    print("=" * 60)

    try:
        # Attempt to initialize client
        api_key = os.getenv('GARAK_API_KEY')

        if not api_key:
            raise InvalidConfigurationError(
                "GARAK_API_KEY environment variable not set. "
                "Get your API key from https://detect.garaksecurity.com"
            )

        client = GarakClient(api_key=api_key)
        print("✓ Client initialized successfully")
        return client

    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("  → Check your API key is valid")
        print("  → Verify your account is active")
        return None

    except InvalidConfigurationError as e:
        print(f"✗ Configuration error: {e}")
        print("  → Set GARAK_API_KEY environment variable")
        return None

    except NetworkError as e:
        print(f"✗ Network error: {e}")
        print("  → Check your internet connection")
        print("  → Verify API endpoint is accessible")
        return None

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def handle_quota_errors(client):
    """Example 2: Handling quota exceeded errors."""
    print("\n" + "=" * 60)
    print("Example 2: Quota Management")
    print("=" * 60)

    try:
        # Check quota before creating scan
        quota = client.scans.get_quota()

        print(f"Quota Status:")
        print(f"  Total: {quota.quota_status.total_scans_used}/{quota.quota_status.total_scans_limit}")
        print(f"  Remaining: {quota.quota_status.remaining_total_scans}")

        if quota.quota_status.remaining_total_scans <= 0:
            print("\n⚠️  Warning: No remaining quota!")
            print("  → Upgrade your subscription to continue")
            return False

        # Create scan
        scan = client.scans.create(
            generator="openai",
            model_name="gpt-3.5-turbo",
            probe_categories=["dan"],  # Valid: dan, security, privacy, toxicity, hallucination, performance, robustness, ethics, stereotype
            use_free_tier=True
        )

        print(f"✓ Scan created: {scan.metadata.scan_id}")
        return scan.metadata.scan_id

    except QuotaExceededError as e:
        print(f"✗ Quota exceeded: {e}")
        print("  → Upgrade your plan at https://detect.garaksecurity.com/settings")
        print("  → Contact support for assistance")
        return None

    except Exception as e:
        print(f"✗ Error creating scan: {e}")
        return None


def handle_scan_errors(client, scan_id):
    """Example 3: Handling scan-related errors."""
    print("\n" + "=" * 60)
    print("Example 3: Scan Error Handling")
    print("=" * 60)

    try:
        # Try to get scan that doesn't exist
        print("Attempting to get non-existent scan...")
        scan = client.scans.get("non-existent-scan-id")

    except ScanNotFoundError as e:
        print(f"✓ Correctly caught ScanNotFoundError: {e}")
        print("  → Verify scan ID is correct")
        print("  → Check scan wasn't deleted")

    try:
        # Try to wait with very short timeout
        print("\nAttempting scan with short timeout...")
        final_scan = client.scans.wait_for_completion(
            scan_id,
            timeout=1,  # Very short timeout
            poll_interval=0.5
        )

    except ScanTimeoutError as e:
        print(f"✓ Correctly caught ScanTimeoutError: {e}")
        print("  → Increase timeout parameter")
        print("  → Check scan status manually")


def handle_rate_limiting(client):
    """Example 4: Handling rate limits with retry."""
    print("\n" + "=" * 60)
    print("Example 4: Rate Limiting with Retry")
    print("=" * 60)

    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")

            # Make API request
            generators = client.metadata.list_generators()
            print(f"✓ Success! Found {len(generators)} generators")
            break

        except RateLimitError as e:
            print(f"✗ Rate limited: {e}")

            if e.retry_after:
                wait_time = e.retry_after
                print(f"  → Waiting {wait_time} seconds (from Retry-After header)...")
            else:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"  → Waiting {wait_time} seconds (exponential backoff)...")

            if attempt < max_retries - 1:
                time.sleep(wait_time)
            else:
                print("  → Max retries exceeded")
                break

        except NetworkError as e:
            print(f"✗ Network error: {e}")
            if attempt < max_retries - 1:
                print(f"  → Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("  → Max retries exceeded")
                break


def handle_context_manager_errors():
    """Example 5: Using context manager for automatic cleanup."""
    print("\n" + "=" * 60)
    print("Example 5: Context Manager for Automatic Cleanup")
    print("=" * 60)

    try:
        with GarakClient() as client:
            print("✓ Client created with context manager")

            # Perform operations
            health = client.health_check()
            print(f"✓ API Status: {health.get('status')}")

            # Client will be automatically closed on exit

        print("✓ Client automatically closed")

    except Exception as e:
        print(f"✗ Error: {e}")


def comprehensive_error_handling_example():
    """Example 6: Comprehensive error handling for production."""
    print("\n" + "=" * 60)
    print("Example 6: Production-Ready Error Handling")
    print("=" * 60)

    client = None
    scan_id = None

    try:
        # Initialize
        client = GarakClient()
        print("✓ Client initialized")

        # Create scan with all error handling
        scan = client.scans.create(
            generator="openai",
            model_name="gpt-3.5-turbo",
            probe_categories=["dan"],  # Valid: dan, security, privacy, toxicity, hallucination, performance, robustness, ethics, stereotype
            use_free_tier=True
        )
        scan_id = scan.metadata.scan_id
        print(f"✓ Scan created: {scan_id}")

        # Wait with timeout
        final_scan = client.scans.wait_for_completion(
            scan_id,
            timeout=3600,
            poll_interval=10
        )
        print(f"✓ Scan completed: {final_scan.metadata.status.value}")

        # Get results
        results = client.scans.get_results(scan_id)
        print(f"✓ Results retrieved: {results['security_score']:.1f}/100")

        return 0  # Success

    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        return 1

    except QuotaExceededError as e:
        print(f"✗ Quota exceeded: {e}")
        print("  → Upgrade your subscription")
        return 2

    except ScanTimeoutError as e:
        print(f"✗ Scan timeout: {e}")
        print(f"  → Check scan status at: https://detect.garaksecurity.com/scans/{scan_id}")
        return 3

    except NetworkError as e:
        print(f"✗ Network error: {e}")
        print("  → Check your connection and retry")
        return 4

    except GarakSDKError as e:
        print(f"✗ SDK error: {e}")
        return 5

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 99

    finally:
        # Cleanup
        if client:
            client.close()
            print("✓ Client closed")


def main():
    """Run all error handling examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  GARAK SDK - ERROR HANDLING EXAMPLES".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    # Example 1: Client initialization
    client = initialize_client_with_error_handling()

    if not client:
        print("\n⚠️  Cannot continue without valid client")
        return

    # Example 2: Quota management
    scan_id = handle_quota_errors(client)

    if scan_id:
        # Example 3: Scan errors
        handle_scan_errors(client, scan_id)

    # Example 4: Rate limiting
    handle_rate_limiting(client)

    # Example 5: Context manager
    handle_context_manager_errors()

    # Example 6: Production-ready handling
    # comprehensive_error_handling_example()

    print("\n" + "=" * 60)
    print("✅ All error handling examples completed!")
    print("=" * 60)
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        raise
