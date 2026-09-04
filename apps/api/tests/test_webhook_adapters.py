from app.integrations.webhooks.adapters import normalize_alert
from app.models.entities import ConnectorType, SeverityEnum


def test_prometheus_normalization_extracts_core_fields() -> None:
    payload = {
        "alerts": [
            {
                "labels": {
                    "alertname": "APIErrorRateHigh",
                    "severity": "critical",
                    "environment": "production",
                    "service": "checkout-api",
                },
                "annotations": {"description": "Error rate above 5%"},
                "fingerprint": "abc-123",
            }
        ]
    }

    normalized = normalize_alert(ConnectorType.PROMETHEUS, payload)

    assert normalized.title == "APIErrorRateHigh"
    assert normalized.severity == SeverityEnum.SEV1
    assert normalized.environment == "production"
    assert normalized.service == "checkout-api"
    assert normalized.external_alert_id == "abc-123"


def test_generic_normalization_falls_back_safely() -> None:
    normalized = normalize_alert(ConnectorType.GENERIC, {"message": "something happened"})

    assert normalized.title == "Generic Alert"
    assert normalized.severity == SeverityEnum.SEV4
    assert normalized.environment == "unknown"
