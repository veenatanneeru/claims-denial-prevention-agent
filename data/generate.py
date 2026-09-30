"""Generate synthetic members and claims. No real PHI is used anywhere."""
from pathlib import Path

import numpy as np
import pandas as pd

from app.reference import ALL_DX, CPT_INFO, PAYERS

rng = np.random.default_rng(42)
OUT = Path(__file__).parent
N_MEMBERS, N_CLAIMS = 800, 5000
PAYER_RISK = {"Aetna": 0.0, "BlueShield": -0.2, "Cigna": 0.2, "UnitedHealth": 0.4, "Medicare": -0.3}


def make_members() -> pd.DataFrame:
    start = pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 365, N_MEMBERS), unit="D")
    members = pd.DataFrame({
        "member_id": [f"M{100000 + i}" for i in range(N_MEMBERS)],
        "payer": rng.choice(PAYERS, N_MEMBERS),
        "coverage_start": start,
    })
    members["coverage_end"] = start + pd.to_timedelta(rng.integers(365, 1095, N_MEMBERS), unit="D")
    members["plan_status"] = rng.choice(["active", "terminated"], N_MEMBERS, p=[0.92, 0.08])
    return members


def make_claims(members: pd.DataFrame) -> pd.DataFrame:
    claims = members.sample(N_CLAIMS, replace=True, random_state=1).reset_index(drop=True)

    # service date falls inside the member's coverage window
    cap = pd.Timestamp("2026-08-31")
    span = (claims["coverage_end"].clip(upper=cap) - claims["coverage_start"]).dt.days
    offset = (rng.random(N_CLAIMS) * span).astype(int)
    claims["service_date"] = claims["coverage_start"] + pd.to_timedelta(offset, unit="D")

    claims["claim_id"] = [f"C{500000 + i}" for i in range(N_CLAIMS)]
    claims["cpt_code"] = rng.choice(list(CPT_INFO), N_CLAIMS)

    # 90% of the time the diagnosis fits the procedure, 10% it does not
    dx = []
    for cpt in claims["cpt_code"]:
        valid = CPT_INFO[cpt]["dx"]
        dx.append(rng.choice(valid) if rng.random() < 0.9 else rng.choice(ALL_DX))
    claims["diagnosis_code"] = dx

    base = claims["cpt_code"].map(lambda c: CPT_INFO[c]["base"])
    claims["billed_amount"] = (base * rng.lognormal(0, 0.25, N_CLAIMS)).round(2)

    needs_auth = claims["cpt_code"].map(lambda c: CPT_INFO[c]["auth"]).astype(bool)
    claims["prior_auth_present"] = np.where(needs_auth, rng.random(N_CLAIMS) < 0.7, rng.random(N_CLAIMS) < 0.1)
    claims["provider_in_network"] = rng.random(N_CLAIMS) < 0.85
    claims["days_to_filing"] = np.clip(rng.gamma(2.0, 20.0, N_CLAIMS), 1, 240).astype(int)

    # ground-truth denial logic (hidden from the model) + noise
    dx_match = np.array([d in CPT_INFO[c]["dx"] for c, d in zip(claims["cpt_code"], claims["diagnosis_code"])])
    auth_missing = needs_auth.to_numpy() & ~claims["prior_auth_present"].to_numpy()
    logit = (
        -3.2
        + 2.6 * auth_missing
        + 1.4 * ~claims["provider_in_network"].to_numpy()
        + 1.6 * (claims["days_to_filing"].to_numpy() > 90)
        + 1.0 * ~dx_match
        + 0.00004 * claims["billed_amount"].to_numpy()
        + claims["payer"].map(PAYER_RISK).to_numpy()
        + rng.normal(0, 0.3, N_CLAIMS)
    )
    claims["denied"] = (rng.random(N_CLAIMS) < 1 / (1 + np.exp(-logit))).astype(int)

    cols = ["claim_id", "member_id", "payer", "cpt_code", "diagnosis_code", "billed_amount",
            "prior_auth_present", "provider_in_network", "days_to_filing", "service_date", "denied"]
    return claims[cols]


if __name__ == "__main__":
    members = make_members()
    claims = make_claims(members)
    members.to_csv(OUT / "members.csv", index=False)
    claims.to_csv(OUT / "claims.csv", index=False)
    print(f"members: {len(members)}, claims: {len(claims)}, denial rate: {claims['denied'].mean():.1%}")