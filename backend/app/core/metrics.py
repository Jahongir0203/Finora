"""Prometheus metrikalari (02-backend.md, 9-bo'lim: alertlar).

Xavfsizlik hodisalari alohida kod yozmasdan, mavjud log yozuvlaridan sanaladi: log nomi
oq ro'yxatda bo'lsa, `finora_security_events_total{event=...}` oshadi. Label'lar faqat shu
ro'yxatdan — foydalanuvchi ma'lumoti (telefon, IP) label'ga tushmaydi (kardinallik ham cheklangan).
Alert qoidalari: deploy/monitoring/alerts.yml.
"""

import logging

from prometheus_client import CollectorRegistry, Counter, Histogram

REGISTRY = CollectorRegistry(auto_describe=True)

SECURITY_EVENTS = frozenset({
    "otp_sent",
    "otp_invalid",
    "otp_blocked",
    "otp_ip_limit_exceeded",
    "otp_ip_many_numbers",
    "refresh_token_reuse",
    "receipt_malware_detected",
    "sms_auth_failed",
    "sms_transport_error",
    "sms_send_failed",
    "push_failed",
    "push_timeout",
    "unhandled_error",
    "export_failed",
    "ai_unavailable",
})

security_events = Counter(
    "finora_security_events", "Xavfsizlik va provayder hodisalari", ["event"], registry=REGISTRY
)
http_responses = Counter(
    "finora_http_responses", "HTTP javoblar status kodi bo'yicha", ["status"], registry=REGISTRY
)
# Latency (BE-004): route shabloni bo'yicha (label'da ID yo'q — kardinallik cheklangan)
http_latency = Histogram(
    "finora_http_request_duration_seconds", "So'rov davomiyligi", ["method", "route"],
    buckets=(0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0, 2.0, 4.0, 10.0), registry=REGISTRY,
)
rate_limited = Counter(
    "finora_rate_limited", "429 javoblar limit doirasi bo'yicha", ["scope"], registry=REGISTRY
)

for _event in SECURITY_EVENTS:  # nol qiymat bilan ko'rinsin — increase() alertlari to'g'ri ishlaydi
    security_events.labels(event=_event)


class SecurityEventCounter(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        name = record.msg if isinstance(record.msg, str) else ""
        if name in SECURITY_EVENTS:
            security_events.labels(event=name).inc()
