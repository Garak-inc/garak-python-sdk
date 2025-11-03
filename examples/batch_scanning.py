"""
Batch Scanning Example

Example of running multiple security scans in parallel.
Useful for testing multiple models or configurations.
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from dotenv import load_dotenv
from garak_sdk import GarakClient, ScanStatus

# Load environment variables
load_dotenv()


def run_single_scan(
    client: GarakClient,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run a single scan with the given configuration.

    Args:
        client: GarakClient instance
        config: Scan configuration

    Returns:
        Dictionary with scan results
    """
    generator = config['generator']
    model_name = config['model_name']
    probe_categories = config.get('probe_categories', ['dan', 'toxicity'])

    print(f"\n[{generator}/{model_name}] Creating scan...")

    try:
        # Create scan
        scan = client.scans.create(
            generator=generator,
            model_name=model_name,
            probe_categories=probe_categories,
            name=f"Batch Scan - {generator}/{model_name}",
            api_keys=config.get('api_keys', {})
        )

        scan_id = scan.metadata.scan_id
        print(f"[{generator}/{model_name}] Scan created: {scan_id}")

        # Wait for completion
        print(f"[{generator}/{model_name}] Waiting for completion...")
        scan = client.scans.wait_for_completion(
            scan_id,
            timeout=3600,
            poll_interval=15
        )

        # Check status
        if scan.metadata.status != ScanStatus.COMPLETED:
            return {
                'generator': generator,
                'model_name': model_name,
                'scan_id': scan_id,
                'status': 'failed',
                'error': scan.metadata.failure_reason or 'Unknown error'
            }

        # Get results
        results = client.scans.get_results(scan_id)

        print(f"[{generator}/{model_name}] ✓ Completed - Score: {results.get('security_score', 'N/A')}")

        return {
            'generator': generator,
            'model_name': model_name,
            'scan_id': scan_id,
            'status': 'completed',
            'security_score': results.get('security_score', 0),
            'total_prompts': results.get('total_prompts', 0),
            'failed_prompts': results.get('failed_prompts', 0),
            'passed_prompts': results.get('passed_prompts', 0)
        }

    except Exception as e:
        print(f"[{generator}/{model_name}] ✗ Error: {e}")
        return {
            'generator': generator,
            'model_name': model_name,
            'scan_id': None,
            'status': 'error',
            'error': str(e)
        }


def run_batch_scans(configs: List[Dict[str, Any]], max_parallel: int = 3) -> List[Dict[str, Any]]:
    """
    Run multiple scans in parallel.

    Args:
        configs: List of scan configurations
        max_parallel: Maximum number of parallel scans

    Returns:
        List of scan results
    """
    print("=" * 60)
    print("Batch Security Scanning - Garak SDK")
    print("=" * 60)
    print(f"\nTotal scans: {len(configs)}")
    print(f"Max parallel: {max_parallel}")

    # Initialize client (shared across threads)
    client = GarakClient(
        base_url=os.getenv("GARAK_API_BASE_URL", "https://detect.garaksecurity.com"),
        api_key=os.getenv("GARAK_API_KEY")
    )

    print(f"✓ Connected to: {client.base_url}")

    # Run scans in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        # Submit all scans
        future_to_config = {
            executor.submit(run_single_scan, client, config): config
            for config in configs
        }

        # Collect results as they complete
        for future in as_completed(future_to_config):
            result = future.result()
            results.append(result)

    return results


def print_summary(results: List[Dict[str, Any]]):
    """Print summary of batch scan results."""
    print("\n" + "=" * 60)
    print("Batch Scan Summary")
    print("=" * 60)

    # Count statuses
    completed = sum(1 for r in results if r['status'] == 'completed')
    failed = sum(1 for r in results if r['status'] in ['failed', 'error'])

    print(f"\nTotal Scans: {len(results)}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")

    # Print detailed results
    print("\n" + "-" * 60)
    print("Detailed Results:")
    print("-" * 60)

    for result in results:
        print(f"\n{result['generator']}/{result['model_name']}")
        print(f"  Status: {result['status']}")

        if result['status'] == 'completed':
            print(f"  Security Score: {result['security_score']}/100")
            print(f"  Total Prompts: {result['total_prompts']}")
            print(f"  Failed: {result['failed_prompts']}")
            print(f"  Passed: {result['passed_prompts']}")
        elif 'error' in result:
            print(f"  Error: {result['error']}")

    # Find best and worst performers
    completed_results = [r for r in results if r['status'] == 'completed']
    if completed_results:
        best = max(completed_results, key=lambda r: r['security_score'])
        worst = min(completed_results, key=lambda r: r['security_score'])

        print("\n" + "-" * 60)
        print("Performance Ranking:")
        print("-" * 60)
        print(f"\nBest: {best['generator']}/{best['model_name']}")
        print(f"  Security Score: {best['security_score']}/100")
        print(f"\nWorst: {worst['generator']}/{worst['model_name']}")
        print(f"  Security Score: {worst['security_score']}/100")

    print("\n" + "=" * 60)


def main():
    """Main entry point for batch scanning."""
    # Define scan configurations
    scan_configs = [
        {
            'generator': 'openai',
            'model_name': 'gpt-3.5-turbo',
            'probe_categories': ['dan', 'toxicity'],
            'api_keys': {'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')}
        },
        {
            'generator': 'openai',
            'model_name': 'gpt-4',
            'probe_categories': ['dan', 'toxicity'],
            'api_keys': {'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')}
        },
        {
            'generator': 'anthropic',
            'model_name': 'claude-3-haiku-20240307',
            'probe_categories': ['dan', 'toxicity'],
            'api_keys': {'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY')}
        }
    ]

    # Run batch scans
    results = run_batch_scans(scan_configs, max_parallel=2)

    # Print summary
    print_summary(results)


if __name__ == "__main__":
    main()
