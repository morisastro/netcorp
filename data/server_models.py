"""Katalog modeli serwerów dostępnych do kupienia.

Każdy model ma warianty jakości (budget / standard / premium) z różnym MTBF i ceną.
"""
from __future__ import annotations

# Tier modyfikator awaryjności (mnożnik bazowego prawdopodobieństwa awarii)
# budget = awaryjniejsze (×2.0), premium = bardziej niezawodne (×0.5)
QUALITY_FAILURE_MULTIPLIER = {
    "budget": 2.0,
    "standard": 1.0,
    "premium": 0.5,
}

# Bazowy MTBF (godziny) per tier jakości
TIER_MTBF = {
    "budget": 4000.0,
    "standard": 10000.0,
    "premium": 25000.0,
}


# Katalog modeli serwerów. Każdy ma: id, nazwa (PL), cpu, ram, dysk, cena bazowa per tier.
SERVER_CATALOG: list[dict] = [
    {
        "id": "micro_1u",
        "name": "Micro 1U (Intel Atom)",
        "cpu_cores": 2,
        "ram_gb": 4,
        "disk_gb": 250,
        "disk_type": "hdd",
        "prices": {"budget": 300.0, "standard": 500.0, "premium": 800.0},
        "tdp_w": 80,
    },
    {
        "id": "rack_r1",
        "name": "Rack R1 (Xeon E3)",
        "cpu_cores": 4,
        "ram_gb": 8,
        "disk_gb": 500,
        "disk_type": "hdd",
        "prices": {"budget": 600.0, "standard": 1000.0, "premium": 1600.0},
        "tdp_w": 150,
    },
    {
        "id": "rack_r2",
        "name": "Rack R2 (Xeon E5)",
        "cpu_cores": 8,
        "ram_gb": 16,
        "disk_gb": 1000,
        "disk_type": "ssd",
        "prices": {"budget": 1200.0, "standard": 2000.0, "premium": 3200.0},
        "tdp_w": 250,
    },
    {
        "id": "blade_x1",
        "name": "Blade X1 (EPYC)",
        "cpu_cores": 16,
        "ram_gb": 32,
        "disk_gb": 2000,
        "disk_type": "nvme",
        "prices": {"budget": 2500.0, "standard": 4000.0, "premium": 6500.0},
        "tdp_w": 400,
    },
    {
        "id": "blade_x2",
        "name": "Blade X2 (EPYC 2×CPU)",
        "cpu_cores": 32,
        "ram_gb": 64,
        "disk_gb": 4000,
        "disk_type": "nvme",
        "prices": {"budget": 5000.0, "standard": 8000.0, "premium": 13000.0},
        "tdp_w": 650,
    },
]


def get_model(model_id: str) -> dict | None:
    for m in SERVER_CATALOG:
        if m["id"] == model_id:
            return m
    return None


def get_price(model_id: str, tier: str) -> float | None:
    m = get_model(model_id)
    if m is None:
        return None
    return m["prices"].get(tier)