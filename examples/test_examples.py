#!/usr/bin/env python3
"""
Test script to validate all examples can be imported and have valid structure.
"""

import sys
import importlib.util
from pathlib import Path

def test_import_example(example_path):
    """Test that an example can be imported without errors."""
    spec = importlib.util.spec_from_file_location("example", example_path)
    module = importlib.util.module_from_spec(spec)

    try:
        # This will execute module-level code but not main()
        spec.loader.exec_module(module)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    """Test all examples."""
    examples = [
        "quickstart.py",
        "end_to_end_flow.py",
        "complete_cicd_integration.py",
        "error_handling.py",
        "batch_scanning.py",
        "basic_scan.py"
    ]

    print("=" * 70)
    print("VALIDATING GARAK SDK EXAMPLES")
    print("=" * 70)

    results = []

    for example in examples:
        example_path = Path(__file__).parent / example

        if not example_path.exists():
            results.append((example, False, "File not found"))
            continue

        print(f"\nTesting: {example}")
        success, message = test_import_example(example_path)
        results.append((example, success, message))

        if success:
            print(f"  ✓ Import successful")
        else:
            print(f"  ✗ Import failed: {message}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for example, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status:8} | {example}")
        if not success:
            print(f"         | Error: {message[:50]}...")

    print(f"\nResult: {passed}/{total} examples passed")

    if passed == total:
        print("✓ All examples validated successfully!")
        return 0
    else:
        print("✗ Some examples failed validation")
        return 1

if __name__ == '__main__':
    sys.exit(main())
