"""
Tests for authentication manager (garak_sdk.auth).

Tests cover:
- API key initialization and validation
- Environment variable loading
- Authentication header generation
- Invalid configurations
"""

import pytest
import os
from garak_sdk.auth import GarakAuthManager
from garak_sdk.exceptions import AuthenticationError, InvalidConfigurationError


@pytest.mark.unit
@pytest.mark.auth
class TestAuthManager:
    """Test suite for GarakAuthManager."""

    def test_init_with_api_key(self, mock_api_key):
        """Test initialization with explicit API key."""
        auth = GarakAuthManager(api_key=mock_api_key)
        assert auth.api_key == mock_api_key
        assert auth.is_authenticated()

    def test_init_with_env_var(self, set_env_vars, mock_api_key):
        """Test initialization from GARAK_API_KEY environment variable."""
        auth = GarakAuthManager()
        assert auth.api_key == mock_api_key
        assert auth.is_authenticated()

    def test_init_without_api_key(self, clean_env):
        """Test that initialization fails without API key."""
        with pytest.raises(AuthenticationError) as exc_info:
            GarakAuthManager()
        assert "No API key provided" in str(exc_info.value)

    def test_invalid_api_key_format_short(self):
        """Test that short API keys are rejected."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            GarakAuthManager(api_key="garak_short")
        assert "Invalid API key format" in str(exc_info.value)

    def test_invalid_api_key_format_wrong_prefix(self):
        """Test that API keys with wrong prefix are rejected."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            GarakAuthManager(api_key="sk_1234567890abcdefghij")
        assert "Invalid API key format" in str(exc_info.value)

    def test_invalid_api_key_empty(self):
        """Test that empty API keys are rejected."""
        with pytest.raises(InvalidConfigurationError) as exc_info:
            GarakAuthManager(api_key="")
        assert "Invalid API key format" in str(exc_info.value)

    def test_get_auth_headers(self, mock_api_key):
        """Test authentication header generation."""
        auth = GarakAuthManager(api_key=mock_api_key)
        headers = auth.get_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == f"Bearer {mock_api_key}"
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == mock_api_key

    def test_is_authenticated_true(self, mock_api_key):
        """Test is_authenticated returns True for valid key."""
        auth = GarakAuthManager(api_key=mock_api_key)
        assert auth.is_authenticated() is True

    def test_get_key_prefix(self, mock_api_key):
        """Test key prefix extraction for safe logging."""
        auth = GarakAuthManager(api_key=mock_api_key)
        prefix = auth.get_key_prefix()

        assert prefix == f"{mock_api_key[:8]}..."
        assert len(prefix) == 11  # 8 chars + "..."

    def test_alternative_env_var(self, clean_env, monkeypatch):
        """Test loading from alternative GARAK_SDK_API_KEY env var."""
        test_key = "garak_alternative_key_test1234567890abcdefghij"
        monkeypatch.setenv("GARAK_SDK_API_KEY", test_key)

        auth = GarakAuthManager()
        assert auth.api_key == test_key

    def test_env_var_priority(self, clean_env, monkeypatch):
        """Test that GARAK_API_KEY takes priority over GARAK_SDK_API_KEY."""
        primary_key = "garak_primary_key_test1234567890abcdefghij"
        secondary_key = "garak_secondary_key_test1234567890abcdefg"

        monkeypatch.setenv("GARAK_API_KEY", primary_key)
        monkeypatch.setenv("GARAK_SDK_API_KEY", secondary_key)

        auth = GarakAuthManager()
        assert auth.api_key == primary_key

    def test_from_env_file_without_dotenv(self, tmp_path, monkeypatch):
        """Test from_env_file raises error if python-dotenv not installed."""
        # Mock ImportError for dotenv
        import sys
        import builtins
        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "dotenv":
                raise ImportError("No module named 'dotenv'")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        with pytest.raises(InvalidConfigurationError) as exc_info:
            GarakAuthManager.from_env_file()
        assert "python-dotenv is required" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.auth
class TestAPIKeyValidation:
    """Test suite for API key validation."""

    def test_valid_api_key(self):
        """Test validation of properly formatted API key."""
        from garak_sdk.utils import validate_api_key

        valid_key = "garak_1234567890abcdefghijklmnopqrstuvwxyz"
        assert validate_api_key(valid_key) is True

    def test_invalid_prefix(self):
        """Test validation rejects wrong prefix."""
        from garak_sdk.utils import validate_api_key

        invalid_key = "sk_1234567890abcdefghij"
        assert validate_api_key(invalid_key) is False

    def test_too_short(self):
        """Test validation rejects short keys."""
        from garak_sdk.utils import validate_api_key

        short_key = "garak_short"
        assert validate_api_key(short_key) is False

    def test_empty_key(self):
        """Test validation rejects empty keys."""
        from garak_sdk.utils import validate_api_key

        assert validate_api_key("") is False
        assert validate_api_key(None) is False

    def test_none_key(self):
        """Test validation handles None gracefully."""
        from garak_sdk.utils import validate_api_key

        assert validate_api_key(None) is False


@pytest.mark.unit
@pytest.mark.auth
class TestAuthenticationFlow:
    """Test authentication flow scenarios."""

    def test_explicit_key_overrides_env(self, set_env_vars):
        """Test that explicit API key overrides environment variable."""
        explicit_key = "garak_explicit_key_1234567890abcdefghijklmnop"
        auth = GarakAuthManager(api_key=explicit_key)

        assert auth.api_key == explicit_key
        # Should not use env var
        assert auth.api_key != os.getenv("GARAK_API_KEY")

    def test_multiple_instances(self, mock_api_key):
        """Test that multiple auth managers can coexist."""
        auth1 = GarakAuthManager(api_key=f"{mock_api_key}_1")
        auth2 = GarakAuthManager(api_key=f"{mock_api_key}_2")

        assert auth1.api_key != auth2.api_key
        assert auth1.is_authenticated()
        assert auth2.is_authenticated()

    def test_auth_headers_immutable(self, mock_api_key):
        """Test that modifying returned headers doesn't affect auth manager."""
        auth = GarakAuthManager(api_key=mock_api_key)

        headers1 = auth.get_auth_headers()
        headers1["Authorization"] = "modified"

        headers2 = auth.get_auth_headers()
        assert headers2["Authorization"] == f"Bearer {mock_api_key}"
