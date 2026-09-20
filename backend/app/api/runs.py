import asyncio
import json
import threading
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db, SessionLocal
from app.db import crud
from app.core import events
from app.agents.graph import run_pipeline

router = APIRouter()


class CreateRunRequest(BaseModel):
    query: str


def _run_in_background(run_id: str, query: str):
    try:
        run_pipeline(run_id, query)
    except Exception as exc:
        db = SessionLocal()
        try:
            crud.update_run(db, run_id, status="failed")
            crud.save_evidence(db, run_id, "OBSERVATION", "system", f"Pipeline failed: {exc}")
        finally:
            db.close()
        events.push_event(run_id, {"node": "pipeline", "status": "failed", "detail": str(exc)})
    finally:
        events.mark_done(run_id)


@router.post("/runs")
def create_run(payload: CreateRunRequest, db: Session = Depends(get_db)):
    run = crud.create_run(db, payload.query)
    events.init_run(run.id)
    thread = threading.Thread(target=_run_in_background, args=(run.id, payload.query), daemon=True)
    thread.start()
    return {"run_id": run.id, "status": run.status}


@router.get("/runs/{run_id}/stream")
async def stream_run(run_id: str):
    async def event_generator():
        offset = 0
        while True:
            new_events, offset = events.get_events_since(run_id, offset)
            for event in new_events:
                yield {"event": "progress", "data": json.dumps(event)}
            if events.is_done(run_id):
                yield {"event": "done", "data": json.dumps({"status": "done"})}
                break
            await asyncio.sleep(0.4)

    return EventSourceResponse(event_generator())


@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db)):
    state = crud.get_full_run_state(db, run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")

    run = state["run"]
    return {
        "run_id": run.id,
        "query": run.query,
        "location": run.location,
        "category": run.category,
        "status": run.status,
        "target_business": next((serialize_business(b) for b in state["businesses"] if b.is_target), None),
        "competitors": [serialize_business(b) for b in state["businesses"] if not b.is_target],
        "reviews": [serialize_review(r) for r in state["reviews"]],
        "website_audit": serialize_audit(state["audits"][0]) if state["audits"] else None,
        "insights": [serialize_insight(i) for i in state["insights"]],
        "recommendations": [serialize_recommendation(r) for r in state["recommendations"]],
        "evidence_count": len(state["evidence"]),
    }


@router.get("/runs/{run_id}/competitors")
def get_competitors(run_id: str, db: Session = Depends(get_db)):
    state = crud.get_full_run_state(db, run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "target": next((serialize_business(b) for b in state["businesses"] if b.is_target), None),
        "competitors": [serialize_business(b) for b in state["businesses"] if not b.is_target],
    }


@router.get("/runs/{run_id}/evidence")
def get_evidence(run_id: str, label: str = None, db: Session = Depends(get_db)):
    state = crud.get_full_run_state(db, run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found")
    evidence = state["evidence"]
    if label:
        evidence = [e for e in evidence if e.label == label]
    return {"evidence": [serialize_evidence(e) for e in evidence]}


@router.get("/runs/{run_id}/report")
def get_report(run_id: str, db: Session = Depends(get_db)):
    return get_run(run_id, db)


def serialize_business(b) -> dict:
    return {
        "id": b.id,
        "name": b.name,
        "category": b.category,
        "address": b.address,
        "latitude": b.latitude,
        "longitude": b.longitude,
        "rating": b.rating,
        "review_count": b.review_count,
        "price_level": b.price_level,
        "website": b.website,
        "phone": b.phone,
        "is_target": b.is_target,
    }


def serialize_review(r) -> dict:
    return {"id": r.id, "author": r.author, "rating": r.rating, "text": r.text, "sentiment": r.sentiment, "topics": r.topics}


def serialize_audit(a) -> dict:
    return {
        "has_online_ordering": a.has_online_ordering,
        "has_menu_pricing": a.has_menu_pricing,
        "mobile_friendly": a.mobile_friendly,
        "seo_title": a.seo_title,
        "contact_info_present": a.contact_info_present,
        "load_time_ms": a.load_time_ms,
    }


def serialize_evidence(e) -> dict:
    return {"id": e.id, "label": e.label, "source_type": e.source_type, "content": e.content, "metric_count": e.metric_count}


def serialize_insight(i) -> dict:
    return {"id": i.id, "category": i.category, "statement": i.statement, "supporting_evidence_ids": i.supporting_evidence_ids, "confidence": i.confidence}


def serialize_recommendation(r) -> dict:
    return {
        "id": r.id,
        "statement": r.statement,
        "supporting_insight_ids": r.supporting_insight_ids,
        "impact_score": r.impact_score,
        "effort_score": r.effort_score,
        "priority_rank": r.priority_rank,
    }
