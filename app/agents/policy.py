"""Agent 3: retrieve the payer policies most relevant to this claim (RAG)."""
from app.rag.store import search
from app.reference import CPT_INFO


def run(state: dict) -> dict:
    claim = state["claim"]
    info = CPT_INFO.get(claim["cpt_code"], {})
    query = (
        f"CPT {claim['cpt_code']} {info.get('desc', '')} "
        f"diagnosis {claim['diagnosis_code']} prior authorization timely filing network"
    )
    hits = search(query, k=3)
    return {"policy_context": [f"[{h['source']}] {h['text'].strip()}" for h in hits]}