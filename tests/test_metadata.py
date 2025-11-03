"""
Tests for metadata resource (garak_sdk.resources.metadata).

Tests cover:
- Generator discovery
- Model listing
- Probe category discovery
- Health checks
- API info retrieval
"""

import pytest
import responses
from garak_sdk.models import GeneratorInfo, ProbeCategory, HealthResponse, APIInfo


@pytest.mark.unit
@pytest.mark.metadata
class TestGeneratorDiscovery:
    """Test generator discovery functionality."""

    @responses.activate
    def test_list_generators(self, mock_client, mock_generators):
        """Test listing all generators."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/generators",
            json={"generators": mock_generators, "total": len(mock_generators)},
            status=200
        )

        generators = mock_client.metadata.list_generators()

        assert len(generators) == 2
        assert all(isinstance(g, GeneratorInfo) for g in generators)
        assert generators[0].name == "openai"
        assert generators[1].name == "anthropic"

    @responses.activate
    def test_get_generator(self, mock_client, mock_generators):
        """Test getting specific generator details."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/generators/openai",
            json=mock_generators[0],
            status=200
        )

        generator = mock_client.metadata.get_generator("openai")

        assert isinstance(generator, GeneratorInfo)
        assert generator.name == "openai"
        assert generator.requires_api_key is True
        assert len(generator.supported_models) > 0

    @responses.activate
    def test_list_models(self, mock_client):
        """Test listing models for a generator."""
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/generators/openai/models",
            json={"generator": "openai", "models": models, "total": len(models)},
            status=200
        )

        result = mock_client.metadata.list_models("openai")

        assert result == models
        assert len(result) == 3


@pytest.mark.unit
@pytest.mark.metadata
class TestProbeDiscovery:
    """Test probe discovery functionality."""

    @responses.activate
    def test_list_probe_categories(self, mock_client, mock_probe_categories):
        """Test listing all probe categories."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/probes",
            json={
                "categories": mock_probe_categories,
                "total_categories": len(mock_probe_categories),
                "total_probes": 2
            },
            status=200
        )

        categories = mock_client.metadata.list_probe_categories()

        assert len(categories) == 2
        assert all(isinstance(c, ProbeCategory) for c in categories)
        assert categories[0].name == "jailbreak"
        assert categories[1].name == "harmful"

    @responses.activate
    def test_list_probes(self, mock_client):
        """Test listing probes in a category."""
        probes = [
            {
                "name": "probe1",
                "display_name": "Probe 1",
                "category": "jailbreak",
                "description": "Test probe",
                "recommended_detectors": []
            }
        ]

        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/probes/jailbreak",
            json={"category": "jailbreak", "probes": probes, "total": 1},
            status=200
        )

        result = mock_client.metadata.list_probes("jailbreak")

        assert len(result) == 1
        assert result[0].name == "probe1"
        assert result[0].category == "jailbreak"


@pytest.mark.unit
@pytest.mark.metadata
class TestHealthAndInfo:
    """Test health check and API info."""

    @responses.activate
    def test_health_check(self, mock_client, mock_health_response):
        """Test health check."""
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/health",
            json=mock_health_response,
            status=200
        )

        health = mock_client.metadata.health_check()

        assert isinstance(health, HealthResponse)
        assert health.status == "healthy"
        assert "redis" in health.services

    @responses.activate
    def test_get_api_info(self, mock_client):
        """Test getting API info."""
        api_info = {
            "api_version": "v1",
            "service": "Garak LLM Security Scanner",
            "description": "Public API for running AI red-teaming security scans",
            "documentation_url": "/api/docs",
            "capabilities": {},
            "supported_generators": ["openai", "anthropic"],
            "supported_probe_categories": ["jailbreak", "harmful"]
        }

        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/info",
            json=api_info,
            status=200
        )

        info = mock_client.metadata.get_api_info()

        assert isinstance(info, APIInfo)
        assert info.api_version == "v1"
        assert len(info.supported_generators) == 2

    @responses.activate
    def test_get_all_metadata(self, mock_client, mock_generators, mock_probe_categories):
        """Test getting all metadata in one call."""
        # Mock generators
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/generators",
            json={"generators": mock_generators},
            status=200
        )

        # Mock probe categories
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/probes",
            json={"categories": mock_probe_categories},
            status=200
        )

        # Mock API info
        responses.add(
            responses.GET,
            "https://test.garaksecurity.com/api/v1/info",
            json={
                "api_version": "v1",
                "service": "Test",
                "description": "Test",
                "documentation_url": "/docs",
                "capabilities": {},
                "supported_generators": [],
                "supported_probe_categories": []
            },
            status=200
        )

        metadata = mock_client.metadata.get_all_metadata()

        assert "generators" in metadata
        assert "probe_categories" in metadata
        assert "api_info" in metadata
        assert len(metadata["generators"]) == 2
        assert len(metadata["probe_categories"]) == 2
