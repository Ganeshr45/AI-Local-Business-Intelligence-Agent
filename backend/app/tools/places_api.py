import random
import httpx
from app.core.config import settings
from app.core.cache import places_cache

MOCK_NAMES = [
    "Third Wave Coffee", "Blue Tokai", "Roastery Coffee House", "Cafe Diem",
    "The Daily Grind", "Brew Culture", "Bean There", "Perch Cafe",
    "Cafe Terra", "Filter Kaapi Co",
]

MOCK_COMPLAINT_POOL = [
    "slow service", "long waiting times", "understaffed during rush hour",
    "limited seating", "inconsistent coffee quality", "expensive pricing",
    "poor wifi", "no online ordering", "unfriendly staff", "small portion sizes",
]

MOCK_PRAISE_POOL = [
    "great ambience", "friendly staff", "good coffee quality",
    "quiet workspace", "good for meetings", "fast service", "value for money",
]


def _mock_business(name: str, is_target: bool, lat: float, lng: float) -> dict:
    rating = round(random.uniform(3.6, 4.6), 1)
    review_count = random.randint(40, 1500)
    return {
        "place_id": f"mock_{name.lower().replace(' ', '_')}",
        "name": name,
        "category": "Cafe",
        "address": f"{random.randint(1, 200)} 100 Feet Road, Indiranagar, Bangalore",
        "latitude": lat + random.uniform(-0.01, 0.01),
        "longitude": lng + random.uniform(-0.01, 0.01),
        "rating": rating,
        "review_count": review_count,
        "price_level": random.randint(1, 3),
        "website": None if is_target else f"https://{name.lower().replace(' ', '')}.example.com",
        "phone": f"+91-80-{random.randint(10000000, 99999999)}",
    }


def _mock_reviews(business_name: str, count: int = 12) -> list[dict]:
    reviews = []
    for i in range(count):
        is_negative = random.random() < 0.35
        if is_negative:
            topic = random.choice(MOCK_COMPLAINT_POOL)
            text = f"Visited {business_name} last week, mostly fine but {topic} was a real issue for us."
            rating = random.randint(2, 3)
        else:
            topic = random.choice(MOCK_PRAISE_POOL)
            text = f"Loved {business_name}, especially the {topic}."
            rating = random.randint(4, 5)
        reviews.append({"author": f"Reviewer{i}", "rating": rating, "text": text})
    return reviews


def text_search(query: str, location: str) -> list[dict]:
    cache_key = f"{query}|{location}"
    cached = places_cache.get(cache_key)
    if cached:
        return cached

    if settings.mock_mode or not settings.google_places_api_key:
        base_lat, base_lng = 12.9784, 77.6408
        results = [_mock_business(name, False, base_lat, base_lng) for name in MOCK_NAMES[:6]]
        places_cache.set(cache_key, results)
        return results

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": f"{query} in {location}", "key": settings.google_places_api_key}
    response = httpx.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    results = []
    for place in data.get("results", []):
        results.append({
            "place_id": place.get("place_id"),
            "name": place.get("name"),
            "category": ",".join(place.get("types", [])),
            "address": place.get("formatted_address"),
            "latitude": place.get("geometry", {}).get("location", {}).get("lat"),
            "longitude": place.get("geometry", {}).get("location", {}).get("lng"),
            "rating": place.get("rating"),
            "review_count": place.get("user_ratings_total"),
            "price_level": place.get("price_level"),
            "website": None,
            "phone": None,
        })
    places_cache.set(cache_key, results)
    return results


def get_place_details(place_id: str) -> dict:
    if settings.mock_mode or not settings.google_places_api_key or place_id.startswith("mock_"):
        return {"website": None, "phone": None, "reviews": []}

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "website,formatted_phone_number,reviews",
        "key": settings.google_places_api_key,
    }
    response = httpx.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json().get("result", {})
    return {
        "website": data.get("website"),
        "phone": data.get("formatted_phone_number"),
        "reviews": data.get("reviews", []),
    }


def get_reviews(place_id: str, business_name: str = "") -> list[dict]:
    if settings.mock_mode or not settings.google_places_api_key or place_id.startswith("mock_"):
        return _mock_reviews(business_name or place_id, count=random.randint(10, 20))

    details = get_place_details(place_id)
    reviews = []
    for r in details.get("reviews", []):
        reviews.append({"author": r.get("author_name"), "rating": r.get("rating"), "text": r.get("text")})
    return reviews
