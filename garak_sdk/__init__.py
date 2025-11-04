"""
Garak Security SDK

Python client library for the Garak AI Security Platform.

This SDK provides programmatic access to the Garak Security API for running
security scans against AI models, discovering vulnerabilities, and integrating
security testing into your CI/CD pipelines.

Quick Start:
    from garak_sdk import GarakClient

    # Initialize client
    client = GarakClient(api_key="gsk_...")

    # Create a security scan
    scan = client.scans.create(
        generator="openai",
        model_name="gpt-4",
        probe_categories=["jailbreak", "harmful"]
    )

    # Wait for completion
    scan = client.scans.wait_for_completion(scan.metadata.scan_id)

    # Get results
    results = client.scans.get_results(scan.metadata.scan_id)

For detailed documentation, visit: https://docs.garaksecurity.com
"""

from .auth import GarakAuthManager
from .client import GarakClient
from .exceptions import (
    APIError,
    AuthenticationError,
    GarakSDKError,
    InvalidConfigurationError,
    NetworkError,
    QuotaExceededError,
    RateLimitError,
    ScanNotFoundError,
    ScanTimeoutError,
    ScanValidationError,
)
from .models import (
    GeneratorInfo,
    GeneratorType,
    ProbeCategory,
    ProbeInfo,
    QuotaResponse,
    ReportType,
    ScanListResponse,
    ScanMetadata,
    ScanResponse,
    ScanStatus,
    ScanStatusResponse,
)

__version__ = "1.0.4"
__author__ = "Garak Security"
__license__ = "MIT"

__all__ = [
    # Main client
    "GarakClient",
    "GarakAuthManager",
    # Models
    "ScanStatus",
    "ReportType",
    "GeneratorType",
    "ScanResponse",
    "ScanListResponse",
    "ScanStatusResponse",
    "ScanMetadata",
    "QuotaResponse",
    "GeneratorInfo",
    "ProbeCategory",
    "ProbeInfo",
    # Exceptions
    "GarakSDKError",
    "AuthenticationError",
    "QuotaExceededError",
    "ScanNotFoundError",
    "ScanValidationError",
    "ScanTimeoutError",
    "RateLimitError",
    "NetworkError",
    "InvalidConfigurationError",
    "APIError",
    # Version
    "__version__",
]
