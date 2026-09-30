"""Send one example claim to the live API and save the request/response for the README."""
import csv
import json
from pathlib import Path

import httpx

URL = "https://claims-denial-prevention-agent.onrender.com/evaluate"
ROOT = Path(__file__).resolve().parents[1]

with open(ROOT / "data" / "members.csv") as f:
    member = next(r for r in csv.DictReader(f) if r["plan_status"] == "active")

claim = {
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

response = httpx.post(URL, json=claim, timeout=120)
response.raise_for_status()
result = response.json()
result["policy_context"] = [p[:90] + "..." for p in result["policy_context"]]  # shortened for readability

docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
(docs / "sample_request.json").write_text(json.dumps(claim, indent=2) + "\n")
(docs / "sample_response.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))