"""
API Key Manager - Handles automatic rotation of API keys when rate limits are hit
"""
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages multiple API keys with automatic rotation on rate limit"""
    
    def __init__(self):
        # Load all API keys
        self.api_keys = []
        for i in range(1, 10):  # Support up to 9 keys
            key = os.getenv(f"GROQ_API_KEY_{i}")
            if key:
                self.api_keys.append(key)
        
        if not self.api_keys:
            # Fallback to single key
            single_key = os.getenv("GROQ_API_KEY")
            if single_key:
                self.api_keys.append(single_key)
        
        self.current_index = 0
        logger.info(f"✅ Loaded {len(self.api_keys)} API key(s) for rotation")
    
    def get_current_key(self):
        """Get the current API key"""
        if not self.api_keys:
            raise ValueError("No API keys configured!")
        return self.api_keys[self.current_index]
    
    def rotate_to_next(self):
        """Rotate to the next API key in circular fashion"""
        if len(self.api_keys) <= 1:
            logger.warning("⚠️ Only 1 API key available, cannot rotate")
            return self.api_keys[0] if self.api_keys else None
        
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        logger.info(f"🔄 Rotating API key: Key #{old_index + 1} → Key #{self.current_index + 1}")
        return self.api_keys[self.current_index]
    
    def get_key_number(self):
        """Get current key number (1-indexed)"""
        return self.current_index + 1
    
    def get_total_keys(self):
        """Get total number of keys"""
        return len(self.api_keys)


# Global instance
_api_key_manager = None

def get_api_key_manager():
    """Get or create the global API key manager"""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager
