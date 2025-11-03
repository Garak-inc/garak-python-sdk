"""
Tests for main SDK client (garak_sdk.client).

Tests cover:
- Client initialization
- HTTP request handling
- Error handling and retries
- Context manager support
- Health checks
"""

import pytest
import responses
from garak_sdk import GarakClient
from garak_sdk.exceptions import (
    AuthenticationError,
    RateLimitError,
    APIError,
    NetworkError,
    InvalidConfigurationError
)


@pytest.mark.unit
@pytest.mark.client
class TestClientInitialization:
    """Test client initialization and configuration."""

    def test_init_with_api_key(self, mock_api_key, mock_base_url):
        """Test client initialization with explicit parameters."""
        client = GarakClient(
            base_url=mock_base_url,
            api_key=mock_api_key
        )

        assert client.base_url == mock_base_url
        assert client.auth.api_key == mock_api_key
        assert client.timeout == 30  # Default timeout

    def test_init_with_custom_timeout(self, mock_api_key, mock_base_url):
        """Test client initialization with custom timeout."""
        client = GarakClient(
            base_url=mock_base_url,
            api_key=mock_api_key,
            timeout=60
        )

        assert client.timeout == 60

    def test_init_with_env_vars(self, set_env_vars):
        """Test client initialization from environment variables."""
        client = GarakClient()

        assert client.auth.is_authenticated()

    def test_init_without_api_key(self, clean_env):
        """Test that initialization fails without API key."""
        with pytest.raises(AuthenticationError):
            GarakClient(base_url="https://test.garaksecurity.com")

    def test_default_base_url(self, mock_api_key, clean_env):
        """Test that default base URL is used when not specified."""
        client = GarakClient(api_key=mock_api_key)
        assert client.base_url == "https://detect.garaksecurity.com"

    def test_base_url_trailing_slash_removed(self, mock_api_key):
        """Test that trailing slash is removed from base URL."""
        client = GarakClient(
            base_url="https://test.garaksecurity.com/",
            api_key=mock_api_key
        )
        assert client.base_url == "https://test.garaksecurity.com"

    def test_ssl_verification_configurable(self, mock_api_key, mock_base_url):
        """Test that SSL verification can be disabled."""
        client = GarakClient(
            base_url=mock_base_url,
            api_key=mock_api_key,
            verify_ssl=False
        )
        assert client.verify_ssl is False

    def test_session_headers(self, mock_api_key, mock_base_url):
        """Test that session has correct default headers."""
        client = GarakClient(
            base_url=mock_base_url,
            api_key=mock_api_key
        )

        headers = client.session.headers
        assert "User-Agent" in headers
        assert "garak-sdk-python" in headers["User-Agent"]
        assert headers["Accept"] == "application/json"
        assert headers["Content-Type"] == "application/json"


@pytest.mark.unit
@pytest.mark.client
class TestHTTPMethods:
    """Test HTTP method wrappers."""

    @responses.activate
    def test_get_request(self, mock_client):
        """Test GET request."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"status": "ok"},
            status=200
        )

        response = mock_client.get("/api/v1/test")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    @responses.activate
    def test_post_request(self, mock_client):
        """Test POST request."""
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/test",
            json={"created": True},
            status=201
        )

        response = mock_client.post("/api/v1/test", json={"data": "test"})
        assert response.status_code == 201
        assert response.json() == {"created": True}

    @responses.activate
    def test_patch_request(self, mock_client):
        """Test PATCH request."""
        responses.add(
            responses.PATCH,
            "https://test.garaksecurity.com/api/v1/test",
            json={"updated": True},
            status=200
        )

        response = mock_client.patch("/api/v1/test", json={"data": "updated"})
        assert response.status_code == 200

    @responses.activate
    def test_delete_request(self, mock_client):
        """Test DELETE request."""
        responses.add(
            responses.DELETE,
            "https://test.garaksecurity.com/api/v1/test",
            json={"deleted": True},
            status=200
        )

        response = mock_client.delete("/api/v1/test")
        assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.client
class TestErrorHandling:
    """Test error handling for various HTTP status codes."""

    @responses.activate
    def test_401_unauthorized(self, mock_client):
        """Test 401 Unauthorized error handling."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"error": "unauthorized"},
            status=401
        )

        with pytest.raises(AuthenticationError) as exc_info:
            mock_client.get("/api/v1/test")
        assert "Authentication failed" in str(exc_info.value)

    @responses.activate
    def test_403_forbidden(self, mock_client):
        """Test 403 Forbidden error handling."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"error": "forbidden"},
            status=403
        )

        with pytest.raises(AuthenticationError):
            mock_client.get("/api/v1/test")

    @responses.activate
    def test_429_rate_limit(self, mock_client):
        """Test 429 Rate Limit error handling."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"error": "rate_limit_exceeded"},
            status=429,
            headers={"Retry-After": "60"}
        )

        with pytest.raises(RateLimitError) as exc_info:
            mock_client.get("/api/v1/test")
        assert exc_info.value.retry_after == 60

    @responses.activate
    def test_404_not_found(self, mock_client):
        """Test 404 Not Found error handling."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"error": "not_found"},
            status=404
        )

        with pytest.raises(APIError) as exc_info:
            mock_client.get("/api/v1/test")
        assert exc_info.value.status_code == 404

    @responses.activate
    def test_500_server_error(self, mock_client):
        """Test 500 Server Error handling."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"error": "internal_server_error"},
            status=500
        )

        with pytest.raises(APIError) as exc_info:
            mock_client.get("/api/v1/test")
        assert exc_info.value.status_code == 500


@pytest.mark.unit
@pytest.mark.client
class TestHealthAndInfo:
    """Test health check and API info methods."""

    @responses.activate
    def test_health_check(self, mock_client, mock_health_response):
        """Test health check method."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/health",
            json=mock_health_response,
            status=200
        )

        health = mock_client.health_check()
        assert health["status"] == "healthy"
        assert "services" in health

    @responses.activate
    def test_get_api_info(self, mock_client):
        """Test API info method."""
        api_info = {
            "api_version": "v1",
            "service": "Garak LLM Security Scanner",
            "supported_generators": ["openai", "anthropic"]
        }

        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/info",
            json=api_info,
            status=200
        )

        info = mock_client.get_api_info()
        assert info["api_version"] == "v1"
        assert "supported_generators" in info


@pytest.mark.unit
@pytest.mark.client
class TestContextManager:
    """Test context manager support."""

    @responses.activate
    def test_context_manager(self, mock_api_key, mock_base_url):
        """Test client as context manager."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/test",
            json={"status": "ok"},
            status=200
        )

        with GarakClient(base_url=mock_base_url, api_key=mock_api_key) as client:
            response = client.get("/api/v1/test")
            assert response.status_code == 200

        # Session should be closed after context exit
        assert client.session is not None  # Session object still exists but is closed

    def test_close_method(self, mock_client):
        """Test explicit close method."""
        mock_client.close()
        # Should not raise any errors


@pytest.mark.unit
@pytest.mark.client
class TestResourceProperties:
    """Test lazy-loaded resource properties."""

    def test_scans_property(self, mock_client):
        """Test scans resource property."""
        from garak_sdk.resources.scans import ScanResource

        assert hasattr(mock_client, "scans")
        assert isinstance(mock_client.scans, ScanResource)

    def test_metadata_property(self, mock_client):
        """Test metadata resource property."""
        from garak_sdk.resources.metadata import MetadataResource

        assert hasattr(mock_client, "metadata")
        assert isinstance(mock_client.metadata, MetadataResource)

    def test_reports_property(self, mock_client):
        """Test reports resource property."""
        from garak_sdk.resources.reports import ReportResource

        assert hasattr(mock_client, "reports")
        assert isinstance(mock_client.reports, ReportResource)

    def test_resources_cached(self, mock_client):
        """Test that resources are cached after first access."""
        # Access resources multiple times
        scans1 = mock_client.scans
        scans2 = mock_client.scans

        # Should be the same instance
        assert scans1 is scans2


@pytest.mark.unit
@pytest.mark.client
class TestURLBuilding:
    """Test URL building functionality."""

    def test_build_url_with_leading_slash(self, mock_client):
        """Test URL building with leading slash."""
        url = mock_client._build_url("/api/v1/test")
        assert url == "https://test.garaksecurity.com/api/v1/test"

    def test_build_url_without_leading_slash(self, mock_client):
        """Test URL building without leading slash."""
        url = mock_client._build_url("api/v1/test")
        assert url == "https://test.garaksecurity.com/api/v1/test"

    def test_build_url_with_query_params(self, mock_client):
        """Test URL building preserves query parameters."""
        url = mock_client._build_url("/api/v1/test?param=value")
        assert "param=value" in url


@pytest.mark.unit
@pytest.mark.client
class TestRepr:
    """Test string representation."""

    def test_client_repr(self, mock_client):
        """Test client __repr__ method."""
        repr_str = repr(mock_client)
        assert "GarakClient" in repr_str
        assert "test.garaksecurity.com" in repr_str
        assert "garak_te..." in repr_str  # API key prefix with ellipsis
