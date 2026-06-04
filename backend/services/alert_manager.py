import requests
import smtplib
from email.mime.text import MIMEText
import logging
import os

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self):
        self.webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "")
        self.smtp_host = os.environ.get("SMTP_HOST", "localhost")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "1025")) # Mailhog default
        self.admin_email = os.environ.get("ADMIN_EMAIL", "admin@cyberframe.local")

    def send_webhook(self, message: str, severity: str = "INFO"):
        """Dispatches an alert to Slack/Discord."""
        if not self.webhook_url:
            logger.info(f"Webhook (Mock) [{severity}]: {message}")
            return
            
        payload = {
            "text": f"[{severity}] {message}"
        }
        try:
            requests.post(self.webhook_url, json=payload, timeout=2)
        except Exception as e:
            logger.error(f"Failed to dispatch webhook: {e}")

    def send_email(self, subject: str, body: str):
        """Dispatches an email via SMTP."""
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = "alerts@cyberframe.local"
        msg['To'] = self.admin_email
        
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.send_message(msg)
                logger.info("Alert email dispatched successfully.")
        except Exception as e:
            logger.warning(f"Email Dispatch (Mock): To: {self.admin_email} | Subject: {subject}")

    def trigger_critical_alert(self, ip_address: str, reason: str):
        """High-level orchestrator for CRITICAL events."""
        msg = f"CRITICAL THREAT: IP {ip_address} has been flagged for: {reason}. Auto-quarantine initiated."
        self.send_webhook(msg, severity="CRITICAL")
        self.send_email(f"CyberFrame Alert - {ip_address}", msg)

alert_manager = AlertManager()
