"""Podstawowa symulacja tury — economia, awarie, churn, pracownicy.

Tu trafia logika wywoływana przez Game.next_day().
"""
from __future__ import annotations

from typing import Any

from data import balance


def simulate_day(state: Any, rng: Any) -> dict[str, Any]:
    """Symuluje jeden dzień gry. Modyfikuje `state` w miejscu. Zwraca raport.

    TODO (faza 1, krok 7): pełna implementacja. Na razie:
    - koszt pracowników (pensje)
    - koszt stały (licencje)
    - minimalny przyrost klientów z reputacji
    """
    income = 0.0
    expenses = 0.0
    new_customers = 0
    churned = 0
    new_failures: list = []
    resolved_failures: list = []
    tickets_resolved = 0
    milestones: list = []

    # ---- Koszty pracowników ----
    for emp in state.employees:
        expenses += emp.salary_daily

    # ---- Koszt stały (licencje) ----
    expenses += balance.LICENSE_DAILY

    # ---- Koszt wynajmu regionów ----
    for region in state.regions:
        expenses += region.rent_daily

    # ---- Przychód z subskrypcji (prosty: count × avg_price/30) ----
    # TODO: realne ceny z planów produktów
    avg_monthly_per_customer = 15.0  # $/mies średnio
    income = (sum(c.count for c in state.customers) * avg_monthly_per_customer) / 30.0

    # ---- Aktualizacja gotówki ----
    state.cash += income - expenses

    # ---- Przyrost klientów (reputacja, brak marketingu w tym stubie) ----
    baseline = balance.MARKETING_BASELINE_NEW_CUSTOMERS
    if rng.chance(0.5) and state.reputation > 30:
        new_customers = rng.randint(0, baseline)
        # Rozdziel na produkty (losowo)
        if new_customers and state.customers:
            target = rng.choice(state.customers)
            target.count += new_customers

    # ---- Churn (uproszczony) ----
    for cust in state.customers:
        if cust.count > 0:
            daily_churn = cust.churn_monthly / 30.0
            lost = sum(1 for _ in range(cust.count) if rng.chance(daily_churn))
            cust.count = max(0, cust.count - lost)
            churned += lost

    return {
        "day": state.day,
        "cash": state.cash,
        "income": income,
        "expenses": expenses,
        "new_customers": new_customers,
        "churned": churned,
        "new_failures": new_failures,
        "resolved_failures": resolved_failures,
        "tickets_resolved": tickets_resolved,
        "milestones_unlocked": milestones,
    }