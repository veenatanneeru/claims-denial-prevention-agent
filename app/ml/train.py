"""Train the denial-risk model on the synthetic claims."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from app.features import build_features

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = Path(__file__).parent / "model.joblib"


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "claims.csv")
    X, y = build_features(df), df["denied"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    model = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1, eval_metric="auc")
    model.fit(X_train, y_train)

    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    print(f"Test AUC: {auc:.3f}")
    joblib.dump({"model": model, "columns": list(X.columns)}, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    main()