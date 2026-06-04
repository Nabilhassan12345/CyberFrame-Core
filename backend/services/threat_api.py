import hashlib
import time
from typing import Dict, Any

class ThreatIntelAPI:
    def __init__(self):
        # Mock Redis/Memcached cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.CACHE_TTL = 3600  # 1 hour

    def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """
        Check the IP reputation against a threat intelligence feed (mocked AbuseIPDB).
        Returns a dict containing the risk score (0-100) and threat category.
        """
        now = time.time()
        
        # Check cache
        if ip_address in self._cache:
            cached_data = self._cache[ip_address]
            if now - cached_data["timestamp"] < self.CACHE_TTL:
                return cached_data["data"]

        # Simulate API call latency and logic
        # In production, this would be: requests.get(f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip_address}")
        
        # Deterministic mock score based on IP hash
        hash_val = int(hashlib.md5(ip_address.encode()).hexdigest(), 16)
        score = hash_val % 100
        
        # Hardcoded malicious IPs for testing
        if ip_address in ["198.51.100.23", "203.0.113.42"]:
            score = 99
            
        category = "Clean"
        if score > 80:
            category = "Critical Threat"
        elif score > 50:
            category = "Suspicious"

        result = {
            "ip": ip_address,
            "risk_score": score,
            "category": category,
            "source": "AbuseIPDB (Mock)"
        }
        
        # Save to cache
        self._cache[ip_address] = {
            "timestamp": now,
            "data": result
        }
        
        return result

# Singleton instance
threat_api = ThreatIntelAPI()
