"""
Cache Manager
Caches LLM responses to reduce API calls and improve performance
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
import config


class CacheManager:
    """Manages caching of LLM responses"""

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory for cache files (optional)
        """
        self.cache_dir = cache_dir or os.path.join(config.DATA_DIR, 'llm_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

        self.cache_file = os.path.join(self.cache_dir, 'response_cache.json')
        self.cache: Dict = {}
        self.max_size = config.CACHE_SIZE_LIMIT
        self.expiry_seconds = config.CACHE_EXPIRY_SECONDS

        # Load existing cache
        self._load_cache()

        # Statistics
        self.hits = 0
        self.misses = 0

    def _load_cache(self):
        """Load cache from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)

                # Remove expired entries
                self._clean_expired()
            except Exception as e:
                print(f"Warning: Could not load cache: {e}")
                self.cache = {}

    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")

    def _generate_key(self, prompt: str, context: Dict = None) -> str:
        """Generate cache key from prompt and context"""
        # Create hashable string
        key_str = prompt
        if context:
            key_str += json.dumps(context, sort_keys=True)

        # Generate hash
        return hashlib.md5(key_str.encode()).hexdigest()

    def _clean_expired(self):
        """Remove expired cache entries"""
        now = datetime.now().timestamp()
        expired_keys = []

        for key, entry in self.cache.items():
            if now - entry['timestamp'] > self.expiry_seconds:
                expired_keys.append(key)

        for key in expired_keys:
            del self.cache[key]

    def get(self, prompt: str, context: Dict = None) -> Optional[str]:
        """
        Get cached response

        Args:
            prompt: The prompt to look up
            context: Optional context dictionary

        Returns:
            Cached response or None if not found
        """
        if not config.ENABLE_LLM_CACHE:
            return None

        key = self._generate_key(prompt, context)

        if key in self.cache:
            entry = self.cache[key]

            # Check expiry
            now = datetime.now().timestamp()
            if now - entry['timestamp'] <= self.expiry_seconds:
                self.hits += 1
                return entry['response']
            else:
                # Expired
                del self.cache[key]

        self.misses += 1
        return None

    def set(self, prompt: str, response: str, context: Dict = None):
        """
        Cache a response

        Args:
            prompt: The prompt
            response: The response to cache
            context: Optional context dictionary
        """
        if not config.ENABLE_LLM_CACHE:
            return

        key = self._generate_key(prompt, context)

        self.cache[key] = {
            'prompt': prompt,
            'response': response,
            'timestamp': datetime.now().timestamp(),
            'context': context
        }

        # Trim cache if too large
        if len(self.cache) > self.max_size:
            self._trim_cache()

        # Save to disk periodically
        if len(self.cache) % 10 == 0:
            self._save_cache()

    def _trim_cache(self):
        """Remove oldest entries when cache is too large"""
        # Sort by timestamp
        sorted_entries = sorted(
            self.cache.items(),
            key=lambda x: x[1]['timestamp']
        )

        # Keep only most recent entries
        keep_count = int(self.max_size * 0.8)
        self.cache = dict(sorted_entries[-keep_count:])

    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self._save_cache()

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }

    def __del__(self):
        """Save cache on destruction"""
        self._save_cache()