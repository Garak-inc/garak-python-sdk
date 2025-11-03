"""
Garak SDK Test Suite

Comprehensive test coverage for the Garak Security SDK.

Test Categories:
- unit: Unit tests (fast, no external dependencies)
- integration: Integration tests (require backend API or mocks)
- auth: Authentication tests
- client: Client tests
- scans: Scan resource tests
- metadata: Metadata resource tests
- reports: Report resource tests
- models: Model validation tests
- exceptions: Exception handling tests
- slow: Slow-running tests

Run all tests:
    pytest

Run only unit tests:
    pytest -m unit

Run only integration tests:
    pytest -m integration

Skip slow tests:
    pytest -m "not slow"

Run with coverage:
    pytest --cov=garak_sdk --cov-report=html
"""

__all__ = []
