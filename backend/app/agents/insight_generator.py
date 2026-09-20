from app.agents.state import BusinessIntelState, make_insight, emit_event
from app.tools import llm

SYSTEM_PROMPT = """You are a business intelligence analyst. You will be given FACT and OBSERVATION evidence
about a local business and its competitors, plus any AI_INSIGHT items already found.
Produce additional AI_INSIGHT items only when at least one piece of evidence clearly supports the claim.
Do not use general knowledge about local businesses beyond the evidence given.
Respond ONLY with JSON: {"insights": [{"statement": "...", "evidence_indexes": [0,1], "confidence": "high|medium|low"}]}"""


def _rule_based_insights(state: BusinessIntelState) -> list[dict]:
    insights = []
    sentiment_evidence = [(i, e) for i, e in enumerate(state["evidence"]) if e["source_type"] == "sentiment_distribution"]
    if sentiment_evidence:
        i, e = sentiment_evidence[0]
        if "negative" in e["content"]:
            insights.append(make_insight(
                "AI_INSIGHT",
                f"A meaningful share of reviews in this micro-market are negative, indicating room to differentiate on service consistency: {e['content']}",
                [e["id"]],
                confidence="medium",
            ))
    return insights


def insight_generator_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "insight_generator", "started")

    if llm.is_live() and state["evidence"]:
        try:
            evidence_summaries = [f"[{i}] {e['label']}: {e['content']}" for i, e in enumerate(state["evidence"])]
            existing_insights = [f"- {ins['statement']}" for ins in state["insights"]]
            user_prompt = "EVIDENCE:\n" + "\n".join(evidence_summaries) + "\n\nEXISTING INSIGHTS:\n" + "\n".join(existing_insights)
            result = llm.call_json(SYSTEM_PROMPT, user_prompt)
            for item in result.get("insights", []):
                evidence_ids = [state["evidence"][idx]["id"] for idx in item.get("evidence_indexes", []) if idx < len(state["evidence"])]
                if evidence_ids:
                    state["insights"].append(make_insight("AI_INSIGHT", item["statement"], evidence_ids, item.get("confidence", "medium")))
            emit_event(state, "insight_generator", "completed", "via LLM")
            return state
        except Exception:
            pass

    new_insights = _rule_based_insights(state)
    state["insights"].extend(new_insights)
    emit_event(state, "insight_generator", "completed", "via rule-based fallback")
    return state
