import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import sqlite3

class CacheManager:
    def __init__(self, cache_db_path: str = "cache.db"):
        self.cache_db_path = cache_db_path
        self._init_cache_db()
    
    def _init_cache_db(self):
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_cache (
                id INTEGER PRIMARY KEY,
                cache_key TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                endpoint TEXT,
                user_id INTEGER
            )
        """)
        conn.commit()
        conn.close()
    
    def get(self, endpoint: str, params: Dict[str, Any], user_id: Optional[int] = None):
        try:
            cache_key = hashlib.md5(json.dumps({"endpoint": endpoint, "params": params, "user_id": user_id}, sort_keys=True).encode()).hexdigest()
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM api_cache WHERE cache_key = ? AND expires_at > datetime(\"now\")", (cache_key,))
            result = cursor.fetchone()
            conn.close()
            return json.loads(result[0]) if result else None
        except Exception as e:
            return None
    
    def set(self, endpoint: str, params: Dict[str, Any], data: Dict[str, Any], ttl_seconds: int = 300, user_id: Optional[int] = None):
        try:
            cache_key = hashlib.md5(json.dumps({"endpoint": endpoint, "params": params, "user_id": user_id}, sort_keys=True).encode()).hexdigest()
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO api_cache (cache_key, data, expires_at, endpoint, user_id) VALUES (?, ?, ?, ?, ?)", (cache_key, json.dumps(data), expires_at, endpoint, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

cache_manager = CacheManager()

