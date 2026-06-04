import time
import random
import threading
import subprocess
import re
from datetime import datetime
from database import SessionLocal, ThreatLog
from services.threat_api import threat_api
from services.geoip_tracker import geoip_tracker
from core.firewall_engine import firewall
from services.alert_manager import alert_manager

class SecurityEngine:
    def __init__(self):
        self.is_running = False
        self.total_threats_blocked = 0
        self.known_connections = set()
        
    def _parse_lsof(self):
        """
        Runs lsof to get real active network connections on the Mac without needing sudo.
        """
        try:
            # lsof -i -n -P gets all network files, numeric IPs, numeric ports
            result = subprocess.run(['lsof', '-i', '-n', '-P'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            for line in lines:
                if "->" not in line:
                    continue
                
                # Extract remote IP and Port (IPv4 and IPv6)
                match_ipv4 = re.search(r'->([0-9\.]+):([0-9]+)', line)
                match_ipv6 = re.search(r'->\[([0-9a-f:]+)\]:([0-9]+)', line)
                
                ip = None
                port = None
                
                if match_ipv4:
                    ip = match_ipv4.group(1)
                    port = int(match_ipv4.group(2))
                elif match_ipv6:
                    ip = match_ipv6.group(1)
                    port = int(match_ipv6.group(2))
                    
                if ip and port:
                    conn_id = f"{ip}:{port}"
                    
                    # Only log new connections so we don't spam the database
                    if conn_id not in self.known_connections:
                        self.known_connections.add(conn_id)
                        
                        # 1. Threat Intel Check
                        intel = threat_api.check_ip_reputation(ip)
                        score = intel.get("risk_score", 0)
                        
                        # 2. GeoIP Check
                        geo = geoip_tracker.lookup(ip)
                        location = f"{geo['city']}, {geo['country']}"
                        
                        # 3. Determine Severity & Action
                        severity = "Low"
                        action = "Logged"
                        detection_type = f"Outbound Connection ({port})"
                        
                        if score > 90:
                            severity = "CRITICAL"
                            action = "Quarantined"
                            detection_type = f"Malicious IP ({intel['category']})"
                        elif score > 70 or port in [22, 23, 445, 135, 139]:
                            severity = "High"
                            action = "Blocked"
                            if port in [22, 23]: detection_type = "Suspicious SSH/Telnet"
                        elif score > 50 or port in [6667, 6668, 6669]:
                            severity = "Medium"
                            if port in [6667, 6668, 6669]: detection_type = "Potential IRC Botnet Comms"
                        else:
                            if random.random() > 0.05: continue # Ignore 95% of safe traffic
                        
                        # 4. Trigger Firewall
                        if action in ["Blocked", "Quarantined"]:
                            firewall.block_ip(ip)
                            
                        # 5. Trigger Alert
                        if severity == "CRITICAL":
                            alert_manager.trigger_critical_alert(ip, detection_type)
                            
                        self._log_threat(ip, f"{detection_type} [{location}]", severity, action)

        except Exception as e:
            print(f"Error parsing lsof: {e}")

    def _log_threat(self, ip, detection_type, severity, action):
        """Helper to save real threats to the SQLite DB"""
        db = SessionLocal()
        try:
            new_threat = ThreatLog(
                threat_id=f"TRT-{random.randint(9000, 9999)}",
                ip_address=ip,
                detection_type=detection_type,
                severity=severity,
                status=action,
                timestamp=datetime.utcnow()
            )
            db.add(new_threat)
            db.commit()
            if action in ["Blocked", "Quarantined"]:
                self.total_threats_blocked += 1
        except Exception as e:
            print(f"Error saving threat: {e}")
        finally:
            db.close()

    def _sniff_loop(self):
        """
        Runs the real network monitor in a background thread.
        Uses lsof to bypass macOS raw socket sudo requirements.
        """
        print("Starting REAL Network Connection Monitor (lsof)...")
        while self.is_running:
            self._parse_lsof()
            time.sleep(5)  # Scan every 5 seconds

    def start(self):
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._sniff_loop, daemon=True)
            thread.start()
            print("Security Engine (Active Connections Monitor) started.")

    def stop(self):
        self.is_running = False

security_engine = SecurityEngine()
