"""Agent 2: check member eligibility against the coverage file."""
from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd

MEMBERS_CSV = Path(__file__).resolve().parents[2] / "data" / "members.csv"


@lru_cache(maxsize=1)
def _members() -> pd.DataFrame:
    return pd.read_csv(MEMBERS_CSV, parse_dates=["coverage_start", "coverage_end"]).set_index("member_id")


def run(state: dict) -> dict:
    claim = state["claim"]
    members = _members()
    member_id = claim["member_id"]

    if member_id not in members.index:
        return {"eligible": False, "eligibility_reason": f"Member {member_id} not found"}

    member = members.loc[member_id]
    service = pd.Timestamp(date.fromisoformat(claim["service_date"]))

    if member["plan_status"] != "active":
        return {"eligible": False, "eligibility_reason": "Plan is not active"}
    if member["payer"] != claim["payer"]:
        return {"eligible": False,
                "eligibility_reason": f"Member is enrolled with {member['payer']}, not {claim['payer']}"}
    if not (member["coverage_start"] <= service <= member["coverage_end"]):
        return {"eligible": False, "eligibility_reason": "Service date is outside the coverage period"}
    return {"eligible": True, "eligibility_reason": "Active coverage on service date"}