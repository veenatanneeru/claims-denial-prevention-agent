"""Shared data models for the claims pipeline."""
import csv
from pathlib import Path
from typing import TypedDict

from pydantic import BaseModel

MEMBERS_CSV = Path(__file__).resolve().parents[1] / "data" / "members.csv"


def _example() -> dict:
    """A working sample claim for the /docs page, built from the first active member."""
    with open(MEMBERS_CSV) as f:
        member = next(r for r in csv.DictReader(f) if r["plan_status"] == "active")
    return {
        "claim_id": "DEMO-001",
        "member_id": member["member_id"],
        "payer": member["payer"],
        "cpt_code": "72148",
        "diagnosis_code": "M54.50",
        "billed_amount": 1800.0,
        "prior_auth_present": False,
        "provider_in_network": False,
        "days_to_filing": 120,
        "service_date": member["coverage_start"][:10],
    }


class Claim(BaseModel):
    claim_id: str
    member_id: str
    payer: str
    cpt_code: str
    diagnosis_code: str
    billed_amount: float
    prior_auth_present: bool
    provider_in_network: bool
    days_to_filing: int
    service_date: str  # ISO date, e.g. "2026-05-17"

    model_config = {"json_schema_extra": {"examples": [_example()]}}


class ClaimState(TypedDict, total=False):
    """The shared state that flows through the LangGraph pipeline."""
    claim: dict
    validation_errors: list[str]
    eligible: bool
    eligibility_reason: str
    policy_context: list[str]
    denial_risk: float
    risk_factors: list[str]
    recommendation: str
    actions: list[str]