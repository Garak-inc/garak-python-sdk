"""
Garak SDK Utilities

Utility functions for retry logic, polling, and request handling.
"""

import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])

from .exceptions import RateLimitError, ScanTimeoutError


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple = (Exception,),
):
    """
    Decorator for retrying function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        retry_on: Tuple of exceptions to retry on
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    # Don't retry on the last attempt
                    if attempt == max_attempts - 1:
                        break

                    # Don't retry on authentication errors
                    from .exceptions import AuthenticationError

                    if isinstance(e, AuthenticationError):
                        raise

                    # Wait before retry
                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)

            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            # This should never happen, but satisfy mypy
            raise Exception("All retry attempts failed")

        return cast(F, wrapper)

    return decorator


def wait_for_condition(
    check_func: Callable[[], tuple[bool, Any]],
    timeout: float = 3600,
    poll_interval: float = 10,
    on_progress: Optional[Callable[[Any], None]] = None,
) -> Any:
    """
    Wait for a condition to be true, polling at regular intervals.

    Args:
        check_func: Function that returns (is_complete, result) tuple
        timeout: Maximum time to wait in seconds
        poll_interval: Time between checks in seconds
        on_progress: Optional callback for progress updates

    Returns:
        Result from check_func when condition is met

    Raises:
        ScanTimeoutError: If timeout is exceeded
    """
    start_time = time.time()

    while True:
        # Check condition
        is_complete, result = check_func()

        # Call progress callback if provided
        if on_progress and result:
            on_progress(result)

        # Return if complete
        if is_complete:
            return result

        # Check timeout
        elapsed = time.time() - start_time
        if elapsed >= timeout:
            raise ScanTimeoutError(f"Operation timed out after {timeout} seconds")

        # Wait before next check
        time.sleep(poll_interval)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def parse_retry_after(retry_after: Any) -> int:
    """
    Parse Retry-After header value.

    Args:
        retry_after: Header value (seconds as int/str, or HTTP date)

    Returns:
        Seconds to wait
    """
    if isinstance(retry_after, int):
        return retry_after

    if isinstance(retry_after, str):
        try:
            return int(retry_after)
        except ValueError:
            # Could be HTTP date format, but we'll default to 60 seconds
            return 60

    return 60


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if valid format
    """
    if not api_key:
        return False

    # API keys should start with 'garak_' (backend format)
    if not api_key.startswith("garak_"):
        return False

    # Backend generates ~49 char keys (garak_ + 43 chars from token_urlsafe(32))
    if len(api_key) < 40:
        return False

    return True


def build_query_params(**kwargs) -> dict:
    """
    Build query parameters dictionary, filtering out None values.

    Args:
        **kwargs: Query parameters

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in kwargs.items() if v is not None}
