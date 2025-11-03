"""
Tests for report resource (garak_sdk.resources.reports).

Tests cover:
- Report listing
- Report download (single and batch)
- File handling
- URL generation
"""

import pytest
import responses
import os
import tempfile
from garak_sdk.models import ReportInfo, ReportType
from garak_sdk.exceptions import ScanNotFoundError


@pytest.mark.unit
@pytest.mark.reports
class TestReportListing:
    """Test report listing functionality."""

    @responses.activate
    def test_list_reports(self, mock_client, mock_scan_id):
        """Test listing available reports."""
        report_list = [
            {
                "type": "json",
                "file_path": f"/reports/{mock_scan_id}.report.json",
                "file_size": 1024,
                "available": True
            },
            {
                "type": "html",
                "file_path": f"/reports/{mock_scan_id}.report.html",
                "file_size": 2048,
                "available": True
            }
        ]

        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports",
            json={"scan_id": mock_scan_id, "reports": report_list},
            status=200
        )

        reports = mock_client.reports.list(mock_scan_id)

        assert len(reports) == 2
        assert all(isinstance(r, ReportInfo) for r in reports)
        assert reports[0].type == ReportType.JSON
        assert reports[1].type == ReportType.HTML


@pytest.mark.unit
@pytest.mark.reports
class TestReportDownload:
    """Test report download functionality."""

    @responses.activate
    def test_download_report(self, mock_client, mock_scan_id, tmp_path):
        """Test downloading a single report."""
        report_content = b'{"test": "data"}'

        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/json",
            body=report_content,
            status=200
        )

        output_path = str(tmp_path / "report.json")
        result_path = mock_client.reports.download(
            mock_scan_id,
            "json",
            output_path
        )

        assert result_path == output_path
        assert os.path.exists(output_path)

        with open(output_path, 'rb') as f:
            assert f.read() == report_content

    @responses.activate
    def test_download_report_not_found(self, mock_client, mock_scan_id, tmp_path):
        """Test downloading non-existent report."""
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/json",
            json={"error": "report_not_found"},
            status=404
        )

        output_path = str(tmp_path / "report.json")

        with pytest.raises(ScanNotFoundError):
            mock_client.reports.download(mock_scan_id, "json", output_path)

    @responses.activate
    def test_download_report_overwrite_protection(self, mock_client, mock_scan_id, tmp_path):
        """Test that existing files are not overwritten by default."""
        output_path = str(tmp_path / "report.json")

        # Create existing file
        with open(output_path, 'w') as f:
            f.write("existing content")

        with pytest.raises(FileExistsError):
            mock_client.reports.download(mock_scan_id, "json", output_path, overwrite=False)

    @responses.activate
    def test_download_report_with_overwrite(self, mock_client, mock_scan_id, tmp_path):
        """Test overwriting existing report file."""
        output_path = str(tmp_path / "report.json")
        new_content = b'{"new": "data"}'

        # Create existing file
        with open(output_path, 'w') as f:
            f.write("existing content")

        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/json",
            body=new_content,
            status=200
        )

        result_path = mock_client.reports.download(
            mock_scan_id,
            "json",
            output_path,
            overwrite=True
        )

        assert os.path.exists(output_path)
        with open(output_path, 'rb') as f:
            assert f.read() == new_content


@pytest.mark.unit
@pytest.mark.reports
class TestBatchDownload:
    """Test batch report download functionality."""

    @responses.activate
    def test_download_all_reports(self, mock_client, mock_scan_id, tmp_path):
        """Test downloading all available reports."""
        # Mock list reports
        report_list = [
            {"type": "json", "file_path": f"/{mock_scan_id}.json", "available": True},
            {"type": "html", "file_path": f"/{mock_scan_id}.html", "available": True}
        ]

        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports",
            json={"scan_id": mock_scan_id, "reports": report_list},
            status=200
        )

        # Mock download JSON
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/json",
            body=b'{"json": "data"}',
            status=200
        )

        # Mock download HTML
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/html",
            body=b'<html>test</html>',
            status=200
        )

        output_dir = str(tmp_path)
        downloaded = mock_client.reports.download_all(mock_scan_id, output_dir)

        assert len(downloaded) == 2
        assert all(os.path.exists(path) for path in downloaded)

    @responses.activate
    def test_download_all_with_filter(self, mock_client, mock_scan_id, tmp_path):
        """Test downloading specific report types."""
        # Mock list reports
        report_list = [
            {"type": "json", "file_path": f"/{mock_scan_id}.json", "available": True},
            {"type": "html", "file_path": f"/{mock_scan_id}.html", "available": True}
        ]

        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports",
            json={"scan_id": mock_scan_id, "reports": report_list},
            status=200
        )

        # Mock download JSON only
        responses.add(
            responses.GET,
            f"https://test.garaksecurity.com/api/v1/scans/{mock_scan_id}/reports/json",
            body=b'{"json": "data"}',
            status=200
        )

        output_dir = str(tmp_path)
        downloaded = mock_client.reports.download_all(
            mock_scan_id,
            output_dir,
            report_types=["json"]
        )

        assert len(downloaded) == 1
        assert downloaded[0].endswith(".json")


@pytest.mark.unit
@pytest.mark.reports
class TestURLGeneration:
    """Test report URL generation."""

    def test_get_report_url(self, mock_client, mock_scan_id):
        """Test generating download URL for report."""
        url = mock_client.reports.get_report_url(mock_scan_id, "json")

        assert mock_scan_id in url
        assert "reports/json" in url
        assert url.startswith("https://test.garaksecurity.com")
