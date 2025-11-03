"""
Metadata Resource

Handles discovery of generators, models, and probes.
"""

from typing import Any, Dict, List, cast

from ..models import APIInfo, GeneratorInfo, HealthResponse, ProbeCategory, ProbeInfo


class MetadataResource:
    """
    Metadata discovery operations.

    Provides methods for discovering available generators, models, probes,
    and API capabilities.
    """

    def __init__(self, client):
        """
        Initialize metadata resource.

        Args:
            client: GarakClient instance
        """
        self.client = client

    def list_generators(self) -> List[GeneratorInfo]:
        """
        List all available model generators.

        Returns:
            List of GeneratorInfo objects

        Example:
            generators = client.metadata.list_generators()
            for gen in generators:
                print(f"{gen.name}: {gen.description}")
        """
        response = self.client.get("/api/v1/generators")
        data = response.json()
        return [GeneratorInfo(**gen) for gen in data.get("generators", [])]

    def get_generator(self, generator_name: str) -> GeneratorInfo:
        """
        Get detailed information about a specific generator.

        Args:
            generator_name: Generator name (e.g., 'openai', 'anthropic')

        Returns:
            GeneratorInfo object

        Example:
            gen = client.metadata.get_generator("openai")
            print(f"Supported models: {gen.supported_models}")
        """
        response = self.client.get(f"/api/v1/generators/{generator_name}")
        return GeneratorInfo(**response.json())

    def list_models(self, generator: str) -> List[str]:
        """
        List available models for a specific generator.

        Args:
            generator: Generator name

        Returns:
            List of model names

        Example:
            models = client.metadata.list_models("openai")
            print(f"Available OpenAI models: {models}")
        """
        response = self.client.get(f"/api/v1/generators/{generator}/models")
        data = response.json()
        return cast(List[str], data.get("models", []))

    def list_probe_categories(self) -> List[ProbeCategory]:
        """
        List all available probe categories with their probes.

        Returns:
            List of ProbeCategory objects

        Example:
            categories = client.metadata.list_probe_categories()
            for cat in categories:
                print(f"{cat.name}: {len(cat.probes)} probes")
        """
        response = self.client.get("/api/v1/probes")
        data = response.json()
        return [ProbeCategory(**cat) for cat in data.get("categories", [])]

    def list_probes(self, category: str) -> List[ProbeInfo]:
        """
        List all probes in a specific category.

        Args:
            category: Category name

        Returns:
            List of ProbeInfo objects

        Example:
            probes = client.metadata.list_probes("jailbreak")
            for probe in probes:
                print(f"- {probe.name}")
        """
        response = self.client.get(f"/api/v1/probes/{category}")
        data = response.json()
        return [ProbeInfo(**probe) for probe in data.get("probes", [])]

    def health_check(self) -> HealthResponse:
        """
        Check API health status.

        Returns:
            HealthResponse object

        Example:
            health = client.metadata.health_check()
            print(f"API Status: {health.status}")
            print(f"Services: {health.services}")
        """
        response = self.client.get("/api/v1/health")
        return HealthResponse(**response.json())

    def get_api_info(self) -> APIInfo:
        """
        Get API information and capabilities.

        Returns:
            APIInfo object

        Example:
            info = client.metadata.get_api_info()
            print(f"API Version: {info.api_version}")
            print(f"Supported generators: {info.supported_generators}")
        """
        response = self.client.get("/api/v1/info")
        return APIInfo(**response.json())

    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata in a single call (generators, probes, API info).

        Returns:
            Dictionary with all metadata

        Example:
            metadata = client.metadata.get_all_metadata()
            print(f"Generators: {len(metadata['generators'])}")
            print(f"Probe categories: {len(metadata['probe_categories'])}")
        """
        generators = self.list_generators()
        probe_categories = self.list_probe_categories()
        api_info = self.get_api_info()

        return {
            "generators": [gen.model_dump() for gen in generators],
            "probe_categories": [cat.model_dump() for cat in probe_categories],
            "api_info": api_info.model_dump(),
        }
