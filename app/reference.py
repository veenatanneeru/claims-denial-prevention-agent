"""Reference tables shared by the data generator and the agents (all fictional)."""

PAYERS = ["Aetna", "BlueShield", "Cigna", "UnitedHealth", "Medicare"]

# CPT code -> description, typical billed amount, prior auth required, clinically valid diagnoses
CPT_INFO = {
    "99213": {"desc": "Office visit, established patient, low complexity", "base": 120, "auth": False,
              "dx": ["I10", "E11.9", "J45.909", "Z00.00", "K21.9"]},
    "99214": {"desc": "Office visit, established patient, moderate complexity", "base": 180, "auth": False,
              "dx": ["I10", "E11.9", "J45.909", "Z00.00", "K21.9"]},
    "70553": {"desc": "MRI brain with and without contrast", "base": 2400, "auth": True,
              "dx": ["G43.909", "R51.9"]},
    "72148": {"desc": "MRI lumbar spine without contrast", "base": 1800, "auth": True,
              "dx": ["M54.50", "M51.16"]},
    "45378": {"desc": "Colonoscopy, diagnostic", "base": 1500, "auth": False,
              "dx": ["Z12.11", "K92.1"]},
    "27447": {"desc": "Total knee arthroplasty", "base": 32000, "auth": True,
              "dx": ["M17.11", "M17.12"]},
    "93000": {"desc": "Electrocardiogram, routine", "base": 90, "auth": False,
              "dx": ["I10", "R07.9", "I48.91"]},
    "80053": {"desc": "Comprehensive metabolic panel", "base": 60, "auth": False,
              "dx": ["E11.9", "I10", "Z00.00"]},
    "97110": {"desc": "Therapeutic exercise, 15 minutes", "base": 110, "auth": False,
              "dx": ["M54.50", "M17.11"]},
}

ALL_DX = sorted({d for info in CPT_INFO.values() for d in info["dx"]})