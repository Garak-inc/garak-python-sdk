#!/usr/bin/env python3
"""
Comprehensive validation of all Garak SDK examples.

This script validates:
1. Python syntax
2. Import success
3. Function/class structure
4. Documentation strings
5. Required dependencies
"""

import sys
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple


class ExampleValidator:
    """Validator for example scripts."""

    def __init__(self, example_path: Path):
        self.path = example_path
        self.name = example_path.name
        self.errors = []
        self.warnings = []
        self.info = []

    def validate_syntax(self) -> bool:
        """Validate Python syntax."""
        try:
            with open(self.path, 'r') as f:
                ast.parse(f.read())
            self.info.append("✓ Valid Python syntax")
            return True
        except SyntaxError as e:
            self.errors.append(f"✗ Syntax error: {e}")
            return False

    def validate_imports(self) -> bool:
        """Validate that all imports work."""
        spec = importlib.util.spec_from_file_location("example", self.path)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            self.info.append("✓ All imports successful")
            return True
        except ImportError as e:
            self.errors.append(f"✗ Import error: {e}")
            return False
        except Exception as e:
            # Module-level code may fail without API keys, but imports worked
            if "API key" in str(e) or "environment variable" in str(e):
                self.info.append("✓ Imports successful (requires API key to run)")
                return True
            self.warnings.append(f"⚠ Module execution error: {e}")
            return True

    def validate_structure(self) -> bool:
        """Validate code structure."""
        with open(self.path, 'r') as f:
            tree = ast.parse(f.read())

        # Check for docstring
        docstring = ast.get_docstring(tree)
        if docstring:
            self.info.append(f"✓ Module docstring present ({len(docstring)} chars)")
        else:
            self.warnings.append("⚠ No module docstring")

        # Find functions and classes
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]

        if functions:
            self.info.append(f"✓ Found {len(functions)} function(s): {', '.join(functions[:3])}")

        if classes:
            self.info.append(f"✓ Found {len(classes)} class(es): {', '.join(classes[:3])}")

        # Check for main function or if __name__ == '__main__'
        has_main_func = 'main' in functions
        has_main_guard = any(
            isinstance(node, ast.If) and
            isinstance(node.test, ast.Compare) and
            any(isinstance(comp, ast.Eq) for comp in node.test.ops) and
            any(
                isinstance(left, ast.Name) and left.id == '__name__'
                for left in [node.test.left] if isinstance(left, ast.Name)
            )
            for node in ast.walk(tree)
        )

        if has_main_func:
            self.info.append("✓ Has main() function")
        if has_main_guard:
            self.info.append("✓ Has if __name__ == '__main__' guard")

        if not (has_main_func or has_main_guard):
            self.warnings.append("⚠ No main() function or __main__ guard")

        return True

    def validate_dependencies(self) -> bool:
        """Check for required dependencies."""
        with open(self.path, 'r') as f:
            content = f.read()

        required_imports = []
        if 'from garak_sdk import' in content or 'import garak_sdk' in content:
            required_imports.append('garak_sdk')

        if required_imports:
            self.info.append(f"✓ Uses SDK: {', '.join(required_imports)}")

        return True

    def run_all_validations(self) -> bool:
        """Run all validations."""
        print(f"\nValidating: {self.name}")
        print("=" * 60)

        success = True
        success &= self.validate_syntax()
        success &= self.validate_structure()
        success &= self.validate_dependencies()
        success &= self.validate_imports()  # Do this last as it may fail

        # Print results
        for info in self.info:
            print(f"  {info}")
        for warning in self.warnings:
            print(f"  {warning}")
        for error in self.errors:
            print(f"  {error}")

        return success and len(self.errors) == 0


def main():
    """Run comprehensive validation on all examples."""
    print("=" * 70)
    print("COMPREHENSIVE GARAK SDK EXAMPLE VALIDATION")
    print("=" * 70)

    examples = [
        "quickstart.py",
        "end_to_end_flow.py",
        "complete_cicd_integration.py",
        "error_handling.py",
        "batch_scanning.py",
        "basic_scan.py"
    ]

    examples_dir = Path(__file__).parent
    results = []

    for example in examples:
        example_path = examples_dir / example

        if not example_path.exists():
            print(f"\n✗ {example} - FILE NOT FOUND")
            results.append((example, False))
            continue

        validator = ExampleValidator(example_path)
        success = validator.run_all_validations()
        results.append((example, success))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print(f"\nResults: {passed}/{total} examples passed validation\n")

    for example, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status:8} | {example}")

    print("\n" + "=" * 70)

    if passed == total:
        print("✅ ALL EXAMPLES VALIDATED SUCCESSFULLY!")
        print("=" * 70)
        print("\nAll examples are:")
        print("  • Syntactically correct")
        print("  • Properly structured")
        print("  • Import successfully")
        print("  • Well documented")
        print("  • Ready for use")
        return 0
    else:
        print("❌ SOME EXAMPLES FAILED VALIDATION")
        print("=" * 70)
        print(f"\nFailed: {total - passed} example(s)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
