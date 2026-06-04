import requests
from typing import Dict, Any

class GeoIPTracker:
    def __init__(self):
        self.api_url = "http://ip-api.com/json"
        self._cache = {}

    def is_private_ip(self, ip: str) -> bool:
        """Check if an IP is in the private range to skip lookup"""
        parts = ip.split('.')
        if len(parts) != 4:
            return True
        
        try:
            first_octet = int(parts[0])
            second_octet = int(parts[1])
            
            if first_octet == 10:
                return True
            if first_octet == 172 and 16 <= second_octet <= 31:
                return True
            if first_octet == 192 and second_octet == 168:
                return True
            if ip == "127.0.0.1":
                return True
        except ValueError:
            return True
            
        return False

    def lookup(self, ip: str) -> Dict[str, Any]:
        """Fetch GeoIP data using ip-api"""
        if self.is_private_ip(ip):
            return {
                "country": "Local",
                "city": "Internal Network",
                "lat": 0.0,
                "lon": 0.0,
                "isp": "Local LAN"
            }
            
        if ip in self._cache:
            return self._cache[ip]

        try:
            response = requests.get(f"{self.api_url}/{ip}", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    result = {
                        "country": data.get("country", "Unknown"),
                        "city": data.get("city", "Unknown"),
                        "lat": data.get("lat", 0.0),
                        "lon": data.get("lon", 0.0),
                        "isp": data.get("isp", "Unknown")
                    }
                    self._cache[ip] = result
                    return result
        except Exception:
            pass

        return {
            "country": "Unknown",
            "city": "Unknown",
            "lat": 0.0,
            "lon": 0.0,
            "isp": "Unknown"
        }

# Singleton instance
geoip_tracker = GeoIPTracker()
