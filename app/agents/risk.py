"""Agent 4: score denial risk with XGBoost and explain the top drivers."""
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb

from app.features import build_features

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "model.joblib"
MIN_CONTRIBUTION = 0.2

# Correlated features are grouped so each problem is explained once, as one concept.
GROUPS = {
    "authorization": ["auth_missing", "prior_auth_present", "auth_required"],
    "network": ["provider_in_network"],
    "diagnosis": ["dx_match"],
    "filing": ["late_filing", "days_to_filing"],
    "amount": ["billed_amount"],
}


def _label(group: str, row: pd.Series) -> str | None:
    """Plain-English problem for a group, or None if this claim does not have that problem."""
    if group == "authorization" and row["auth_missing"] == 1:
        return "Prior authorization is required but not on file"
    if group == "network" and row["provider_in_network"] == 0:
        return "Provider is out of network"
    if group == "diagnosis" and row["dx_match"] == 0:
        return "Diagnosis does not support the billed procedure"
    if group == "filing":
        if row["late_filing"] == 1:
            return "Claim was filed after the 90-day limit"
        if row["days_to_filing"] > 60:
            return "Long delay between service and filing"
    if group == "amount":
        return "High billed amount"
    return None


@lru_cache(maxsize=1)
def _load() -> dict:
    return joblib.load(MODEL_PATH)


def run(state: dict) -> dict:
    bundle = _load()
    model, columns = bundle["model"], bundle["columns"]
    X = build_features(pd.DataFrame([state["claim"]]))[columns]

    risk = float(model.predict_proba(X)[0, 1])
    contribs = dict(zip(columns, model.get_booster().predict(xgb.DMatrix(X), pred_contribs=True)[0][:-1]))
    row = X.iloc[0]

    scored = []
    for group, features in GROUPS.items():
        total = sum(contribs[f] for f in features)
        label = _label(group, row)
        if label and total > MIN_CONTRIBUTION:
            scored.append((total, label))
    scored.sort(reverse=True)

    return {"denial_risk": round(risk, 3), "risk_factors": [label for _, label in scored[:3]]}