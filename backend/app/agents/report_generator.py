from app.agents.state import BusinessIntelState, emit_event
from app.db import crud
from app.db.database import SessionLocal


def report_generator_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "report_generator", "started")
    db = SessionLocal()
    try:
        crud.update_run(db, state["run_id"], location=state["location"], category=state["category"], status="completed")

        place_id_to_row_id = {}

        if state["target_business"]:
            row = crud.save_business(db, state["run_id"], state["target_business"], is_target=True)
            place_id_to_row_id[state["target_business"].get("place_id")] = row.id

        for competitor in state["competitors"]:
            row = crud.save_business(db, state["run_id"], competitor, is_target=False)
            place_id_to_row_id[competitor.get("place_id")] = row.id

        for review in state["reviews"]:
            business_row_id = place_id_to_row_id.get(review.get("business_id"))
            if business_row_id:
                crud.save_review(db, business_row_id, review)

        if state["website_audit"] and state["target_business"]:
            target_row_id = place_id_to_row_id.get(state["target_business"].get("place_id"))
            if target_row_id:
                crud.save_website_audit(db, target_row_id, state["website_audit"])

        for evidence in state["evidence"]:
            crud.save_evidence(
                db,
                state["run_id"],
                evidence["label"],
                evidence["source_type"],
                evidence["content"],
                source_id=evidence.get("source_id"),
                metric_count=evidence.get("metric_count"),
                evidence_id=evidence.get("id"),
            )

        for insight in state["insights"]:
            crud.save_insight(
                db,
                state["run_id"],
                insight["category"],
                insight["statement"],
                insight.get("supporting_evidence_ids", []),
                insight.get("confidence", "medium"),
                insight_id=insight.get("id"),
            )

        for rec in state["recommendations"]:
            crud.save_recommendation(
                db,
                state["run_id"],
                rec["statement"],
                rec.get("supporting_insight_ids", []),
                rec.get("impact_score", 3),
                rec.get("effort_score", 3),
                rec.get("priority_rank", 0),
            )

        if state["errors"]:
            crud.save_evidence(db, state["run_id"], "OBSERVATION", "system", "; ".join(state["errors"]))

    finally:
        db.close()

    emit_event(state, "report_generator", "completed")
    return state
