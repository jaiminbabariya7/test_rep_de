"""
Multi-channel alert routing for data quality anomalies.

Supports Slack webhooks, SMTP email, and BigQuery audit log.
"""
from __future__ import annotations
import json, logging, os, smtplib
from email.mime.text import MIMEText
from datetime import datetime, timezone
from .anomaly_detector import AnomalyReport

logger = logging.getLogger(__name__)

SLACK_WEBHOOK  = os.getenv("SLACK_WEBHOOK_URL", "")
ALERT_EMAIL    = os.getenv("ALERT_EMAIL_TO", "")
SMTP_HOST      = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT      = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER      = os.getenv("SMTP_USER", "")
SMTP_PASSWORD  = os.getenv("SMTP_PASSWORD", "")


class AlertManager:
    """Route data quality alerts to configured channels."""

    def __init__(self, bq_connector=None) -> None:
        self.bq = bq_connector

    def send_all(self, report: AnomalyReport, explanation: str) -> dict[str, bool]:
        """Send alert to all configured channels.

        Args:
            report: AnomalyReport with anomaly details.
            explanation: LLM-generated explanation string.

        Returns:
            Dict mapping channel name to success boolean.
        """
        results: dict[str, bool] = {}
        if SLACK_WEBHOOK:
            results["slack"] = self._send_slack(report, explanation)
        if ALERT_EMAIL:
            results["email"] = self._send_email(report, explanation)
        if self.bq:
            results["bigquery"] = self._write_audit_log(report, explanation)
        return results

    def _send_slack(self, report: AnomalyReport, explanation: str) -> bool:
        import urllib.request
        emoji = ":red_circle:" if report.critical_count else ":large_yellow_circle:"
        payload = {
            "text": f"{emoji} *Data Quality Alert — {report.dataset}.{report.table}*",
            "blocks": [
                {"type": "header", "text": {"type": "plain_text",
                    "text": f"{emoji} DQ Alert: {report.dataset}.{report.table}"}},
                {"type": "section", "text": {"type": "mrkdwn",
                    "text": f"*Run ID:* {report.run_id}
*Anomalies:* {len(report.anomalies)} "
                            f"({report.critical_count} critical)"}},
                {"type": "section", "text": {"type": "mrkdwn",
                    "text": explanation[:2900]}},
            ],
        }
        try:
            req = urllib.request.Request(SLACK_WEBHOOK,
                data=json.dumps(payload).encode(), method="POST",
                headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10)
            logger.info("Slack alert sent for %s.%s", report.dataset, report.table)
            return True
        except Exception as e:
            logger.error("Slack alert failed: %s", e)
            return False

    def _send_email(self, report: AnomalyReport, explanation: str) -> bool:
        subject = (f"[DQ Alert] {report.dataset}.{report.table} — "
                   f"{len(report.anomalies)} anomalies detected")
        body = f"Run ID: {report.run_id}

{explanation}"
        msg = MIMEText(body)
        msg["Subject"], msg["From"], msg["To"] = subject, SMTP_USER, ALERT_EMAIL
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASSWORD)
                s.sendmail(SMTP_USER, [ALERT_EMAIL], msg.as_string())
            logger.info("Email alert sent to %s", ALERT_EMAIL)
            return True
        except Exception as e:
            logger.error("Email alert failed: %s", e)
            return False

    def _write_audit_log(self, report: AnomalyReport, explanation: str) -> bool:
        record = {
            "run_id": report.run_id,
            "dataset": report.dataset,
            "table": report.table,
            "anomaly_count": len(report.anomalies),
            "critical_count": report.critical_count,
            "anomaly_details": json.dumps([{"type":a.anomaly_type,"col":a.column,
                "desc":a.description,"severity":a.severity} for a in report.anomalies]),
            "llm_explanation": explanation,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            self.bq.write_audit_log(report.dataset, [record])
            return True
        except Exception as e:
            logger.error("BigQuery audit log write failed: %s", e)
            return False
