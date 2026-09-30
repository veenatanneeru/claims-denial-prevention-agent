"""LangGraph pipeline wiring the five agents together."""
from langgraph.graph import END, StateGraph

from app.agents import eligibility, policy, resolution, risk, validation
from app.schemas import ClaimState

graph = StateGraph(ClaimState)
graph.add_node("validate", validation.run)
graph.add_node("eligibility", eligibility.run)
graph.add_node("policy", policy.run)
graph.add_node("risk", risk.run)
graph.add_node("resolve", resolution.run)

graph.set_entry_point("validate")

# Invalid claims skip straight to resolution.
graph.add_conditional_edges(
    "validate",
    lambda s: "resolve" if s.get("validation_errors") else "eligibility",
    {"resolve": "resolve", "eligibility": "eligibility"},
)
# Ineligible members skip the policy lookup and scoring.
graph.add_conditional_edges(
    "eligibility",
    lambda s: "policy" if s.get("eligible") else "resolve",
    {"policy": "policy", "resolve": "resolve"},
)
graph.add_edge("policy", "risk")
graph.add_edge("risk", "resolve")
graph.add_edge("resolve", END)

pipeline = graph.compile()