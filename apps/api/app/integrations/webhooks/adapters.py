from dataclasses import dataclass
from typing import Any

from app.models.entities import ConnectorType, SeverityEnum


@dataclass
class NormalizedAlert:
    title: str
    description: str
    severity: SeverityEnum
    environment: str
    service: str
    external_alert_id: str
    tags: list[str]
    raw_payload: dict[str, Any]


def map_severity(value: str | None) -> SeverityEnum:
    lowered = (value or "").lower()
    if lowered in {"critical", "sev1", "p1"}:
        return SeverityEnum.SEV1
    if lowered in {"high", "sev2", "p2"}:
        return SeverityEnum.SEV2
    if lowered in {"medium", "sev3", "warning", "p3"}:
        return SeverityEnum.SEV3
    return SeverityEnum.SEV4


def normalize_generic(payload: dict[str, Any]) -> NormalizedAlert:
    return NormalizedAlert(
        title=payload.get("title") or payload.get("alert") or "Generic Alert",
        description=payload.get("description") or payload.get("message") or "",
        severity=map_severity(payload.get("severity")),
        environment=payload.get("environment") or payload.get("env") or "unknown",
        service=payload.get("service") or "unknown",
        external_alert_id=str(payload.get("id") or payload.get("alert_id") or ""),
        tags=payload.get("tags") if isinstance(payload.get("tags"), list) else [],
        raw_payload=payload,
    )


def normalize_datadog(payload: dict[str, Any]) -> NormalizedAlert:
    body = payload.get("body") if isinstance(payload.get("body"), dict) else payload
    return NormalizedAlert(
        title=body.get("title") or body.get("alert_title") or "Datadog Alert",
        description=body.get("alert_transition") or body.get("text") or "",
        severity=map_severity(body.get("priority") or body.get("severity")),
        environment=(body.get("tags", {}).get("env") if isinstance(body.get("tags"), dict) else "unknown"),
        service=(body.get("tags", {}).get("service") if isinstance(body.get("tags"), dict) else "unknown"),
        external_alert_id=str(body.get("id") or body.get("alert_id") or ""),
        tags=body.get("tags") if isinstance(body.get("tags"), list) else [],
        raw_payload=payload,
    )


def normalize_prometheus(payload: dict[str, Any]) -> NormalizedAlert:
    alerts = payload.get("alerts") or []
    first = alerts[0] if alerts else {}
    labels = first.get("labels", {})
    annotations = first.get("annotations", {})
    return NormalizedAlert(
        title=labels.get("alertname", "Prometheus Alert"),
        description=annotations.get("description") or annotations.get("summary") or "",
        severity=map_severity(labels.get("severity")),
        environment=labels.get("environment") or labels.get("env") or "unknown",
        service=labels.get("service") or "unknown",
        external_alert_id=str(first.get("fingerprint") or ""),
        tags=[f"{k}:{v}" for k, v in labels.items()],
        raw_payload=payload,
    )


def normalize_grafana(payload: dict[str, Any]) -> NormalizedAlert:
    return NormalizedAlert(
        title=payload.get("title") or payload.get("message") or "Grafana Alert",
        description=payload.get("message") or "",
        severity=map_severity(payload.get("state") or payload.get("severity")),
        environment=payload.get("labels", {}).get("env", "unknown") if isinstance(payload.get("labels"), dict) else "unknown",
        service=payload.get("labels", {}).get("service", "unknown") if isinstance(payload.get("labels"), dict) else "unknown",
        external_alert_id=str(payload.get("ruleId") or payload.get("id") or ""),
        tags=[f"{k}:{v}" for k, v in payload.get("labels", {}).items()] if isinstance(payload.get("labels"), dict) else [],
        raw_payload=payload,
    )


def normalize_cloud_style(payload: dict[str, Any], default_title: str) -> NormalizedAlert:
    detail = payload.get("detail") if isinstance(payload.get("detail"), dict) else payload
    return NormalizedAlert(
        title=detail.get("title") or detail.get("alarmName") or default_title,
        description=detail.get("description") or detail.get("stateReason") or "",
        severity=map_severity(detail.get("severity") or detail.get("stateValue")),
        environment=detail.get("environment") or detail.get("env") or "unknown",
        service=detail.get("service") or detail.get("resourceType") or "unknown",
        external_alert_id=str(detail.get("id") or detail.get("alarmArn") or payload.get("id") or ""),
        tags=detail.get("tags") if isinstance(detail.get("tags"), list) else [],
        raw_payload=payload,
    )


def normalize_alert(connector_type: ConnectorType, payload: dict[str, Any]) -> NormalizedAlert:
    if connector_type == ConnectorType.DATADOG:
        return normalize_datadog(payload)
    if connector_type == ConnectorType.PROMETHEUS:
        return normalize_prometheus(payload)
    if connector_type == ConnectorType.GRAFANA:
        return normalize_grafana(payload)
    if connector_type == ConnectorType.CLOUDWATCH:
        return normalize_cloud_style(payload, "CloudWatch Alert")
    if connector_type == ConnectorType.AZURE_MONITOR:
        return normalize_cloud_style(payload, "Azure Monitor Alert")
    if connector_type == ConnectorType.GCP_MONITORING:
        return normalize_cloud_style(payload, "GCP Monitoring Alert")
    return normalize_generic(payload)
