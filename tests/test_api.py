from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from app.api.main import app

ROOT = Path(__file__).resolve().parents[1]


def risky_payload() -> dict:
    m = pd.read_csv(ROOT / "data" / "members.csv")
    m = m[m.plan_status == "active"].iloc[0]
    return dict(
        claim_id="C1", member_id=str(m.member_id), payer=str(m.payer),
        cpt_code="72148", diagnosis_code="M54.50", billed_amount=1800.0,
        prior_auth_present=False, provider_in_network=False, days_to_filing=120,
        service_date=str(m.coverage_start)[:10],
    )


def test_health():
    with TestClient(app) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_evaluate_risky_claim():
    with TestClient(app) as client:
        response = client.post("/evaluate", json=risky_payload())
    body = response.json()
    assert response.status_code == 200
    assert body["recommendation"].startswith("High")
    assert body["risk_factors"]
    assert body["policy_context"]


def test_missing_field_is_rejected():
    payload = risky_payload()
    del payload["cpt_code"]
    with TestClient(app) as client:
        assert client.post("/evaluate", json=payload).status_code == 422