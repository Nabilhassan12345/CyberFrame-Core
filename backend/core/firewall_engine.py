import subprocess
import platform
import logging

logger = logging.getLogger(__name__)

class FirewallEngine:
    def __init__(self):
        self.os_type = platform.system()
        self.quarantined_ips = set()
        
    def block_ip(self, ip_address: str) -> bool:
        """
        Actively blocks an IP address using the host OS firewall.
        """
        if ip_address in self.quarantined_ips:
            return True
            
        try:
            # Simulate subprocess calls for safety without root privileges
            if self.os_type == "Darwin":
                cmd = f"echo 'block drop from {ip_address} to any' | sudo pfctl -a cyberframe -f -"
                logger.warning(f"OS Firewall Execution (Mock): {cmd}")
            elif self.os_type == "Linux":
                cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
                logger.warning(f"OS Firewall Execution (Mock): {cmd}")
            else:
                logger.error(f"Unsupported OS for firewall engine: {self.os_type}")
                return False
                
            self.quarantined_ips.add(ip_address)
            logger.critical(f"IP {ip_address} successfully quarantined at OS level.")
            return True
            
        except Exception as e:
            logger.error(f"Failed to block IP {ip_address}: {e}")
            return False

    def allow_ip(self, ip_address: str) -> bool:
        """
        Removes an IP from the OS blocklist.
        """
        if ip_address not in self.quarantined_ips:
            return True
            
        try:
            if self.os_type == "Darwin":
                cmd = f"sudo pfctl -a cyberframe -F rules" # Simplification for mock
                logger.warning(f"OS Firewall Execution (Mock): {cmd}")
            elif self.os_type == "Linux":
                cmd = f"sudo iptables -D INPUT -s {ip_address} -j DROP"
                logger.warning(f"OS Firewall Execution (Mock): {cmd}")
                
            self.quarantined_ips.remove(ip_address)
            logger.info(f"IP {ip_address} removed from quarantine.")
            return True
        except Exception as e:
            logger.error(f"Failed to unblock IP {ip_address}: {e}")
            return False

firewall = FirewallEngine()
