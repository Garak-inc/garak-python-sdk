"""
Pytest configuration and fixtures for Garak SDK tests.

This module provides common fixtures and utilities used across all tests.
"""

import os
import pytest
import responses
from datetime import datetime, timezone
from typing import Dict, Any

# Set test environment variables
os.environ["GARAK_API_KEY"] = "garak_test_key_1234567890abcdefghijklmnopqrst"
os.environ["GARAK_API_BASE_URL"] = "https://test.garaksecurity.com"


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_api_key():
    """Provide a test API key."""
    return "garak_test_key_1234567890abcdefghijklmnopqrst"


@pytest.fixture
def mock_base_url():
    """Provide a test base URL."""
    return "https://test.garaksecurity.com"


@pytest.fixture
def mock_scan_id():
    """Provide a test scan ID."""
    return "test-scan-123456"


@pytest.fixture
def mock_scan_metadata():
    """Provide mock scan metadata."""
    return {
        "scan_id": "test-scan-123456",
        "name": "Test Security Scan",
        "description": "Test scan description",
        "status": "completed",
        "generator": "openai",
        "model_name": "gpt-4",
        "probe_categories": ["jailbreak", "harmful"],
        "probes": ["probe1", "probe2"],
        "created_at": "2024-01-01T00:00:00Z",
        "started_at": "2024-01-01T00:01:00Z",
        "completed_at": "2024-01-01T00:10:00Z",
        "progress": {
            "current": 100,
            "total": 100,
            "percentage": 100.0,
            "message": "Scan completed"
        },
        "user_email": "test@example.com",
        "use_free_tier": False,
        "needs_subscription": False
    }


@pytest.fixture
def mock_scan_results():
    """Provide mock scan results."""
    return {
        "scan_id": "test-scan-123456",
        "security_score": 85.5,
        "total_prompts": 100,
        "passed_prompts": 85,
        "failed_prompts": 15,
        "detector_summary": {
            "jailbreak_detector": {"passed": 90, "failed": 10},
            "harmful_detector": {"passed": 80, "failed": 20}
        },
        "probe_summary": {
            "probe1": {"passed": 45, "failed": 5},
            "probe2": {"passed": 40, "failed": 10}
        }
    }


@pytest.fixture
def mock_generators():
    """Provide mock generator list."""
    return [
        {
            "name": "openai",
            "display_name": "OpenAI",
            "description": "OpenAI GPT models",
            "requires_api_key": True,
            "api_key_env": "OPENAI_API_KEY",
            "supported_models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        },
        {
            "name": "anthropic",
            "display_name": "Anthropic",
            "description": "Anthropic Claude models",
            "requires_api_key": True,
            "api_key_env": "ANTHROPIC_API_KEY",
            "supported_models": ["claude-3-haiku-20240307", "claude-3-opus-20240229"]
        }
    ]


@pytest.fixture
def mock_probe_categories():
    """Provide mock probe categories."""
    return [
        {
            "name": "jailbreak",
            "display_name": "Jailbreak",
            "description": "Tests for jailbreak attempts",
            "probes": [
                {
                    "name": "probe1",
                    "display_name": "Probe 1",
                    "category": "jailbreak",
                    "description": "Test probe 1",
                    "recommended_detectors": ["detector1"]
                }
            ]
        },
        {
            "name": "harmful",
            "display_name": "Harmful Content",
            "description": "Tests for harmful content",
            "probes": [
                {
                    "name": "probe2",
                    "display_name": "Probe 2",
                    "category": "harmful",
                    "description": "Test probe 2",
                    "recommended_detectors": ["detector2"]
                }
            ]
        }
    ]


@pytest.fixture
def mock_health_response():
    """Provide mock health check response."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "services": {
            "redis": "healthy",
            "database": "healthy",
            "storage": "healthy",
            "job_system": "healthy"
        }
    }


@pytest.fixture
def mock_quota_response():
    """Provide mock quota response."""
    return {
        "quota_status": {
            "total_scans_used": 5,
            "total_scans_limit": 10,
            "remaining_total_scans": 5,
            "free_scans_used": 2,
            "free_scans_limit": 2,
            "remaining_free_scans": 0,
            "can_use_free_tier": False,
            "can_use_paid_tier": True,
            "user_id": "test-user-123"
        },
        "message": "Quota information retrieved successfully"
    }


# ============================================================================
# HTTP Mocking Fixtures
# ============================================================================

@pytest.fixture
def mocked_responses():
    """
    Provide a responses mock for HTTP requests.
    Automatically starts and stops for each test.
    """
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def mock_successful_scan_creation(mocked_responses, mock_scan_metadata, mock_scan_id):
    """Mock successful scan creation API call."""
    mocked_responses.add(
        responses.POST,
        "https://test.garaksecurity.com/api/v1/scans",
        json={
            "scan_id": mock_scan_id,
            "message": f"Scan created successfully with ID: {mock_scan_id}",
            "metadata": mock_scan_metadata
        },
        status=201
    )
    return mocked_responses


@pytest.fixture
def mock_scan_status_pending(mocked_responses, mock_scan_id):
    """Mock scan status API call - pending status."""
    mocked_responses.add(
        responses.GET,
        f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
        json={
            "scan_id": mock_scan_id,
            "status": "pending",
            "progress": {"current": 0, "total": 100, "percentage": 0.0},
            "created_at": "2024-01-01T00:00:00Z"
        },
        status=200
    )
    return mocked_responses


@pytest.fixture
def mock_scan_status_running(mocked_responses, mock_scan_id):
    """Mock scan status API call - running status."""
    mocked_responses.add(
        responses.GET,
        f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
        json={
            "scan_id": mock_scan_id,
            "status": "running",
            "progress": {"current": 50, "total": 100, "percentage": 50.0},
            "created_at": "2024-01-01T00:00:00Z",
            "started_at": "2024-01-01T00:01:00Z"
        },
        status=200
    )
    return mocked_responses


@pytest.fixture
def mock_scan_status_completed(mocked_responses, mock_scan_id):
    """Mock scan status API call - completed status."""
    mocked_responses.add(
        responses.GET,
        f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
        json={
            "scan_id": mock_scan_id,
            "status": "completed",
            "progress": {"current": 100, "total": 100, "percentage": 100.0},
            "created_at": "2024-01-01T00:00:00Z",
            "started_at": "2024-01-01T00:01:00Z",
            "completed_at": "2024-01-01T00:10:00Z"
        },
        status=200
    )
    return mocked_responses


@pytest.fixture
def mock_health_check(mocked_responses, mock_health_response):
    """Mock health check API call."""
    mocked_responses.add(
        responses.GET,
        "https://test.garaksecurity.com/api/v1/health",
        json=mock_health_response,
        status=200
    )
    return mocked_responses


# ============================================================================
# Client Fixtures
# ============================================================================

@pytest.fixture
def mock_client(mock_api_key, mock_base_url):
    """
    Provide a GarakClient instance configured for testing.
    Does NOT make actual HTTP requests - use with mocked_responses.
    """
    from garak_sdk import GarakClient

    client = GarakClient(
        base_url=mock_base_url,
        api_key=mock_api_key,
        timeout=5
    )
    return client


@pytest.fixture
def auth_manager(mock_api_key):
    """Provide an authentication manager for testing."""
    from garak_sdk.auth import GarakAuthManager
    return GarakAuthManager(api_key=mock_api_key)


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables for testing."""
    # Remove any existing Garak env vars
    env_vars = ["GARAK_API_KEY", "GARAK_SDK_API_KEY", "GARAK_API_BASE_URL"]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


@pytest.fixture
def set_env_vars(monkeypatch, mock_api_key, mock_base_url):
    """Set test environment variables."""
    monkeypatch.setenv("GARAK_API_KEY", mock_api_key)
    monkeypatch.setenv("GARAK_API_BASE_URL", mock_base_url)
    return monkeypatch


# ============================================================================
# Error Response Fixtures
# ============================================================================

@pytest.fixture
def mock_auth_error(mocked_responses):
    """Mock authentication error response."""
    mocked_responses.add(
        responses.POST,
        "https://test.garaksecurity.com/api/v1/scans",
        json={"error": "unauthorized", "message": "Invalid API key"},
        status=401
    )
    return mocked_responses


@pytest.fixture
def mock_rate_limit_error(mocked_responses):
    """Mock rate limit error response."""
    mocked_responses.add(
        responses.POST,
        "https://test.garaksecurity.com/api/v1/scans",
        json={"error": "rate_limit_exceeded", "message": "Too many requests"},
        status=429,
        headers={"Retry-After": "60"}
    )
    return mocked_responses


@pytest.fixture
def mock_quota_exceeded_error(mocked_responses):
    """Mock quota exceeded error response."""
    mocked_responses.add(
        responses.POST,
        "https://test.garaksecurity.com/api/v1/scans",
        json={
            "scan_id": "test-scan-123",
            "metadata": {"needs_subscription": True},
            "needs_subscription": True
        },
        status=201
    )
    return mocked_responses


@pytest.fixture
def mock_not_found_error(mocked_responses, mock_scan_id):
    """Mock 404 not found error."""
    mocked_responses.add(
        responses.GET,
        f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
        json={"error": "scan_not_found", "message": f"Scan {mock_scan_id} not found"},
        status=404
    )
    return mocked_responses


# ============================================================================
# Utility Functions
# ============================================================================

def assert_valid_scan_metadata(metadata: Dict[str, Any]):
    """Assert that scan metadata has all required fields."""
    required_fields = [
        "scan_id", "status", "generator", "model_name",
        "probe_categories", "probes", "created_at"
    ]
    for field in required_fields:
        assert field in metadata, f"Missing required field: {field}"


def assert_valid_api_response(response: Dict[str, Any]):
    """Assert that API response is valid."""
    assert isinstance(response, dict), "Response must be a dictionary"
    assert "error" not in response or response["error"] is None, "Response contains error"
