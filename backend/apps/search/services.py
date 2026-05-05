import hashlib
import json
import logging
from django.core.cache import cache
from .orchestrator import SearchOrchestrator

logger = logging.getLogger(__name__)

class SearchService:

    @staticmethod
    def search(payload):
        # 1. Generate Cache Key
        key_parts = [
            payload["origin"],
            payload["destination"],
            str(payload["date"]),
            str(payload.get("adults", 1))
        ]
        key_string = ":".join(key_parts).upper()
        cache_key = f"flights_cache:{hashlib.md5(key_string.encode()).hexdigest()}"

        # 2. Try Cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return json.loads(cached_data)

        # 3. Fetch Fresh Data
        orchestrator = SearchOrchestrator()
        results = orchestrator.run(payload)

        # 4. Save to Cache (10 minutes)
        if results:
            cache.set(cache_key, json.dumps(results), 600)

        return results