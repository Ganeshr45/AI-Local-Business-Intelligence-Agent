from app.agents.state import BusinessIntelState, make_evidence, emit_event
from app.tools import places_api, sentiment


def review_intelligence_node(state: BusinessIntelState) -> BusinessIntelState:
    emit_event(state, "review_intelligence", "started")

    all_businesses = [state["target_business"]] + state["competitors"]
    all_reviews = []

    for business in all_businesses:
        if not business:
            continue
        raw_reviews = places_api.get_reviews(business.get("place_id", ""), business.get("name", ""))
        for review in raw_reviews:
            review["business_id"] = business.get("place_id")
            review["business_name"] = business.get("name")
        all_reviews.extend(raw_reviews)

    if not all_reviews:
        state["errors"].append("No review data available")
        emit_event(state, "review_intelligence", "failed", "no reviews")
        return state

    scored = sentiment.score_batch(all_reviews)
    state["reviews"] = scored

    topic_counts = sentiment.extract_topics(scored)
    distribution = sentiment.sentiment_distribution(scored)

    for topic, count in topic_counts.items():
        state["evidence"].append(
            make_evidence("OBSERVATION", "review_topics", None, f"{count} reviews mention {topic}", metric_count=count)
        )

    state["evidence"].append(
        make_evidence(
            "OBSERVATION",
            "sentiment_distribution",
            None,
            f"Sentiment distribution across {len(scored)} reviews: {distribution['positive']} positive, {distribution['neutral']} neutral, {distribution['negative']} negative",
        )
    )

    emit_event(state, "review_intelligence", "completed", f"{len(scored)} reviews analyzed")
    return state
