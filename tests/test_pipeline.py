from pathlib import Path

import pandas as pd
import pytest

from app.graph import pipeline

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def member() -> dict:
    row = pd.read_csv(ROOT / "data" / "members.csv")
    row = row[row.plan_status == "active"].iloc[0]
    return {
        "member_id": str(row.member_id),
        "payer": str(row.payer),
        "service_date": str(row.coverage_start)[:10],
    }


def make_claim(member: dict, **overrides) -> dict:
    claim = dict(
        claim_id="C1", cpt_code="99213", diagnosis_code="I10", billed_amount=120.0,
        prior_auth_present=False, provider_in_network=True, days_to_filing=10, **member,
    )
    claim.update(overrides)
    return claim


def test_clean_claim_is_not_flagged_high(member):
    result = pipeline.invoke({"claim": make_claim(member)})
    assert result["eligible"] is True
    assert result["denial_risk"] < 0.3
    assert not result["recommendation"].startswith("High")


def test_risky_claim_is_held(member):
    claim = make_claim(
        member, cpt_code="72148", diagnosis_code="M54.50", billed_amount=1800.0,
        provider_in_network=False, days_to_filing=120,
    )
    result = pipeline.invoke({"claim": claim})
    assert result["denial_risk"] > 0.5
    assert result["recommendation"].startswith("High")
    assert result["actions"]


def test_invalid_claim_short_circuits(member):
    result = pipeline.invoke({"claim": make_claim(member, cpt_code="00000")})
    assert result["validation_errors"]
    assert "denial_risk" not in result


def test_unknown_member_short_circuits(member):
    result = pipeline.invoke({"claim": make_claim(member, member_id="M999999")})
    assert result["eligible"] is False
    assert "denial_risk" not in result