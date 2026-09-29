"""Podstawowa symulacja tury — ekonomia, awarie, churn, pracownicy, tickety.

Tu trafia logika wywoływana przez Game.next_day().
"""
from __future__ import annotations

from typing import Any

from core.models import Failure
from core import services as svc
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
    new_tickets = 0
    milestones: list = []

    # ---- Koszty pracowników ----
    for emp in state.employees:
        expenses += emp.salary_daily

    # ---- Koszt stały (licencje) ----
    expenses += balance.LICENSE_DAILY

    # ---- Koszt wynajmu regionów + prąd ----
    for region in state.regions:
        expenses += region.rent_daily
        expenses += region.power_kw_used * balance.POWER_PRICE_PER_KWH * 24

    # ---- Aktualizacja obciążenia serwerów ----
    svc.update_server_loads(state)

    # ---- Awarie ----
    new_failures = _generate_failures(state, rng)
    # Awarie generują tickety dla usług na serwerach
    for f in new_failures:
        if f.server_id:
            # Znajdź usługi na tym serwerze → każdy klient zgłasza ticket
            affected = [s for s in state.services if s.server_id == f.server_id and s.status == "active"]
            for inst in affected[:3]:  # max 3 tickety na awarię (żeby nie zalło)
                ticket_type = "network" if f.type in ("network", "ddos") else "failure"
                svc.generate_ticket(
                    state, ticket_type,
                    instance_id=inst.id, server_id=f.server_id,
                    description=f"Awararia {f.type} na serwerze {f.server_id}",
                    priority=3 if f.type in ("ddos", "power") else 2,
                )
                new_tickets += 1

    # ---- Przyrost klientów (nowe usługi na serwerach) ----
    marketing = state.marketing_budget_daily
    total_active = sum(1 for s in state.services if s.status == "active")

    if state.reputation > 20 and rng.chance(0.4):
        new_customers += 1
    elif rng.chance(0.15):
        new_customers += 1
    if marketing > 0 and total_active < 100000:
        website_bonus = state.website.conversion_bonus() if state.website else 0.0
        conv_rate = 1.0 + website_bonus
        from_marketing = int(marketing / balance.MARKETING_COST_PER_NEW_CUSTOMER * conv_rate)
        new_customers += from_marketing
    if len(state.products) >= 1 and rng.chance(0.25):
        new_customers += 1

    # Twórz usługi dla nowych klientów
    placed_customers = 0
    unplaced = 0
    if new_customers > 0 and state.products:
        product_weights = _product_weights(state)
        if product_weights:
            for _ in range(new_customers):
                r = rng.random()
                cumulative = 0.0
                for pt, w in product_weights.items():
                    cumulative += w
                    if r <= cumulative:
                        # Wybierz plan dla tego produktu
                        plans = [p for p in state.products if p.product_type == pt]
                        if plans:
                            plan = rng.choice(plans)
                            segment = "hobbyist" if plan.price_monthly < 20 else "small_biz"
                            if pt == "domain":
                                # Domeny → tylko CustomerAggregate, bez ServiceInstance
                                for cust in state.customers:
                                    if cust.product_type == "domain":
                                        cust.count += 1
                                        cust.arrival_days.append(state.day)
                                        cust.avg_stay_days = rng.randint(30, 365)  # domeny zostają długo
                                        break
                                placed_customers += 1
                            else:
                                instance = svc.create_service(state, plan, segment, rng)
                                if instance is not None:
                                    placed_customers += 1
                                else:
                                    unplaced += 1  # brak serwera — klient nie kupił
                        break
    new_customers = placed_customers
    if unplaced > 0:
        # Brak serwerów → klienci zniechęceni → reputacja -
        state.reputation = max(0, state.reputation - unplaced * 0.5)

    # ---- Sync CustomerAggregate z services ----
    for cust in state.customers:
        if cust.product_type == "domain":
            continue  # domeny liczone osobno
        cust.count = sum(1 for s in state.services if s.product_type == cust.product_type and s.status == "active")

    # ---- Churn usług ----
    churned = svc.churn_services(state, rng)

    # ---- Przychód z aktywnych usług ----
    income = svc.generate_revenue(state)

    # ---- Auto-rozwiązywanie ticketów przez pracowników ----
    ticket_result = svc.auto_resolve_tickets(state, rng)
    tickets_resolved = ticket_result["resolved"]
    state.tickets_resolved_today = tickets_resolved
    state.tickets_open = ticket_result["leftover"]

    # Nierozwiązane tickety → spadek reputacji
    if state.tickets_open > 0:
        state.reputation = max(0, state.reputation - state.tickets_open * 0.2)
    elif tickets_resolved > 0:
        state.reputation = min(100, state.reputation + 0.1)

    # ---- Aktualizacja gotówki ----
    state.cash += income - expenses

    # ---- Odsetki od pożyczki ----
    if state.debt > 0:
        interest = state.debt * state.debt_daily_interest
        state.debt += interest
        state.cash -= interest

    # ---- Bankructwo ----
    if state.cash < 0 and not state.bankrupt:
        state.bankrupt = True

    # ---- Reputacja z awarii ----
    if state.failures_active:
        state.reputation = max(0, state.reputation - len(state.failures_active) * 0.5)
    elif total_active > 0 and not state.failures_active and tickets_resolved > 0:
        state.reputation = min(100, state.reputation + 0.1)

    # ---- Kamienie milowe ----
    total = sum(c.count for c in state.customers)
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
        "tickets_open": state.tickets_open,
        "new_tickets": new_tickets,
        "milestones_unlocked": milestones,
        "bankrupt": state.bankrupt,
        "debt": state.debt,
    }


def _product_weights(state: Any) -> dict[str, float]:
    """Wagi produktów do rozdzielania nowych klientów."""
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
        base = balance.FAILURE_BASE_DAILY
        tier_mult = balance.TIER_FAILURE_MULTIPLIER.get(server.quality_tier, 1.0)
        age_mult = balance.FAILURE_MOD_AGE if server.age_days > balance.THRESHOLD_AGE_DAYS else 1.0
        load_mult = balance.FAILURE_MOD_OVERLOAD_CPU if server.load_cpu > balance.THRESHOLD_CPU_OVERLOAD else 1.0
        ram_mult = balance.FAILURE_MOD_OVERLOAD_RAM if server.load_ram > balance.THRESHOLD_RAM_OVERLOAD else 1.0
        cooling_mult = 1.0
        region = next((r for r in state.regions if r.id == server.region_id), None)
        if region and region.cooling_factor < 0.7:
            cooling_mult = balance.FAILURE_MOD_HIGH_TEMP

        p_failure = base * tier_mult * age_mult * load_mult * ram_mult * cooling_mult
        p_failure *= getattr(state, "failure_multiplier", 1.0)

        if rng.chance(p_failure):
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
            if failure_type == "ddos":
                failure.server_id = None
            state.failures_active.append(failure)
            new_failures.append(failure)
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