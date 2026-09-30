"""Agent 5: turn the analysis into a recommendation and concrete next steps."""

HIGH_RISK = 0.5
MEDIUM_RISK = 0.2

ACTIONS = {
    "Prior authorization is required but not on file":
        "Obtain the prior authorization and attach its number before submitting",
    "Provider is out of network":
        "Verify network status; expect reduced reimbursement or request an exception",
    "Diagnosis does not support the billed procedure":
        "Send to coder review to correct the diagnosis or procedure code",
    "Claim was filed after the 90-day limit":
        "Attach proof of timely filing or of a payer-caused delay",
    "Long delay between service and filing":
        "Submit as soon as possible; filing delays are a leading cause of denials",
    "High billed amount":
        "Double-check coding and attach supporting documentation for this high-dollar claim",
}


def run(state: dict) -> dict:
    errors = state.get("validation_errors") or []
    if errors:
        return {"recommendation": "Do not submit: fix the claim errors first", "actions": errors}

    if state.get("eligible") is False:
        return {
            "recommendation": "Do not submit: member is not eligible",
            "actions": [state.get("eligibility_reason", "Eligibility check failed")],
        }

    risk = state["denial_risk"]
    actions = [ACTIONS[f] for f in state.get("risk_factors", []) if f in ACTIONS]

    if risk >= HIGH_RISK:
        recommendation = "High denial risk: hold the claim and fix the issues below before submitting"
    elif risk >= MEDIUM_RISK:
        recommendation = "Moderate denial risk: review the items below, then submit"
    else:
        recommendation = "Low denial risk: submit as is"
        actions = actions or ["No action needed"]

    return {"recommendation": recommendation, "actions": actions}