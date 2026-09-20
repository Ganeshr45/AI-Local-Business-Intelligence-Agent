from app.agents.state import BusinessIntelState, emit_event
from app.tools import llm

SYSTEM_PROMPT = """You are a research planner for a local business intelligence agent.
Given a free-text query describing a business, idea, or location, extract the category of business and the location.
Respond ONLY with JSON: {"category": "...", "location": "..."}
Do not invent a location if none is present in the query, return an empty string instead."""


def _heuristic_parse(query: str) -> dict:
    lowered = query.lower()
    if " in " in lowered:
        category_part, location_part = query.split(" in ", 1)
        return {"category": category_part.strip(), "location": location_part.strip()}
    return {"category": query.strip(), "location": ""}


def query_planner_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "query_planner", "started")
    query = state["query"]

    if llm.is_live():
        try:
            plan = llm.call_json(SYSTEM_PROMPT, query)
        except Exception:
            plan = _heuristic_parse(query)
    else:
        plan = _heuristic_parse(query)

    state["category"] = plan.get("category") or ""
    state["location"] = plan.get("location") or ""

    if not state["location"]:
        state["errors"].append("Could not determine a specific location from the query, results may be broad")
    if not state["category"]:
        state["errors"].append("Could not determine a specific business category from the query")

    emit_event(state, "query_planner", "completed", f"category={state['category']}, location={state['location']}")
    return state
