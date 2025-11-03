"""
Tests for Pydantic models (garak_sdk.models).

Tests cover:
- Model validation
- Enum values
- Required fields
- Optional fields
- Type coercion
"""

import pytest
from pydantic import ValidationError
from garak_sdk.models import (
    ScanStatus,
    ReportType,
    GeneratorType,
    CreateScanRequest,
    ScanMetadata,
    ScanProgress,
    ScanResults,
    QuotaStatus,
    GeneratorInfo,
    ProbeCategory,
    ProbeInfo
)


@pytest.mark.unit
@pytest.mark.models
class TestEnums:
    """Test enum definitions."""

    def test_scan_status_enum(self):
        """Test ScanStatus enum values."""
        assert ScanStatus.PENDING.value == "pending"
        assert ScanStatus.RUNNING.value == "running"
        assert ScanStatus.COMPLETED.value == "completed"
        assert ScanStatus.FAILED.value == "failed"
        assert ScanStatus.CANCELLED.value == "cancelled"

    def test_report_type_enum(self):
        """Test ReportType enum values."""
        assert ReportType.JSON.value == "json"
        assert ReportType.JSONL.value == "jsonl"
        assert ReportType.HTML.value == "html"
        assert ReportType.HITS.value == "hits"

    def test_generator_type_enum(self):
        """Test GeneratorType enum values."""
        assert GeneratorType.OPENAI.value == "openai"
        assert GeneratorType.ANTHROPIC.value == "anthropic"
        assert GeneratorType.HUGGINGFACE.value == "huggingface"


@pytest.mark.unit
@pytest.mark.models
class TestRequestModels:
    """Test request model validation."""

    def test_create_scan_request_minimal(self):
        """Test CreateScanRequest with minimal required fields."""
        request = CreateScanRequest(
            generator="openai",
            model_name="gpt-4"
        )

        assert request.generator == "openai"
        assert request.model_name == "gpt-4"
        assert request.probe_categories == []
        assert request.parallel_attempts == 1

    def test_create_scan_request_full(self):
        """Test CreateScanRequest with all fields."""
        request = CreateScanRequest(
            generator="openai",
            model_name="gpt-4",
            name="Test Scan",
            description="Test description",
            probe_categories=["jailbreak", "harmful"],
            probes=["probe1", "probe2"],
            parallel_attempts=2,
            api_keys={"OPENAI_API_KEY": "test"},
            use_free_tier=True
        )

        assert request.name == "Test Scan"
        assert len(request.probe_categories) == 2
        assert request.parallel_attempts == 2

    def test_create_scan_request_missing_required(self):
        """Test that CreateScanRequest fails without required fields."""
        with pytest.raises(ValidationError):
            CreateScanRequest(generator="openai")  # Missing model_name

        with pytest.raises(ValidationError):
            CreateScanRequest(model_name="gpt-4")  # Missing generator


@pytest.mark.unit
@pytest.mark.models
class TestResponseModels:
    """Test response model validation."""

    def test_scan_metadata_validation(self):
        """Test ScanMetadata validation."""
        metadata = ScanMetadata(
            scan_id="test-123",
            status=ScanStatus.COMPLETED,
            generator="openai",
            model_name="gpt-4",
            probe_categories=["jailbreak"],
            probes=["probe1"],
            created_at="2024-01-01T00:00:00Z"
        )

        assert metadata.scan_id == "test-123"
        assert metadata.status == ScanStatus.COMPLETED

    def test_scan_progress_validation(self):
        """Test ScanProgress validation."""
        progress = ScanProgress(
            completed_items=50,
            total_items=100,
            progress_percent=50.0,
            message="In progress"
        )

        assert progress.completed_items == 50
        assert progress.progress_percent == 50.0

    def test_scan_results_validation(self):
        """Test ScanResults validation."""
        results = ScanResults(
            scan_id="test-123",
            security_score=85.5,
            total_prompts=100,
            passed_prompts=85,
            failed_prompts=15
        )

        assert results.security_score == 85.5
        assert results.total_prompts == 100

    def test_quota_status_validation(self):
        """Test QuotaStatus validation."""
        quota = QuotaStatus(
            total_scans_used=5,
            total_scans_limit=10,
            remaining_total_scans=5,
            free_scans_used=2,
            free_scans_limit=2,
            remaining_free_scans=0
        )

        assert quota.total_scans_limit == 10
        assert quota.remaining_free_scans == 0


@pytest.mark.unit
@pytest.mark.models
class TestMetadataModels:
    """Test metadata model validation."""

    def test_generator_info_validation(self):
        """Test GeneratorInfo validation."""
        generator = GeneratorInfo(
            name="openai",
            display_name="OpenAI",
            description="OpenAI GPT models",
            requires_api_key=True,
            api_key_env="OPENAI_API_KEY",
            supported_models=["gpt-3.5-turbo", "gpt-4"]
        )

        assert generator.name == "openai"
        assert generator.requires_api_key is True
        assert len(generator.supported_models) == 2

    def test_probe_info_validation(self):
        """Test ProbeInfo validation."""
        probe = ProbeInfo(
            name="probe1",
            display_name="Probe 1",
            category="jailbreak",
            description="Test probe",
            recommended_detectors=["detector1"]
        )

        assert probe.name == "probe1"
        assert probe.category == "jailbreak"

    def test_probe_category_validation(self):
        """Test ProbeCategory validation."""
        probe_info = ProbeInfo(
            name="probe1",
            display_name="Probe 1",
            category="jailbreak",
            description="Test",
            recommended_detectors=[]
        )

        category = ProbeCategory(
            name="jailbreak",
            display_name="Jailbreak",
            description="Jailbreak tests",
            probes=[probe_info]
        )

        assert category.name == "jailbreak"
        assert len(category.probes) == 1


@pytest.mark.unit
@pytest.mark.models
class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_model_dump(self):
        """Test model_dump() method."""
        progress = ScanProgress(
            completed_items=50,
            total_items=100,
            progress_percent=50.0
        )

        data = progress.model_dump()

        assert isinstance(data, dict)
        assert data["completed_items"] == 50
        assert data["total_items"] == 100

    def test_model_dump_exclude_none(self):
        """Test model_dump() with exclude_none."""
        metadata = ScanMetadata(
            scan_id="test-123",
            status=ScanStatus.PENDING,
            generator="openai",
            model_name="gpt-4",
            probe_categories=[],
            probes=[],
            created_at="2024-01-01T00:00:00Z"
        )

        data = metadata.model_dump(exclude_none=True)

        assert "scan_id" in data
        assert "started_at" not in data  # Should be excluded (None)

    def test_model_json_serialization(self):
        """Test JSON serialization."""
        progress = ScanProgress(
            completed_items=50,
            total_items=100,
            progress_percent=50.0
        )

        json_str = progress.model_dump_json()

        assert isinstance(json_str, str)
        assert "50" in json_str


@pytest.mark.unit
@pytest.mark.models
class TestModelDefaults:
    """Test model default values."""

    def test_scan_progress_defaults(self):
        """Test ScanProgress default values."""
        progress = ScanProgress()

        assert progress.completed_items == 0
        assert progress.total_items == 0
        assert progress.progress_percent == 0.0
        assert progress.message is None

    def test_scan_results_defaults(self):
        """Test ScanResults default values."""
        results = ScanResults(scan_id="test-123")

        assert results.security_score is None
        assert results.total_prompts == 0
        assert results.passed_prompts == 0

    def test_create_scan_request_defaults(self):
        """Test CreateScanRequest default values."""
        request = CreateScanRequest(
            generator="openai",
            model_name="gpt-4"
        )

        assert request.name is None
        assert request.parallel_attempts == 1
        assert request.use_free_tier is False
        assert request.api_keys == {}
