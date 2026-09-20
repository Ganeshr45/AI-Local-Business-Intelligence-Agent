import uuid
from typing import TypedDict, Optional
from app.core import events


class BusinessIntelState(TypedDict):
    run_id: str
    query: str
    location: Optional[str]
    category: Optional[str]
    target_business: Optional[dict]
    competitors: list[dict]
    reviews: list[dict]
    website_audit: Optional[dict]
    evidence: list[dict]
    insights: list[dict]
    recommendations: list[dict]
    errors: list[str]
    events: list[dict]


def make_evidence(label: str, source_type: str, source_id, content: str, metric_count: int = None) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "label": label,
        "source_type": source_type,
        "source_id": source_id,
        "content": content,
        "metric_count": metric_count,
    }


def make_insight(category: str, statement: str, evidence_ids: list, confidence: str = "medium") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "category": category,
        "statement": statement,
        "supporting_evidence_ids": evidence_ids or [],
        "confidence": confidence,
    }


def emit_event(state: BusinessIntelState, node: str, status: str, detail: str = ""):
    event = {"node": node, "status": status, "detail": detail}
    state["events"].append(event)
    events.push_event(state["run_id"], event)
