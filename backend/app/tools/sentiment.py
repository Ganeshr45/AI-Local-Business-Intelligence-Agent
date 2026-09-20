TOPIC_KEYWORDS = {
    "slow service": ["slow service", "took forever", "long wait", "waiting time", "slow staff"],
    "long waiting times": ["long wait", "waited", "queue", "line was long"],
    "understaffed": ["understaffed", "not enough staff", "short staffed"],
    "pricing": ["expensive", "overpriced", "pricey", "costly", "price"],
    "seating": ["seating", "no seats", "crowded", "limited space"],
    "quality": ["quality", "stale", "cold coffee", "inconsistent"],
    "wifi": ["wifi", "wi-fi", "internet"],
    "staff friendliness": ["rude", "unfriendly", "friendly staff", "helpful staff"],
    "cleanliness": ["dirty", "unclean", "hygiene", "clean"],
    "ambience": ["ambience", "vibe", "atmosphere", "cozy", "aesthetic"],
}

NEGATIVE_MARKERS = ["slow", "rude", "expensive", "dirty", "bad", "worst", "poor", "disappoint", "cold", "stale", "understaffed"]
POSITIVE_MARKERS = ["great", "love", "friendly", "fast", "good", "amazing", "best", "cozy", "excellent", "fresh"]


def score_review(review: dict) -> dict:
    text = (review.get("text") or "").lower()
    rating = review.get("rating")

    negative_hits = sum(1 for m in NEGATIVE_MARKERS if m in text)
    positive_hits = sum(1 for m in POSITIVE_MARKERS if m in text)

    if rating is not None:
        if rating <= 2:
            sentiment = "negative"
        elif rating == 3:
            sentiment = "neutral"
        else:
            sentiment = "positive"
    else:
        sentiment = "negative" if negative_hits > positive_hits else ("positive" if positive_hits > negative_hits else "neutral")

    topics = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(k in text for k in keywords):
            topics.append(topic)

    review = dict(review)
    review["sentiment"] = sentiment
    review["topics"] = topics
    return review


def score_batch(reviews: list[dict]) -> list[dict]:
    return [score_review(r) for r in reviews]


def extract_topics(scored_reviews: list[dict]) -> dict:
    counts = {}
    for review in scored_reviews:
        for topic in review.get("topics", []):
            counts[topic] = counts.get(topic, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))


def sentiment_distribution(scored_reviews: list[dict]) -> dict:
    distribution = {"positive": 0, "neutral": 0, "negative": 0}
    for review in scored_reviews:
        sentiment = review.get("sentiment", "neutral")
        distribution[sentiment] = distribution.get(sentiment, 0) + 1
    return distribution
