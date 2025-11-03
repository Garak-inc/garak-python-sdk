"""
Scan Resource

Handles scan creation, management, and monitoring.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Union, cast

from ..exceptions import QuotaExceededError, ScanNotFoundError, ScanTimeoutError
from ..models import (
    CreateScanRequest,
    QuotaResponse,
    ScanListResponse,
    ScanMetadata,
    ScanResponse,
    ScanStatus,
    ScanStatusResponse,
    UpdateScanRequest,
)
from ..utils import wait_for_condition


class ScanResource:
    """
    Scan management operations.

    Provides methods for creating, listing, updating, and monitoring security scans.
    """

    def __init__(self, client):
        """
        Initialize scan resource.

        Args:
            client: GarakClient instance
        """
        self.client = client

    def create(
        self,
        generator: str,
        model_name: str,
        probe_categories: Optional[List[str]] = None,
        probes: Optional[List[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parallel_attempts: int = 1,
        api_keys: Optional[Dict[str, str]] = None,
        use_free_tier: bool = False,
        **kwargs,
    ) -> Union[ScanResponse, Dict[str, Any]]:
        """
        Create a new security scan.

        Args:
            generator: Generator type (e.g., 'openai', 'anthropic')
            model_name: Model name (e.g., 'gpt-4', 'claude-3-opus')
            probe_categories: List of probe categories to run
            probes: List of specific probes to run (alternative to categories)
            name: Scan name for identification
            description: Scan description
            parallel_attempts: Number of parallel attempts per probe
            api_keys: API keys required by the generator
            use_free_tier: Whether to use free tier (platform API keys)
            **kwargs: Additional generator-specific configs (rest_config, ollama_host, etc.)

        Returns:
            ScanResponse with scan metadata

        Raises:
            QuotaExceededError: If scan quota is exceeded
            ValidationError: If scan parameters are invalid

        Example:
            scan = client.scans.create(
                generator="openai",
                model_name="gpt-4",
                probe_categories=["jailbreak", "harmful"],
                api_keys={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
            )
        """
        # Normalize API keys to lowercase format expected by backend
        normalized_api_keys = {}
        if api_keys:
            for key, value in api_keys.items():
                # Convert OPENAI_API_KEY -> openai_api_key
                normalized_key = key.lower()
                normalized_api_keys[normalized_key] = value

        # Build request
        request_data = CreateScanRequest(
            name=name,
            description=description,
            generator=generator,
            model_name=model_name,
            probe_categories=probe_categories or [],
            probes=probes,
            parallel_attempts=parallel_attempts,
            api_keys=normalized_api_keys,
            use_free_tier=use_free_tier,
            **kwargs,
        )

        # Make request
        response = self.client.post(
            "/api/v1/scans", json=request_data.model_dump(exclude_none=True)
        )

        result = response.json()

        # Check for quota exceeded
        if result.get("needs_subscription"):
            raise QuotaExceededError(f"Free tier quota exceeded. Please upgrade your subscription.")

        # Handle redirect to jobs page (multiple scans created from cache)
        if result.get("redirect") == "jobs":
            # Multiple scans created - return a special response
            return {
                "message": result.get("message"),
                "scan_count": result.get("count"),
                "redirect": "jobs",
            }

        # Parse response
        scan_id = result.get("scan_id")
        metadata = ScanMetadata(**result.get("metadata", {}))

        return ScanResponse(metadata=metadata, results=None, reports=[], output_log=None)

    def list(
        self,
        status: Optional[ScanStatus] = None,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> ScanListResponse:
        """
        List scans with pagination.

        Args:
            status: Filter by scan status
            search: Search query for scan name/model
            page: Page number (starts at 1)
            per_page: Results per page

        Returns:
            ScanListResponse with paginated scans

        Example:
            scans = client.scans.list(status=ScanStatus.COMPLETED, page=1)
            for scan in scans.scans:
                print(f"{scan.scan_id}: {scan.status}")
        """
        params: Dict[str, Any] = {"page": page, "per_page": per_page}

        if status:
            params["status"] = status.value
        if search:
            params["search"] = search

        response = self.client.get("/api/v1/scans", params=params)
        return ScanListResponse(**response.json())

    def get(self, scan_id: str) -> ScanResponse:
        """
        Get detailed information about a scan.

        Args:
            scan_id: Scan ID

        Returns:
            ScanResponse with full scan details

        Raises:
            ScanNotFoundError: If scan not found

        Example:
            scan = client.scans.get("abc123")
            print(f"Status: {scan.metadata.status}")
        """
        try:
            response = self.client.get(f"/api/v1/scans/{scan_id}")
            return ScanResponse(**response.json())
        except Exception as e:
            if "404" in str(e):
                raise ScanNotFoundError(f"Scan {scan_id} not found")
            raise

    def get_status(
        self, scan_id: str, include_output: bool = False, start_line: int = 0, max_lines: int = 2000
    ) -> ScanStatusResponse:
        """
        Get current scan status and progress.

        Args:
            scan_id: Scan ID
            include_output: Whether to include output logs
            start_line: Starting line for output (for pagination)
            max_lines: Maximum lines to return

        Returns:
            ScanStatusResponse with status and progress

        Example:
            status = client.scans.get_status("abc123", include_output=True)
            print(f"Progress: {status.progress.percentage}%")
        """
        params: Dict[str, Any] = {}
        if include_output:
            params["include_output"] = "true"
            params["start_line"] = start_line
            params["max_lines"] = max_lines

        response = self.client.get(f"/api/v1/scans/{scan_id}/status", params=params)
        return ScanStatusResponse(**response.json())

    def wait_for_completion(
        self,
        scan_id: str,
        timeout: float = 3600,
        poll_interval: float = 10,
        on_progress: Optional[Callable[[ScanStatusResponse], None]] = None,
    ) -> ScanResponse:
        """
        Wait for scan to complete, polling at regular intervals.

        This is a blocking operation that polls the scan status until completion
        or timeout. Useful for CI/CD pipelines.

        Args:
            scan_id: Scan ID
            timeout: Maximum time to wait in seconds (default: 1 hour)
            poll_interval: Time between status checks in seconds (default: 10s)
            on_progress: Optional callback for progress updates

        Returns:
            ScanResponse with completed scan details

        Raises:
            ScanTimeoutError: If timeout is exceeded

        Example:
            scan = client.scans.create(...)
            scan = client.scans.wait_for_completion(
                scan.metadata.scan_id,
                on_progress=lambda s: print(f"Progress: {s.progress.percentage}%")
            )
        """

        def check_completion():
            status = self.get_status(scan_id)

            # Check if complete
            is_complete = status.status in [
                ScanStatus.COMPLETED,
                ScanStatus.FAILED,
                ScanStatus.CANCELLED,
            ]

            return is_complete, status

        # Wait for completion
        final_status = wait_for_condition(
            check_func=check_completion,
            timeout=timeout,
            poll_interval=poll_interval,
            on_progress=on_progress,
        )

        # Get full scan details
        return self.get(scan_id)

    def update(
        self, scan_id: str, name: Optional[str] = None, description: Optional[str] = None
    ) -> ScanResponse:
        """
        Update scan metadata.

        Args:
            scan_id: Scan ID
            name: New scan name
            description: New scan description

        Returns:
            ScanResponse with updated metadata

        Example:
            scan = client.scans.update(
                "abc123",
                name="Production Security Scan",
                description="Weekly security audit"
            )
        """
        request_data = UpdateScanRequest(name=name, description=description)

        response = self.client.patch(
            f"/api/v1/scans/{scan_id}", json=request_data.model_dump(exclude_none=True)
        )

        result = response.json()
        return ScanResponse(
            metadata=ScanMetadata(**result.get("metadata", {})),
            results=None,
            reports=[],
            output_log=None,
        )

    def cancel(self, scan_id: str) -> Dict[str, Any]:
        """
        Cancel a running scan.

        Args:
            scan_id: Scan ID

        Returns:
            Cancellation result

        Example:
            result = client.scans.cancel("abc123")
            print(result['message'])
        """
        response = self.client.delete(f"/api/v1/scans/{scan_id}")
        return cast(Dict[str, Any], response.json())

    def get_results(self, scan_id: str) -> Dict[str, Any]:
        """
        Get parsed scan results and security analysis.

        Args:
            scan_id: Scan ID

        Returns:
            Scan results dictionary with security scores and analysis

        Example:
            results = client.scans.get_results("abc123")
            print(f"Security Score: {results['security_score']}/100")
        """
        response = self.client.get(f"/api/v1/scans/{scan_id}/results")
        return cast(Dict[str, Any], response.json())

    def get_quota(self) -> QuotaResponse:
        """
        Get current scan quota information.

        Returns:
            QuotaResponse with quota status

        Example:
            quota = client.scans.get_quota()
            print(f"Free scans remaining: {quota.quota_status.remaining_free_scans}")
        """
        response = self.client.get("/api/v1/scans/quota")
        return QuotaResponse(**response.json())
