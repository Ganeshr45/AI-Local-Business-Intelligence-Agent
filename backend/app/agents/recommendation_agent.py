from app.agents.state import BusinessIntelState, emit_event
from app.tools import llm

SYSTEM_PROMPT = """You are a small-business growth advisor.
Convert the given AI_INSIGHT items into concrete RECOMMENDATION items.
Every recommendation must reference the insight_indexes it addresses.
Score impact (1-5) and effort (1-5) honestly, most quick wins should have low effort.
Respond ONLY with JSON: {"recommendations": [{"statement": "...", "insight_indexes": [0], "impact_score": 4, "effort_score": 2}]}"""

FALLBACK_TEMPLATES = {
    "slow service": "Introduce a pre-order/pickup window and add staffing during peak hours to reduce wait-time complaints.",
    "online ordering": "Add a simple online ordering or delivery-partner listing, since this is now a baseline customer expectation.",
    "negative": "Set up a lightweight review-response process to address recurring negative feedback within 48 hours.",
}


def _rule_based_recommendations(state: BusinessIntelState) -> list[dict]:
    recommendations = []
    for insight in state["insights"]:
        statement_lower = insight["statement"].lower()
        for keyword, template in FALLBACK_TEMPLATES.items():
            if keyword in statement_lower:
                recommendations.append({
                    "statement": template,
                    "supporting_insight_ids": [insight.get("id")] if insight.get("id") else [],
                    "impact_score": 4,
                    "effort_score": 2,
                })
                break
    return recommendations


def recommendation_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "recommendation_agent", "started")

    if not state["insights"]:
        state["errors"].append("No insights available to base recommendations on")
        emit_event(state, "recommendation_agent", "skipped", "no insights")
        return state

    recommendations = []

    if llm.is_live():
        try:
            insight_summaries = [f"[{i}] {ins['statement']}" for i, ins in enumerate(state["insights"])]
            result = llm.call_json(SYSTEM_PROMPT, "\n".join(insight_summaries))
            for item in result.get("recommendations", []):
                insight_ids = [state["insights"][idx].get("id") for idx in item.get("insight_indexes", []) if idx < len(state["insights"])]
                recommendations.append({
                    "statement": item["statement"],
                    "supporting_insight_ids": insight_ids,
                    "impact_score": item.get("impact_score", 3),
                    "effort_score": item.get("effort_score", 3),
                })
        except Exception:
            recommendations = []

    if not recommendations:
        recommendations = _rule_based_recommendations(state)

    for rec in recommendations:
        rec["priority_rank"] = rec["effort_score"] - rec["impact_score"]

    recommendations.sort(key=lambda r: r["priority_rank"])
    for rank, rec in enumerate(recommendations, start=1):
        rec["priority_rank"] = rank

    state["recommendations"] = recommendations
    emit_event(state, "recommendation_agent", "completed", f"{len(recommendations)} recommendations")
    return state
