"""
Garak SDK Client

Main client for interacting with the Garak Security API.
"""

import os
from typing import Any, Dict, Optional, cast
from urllib.parse import urljoin

import requests

from .auth import GarakAuthManager
from .exceptions import (
    APIError,
    AuthenticationError,
    InvalidConfigurationError,
    NetworkError,
    RateLimitError,
    ScanNotFoundError,
)
from .utils import parse_retry_after, retry_with_backoff


class GarakClient:
    """
    Main client for the Garak Security SDK.

    This client provides access to the Garak API for running security scans
    against AI models, discovering available generators and probes, and
    downloading scan reports.

    Usage:
        from garak_sdk import GarakClient

        # Initialize client
        client = GarakClient(
            base_url="https://scans.garaksecurity.com",
            api_key=os.getenv("GARAK_API_KEY")
        )

        # Create a scan
        scan = client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak", "harmful"]
        )

        # Wait for completion
        scan = client.scans.wait_for_completion(scan.scan_id)

        # Get results
        results = client.scans.get_results(scan.scan_id)

    Attributes:
        scans: Scan management resource
        metadata: Generator/probe discovery resource
        reports: Report download resource
    """

    DEFAULT_BASE_URL = "https://scans.garaksecurity.com"
    DEFAULT_TIMEOUT = 30  # seconds
    SDK_VERSION = "1.0.1"

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        verify_ssl: bool = True,
        **kwargs,
    ):
        """
        Initialize Garak client.

        Args:
            base_url: Base URL for the API (default: https://scans.garaksecurity.com)
            api_key: API key for authentication. If not provided, will load from
                    GARAK_API_KEY environment variable.
            timeout: Request timeout in seconds (default: 30)
            verify_ssl: Whether to verify SSL certificates (default: True)
            **kwargs: Additional configuration options

        Raises:
            AuthenticationError: If no API key is provided
            InvalidConfigurationError: If configuration is invalid
        """
        # Check for base URL in order: parameter, kwargs, environment variable, default
        self.base_url = (
            base_url
            or kwargs.get("url")
            or os.environ.get("GARAK_API_BASE_URL")
            or self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.verify_ssl = verify_ssl

        # Initialize authentication
        self.auth = GarakAuthManager(api_key)

        # Initialize HTTP session
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": f"garak-sdk-python/{self.SDK_VERSION}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        self.session.headers.update(self.auth.get_auth_headers())

        # Initialize resources (lazy import to avoid circular dependencies)
        self._scans = None
        self._metadata = None
        self._reports = None

    @property
    def scans(self):
        """Scan management resource."""
        if self._scans is None:
            from .resources.scans import ScanResource

            self._scans = ScanResource(self)
        return self._scans

    @property
    def metadata(self):
        """Metadata discovery resource."""
        if self._metadata is None:
            from .resources.metadata import MetadataResource

            self._metadata = MetadataResource(self)
        return self._metadata

    @property
    def reports(self):
        """Report download resource."""
        if self._reports is None:
            from .resources.reports import ReportResource

            self._reports = ReportResource(self)
        return self._reports

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint path.

        Args:
            endpoint: API endpoint path (e.g., '/api/v1/scans')

        Returns:
            Full URL
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        return urljoin(self.base_url, endpoint)

    @retry_with_backoff(max_attempts=3, retry_on=(requests.exceptions.RequestException,))
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make HTTP request with automatic retry and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters
            json: JSON body
            data: Request body
            headers: Additional headers
            **kwargs: Additional requests options

        Returns:
            Response object

        Raises:
            AuthenticationError: On 401/403 errors
            RateLimitError: On 429 errors
            APIError: On other API errors
            NetworkError: On network failures
        """
        url = self._build_url(endpoint)

        # Merge headers
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=request_headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs,
            )

            # Handle specific status codes
            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError(
                    f"Authentication failed: {response.text}", response=response
                )

            if response.status_code == 429:
                retry_after = parse_retry_after(response.headers.get("Retry-After"))
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds.",
                    retry_after=retry_after,
                    response=response,
                )

            # Handle 404 Not Found errors
            if response.status_code == 404:
                error_data = (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                error_type = error_data.get("error", "")
                error_message = error_data.get("message", response.text).lower()

                # Raise ScanNotFoundError only for scan-related 404s
                # Check if error type contains 'scan' or the URL contains '/scans/'
                if (
                    "scan" in error_type.lower()
                    or "scan" in error_message
                    or "/scans/" in response.url
                ):
                    raise ScanNotFoundError(
                        message=error_data.get("message", f"Scan not found: {response.text}"),
                        response=response,
                    )

            # Raise for other client/server errors
            if response.status_code >= 400:
                error_data = (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                raise APIError(
                    message=error_data.get("message", response.text),
                    status_code=response.status_code,
                    error_code=error_data.get("error"),
                    response=response,
                )

            return response

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Failed to connect to {url}: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request to {url} timed out: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return cast(requests.Response, self._request("GET", endpoint, **kwargs))

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make POST request."""
        return cast(requests.Response, self._request("POST", endpoint, **kwargs))

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        """Make PATCH request."""
        return cast(requests.Response, self._request("PATCH", endpoint, **kwargs))

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return cast(requests.Response, self._request("DELETE", endpoint, **kwargs))

    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.

        Returns:
            Health status information

        Example:
            health = client.health_check()
            print(f"API Status: {health['status']}")
        """
        response = self.get("/api/v1/health")
        return cast(Dict[str, Any], response.json())

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and capabilities.

        Returns:
            API information

        Example:
            info = client.get_api_info()
            print(f"API Version: {info['api_version']}")
            print(f"Supported generators: {info['supported_generators']}")
        """
        response = self.get("/api/v1/info")
        return cast(Dict[str, Any], response.json())

    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self):
        """String representation."""
        return f"GarakClient(base_url='{self.base_url}', api_key='{self.auth.get_key_prefix()}')"
