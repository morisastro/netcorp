"""Podstawowa symulacja tury — ekonomia, awarie, churn, pracownicy.

Tu trafia logika wywoływana przez Game.next_day().
"""
from __future__ import annotations

from typing import Any

from core.models import Failure
from data import balance


def simulate_day(state: Any, rng: Any) -> dict[str, Any]:
    """Symuluje jeden dzień gry. Modyfikuje `state` w miejscu. Zwraca raport."""
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

    # ---- Koszt wynajmu regionów + prąd ----
    for region in state.regions:
        expenses += region.rent_daily
        # Prąd: zużyte kW × cena/kWh × 24h
        expenses += region.power_kw_used * balance.POWER_PRICE_PER_KWH * 24

    # ---- Przychód z subskrypcji ----
    # Każdy klient płaci średnią cenę planu / 30 dziennie
    # Uproszczenie: jeśli brak planów, używamy średniej $15/mies
    avg_monthly = _avg_plan_price(state) if state.products else 15.0
    total_customers = sum(c.count for c in state.customers)
    income = (total_customers * avg_monthly) / 30.0

    # ---- Aktualizacja gotówki ----
    state.cash += income - expenses

    # ---- Awarie ----
    new_failures = _generate_failures(state, rng)

    # ---- Przyrost klientów ----
    marketing = state.marketing_budget_daily
    # Bazowo: 1 klient z reputacji dziennie (50% szans)
    if rng.chance(0.5) and state.reputation > 20:
        baseline = rng.randint(0, balance.MARKETING_BASELINE_NEW_CUSTOMERS)
        new_customers += baseline
    # Z marketingu: każdy $ wygeneruje 1/MARKETING_COST_PER_NEW_CUSTOMER klienta
    if marketing > 0 and total_customers < 100000:
        # Bonus ze strony (conversion_bonus)
        website_bonus = state.website.conversion_bonus() if state.website else 0.0
        # Wskaźnik konwersji: 1.0 + bonus (0.0 - 0.5)
        conv_rate = 1.0 + website_bonus
        from_marketing = int(marketing / balance.MARKETING_COST_PER_NEW_CUSTOMER * conv_rate)
        new_customers += from_marketing

    if new_customers > 0 and state.customers:
        # Rozdziel proporcjonalnie do istniejących planów produktów
        product_weights = _product_weights(state)
        if product_weights:
            for _ in range(new_customers):
                # Wybierz produkt wg wagi (prosta ruletka)
                r = rng.random()
                cumulative = 0.0
                for pt, w in product_weights.items():
                    cumulative += w
                    if r <= cumulative:
                        for cust in state.customers:
                            if cust.product_type == pt:
                                cust.count += 1
                                break
                        break

    # ---- Churn ----
    for cust in state.customers:
        if cust.count > 0:
            daily_churn = cust.churn_monthly / 30.0
            # Bonus churn jeśli aktywne awarie
            if state.failures_active:
                daily_churn += 0.02
            lost = sum(1 for _ in range(cust.count) if rng.chance(daily_churn))
            cust.count = max(0, cust.count - lost)
            churned += lost

    # ---- Reputacja ----
    if state.failures_active:
        state.reputation = max(0, state.reputation - len(state.failures_active) * 0.5)
    elif total_customers > 0 and not state.failures_active:
        state.reputation = min(100, state.reputation + 0.1)

    # ---- Kamienie milowe ----
    total = total_customers
    if total >= 50 and "milestone_small_office" not in state.unlocked_milestones:
        state.unlocked_milestones.append("milestone_small_office")
        milestones.append("Odblokowano: wynajem małej serwerowni (50 klientów)")
    if total >= 500 and "milestone_dc" not in state.unlocked_milestones:
        state.unlocked_milestones.append("milestone_dc")
        milestones.append("Odblokowano: pełne DC (500 klientów)")
    if total >= 2000 and "milestone_second_region" not in state.unlocked_milestones:
        state.unlocked_milestones.append("milestone_second_region")
        milestones.append("Odblokowano: drugi region (2000 klientów)")

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


def _avg_plan_price(state: Any) -> float:
    """Średnia cena miesięczna z planów produktów."""
    if not state.products:
        return 15.0
    prices = [p.price_monthly for p in state.products if p.price_monthly > 0]
    if not prices:
        return 15.0
    return sum(prices) / len(prices)


def _product_weights(state: Any) -> dict[str, float]:
    """Wagi produktów do rozdzielania nowych klientów.

    Jeśli są plany: każdy produkt z co najmniej 1 planem ma wagę 1.0.
    Brak planów → produkt niedostępny (waga 0).
    """
    weights: dict[str, float] = {}
    for pt in ("www", "vps", "dedicated", "domain"):
        has_plan = any(p.product_type == pt for p in state.products)
        if has_plan:
            weights[pt] = 1.0
    return weights


def _generate_failures(state: Any, rng: Any) -> list:
    """Generuje awarie dla serwerów na podstawie modyfikatorów stanu."""
    new_failures: list = []

    for server in state.servers:
        if server.status != "ok":
            continue
        # Bazowe prawdopodobieństwo
        base = balance.FAILURE_BASE_DAILY
        # Modyfikator tieru jakości
        tier_mult = balance.TIER_FAILURE_MULTIPLIER.get(server.quality_tier, 1.0)
        # Modyfikator wieku
        age_mult = balance.FAILURE_MOD_AGE if server.age_days > balance.THRESHOLD_AGE_DAYS else 1.0
        # Modyfikator obciążenia CPU
        load_mult = balance.FAILURE_MOD_OVERLOAD_CPU if server.load_cpu > balance.THRESHOLD_CPU_OVERLOAD else 1.0
        # Modyfikator RAM
        ram_mult = balance.FAILURE_MOD_OVERLOAD_RAM if server.load_ram > balance.THRESHOLD_RAM_OVERLOAD else 1.0
        # Modyfikator chłodzenia (znajdź region)
        cooling_mult = 1.0
        region = next((r for r in state.regions if r.id == server.region_id), None)
        if region and region.cooling_factor < 0.7:
            cooling_mult = balance.FAILURE_MOD_HIGH_TEMP

        p_failure = base * tier_mult * age_mult * load_mult * ram_mult * cooling_mult

        if rng.chance(p_failure):
            # Wybierz typ awarii wg wag
            failure_type = _weighted_choice(balance.FAILURE_TYPES, rng)
            failure = Failure(
                id=f"fail_{state.day}_{server.id}_{failure_type}_{rng.randint(0, 99999)}",
                type=failure_type,
                server_id=server.id,
                region_id=server.region_id,
                started_day=state.day,
                duration_hours=rng.randint(1, 6),
                status="active",
                actions_taken=[],
            )
            # DDoS dotyczy sieci regionu, nie serwera
            if failure_type == "ddos":
                failure.server_id = None
            state.failures_active.append(failure)
            new_failures.append(failure)
            # Serwer oznaczony jako down
            server.status = "down"

    return new_failures


def _weighted_choice(weights: dict[str, float], rng: Any) -> str:
    """Wybiera klucz wg wag."""
    total = sum(weights.values())
    r = rng.random() * total
    cumulative = 0.0
    for key, w in weights.items():
        cumulative += w
        if r <= cumulative:
            return key
    return next(iter(weights))