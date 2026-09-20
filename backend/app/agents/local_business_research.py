from app.agents.state import BusinessIntelState, make_evidence, emit_event
from app.tools import places_api


def _describe_business(business: dict) -> str:
    parts = [business.get("name", "Unknown business")]
    if business.get("rating") is not None:
        parts.append(f"{business['rating']} star rating")
    if business.get("review_count") is not None:
        parts.append(f"{business['review_count']} reviews")
    if business.get("price_level") is not None:
        parts.append(f"price level {business['price_level']}")
    return ", ".join(parts)


def local_business_research_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "local_business_research", "started")
    results = places_api.text_search(state["category"], state["location"])

    if not results:
        state["errors"].append("No local business data available for this location and category")
        emit_event(state, "local_business_research", "failed", "no results")
        return state

    target_query_lower = state["query"].lower()
    target = None
    for business in results:
        if business["name"].lower() in target_query_lower:
            target = business
            break

    if not target:
        target = dict(results[0])
        target["name"] = f"Your business ({state['category'].strip().title()})"
        target["place_id"] = "target_placeholder"
        target["rating"] = None
        target["review_count"] = None

    competitors = [b for b in results if b.get("place_id") != target.get("place_id")]

    state["target_business"] = target
    state["competitors"] = competitors

    for business in results:
        state["evidence"].append(
            make_evidence("FACT", "places_api", business.get("place_id"), _describe_business(business))
        )

    emit_event(state, "local_business_research", "completed", f"{len(competitors)} competitors found")
    return state
