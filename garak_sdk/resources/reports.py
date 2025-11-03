"""
Report Resource

Handles report download and management.
"""

import os
from typing import Dict, List, Optional, cast

from ..exceptions import ScanNotFoundError
from ..models import ReportInfo, ReportType


class ReportResource:
    """
    Report download and management operations.

    Provides methods for listing, downloading, and managing scan reports.
    """

    def __init__(self, client):
        """
        Initialize report resource.

        Args:
            client: GarakClient instance
        """
        self.client = client

    def list(self, scan_id: str) -> List[ReportInfo]:
        """
        List available reports for a scan.

        Args:
            scan_id: Scan ID

        Returns:
            List of ReportInfo objects

        Example:
            reports = client.reports.list("abc123")
            for report in reports:
                print(f"{report.type}: {report.file_size} bytes")
        """
        response = self.client.get(f"/api/v1/scans/{scan_id}/reports")
        data = response.json()
        return [ReportInfo(**report) for report in data.get("reports", [])]

    def download(
        self, scan_id: str, report_type: str, output_path: str, overwrite: bool = False
    ) -> str:
        """
        Download a specific report file.

        Args:
            scan_id: Scan ID
            report_type: Report type ('json', 'jsonl', 'html', 'hits')
            output_path: Path to save the report
            overwrite: Whether to overwrite existing file

        Returns:
            Path to downloaded file

        Raises:
            FileExistsError: If file exists and overwrite is False
            ScanNotFoundError: If scan or report not found

        Example:
            path = client.reports.download(
                "abc123",
                "json",
                "./reports/scan_abc123.json"
            )
            print(f"Downloaded to: {path}")
        """
        # Check if file exists
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(
                f"File already exists: {output_path}. Use overwrite=True to replace."
            )

        # Download report
        try:
            response = self.client.get(
                f"/api/v1/scans/{scan_id}/reports/{report_type}",
                headers={"Accept": "application/octet-stream"},
            )

            # Create directory if needed
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

            # Save file
            with open(output_path, "wb") as f:
                f.write(response.content)

            return output_path

        except Exception as e:
            if "404" in str(e):
                raise ScanNotFoundError(f"Report {report_type} not found for scan {scan_id}")
            raise

    def download_all(
        self,
        scan_id: str,
        output_dir: str,
        overwrite: bool = False,
        report_types: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Download all available reports for a scan.

        Args:
            scan_id: Scan ID
            output_dir: Directory to save reports
            overwrite: Whether to overwrite existing files
            report_types: Optional list of specific report types to download

        Returns:
            List of downloaded file paths

        Example:
            paths = client.reports.download_all("abc123", "./reports/")
            print(f"Downloaded {len(paths)} reports")
        """
        # Get available reports
        available_reports = self.list(scan_id)

        # Filter by requested types if specified
        if report_types:
            available_reports = [r for r in available_reports if r.type.value in report_types]

        # Download each report
        downloaded_paths = []
        for report in available_reports:
            if not report.available:
                continue

            output_path = os.path.join(output_dir, f"{scan_id}_report.{report.type.value}")

            try:
                path = self.download(scan_id, report.type.value, output_path, overwrite=overwrite)
                downloaded_paths.append(path)
            except Exception as e:
                # Log error but continue with other reports
                print(f"Warning: Failed to download {report.type.value} report: {e}")

        return downloaded_paths

    def get_report_url(self, scan_id: str, report_type: str) -> str:
        """
        Get download URL for a report.

        Args:
            scan_id: Scan ID
            report_type: Report type

        Returns:
            Download URL

        Example:
            url = client.reports.get_report_url("abc123", "json")
            print(f"Download from: {url}")
        """
        return cast(str, self.client._build_url(f"/api/v1/scans/{scan_id}/reports/{report_type}"))
