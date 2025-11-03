"""
Tests for exception handling (garak_sdk.exceptions).

Tests cover:
- Exception hierarchy
- Exception attributes
- Error message formatting
- Exception raising
"""

import pytest
from garak_sdk.exceptions import (
    GarakSDKError,
    AuthenticationError,
    QuotaExceededError,
    ScanNotFoundError,
    ScanValidationError,
    ScanTimeoutError,
    RateLimitError,
    NetworkError,
    InvalidConfigurationError,
    APIError
)


@pytest.mark.unit
@pytest.mark.exceptions
class TestExceptionHierarchy:
    """Test exception class hierarchy."""

    def test_base_exception(self):
        """Test base GarakSDKError exception."""
        exc = GarakSDKError("Test error")

        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.response is None

    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inherits from base."""
        exc = AuthenticationError("Auth failed")

        assert isinstance(exc, GarakSDKError)
        assert isinstance(exc, Exception)

    def test_all_exceptions_inherit_base(self):
        """Test all exceptions inherit from GarakSDKError."""
        exceptions = [
            AuthenticationError("test"),
            QuotaExceededError("test"),
            ScanNotFoundError("test"),
            ScanValidationError("test"),
            ScanTimeoutError("test"),
            RateLimitError("test"),
            NetworkError("test"),
            InvalidConfigurationError("test"),
            APIError("test")
        ]

        for exc in exceptions:
            assert isinstance(exc, GarakSDKError)


@pytest.mark.unit
@pytest.mark.exceptions
class TestExceptionAttributes:
    """Test exception attributes and metadata."""

    def test_exception_with_response(self):
        """Test exception with response object."""
        class MockResponse:
            status_code = 401
            text = "Unauthorized"

        response = MockResponse()
        exc = AuthenticationError("Auth failed", response=response)

        assert exc.response is not None
        assert exc.response.status_code == 401

    def test_rate_limit_error_attributes(self):
        """Test RateLimitError retry_after attribute."""
        exc = RateLimitError("Rate limited", retry_after=60)

        assert exc.retry_after == 60
        assert exc.message == "Rate limited"

    def test_api_error_attributes(self):
        """Test APIError status code and error code."""
        exc = APIError(
            "API error occurred",
            status_code=400,
            error_code="validation_failed"
        )

        assert exc.status_code == 400
        assert exc.error_code == "validation_failed"
        assert exc.message == "API error occurred"


@pytest.mark.unit
@pytest.mark.exceptions
class TestExceptionMessages:
    """Test exception message handling."""

    def test_authentication_error_message(self):
        """Test AuthenticationError message."""
        exc = AuthenticationError("Invalid API key provided")

        assert "Invalid API key" in str(exc)

    def test_quota_exceeded_message(self):
        """Test QuotaExceededError message."""
        exc = QuotaExceededError("Free tier quota exceeded. Please upgrade.")

        assert "quota exceeded" in str(exc).lower()

    def test_scan_not_found_message(self):
        """Test ScanNotFoundError message."""
        scan_id = "test-scan-123"
        exc = ScanNotFoundError(f"Scan {scan_id} not found")

        assert scan_id in str(exc)
        assert "not found" in str(exc).lower()

    def test_timeout_error_message(self):
        """Test ScanTimeoutError message."""
        exc = ScanTimeoutError("Operation timed out after 3600 seconds")

        assert "timed out" in str(exc).lower()
        assert "3600" in str(exc)


@pytest.mark.unit
@pytest.mark.exceptions
class TestExceptionRaising:
    """Test exception raising scenarios."""

    def test_raise_authentication_error(self):
        """Test raising AuthenticationError."""
        with pytest.raises(AuthenticationError) as exc_info:
            raise AuthenticationError("Invalid credentials")

        assert "Invalid credentials" in str(exc_info.value)

    def test_raise_quota_exceeded(self):
        """Test raising QuotaExceededError."""
        with pytest.raises(QuotaExceededError) as exc_info:
            raise QuotaExceededError("Quota limit reached")

        assert "Quota" in str(exc_info.value)

    def test_raise_scan_timeout(self):
        """Test raising ScanTimeoutError."""
        with pytest.raises(ScanTimeoutError) as exc_info:
            raise ScanTimeoutError("Scan timeout")

        assert isinstance(exc_info.value, GarakSDKError)

    def test_catch_base_exception(self):
        """Test catching specific exception as base exception."""
        try:
            raise AuthenticationError("Test")
        except GarakSDKError as e:
            assert isinstance(e, AuthenticationError)


@pytest.mark.unit
@pytest.mark.exceptions
class TestExceptionFormatting:
    """Test exception string formatting."""

    def test_api_error_with_all_attributes(self):
        """Test APIError string representation with all attributes."""
        exc = APIError(
            "Validation failed: Invalid model name",
            status_code=400,
            error_code="invalid_model"
        )

        exc_str = str(exc)
        assert "Validation failed" in exc_str

    def test_rate_limit_error_formatting(self):
        """Test RateLimitError formatting with retry_after."""
        exc = RateLimitError("Too many requests", retry_after=120)

        exc_str = str(exc)
        assert "Too many requests" in exc_str

    def test_exception_repr(self):
        """Test exception __repr__ method."""
        exc = NetworkError("Connection failed")

        repr_str = repr(exc)
        assert "NetworkError" in repr_str or "Connection failed" in repr_str
