from app.agents.state import BusinessIntelState, make_insight, emit_event
from app.tools import llm

SYSTEM_PROMPT = """You are a market gap analyst for local businesses.
You will receive a list of FACT and OBSERVATION evidence items about a business and its competitors.
Identify underserved customer needs or market gaps. Only propose a gap if at least one piece of evidence supports it.
Respond ONLY with JSON: {"gaps": [{"statement": "...", "evidence_indexes": [0,2], "confidence": "high|medium|low"}]}
evidence_indexes refers to the position of the supporting item in the evidence list you were given, zero-indexed."""


def _rule_based_gaps(state: BusinessIntelState) -> list[dict]:
    gaps = []
    topic_evidence = [(i, e) for i, e in enumerate(state["evidence"]) if e["source_type"] == "review_topics"]

    for i, e in topic_evidence:
        if e.get("metric_count", 0) >= 3 and any(k in e["content"].lower() for k in ["slow service", "waiting", "understaffed"]):
            gaps.append(make_insight(
                "AI_INSIGHT",
                f"Repeated complaints about service speed suggest an operational gap during peak hours that no competitor has visibly solved: {e['content']}",
                [e["id"]],
                confidence="medium",
            ))
            break

    ordering_evidence = [(i, e) for i, e in enumerate(state["evidence"]) if e["source_type"] == "website_scrape" and "no online ordering" in e["content"].lower()]
    if ordering_evidence:
        i, e = ordering_evidence[0]
        gaps.append(make_insight(
            "AI_INSIGHT",
            "The target business has no detected online ordering, a feature that is increasingly expected in this category",
            [e["id"]],
            confidence="medium",
        ))

    return gaps


def market_gap_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "market_gap", "started")

    if llm.is_live() and state["evidence"]:
        try:
            evidence_summaries = [f"[{i}] {e['label']}: {e['content']}" for i, e in enumerate(state["evidence"])]
            user_prompt = "\n".join(evidence_summaries)
            result = llm.call_json(SYSTEM_PROMPT, user_prompt)
            for gap in result.get("gaps", []):
                evidence_ids = [state["evidence"][idx].get("id") for idx in gap.get("evidence_indexes", []) if idx < len(state["evidence"])]
                state["insights"].append(make_insight("AI_INSIGHT", gap["statement"], evidence_ids, gap.get("confidence", "medium")))
            emit_event(state, "market_gap", "completed", f"{len(result.get('gaps', []))} gaps found via LLM")
            return state
        except Exception:
            pass

    gaps = _rule_based_gaps(state)
    state["insights"].extend(gaps)
    emit_event(state, "market_gap", "completed", f"{len(gaps)} gaps found via rule-based analysis")
    return state
