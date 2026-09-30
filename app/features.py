"""Feature engineering shared by model training and the risk agent."""
import pandas as pd

from app.reference import CPT_INFO, PAYERS

LATE_FILING_DAYS = 90


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["billed_amount"] = df["billed_amount"].astype(float)
    out["days_to_filing"] = df["days_to_filing"].astype(int)
    out["prior_auth_present"] = df["prior_auth_present"].astype(int)
    out["provider_in_network"] = df["provider_in_network"].astype(int)

    out["auth_required"] = df["cpt_code"].map(lambda c: int(CPT_INFO.get(c, {}).get("auth", False)))
    out["auth_missing"] = ((out["auth_required"] == 1) & (out["prior_auth_present"] == 0)).astype(int)
    out["dx_match"] = [
        int(d in CPT_INFO.get(c, {}).get("dx", []))
        for c, d in zip(df["cpt_code"], df["diagnosis_code"])
    ]
    out["late_filing"] = (out["days_to_filing"] > LATE_FILING_DAYS).astype(int)

    for payer in PAYERS:
        out[f"payer_{payer}"] = (df["payer"] == payer).astype(int)
    for cpt in CPT_INFO:
        out[f"cpt_{cpt}"] = (df["cpt_code"] == cpt).astype(int)
    return out