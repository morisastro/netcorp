"""Logika usług (instances) na serwerach + tickety + auto-rozwiązywanie przez pracowników.

- Klienci kupujący VPS/WWW/dedyk → tworzymy ServiceInstance na konkretnym serwerze
- Serwer ma ograniczone zasoby (CPU/RAM/dysk) — oversubscription możliwa
- Awarie generują tickety; pracownicy (support/sysadmin/neteng) rozwiązują je auto.
"""
from __future__ import annotations

import uuid
from typing import Any

from core.models import ServiceInstance, Ticket
from data import balance


# Zużycie zasobów per typ usługi (jako ułamek całego serwera)
# VPS potrzebuje realne vCPU/RAM/dysk z planu; WWW i dedyk — uproszczone
def service_resource_usage(plan: Any, product_type: str) -> dict[str, float]:
    """Zwraca {cpu, ram_gb, disk_gb} zużywane przez usługę na serwerze."""
    if product_type == "vps":
        return {
            "cpu": plan.cpu_cores,
            "ram_gb": plan.ram_gb,
            "disk_gb": plan.disk_gb,
        }
    elif product_type == "www":
        # Hosting WWW — małe zużycie (1/100 CPU, 1GB RAM, 10GB dysk)
        return {"cpu": 0.05, "ram_gb": 1.0, "disk_gb": 10.0}
    elif product_type == "dedicated":
        # Dedyk — cały serwer dla jednego klienta
        return {
            "cpu": plan.cpu_cores,
            "ram_gb": plan.ram_gb,
            "disk_gb": plan.disk_gb,
        }
    return {"cpu": 0, "ram_gb": 0, "disk_gb": 0}


def server_capacity(server: Any) -> dict[str, float]:
    """Zwraca {cpu, ram_gb, disk_gb} całkowitą pojemność serwera."""
    return {
        "cpu": server.cpu_cores,
        "ram_gb": server.ram_gb,
        "disk_gb": server.disk_gb,
    }


def server_usage(server: Any, services: list[ServiceInstance], plans_by_id: dict) -> dict[str, float]:
    """Zwraca aktualne zużycie {cpu, ram_gb, disk_gb} na serwerze."""
    used = {"cpu": 0.0, "ram_gb": 0.0, "disk_gb": 0.0}
    for svc in services:
        if svc.server_id != server.id or svc.status != "active":
            continue
        plan = plans_by_id.get(svc.plan_id)
        if plan is None:
            continue
        usage = service_resource_usage(plan, svc.product_type)
        used["cpu"] += usage["cpu"]
        used["ram_gb"] += usage["ram_gb"]
        used["disk_gb"] += usage["disk_gb"]
    return used


def server_load(server: Any, services: list[ServiceInstance], plans_by_id: dict) -> dict[str, float]:
    """Zwraca obciążenie serwera {cpu, ram, disk} jako ułamek 0-1."""
    cap = server_capacity(server)
    used = server_usage(server, services, plans_by_id)
    return {
        "cpu": used["cpu"] / max(cap["cpu"], 0.01),
        "ram": used["ram_gb"] / max(cap["ram_gb"], 0.01),
        "disk": used["disk_gb"] / max(cap["disk_gb"], 0.01),
    }


def can_host(server: Any, plan: Any, product_type: str, services: list[ServiceInstance], plans_by_id: dict) -> bool:
    """Czy serwer może przyjąć jeszcze jedną usługę tego planu?"""
    if product_type == "dedicated":
        # Dedyk musi być jedynym klientem na serwerze
        active = [s for s in services if s.server_id == server.id and s.status == "active"]
        return len(active) == 0
    cap = server_capacity(server)
    used = server_usage(server, services, plans_by_id)
    usage = service_resource_usage(plan, product_type)
    return (
        used["cpu"] + usage["cpu"] <= cap["cpu"] * 3.0  # oversubscription 3× (VPSy mogą być overcommit)
        and used["ram_gb"] + usage["ram_gb"] <= cap["ram_gb"] * 2.0
        and used["disk_gb"] + usage["disk_gb"] <= cap["disk_gb"]
    )


def find_server_for_plan(state: Any, plan: Any, product_type: str) -> str | None:
    """Znajduje serwer który może przyjąć usługę. Zwraca server_id lub None."""
    plans_by_id = {p.id: p for p in state.products}
    for server in state.servers:
        if server.status != "ok":
            continue
        if can_host(server, plan, product_type, state.services, plans_by_id):
            return server.id
    return None


def create_service(state: Any, plan: Any, segment: str, rng: Any) -> ServiceInstance | None:
    """Tworzy usługę (klienta) dla danego planu. Zwraca instancję lub None (brak serwera)."""
    if plan.product_type == "domain":
        return None
    server_id = find_server_for_plan(state, plan, plan.product_type)
    if server_id is None:
        return None
    stay = rng.randint(5, 15)  # klienci zostają 5-15 dni (było 1-7)
    svc = ServiceInstance(
        id=f"svc_{uuid.uuid4().hex[:8]}",
        product_type=plan.product_type,
        plan_id=plan.id,
        server_id=server_id,
        segment=segment,
        arrived_day=state.day,
        stay_days=stay,
        monthly_price=plan.price_monthly,
        status="active",
    )
    state.services.append(svc)
    # Jednorazowa opłata setup (zastrzyk gotówki)
    setup = getattr(plan, "setup_fee", 0.0)
    if setup > 0:
        state.cash += setup
    return svc


def update_server_loads(state: Any) -> None:
    """Aktualizuje load_cpu/load_ram na serwerach na podstawie usług."""
    plans_by_id = {p.id: p for p in state.products}
    for server in state.servers:
        load = server_load(server, state.services, plans_by_id)
        server.load_cpu = load["cpu"]
        server.load_ram = load["ram"]


# ---- Tickety ----

def generate_ticket(state: Any, ticket_type: str, instance_id: str | None = None,
                    server_id: str | None = None, description: str = "",
                    priority: int = 1) -> Ticket:
    """Tworzy nowy ticket."""
    ticket = Ticket(
        id=f"tkt_{uuid.uuid4().hex[:8]}",
        type=ticket_type,
        instance_id=instance_id,
        server_id=server_id,
        created_day=state.day,
        priority=priority,
        status="open",
        description=description,
    )
    state.tickets.append(ticket)
    return ticket


def employee_capacity(state: Any, role: str) -> int:
    """Pojemność roli pracowników (sumaryczna)."""
    total = 0
    for emp in state.employees:
        if emp.role == role:
            total += emp.level * balance.EMPLOYEE_CAPACITY_PER_LEVEL
    return total


def auto_resolve_tickets(state: Any, rng: Any) -> dict[str, int]:
    """Pracownicy automatycznie rozwiązują tickety wg roli i poziomu.

    Zwraca {resolved, leftover} per typ.
    """
    result = {"resolved": 0, "leftover": 0}

    # Pojemność per rola
    cap_support = employee_capacity(state, "support")
    cap_sysadmin = employee_capacity(state, "sysadmin")
    cap_neteng = employee_capacity(state, "neteng")

    # Sortuj tickety po priorytecie (wysoki najpierw)
    open_tickets = [t for t in state.tickets if t.status == "open"]
    open_tickets.sort(key=lambda t: -t.priority)

    resolved_count = 0
    for ticket in open_tickets:
        # Wybierz pracownika wg typu ticketa
        if ticket.type in ("support", "sla"):
            cap = cap_support
        elif ticket.type == "failure":
            cap = cap_sysadmin
        elif ticket.type == "network":
            cap = cap_neteng
        else:
            cap = cap_support

        if cap > 0:
            # Rozwiąż ticket (zużyj 1 pojemności)
            ticket.status = "resolved"
            ticket.resolved_day = state.day
            if ticket.type in ("support", "sla"):
                cap_support -= 1
            elif ticket.type == "failure":
                cap_sysadmin -= 1
            elif ticket.type == "network":
                cap_neteng -= 1
            resolved_count += 1
        # else: brak pracownika — ticket zostaje otwarty

    result["resolved"] = resolved_count
    result["leftover"] = sum(1 for t in state.tickets if t.status == "open")
    return result


def churn_services(state: Any, rng: Any) -> int:
    """Usuwa usługi których czas pobytu minął. Zwraca liczbę odeszłych."""
    churned = 0
    keep: list[ServiceInstance] = []
    for svc in state.services:
        if svc.status != "active":
            keep.append(svc)
            continue
        age = state.day - svc.arrived_day
        if age >= svc.stay_days:
            # Klient odchodzi
            churned += 1
        elif age >= svc.stay_days - 1 and rng.chance(0.3):
            churned += 1
        else:
            keep.append(svc)
    state.services = keep

    # Sync z CustomerAggregate (count = liczba aktywnych usług per produkt)
    # Domeny NIE są services — liczone osobno, nie nadpisujemy ich!
    for cust in state.customers:
        if cust.product_type == "domain":
            continue
        cust.count = sum(1 for s in state.services if s.product_type == cust.product_type and s.status == "active")

    return churned


def generate_revenue(state: Any) -> float:
    """Przychód dzienny z wszystkich aktywnych usług.

    Uproszczenie: przychód dzienny = cena miesięczna / 10 (zamiast /30)
    — szybsza rotacja pieniędzy dla lepszej grywalności.
    """
    total = 0.0
    for svc in state.services:
        if svc.status == "active":
            total += svc.monthly_price / 10.0
    # Domeny — $12/rok → ~$1.20/dzień (z marżą)
    for cust in state.customers:
        if cust.product_type == "domain":
            total += cust.count * 1.20
    return total


def setup_fee_income(plan: Any) -> float:
    """Jednorazowy przychód z opłaty setup przy nowej usłudze."""
    return getattr(plan, "setup_fee", 0.0)