"""FastAPI service exposing the claims denial-prevention pipeline."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from app.graph import pipeline
from app.rag.store import search
from app.schemas import Claim


class EvaluationResponse(BaseModel):
    claim_id: str
    validation_errors: list[str] = []
    eligible: bool | None = None
    eligibility_reason: str | None = None
    denial_risk: float | None = None
    risk_factors: list[str] = []
    policy_context: list[str] = []
    recommendation: str
    actions: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    search("warmup", k=1)  # build the vector store and load the embedding model once at startup
    yield


app = FastAPI(title="Claims Denial Prevention", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate(claim: Claim):
    result = pipeline.invoke({"claim": claim.model_dump()})
    result.pop("claim", None)
    return EvaluationResponse(claim_id=claim.claim_id, **result)