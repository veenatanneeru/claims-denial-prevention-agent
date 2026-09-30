"""Agent 1: validate the structure and codes on a claim."""
import re
from datetime import date

from app.reference import CPT_INFO, PAYERS

ICD10_PATTERN = re.compile(r"^[A-Z]\d{2}(\.[A-Z0-9]{1,4})?$")


def run(state: dict) -> dict:
    claim = state["claim"]
    errors: list[str] = []

    if claim["cpt_code"] not in CPT_INFO:
        errors.append(f"Unknown or unsupported CPT code: {claim['cpt_code']}")
    if not ICD10_PATTERN.match(claim["diagnosis_code"]):
        errors.append(f"Diagnosis code is not a valid ICD-10 format: {claim['diagnosis_code']}")
    if claim["payer"] not in PAYERS:
        errors.append(f"Unknown payer: {claim['payer']}")
    if claim["billed_amount"] <= 0:
        errors.append("Billed amount must be greater than zero")
    if claim["days_to_filing"] < 0:
        errors.append("Days to filing cannot be negative")
    try:
        date.fromisoformat(claim["service_date"])
    except ValueError:
        errors.append("Service date must be in YYYY-MM-DD format")

    return {"validation_errors": errors}