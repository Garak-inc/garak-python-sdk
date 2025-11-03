"""
Garak SDK Authentication

Handles API key authentication for the Garak Security API.
"""

import os
from typing import Dict, Optional

from .exceptions import AuthenticationError, InvalidConfigurationError
from .utils import validate_api_key


class GarakAuthManager:
    """
    Manages API key authentication for the Garak SDK.

    Unlike some APIs that use M2M token exchange (e.g., Vijil),
    Garak uses long-lived API keys that are created through the
    admin dashboard at /api/v1/admin/api-keys.

    API keys are passed in request headers as:
    - Authorization: Bearer <api_key>
    - OR X-API-Key: <api_key>
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize authentication manager.

        Args:
            api_key: API key for authentication. If not provided,
                    will try to load from GARAK_API_KEY environment variable.

        Raises:
            AuthenticationError: If no API key is provided or found
            InvalidConfigurationError: If API key format is invalid
        """
        # Check for explicitly provided empty string
        if api_key is not None and api_key == "":
            raise InvalidConfigurationError(
                "Invalid API key format. API keys should start with 'garak_' and be at least 40 characters long."
            )

        loaded_key = api_key or self._load_api_key_from_env()

        if not loaded_key:
            raise AuthenticationError(
                "No API key provided. Pass api_key parameter or set GARAK_API_KEY environment variable."
            )

        if not validate_api_key(loaded_key):
            raise InvalidConfigurationError(
                "Invalid API key format. API keys should start with 'garak_' and be at least 40 characters long."
            )

        # At this point, we have a valid non-None API key
        self.api_key: str = loaded_key

    def _load_api_key_from_env(self) -> Optional[str]:
        """
        Load API key from environment variables.

        Checks the following environment variables in order:
        1. GARAK_API_KEY (recommended)
        2. GARAK_SDK_API_KEY (alternative)

        Returns:
            API key if found, None otherwise
        """
        return os.environ.get("GARAK_API_KEY") or os.environ.get("GARAK_SDK_API_KEY")

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dictionary with authentication headers
        """
        return {"Authorization": f"Bearer {self.api_key}", "X-API-Key": self.api_key}

    def is_authenticated(self) -> bool:
        """
        Check if authentication is configured.

        Returns:
            True if API key is set and valid format
        """
        return bool(self.api_key) and validate_api_key(self.api_key)

    def get_key_prefix(self) -> str:
        """
        Get the API key prefix for logging (safe to display).

        Returns:
            First 8 characters of API key
        """
        if not self.api_key:
            return "None"
        return self.api_key[:8] + "..."

    @staticmethod
    def from_env_file(env_file: str = ".env") -> "GarakAuthManager":
        """
        Create auth manager from environment file.

        Args:
            env_file: Path to .env file

        Returns:
            GarakAuthManager instance

        Example:
            auth = GarakAuthManager.from_env_file('.env.production')
        """
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file)
        except ImportError:
            raise InvalidConfigurationError(
                "python-dotenv is required to load from .env file. "
                "Install with: pip install python-dotenv"
            )

        return GarakAuthManager()
