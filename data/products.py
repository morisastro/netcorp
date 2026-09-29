"""Szablony i metadane produktów oferowanych przez gracza."""
from __future__ import annotations

# Typy produktów — etykiety po polsku
PRODUCT_TYPES: list[dict] = [
    {"id": "www", "name": "Hosting WWW", "unit": "konto"},
    {"id": "vps", "name": "VPS", "unit": "instancja"},
    {"id": "dedicated", "name": "Serwer dedykowany", "unit": "serwer"},
    {"id": "domain", "name": "Domena", "unit": "domena"},
]


def product_name(product_type: str) -> str:
    for p in PRODUCT_TYPES:
        if p["id"] == product_type:
            return p["name"]
    return product_type