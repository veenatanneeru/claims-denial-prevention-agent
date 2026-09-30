"""Agent 4: score denial risk with XGBoost and explain the top drivers."""
from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
import xgboost as xgb

from app.features import build_features

MODEL_PATH = Path(__file__).resolve().parents[1] / "ml" / "model.joblib"

# Shown only when a feature pushes the risk UP, so each label reads as a problem.
FACTOR_LABELS = {
    "auth_missing": "Prior authorization is required but not on file",
    "prior_auth_present": "No prior authorization on file",
    "provider_in_network": "Provider is out of network",
    "dx_match": "Diagnosis does not support the billed procedure",
    "late_filing": "Claim was filed after the 90-day limit",
    "days_to_filing": "Long delay between service and filing",
    "billed_amount": "High billed amount",
}


@lru_cache(maxsize=1)
def _load() -> dict:
    return joblib.load(MODEL_PATH)


def run(state: dict) -> dict:
    bundle = _load()
    model, columns = bundle["model"], bundle["columns"]
    X = build_features(pd.DataFrame([state["claim"]]))[columns]

    risk = float(model.predict_proba(X)[0, 1])
    contribs = model.get_booster().predict(xgb.DMatrix(X), pred_contribs=True)[0][:-1]
    ranked = sorted(zip(columns, contribs), key=lambda t: t[1], reverse=True)
    factors = [FACTOR_LABELS[name] for name, value in ranked if name in FACTOR_LABELS and value > 0.2][:3]

    return {"denial_risk": round(risk, 3), "risk_factors": factors}