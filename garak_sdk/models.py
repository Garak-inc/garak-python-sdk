"""
Garak SDK Models

Pydantic models for requests and responses.
Subset of backend models needed for SDK functionality.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ScanStatus(str, Enum):
    """Scan status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ReportType(str, Enum):
    """Available report types."""

    JSON = "json"
    JSONL = "jsonl"
    HTML = "html"
    HITS = "hits"


class GeneratorType(str, Enum):
    """Available generator types."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    REST = "rest"
    LITELLM = "litellm"
    CUSTOM_AGENT = "custom-agent"


# Request Models


class CreateScanRequest(BaseModel):
    """Request to create a new scan."""

    name: Optional[str] = None
    description: Optional[str] = None
    generator: str
    model_name: str
    probe_categories: List[str] = Field(default_factory=list)
    probes: Optional[List[str]] = None
    parallel_attempts: int = 1
    api_keys: Dict[str, str] = Field(default_factory=dict)
    use_free_tier: bool = False

    # Generator-specific configs
    rest_config: Optional[Dict[str, Any]] = None
    ollama_host: Optional[str] = None
    litellm_config: Optional[Dict[str, Any]] = None

    # Custom agent configs
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    agent_system_prompt: Optional[str] = None
    agent_platform: Optional[str] = None


class UpdateScanRequest(BaseModel):
    """Request to update scan metadata."""

    name: Optional[str] = None
    description: Optional[str] = None


# Response Models


class ScanProgress(BaseModel):
    """Scan progress information (matches backend API format)."""

    completed_items: int = 0
    total_items: int = 0
    progress_percent: float = 0.0
    elapsed_time: Optional[str] = None
    estimated_remaining: Optional[str] = None
    estimated_completion: Optional[str] = None
    message: Optional[str] = None


class ScanMetadata(BaseModel):
    """Scan metadata information."""

    scan_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    status: ScanStatus
    generator: str
    model_name: str
    probe_categories: List[str] = Field(default_factory=list)
    probes: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: Optional[ScanProgress] = None
    failure_reason: Optional[str] = None
    user_email: Optional[str] = None
    use_free_tier: bool = False
    needs_subscription: bool = False


class ScanResults(BaseModel):
    """Scan results summary."""

    scan_id: str
    security_score: Optional[float] = None
    total_prompts: int = 0
    passed_prompts: int = 0
    failed_prompts: int = 0
    detector_summary: Dict[str, Any] = Field(default_factory=dict)
    probe_summary: Dict[str, Any] = Field(default_factory=dict)


class ReportInfo(BaseModel):
    """Information about an available report."""

    type: ReportType
    file_path: str
    file_size: Optional[int] = None
    available: bool = True


class ScanResponse(BaseModel):
    """Full scan response with metadata, results, and reports."""

    metadata: ScanMetadata
    results: Optional[ScanResults] = None
    reports: List[ReportInfo] = Field(default_factory=list)
    output_log: Optional[str] = None


class ScanListResponse(BaseModel):
    """Paginated list of scans."""

    scans: List[ScanMetadata]
    total: int
    page: int
    per_page: int
    has_next: bool


class ScanStatusResponse(BaseModel):
    """Scan status response."""

    scan_id: str
    status: ScanStatus
    progress: Optional[ScanProgress] = None
    failure: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    output: Optional[str] = None
    output_metadata: Optional[Dict[str, Any]] = None


class QuotaStatus(BaseModel):
    """User quota status."""

    total_scans_used: int = 0
    total_scans_limit: int = 10
    remaining_total_scans: int = 10
    free_scans_used: int = 0
    free_scans_limit: int = 2
    remaining_free_scans: int = 2
    can_use_free_tier: bool = True
    can_use_paid_tier: bool = True
    user_id: Optional[str] = None


class QuotaResponse(BaseModel):
    """Quota information response."""

    quota_status: QuotaStatus
    message: str


# Metadata Models


class GeneratorInfo(BaseModel):
    """Generator information."""

    name: str
    display_name: str
    description: str
    requires_api_key: bool
    api_key_env: Optional[str] = None
    supported_models: List[str] = Field(default_factory=list)


class ProbeInfo(BaseModel):
    """Individual probe information."""

    name: str
    display_name: str
    category: str
    description: str
    recommended_detectors: List[str] = Field(default_factory=list)


class ProbeCategory(BaseModel):
    """Probe category with probes."""

    name: str
    display_name: str
    description: str
    probes: List[ProbeInfo] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str
    services: Dict[str, str] = Field(default_factory=dict)


class APIInfo(BaseModel):
    """API information."""

    api_version: str
    service: str
    description: str
    documentation_url: str
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    supported_generators: List[str] = Field(default_factory=list)
    supported_probe_categories: List[str] = Field(default_factory=list)
