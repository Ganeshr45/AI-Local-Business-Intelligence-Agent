import math


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    if None in (lat1, lng1, lat2, lng2):
        return None
    radius = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(radius * c, 2)


def within_radius(target: dict, candidate: dict, radius_km: float = 3.0) -> bool:
    distance = haversine_km(target.get("latitude"), target.get("longitude"), candidate.get("latitude"), candidate.get("longitude"))
    if distance is None:
        return True
    return distance <= radius_km
