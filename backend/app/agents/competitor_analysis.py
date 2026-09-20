from app.agents.state import BusinessIntelState, make_evidence, emit_event


def _rule_based_comparison(target: dict, competitors: list[dict]) -> str:
    rated_competitors = [c for c in competitors if c.get("rating") is not None]
    if not rated_competitors:
        return "No competitor rating data available for comparison"

    avg_rating = sum(c["rating"] for c in rated_competitors) / len(rated_competitors)
    top_competitor = max(rated_competitors, key=lambda c: c["rating"])

    if target.get("rating") is not None:
        gap = round(avg_rating - target["rating"], 2)
        direction = "above" if gap > 0 else "below"
        return f"Average competitor rating is {round(avg_rating, 2)}, which is {abs(gap)} points {direction} the target business. Top rated competitor is {top_competitor['name']} at {top_competitor['rating']} stars."
    return f"Average competitor rating is {round(avg_rating, 2)}. Top rated competitor is {top_competitor['name']} at {top_competitor['rating']} stars."


def competitor_analysis_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "competitor_analysis", "started")

    if not state["competitors"]:
        state["errors"].append("No competitors available to analyze")
        emit_event(state, "competitor_analysis", "failed", "no competitors")
        return state

    summary = _rule_based_comparison(state["target_business"], state["competitors"])
    state["evidence"].append(make_evidence("OBSERVATION", "competitor_comparison", None, summary))

    priced_competitors = [c for c in state["competitors"] if c.get("price_level") is not None]
    if priced_competitors:
        avg_price = sum(c["price_level"] for c in priced_competitors) / len(priced_competitors)
        state["evidence"].append(
            make_evidence("OBSERVATION", "competitor_comparison", None, f"Average competitor price level is {round(avg_price, 1)} out of 4")
        )

    emit_event(state, "competitor_analysis", "completed")
    return state
