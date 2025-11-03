"""
Tests for scan resource (garak_sdk.resources.scans).

Tests cover:
- Scan creation with various configurations
- Scan listing and filtering
- Scan status monitoring
- Waiting for completion with polling
- Scan cancellation
- Results retrieval
- Quota management
"""

import pytest
import responses
import time
from garak_sdk.models import ScanStatus, ScanMetadata
from garak_sdk.exceptions import (
    QuotaExceededError,
    ScanNotFoundError,
    ScanTimeoutError
)


@pytest.mark.unit
@pytest.mark.scans
class TestScanCreation:
    """Test scan creation functionality."""

    @responses.activate
    def test_create_scan_basic(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test basic scan creation."""
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": mock_scan_id,
                "message": f"Scan created successfully with ID: {mock_scan_id}",
                "metadata": mock_scan_metadata
            },
            status=201
        )

        scan = mock_client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak", "harmful"]
        )

        assert scan.metadata.scan_id == mock_scan_id
        assert scan.metadata.generator == "openai"
        assert scan.metadata.model_name == "gpt-4"

    @responses.activate
    def test_create_scan_with_all_options(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test scan creation with all optional parameters."""
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": mock_scan_id,
                "metadata": mock_scan_metadata
            },
            status=201
        )

        scan = mock_client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak"],
            name="Test Scan",
            description="Test description",
            parallel_attempts=2,
            api_keys={"OPENAI_API_KEY": "test-key"},
            use_free_tier=False
        )

        assert scan.metadata.scan_id == mock_scan_id

    @responses.activate
    def test_create_scan_with_specific_probes(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test scan creation with specific probe list."""
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": mock_scan_id,
                "metadata": mock_scan_metadata
            },
            status=201
        )

        scan = mock_client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probes=["probe1", "probe2", "probe3"]
        )

        assert scan.metadata.scan_id == mock_scan_id

    @responses.activate
    def test_create_scan_quota_exceeded(self, mock_client):
        """Test scan creation when quota is exceeded."""
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": "test-scan-123",
                "metadata": {"needs_subscription": True},
                "needs_subscription": True
            },
            status=201
        )

        with pytest.raises(QuotaExceededError) as exc_info:
            mock_client.scans.create(
                generator="openai",
                model_name="gpt-4",
                probe_categories=["jailbreak"]
            )
        assert "quota exceeded" in str(exc_info.value).lower()

    @responses.activate
    def test_create_scan_free_tier(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test scan creation with free tier."""
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": mock_scan_id,
                "metadata": mock_scan_metadata,
                "free_tier": True,
                "remaining_free_scans": 1
            },
            status=201
        )

        scan = mock_client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak"],
            use_free_tier=True
        )

        assert scan.metadata.scan_id == mock_scan_id


@pytest.mark.unit
@pytest.mark.scans
class TestScanListing:
    """Test scan listing and filtering."""

    @responses.activate
    def test_list_scans_default(self, mock_client, mock_scan_metadata):
        """Test listing scans with default parameters."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scans": [mock_scan_metadata],
                "total": 1,
                "page": 1,
                "per_page": 20,
                "has_next": False
            },
            status=200
        )

        result = mock_client.scans.list()

        assert result.total == 1
        assert len(result.scans) == 1
        assert result.page == 1
        assert result.has_next is False

    @responses.activate
    def test_list_scans_with_status_filter(self, mock_client, mock_scan_metadata):
        """Test listing scans filtered by status."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scans": [mock_scan_metadata],
                "total": 1,
                "page": 1,
                "per_page": 20,
                "has_next": False
            },
            status=200,
            match=[
                responses.matchers.query_param_matcher({
                    "page": "1",
                    "per_page": "20",
                    "status": "completed"
                })
            ]
        )

        result = mock_client.scans.list(status=ScanStatus.COMPLETED)

        assert result.total == 1
        assert result.scans[0].status == ScanStatus.COMPLETED

    @responses.activate
    def test_list_scans_with_search(self, mock_client, mock_scan_metadata):
        """Test listing scans with search query."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scans": [mock_scan_metadata],
                "total": 1,
                "page": 1,
                "per_page": 20,
                "has_next": False
            },
            status=200,
            match=[
                responses.matchers.query_param_matcher({
                    "page": "1",
                    "per_page": "20",
                    "search": "test"
                })
            ]
        )

        result = mock_client.scans.list(search="test")

        assert result.total == 1

    @responses.activate
    def test_list_scans_pagination(self, mock_client, mock_scan_metadata):
        """Test scan listing with pagination."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scans": [mock_scan_metadata],
                "total": 100,
                "page": 2,
                "per_page": 10,
                "has_next": True
            },
            status=200,
            match=[
                responses.matchers.query_param_matcher({"page": "2", "per_page": "10"})
            ]
        )

        result = mock_client.scans.list(page=2, per_page=10)

        assert result.page == 2
        assert result.per_page == 10
        assert result.has_next is True


@pytest.mark.unit
@pytest.mark.scans
class TestScanRetrieval:
    """Test scan retrieval functionality."""

    @responses.activate
    def test_get_scan(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test getting scan details."""
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "metadata": mock_scan_metadata,
                "results": None,
                "reports": [],
                "output_log": ""
            },
            status=200
        )

        scan = mock_client.scans.get(mock_scan_id)

        assert scan.metadata.scan_id == mock_scan_id
        assert scan.metadata.status == ScanStatus.COMPLETED

    @responses.activate
    def test_get_scan_not_found(self, mock_client, mock_scan_id):
        """Test getting non-existent scan."""
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={"error": "scan_not_found"},
            status=404
        )

        with pytest.raises(ScanNotFoundError):
            mock_client.scans.get(mock_scan_id)

    @responses.activate
    def test_get_scan_status(self, mock_client, mock_scan_id):
        """Test getting scan status."""
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
            json={
                "scan_id": mock_scan_id,
                "status": "running",
                "progress": {"completed_items": 50, "total_items": 100, "progress_percent": 50.0},
                "created_at": "2024-01-01T00:00:00Z"
            },
            status=200
        )

        status = mock_client.scans.get_status(mock_scan_id)

        assert status.scan_id == mock_scan_id
        assert status.status == ScanStatus.RUNNING
        assert status.progress.progress_percent == 50.0

    @responses.activate
    def test_get_scan_status_with_output(self, mock_client, mock_scan_id):
        """Test getting scan status with output logs."""
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
            json={
                "scan_id": mock_scan_id,
                "status": "running",
                "progress": {"completed_items": 50, "total_items": 100, "progress_percent": 50.0},
                "output": "Test output logs",
                "output_metadata": {
                    "total_lines": 100,
                    "start_line": 0,
                    "returned_lines": 100
                }
            },
            status=200
        )

        status = mock_client.scans.get_status(mock_scan_id, include_output=True)

        assert status.output == "Test output logs"
        assert status.output_metadata is not None


@pytest.mark.unit
@pytest.mark.scans
class TestScanWaiting:
    """Test waiting for scan completion."""

    @responses.activate
    def test_wait_for_completion_immediate(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test waiting when scan is already completed."""
        # Status check returns completed
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
            json={
                "scan_id": mock_scan_id,
                "status": "completed",
                "progress": {"current": 100, "total": 100, "percentage": 100.0}
            },
            status=200
        )

        # Get full scan details
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "metadata": mock_scan_metadata,
                "results": None,
                "reports": []
            },
            status=200
        )

        scan = mock_client.scans.wait_for_completion(mock_scan_id, timeout=10, poll_interval=1)

        assert scan.metadata.status == ScanStatus.COMPLETED

    @responses.activate
    def test_wait_for_completion_with_progress(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test waiting with progress callback."""
        # First status check - running
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
            json={
                "scan_id": mock_scan_id,
                "status": "running",
                "progress": {"current": 50, "total": 100, "percentage": 50.0}
            },
            status=200
        )

        # Second status check - completed
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
            json={
                "scan_id": mock_scan_id,
                "status": "completed",
                "progress": {"current": 100, "total": 100, "percentage": 100.0}
            },
            status=200
        )

        # Get full scan details
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "metadata": mock_scan_metadata,
                "results": None,
                "reports": []
            },
            status=200
        )

        progress_updates = []

        def on_progress(status):
            progress_updates.append(status.progress.progress_percent)

        scan = mock_client.scans.wait_for_completion(
            mock_scan_id,
            timeout=30,
            poll_interval=1,
            on_progress=on_progress
        )

        assert scan.metadata.status == ScanStatus.COMPLETED
        assert len(progress_updates) >= 1  # At least one progress update

    @responses.activate
    def test_wait_for_completion_timeout(self, mock_client, mock_scan_id):
        """Test that waiting times out for long-running scans."""
        # Always return running status
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/status",
            json={
                "scan_id": mock_scan_id,
                "status": "running",
                "progress": {"current": 50, "total": 100, "percentage": 50.0}
            },
            status=200
        )

        with pytest.raises(ScanTimeoutError):
            mock_client.scans.wait_for_completion(
                mock_scan_id,
                timeout=2,  # Short timeout
                poll_interval=0.5
            )


@pytest.mark.unit
@pytest.mark.scans
class TestScanManagement:
    """Test scan management operations."""

    @responses.activate
    def test_update_scan(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test updating scan metadata."""
        responses.add(
            responses.PATCH,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "message": "Scan updated successfully",
                "metadata": {**mock_scan_metadata, "name": "Updated Name"}
            },
            status=200
        )

        scan = mock_client.scans.update(mock_scan_id, name="Updated Name")

        assert scan.metadata.name == "Updated Name"

    @responses.activate
    def test_cancel_scan(self, mock_client, mock_scan_id):
        """Test cancelling a scan."""
        responses.add(
            responses.DELETE,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "message": f"Cancellation requested for scan {mock_scan_id}",
                "status": "cancellation_requested"
            },
            status=200
        )

        result = mock_client.scans.cancel(mock_scan_id)

        assert result["status"] == "cancellation_requested"

    @responses.activate
    def test_get_results(self, mock_client, mock_scan_id, mock_scan_results):
        """Test getting scan results."""
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/results",
            json=mock_scan_results,
            status=200
        )

        results = mock_client.scans.get_results(mock_scan_id)

        assert results["scan_id"] == mock_scan_id
        assert results["security_score"] == 85.5
        assert results["total_prompts"] == 100


@pytest.mark.unit
@pytest.mark.scans
class TestQuotaManagement:
    """Test quota management."""

    @responses.activate
    def test_get_quota(self, mock_client, mock_quota_response):
        """Test getting quota information."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans/quota",
            json=mock_quota_response,
            status=200
        )

        quota = mock_client.scans.get_quota()

        assert quota.quota_status.total_scans_limit == 10
        assert quota.quota_status.free_scans_limit == 2
        assert quota.message == "Quota information retrieved successfully"
