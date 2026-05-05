import logging
from .providers.airpeace_playwright import AirPeacePlaywrightProvider

logger = logging.getLogger(__name__)


class SearchOrchestrator:

    def __init__(self):
        self.providers = [
            AirPeacePlaywrightProvider(),  # ✅ correct provider
        ]

    def run(self, payload):
        results = []

        for provider in self.providers:
            try:
                provider_results = provider.search(payload)
                results.extend(provider_results)
            except Exception as e:
                logger.error(f"[SEARCH ERROR] {provider.name}: {e}")

        # Sort cheapest first
        results = sorted(
            results,
            key=lambda x: x.get("price") or 999999
        )

        return results