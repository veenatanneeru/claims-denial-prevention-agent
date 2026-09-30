"""Shared data models for the claims pipeline."""
from typing import TypedDict

from pydantic import BaseModel


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