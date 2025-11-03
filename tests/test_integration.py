"""
Integration tests for Garak SDK.

These tests require a running backend API (or mocked complete workflows).
Use pytest markers to skip when backend is not available.

Run with: pytest -m integration
Skip with: pytest -m "not integration"
"""

import pytest
import os
import responses
from garak_sdk import GarakClient
from garak_sdk.models import ScanStatus


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndScanFlow:
    """Test complete end-to-end scan workflows."""

    @responses.activate
    def test_create_and_monitor_scan(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test creating a scan and monitoring it to completion."""
        # Step 1: Create scan
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": mock_scan_id,
                "metadata": {**mock_scan_metadata, "status": "pending"}
            },
            status=201
        )

        # Step 2: Check status - running
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

        # Step 3: Check status - completed
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

        # Step 4: Get full scan details
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

        # Step 5: Get results
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/results",
            json={
                "scan_id": mock_scan_id,
                "security_score": 85.0,
                "total_prompts": 100,
                "passed_prompts": 85,
                "failed_prompts": 15
            },
            status=200
        )

        # Execute workflow
        scan = mock_client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak"]
        )

        assert scan.metadata.scan_id == mock_scan_id

        # Wait for completion
        final_scan = mock_client.scans.wait_for_completion(
            scan.metadata.scan_id,
            timeout=30,
            poll_interval=1
        )

        assert final_scan.metadata.status == ScanStatus.COMPLETED

        # Get results
        results = mock_client.scans.get_results(scan.metadata.scan_id)

        assert results["security_score"] == 85.0
        assert results["total_prompts"] == 100

    @responses.activate
    def test_create_update_cancel_scan(self, mock_client, mock_scan_id, mock_scan_metadata):
        """Test creating, updating, and canceling a scan."""
        # Create scan
        responses.add(
            responses.POST,
            "https://test.garaksecurity.com/api/v1/scans",
            json={
                "scan_id": mock_scan_id,
                "metadata": {**mock_scan_metadata, "status": "pending"}
            },
            status=201
        )

        # Update scan
        responses.add(
            responses.PATCH,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "metadata": {**mock_scan_metadata, "name": "Updated Name"}
            },
            status=200
        )

        # Cancel scan
        responses.add(
            responses.DELETE,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}",
            json={
                "message": "Cancellation requested",
                "status": "cancellation_requested"
            },
            status=200
        )

        # Execute workflow
        scan = mock_client.scans.create(
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak"]
        )

        updated = mock_client.scans.update(scan.metadata.scan_id, name="Updated Name")
        assert updated.metadata.name == "Updated Name"

        result = mock_client.scans.cancel(scan.metadata.scan_id)
        assert result["status"] == "cancellation_requested"


@pytest.mark.integration
class TestMetadataDiscovery:
    """Test metadata discovery workflows."""

    @responses.activate
    def test_discover_generators_and_models(self, mock_client, mock_generators):
        """Test discovering generators and their models."""
        # List generators
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/generators",
            json={"generators": mock_generators},
            status=200
        )

        # Get OpenAI models
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/generators/openai/models",
            json={
                "models": ["gpt-3.5-turbo", "gpt-4"]
            },
            status=200
        )

        # Execute workflow
        generators = mock_client.metadata.list_generators()
        assert len(generators) > 0

        openai_models = mock_client.metadata.list_models("openai")
        assert "gpt-4" in openai_models

    @responses.activate
    def test_discover_probes(self, mock_client, mock_probe_categories):
        """Test discovering probe categories and probes."""
        # List categories
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/probes",
            json={"categories": mock_probe_categories},
            status=200
        )

        # List probes in category
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/probes/jailbreak",
            json={
                "category": "jailbreak",
                "probes": [
                    {
                        "name": "probe1",
                        "display_name": "Probe 1",
                        "category": "jailbreak",
                        "description": "Test",
                        "recommended_detectors": []
                    }
                ]
            },
            status=200
        )

        # Execute workflow
        categories = mock_client.metadata.list_probe_categories()
        assert len(categories) > 0

        jailbreak_probes = mock_client.metadata.list_probes("jailbreak")
        assert len(jailbreak_probes) > 0


@pytest.mark.integration
class TestReportWorkflow:
    """Test report download workflows."""

    @responses.activate
    def test_list_and_download_reports(self, mock_client, mock_scan_id, tmp_path):
        """Test listing and downloading all reports."""
        # List reports
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports",
            json={
                "scan_id": mock_scan_id,
                "reports": [
                    {"type": "json", "file_path": "/report.json", "available": True},
                    {"type": "html", "file_path": "/report.html", "available": True}
                ]
            },
            status=200
        )

        # Download JSON
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/json",
            body=b'{"test": "data"}',
            status=200
        )

        # Download HTML
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/html",
            body=b'<html>test</html>',
            status=200
        )

        # Execute workflow
        reports = mock_client.reports.list(mock_scan_id)
        assert len(reports) == 2

        downloaded = mock_client.reports.download_all(mock_scan_id, str(tmp_path))
        assert len(downloaded) == 2


@pytest.mark.integration
class TestQuotaWorkflow:
    """Test quota management workflows."""

    @responses.activate
    def test_check_quota_before_scan(self, mock_client, mock_quota_response):
        """Test checking quota before creating scan."""
        # Check quota
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans/quota",
            json=mock_quota_response,
            status=200
        )

        quota = mock_client.scans.get_quota()

        assert quota.quota_status.total_scans_limit > 0
        can_create_scan = quota.quota_status.remaining_total_scans > 0
        assert isinstance(can_create_scan, bool)


@pytest.mark.integration
class TestErrorScenarios:
    """Test error handling in complete workflows."""

    @responses.activate
    def test_authentication_failure_workflow(self, mock_base_url):
        """Test workflow with authentication failure."""
        responses.add(
            responses.POST,
            f"{mock_base_url}/api/v1/scans",
            json={"error": "unauthorized"},
            status=401
        )

        from garak_sdk.exceptions import AuthenticationError

        client = GarakClient(
            base_url=mock_base_url,
            api_key="garak_invalid_key_test1234567890abcdefghijklmnop"
        )

        with pytest.raises(AuthenticationError):
            client.scans.create(
                generator="openai",
                model_name="gpt-4",
                probe_categories=["jailbreak"]
            )

    @responses.activate
    def test_scan_not_found_workflow(self, mock_client):
        """Test workflow when scan is not found."""
        from garak_sdk.exceptions import ScanNotFoundError

        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/scans/nonexistent",
            json={"error": "scan_not_found"},
            status=404
        )

        with pytest.raises(ScanNotFoundError):
            mock_client.scans.get("nonexistent")


@pytest.mark.integration
class TestClientContextManager:
    """Test client as context manager in workflows."""

    @responses.activate
    def test_context_manager_workflow(self, mock_api_key, mock_base_url, mock_health_response):
        """Test using client as context manager."""
        responses.add(
            responses.GET,
            f"{mock_base_url}/api/v1/health",
            json=mock_health_response,
            status=200
        )

        with GarakClient(base_url=mock_base_url, api_key=mock_api_key) as client:
            health = client.health_check()
            assert health["status"] == "healthy"

        # Client should be closed after context


@pytest.mark.integration
@pytest.mark.slow
class TestMultipleConcurrentScans:
    """Test creating multiple scans concurrently."""

    @responses.activate
    def test_create_multiple_scans(self, mock_client, mock_scan_metadata):
        """Test creating multiple scans in sequence."""
        # Mock 3 scan creations
        for i in range(3):
            responses.add(
                responses.POST,
                "https://test.garaksecurity.com/api/v1/scans",
                json={
                    "scan_id": f"test-scan-{i}",
                    "metadata": {**mock_scan_metadata, "scan_id": f"test-scan-{i}"}
                },
                status=201
            )

        # Create multiple scans
        scans = []
        for i in range(3):
            scan = mock_client.scans.create(
                generator="openai",
                model_name="gpt-4",
                probe_categories=["jailbreak"]
            )
            scans.append(scan)

        assert len(scans) == 3
        assert all(s.metadata.scan_id.startswith("test-scan-") for s in scans)
