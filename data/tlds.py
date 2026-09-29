"""TLD (domeny najwyższego poziomu) z cenami bazowymi."""
from __future__ import annotations

# TLD: id, nazwa, cena rejestracji, cena odnowy/rok, popularność (waga)
TLDS: list[dict] = [
    {"id": "com", "name": ".com", "register": 12.0, "renew": 12.0, "popularity": 0.5},
    {"id": "net", "name": ".net", "register": 14.0, "renew": 14.0, "popularity": 0.2},
    {"id": "org", "name": ".org", "register": 13.0, "renew": 13.0, "popularity": 0.1},
    {"id": "pl", "name": ".pl", "register": 15.0, "renew": 15.0, "popularity": 0.3},
    {"id": "io", "name": ".io", "register": 40.0, "renew": 40.0, "popularity": 0.15},
    {"id": "eu", "name": ".eu", "register": 10.0, "renew": 10.0, "popularity": 0.1},
    {"id": "dev", "name": ".dev", "register": 12.0, "renew": 12.0, "popularity": 0.08},
    {"id": "app", "name": ".app", "register": 14.0, "renew": 14.0, "popularity": 0.07},
]


def get_tld(tld_id: str) -> dict | None:
    for t in TLDS:
        if t["id"] == tld_id:
            return t
    return None