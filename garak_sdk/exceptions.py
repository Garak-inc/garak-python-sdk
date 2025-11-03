"""
Garak SDK Exceptions

Custom exceptions for the Garak Security SDK.
"""

from typing import Optional


class GarakSDKError(Exception):
    """Base exception for all Garak SDK errors."""

    def __init__(self, message: str, response=None):
        super().__init__(message)
        self.message = message
        self.response = response


class AuthenticationError(GarakSDKError):
    """Raised when authentication fails (401/403)."""

    pass


class QuotaExceededError(GarakSDKError):
    """Raised when scan quota is exceeded."""

    pass


class ScanNotFoundError(GarakSDKError):
    """Raised when a scan is not found (404)."""

    pass


class ScanValidationError(GarakSDKError):
    """Raised when scan request validation fails."""

    pass


class ScanTimeoutError(GarakSDKError):
    """Raised when scan exceeds timeout while waiting."""

    pass


class RateLimitError(GarakSDKError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self, message: str, retry_after: Optional[int] = None, response=None
    ):
        super().__init__(message, response)
        self.retry_after = retry_after


class NetworkError(GarakSDKError):
    """Raised when network request fails."""

    pass


class InvalidConfigurationError(GarakSDKError):
    """Raised when SDK configuration is invalid."""

    pass


class APIError(GarakSDKError):
    """Raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        response=None,
    ):
        super().__init__(message, response)
        self.status_code = status_code
        self.error_code = error_code
