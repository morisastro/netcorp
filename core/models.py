"""Modele danych gry — dataclasses serializowalne do JSON.

Wszystkie klasy mają to_dict() / from_dict() do zapisu/odczytu stanu.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Server:
    id: str
    model_id: str            # referencja do data/server_models.py
    quality_tier: str        # "budget" | "standard" | "premium"
    cpu_cores: int
    ram_gb: int
    disk_gb: int
    disk_type: str           # "hdd" | "ssd" | "nvme"
    slot_id: str             # pozycja w serwerowni
    region_id: str
    age_days: int = 0
    mtbf_base: float = 10000.0   # godziny do awarii (modyfikowane przez tier)
    load_cpu: float = 0.0         # 0.0-1.0
    load_ram: float = 0.0
    status: str = "ok"            # "ok" | "down" | "maintenance"
    host_of: list[str] = field(default_factory=list)  # lista plan_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "model_id": self.model_id,
            "quality_tier": self.quality_tier,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "disk_gb": self.disk_gb,
            "disk_type": self.disk_type,
            "slot_id": self.slot_id,
            "region_id": self.region_id,
            "age_days": self.age_days,
            "mtbf_base": self.mtbf_base,
            "load_cpu": self.load_cpu,
            "load_ram": self.load_ram,
            "status": self.status,
            "host_of": list(self.host_of),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Server":
        return cls(**d)


@dataclass
class ProductPlan:
    id: str
    product_type: str       # "www" | "vps" | "dedicated" | "domain"
    name: str
    cpu_cores: int = 0
    ram_gb: int = 0
    disk_gb: int = 0
    bandwidth_mbps: int = 0
    price_monthly: float = 0.0
    sla_target: float = 99.9     # %
    setup_fee: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "product_type": self.product_type,
            "name": self.name,
            "cpu_cores": self.cpu_cores,
            "ram_gb": self.ram_gb,
            "disk_gb": self.disk_gb,
            "bandwidth_mbps": self.bandwidth_mbps,
            "price_monthly": self.price_monthly,
            "sla_target": self.sla_target,
            "setup_fee": self.setup_fee,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ProductPlan":
        return cls(**d)


@dataclass
class CustomerAggregate:
    product_type: str
    segment: str            # "hobbyist" | "small_biz" | "enterprise"
    count: int = 0
    churn_monthly: float = 0.05
    nps: int = 0
    sla_breaches_this_month: int = 0
    # Średni czas pobytu klienta w dniach (1-7 przy zakupie, losowo)
    avg_stay_days: int = 3
    # Dni przyjazdu poszczególnych klientów (do śledzenia wieku; długość == count)
    arrival_days: list[int] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {
            "product_type": self.product_type,
            "segment": self.segment,
            "count": self.count,
            "churn_monthly": self.churn_monthly,
            "nps": self.nps,
            "sla_breaches_this_month": self.sla_breaches_this_month,
            "avg_stay_days": self.avg_stay_days,
            "arrival_days": list(self.arrival_days),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CustomerAggregate":
        d = dict(d)  # kopia, nie mutuj oryginału
        d.setdefault("arrival_days", [])
        return cls(**d)


@dataclass
class Employee:
    id: str
    name: str
    role: str               # "support" | "sysadmin" | "neteng" | "sales" | "marketing"
    level: int              # 1-5
    salary_daily: float = 0.0
    hired_day: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "level": self.level,
            "salary_daily": self.salary_daily,
            "hired_day": self.hired_day,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Employee":
        return cls(**d)


@dataclass
class ServiceInstance:
    """Pojedyncza usługa (VPS/WWW/dedyk) uruchomiona na konkretnym serwerze.

    Reprezentuje faktycznego klienta — zużywa zasoby serwera (CPU/RAM/dysk).
    Domeny nie są instances (nie zużywają serwerów).
    """
    id: str
    product_type: str        # "www" | "vps" | "dedicated"
    plan_id: str             # referencja do ProductPlan
    server_id: str           # na jakim serwerze żyje
    segment: str             # "hobbyist" | "small_biz"
    arrived_day: int         # dzień przyjazdu (do churn)
    stay_days: int           # ile dni zostaje (1-7, losowane)
    monthly_price: float     # cena (kopia z planu)
    status: str = "active"   # "active" | "churning" | "down"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "product_type": self.product_type,
            "plan_id": self.plan_id,
            "server_id": self.server_id,
            "segment": self.segment,
            "arrived_day": self.arrived_day,
            "stay_days": self.stay_days,
            "monthly_price": self.monthly_price,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ServiceInstance":
        return cls(**d)


@dataclass
class Ticket:
    """Ticket supportu — problem zgłoszony przez klienta.

    Typy: support (ogólne), failure (awaria sprzętu), network (sieć), sla (SLA naruszenie).
    Pracownicy automatycznie rozwiązują tickety wg roli i poziomu.
    """
    id: str
    type: str                # "support" | "failure" | "network" | "sla"
    instance_id: str | None  # usługa której dotyczy (None = ogólny)
    server_id: str | None    # serwer jeśli dotyczy
    created_day: int
    priority: int = 1        # 1=niski, 2=średni, 3=wysoki
    status: str = "open"     # "open" | "resolved" | "ignored"
    resolved_day: int = 0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "instance_id": self.instance_id,
            "server_id": self.server_id,
            "created_day": self.created_day,
            "priority": self.priority,
            "status": self.status,
            "resolved_day": self.resolved_day,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Ticket":
        return cls(**d)


@dataclass
class Failure:
    id: str
    type: str               # "disk" | "cpu_overload" | "overheat" | "power" | "network" | "ddos"
    server_id: str | None
    region_id: str
    started_day: int
    duration_hours: int = 1
    status: str = "active"  # "active" | "resolved" | "ignored"
    actions_taken: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "server_id": self.server_id,
            "region_id": self.region_id,
            "started_day": self.started_day,
            "duration_hours": self.duration_hours,
            "status": self.status,
            "actions_taken": list(self.actions_taken),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Failure":
        return cls(**d)


@dataclass
class Region:
    id: str
    name: str
    slots_total: int
    slots_used: int = 0
    power_kw_total: float = 10.0
    power_kw_used: float = 0.0
    network_gbps: float = 1.0
    uplinks: int = 1            # redundancja 1/2/3
    cooling_factor: float = 1.0  # 1.0 = nominal; <1.0 = słabe chłodzenie
    ddos_protection: bool = False
    rent_daily: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slots_total": self.slots_total,
            "slots_used": self.slots_used,
            "power_kw_total": self.power_kw_total,
            "power_kw_used": self.power_kw_used,
            "network_gbps": self.network_gbps,
            "uplinks": self.uplinks,
            "cooling_factor": self.cooling_factor,
            "ddos_protection": self.ddos_protection,
            "rent_daily": self.rent_daily,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Region":
        return cls(**d)


@dataclass
class WebsiteBlock:
    block_type: str            # "hero" | "pricing" | "reviews" | "status" | "faq" | "contact" | "chat" | "blog"
    order: int = 0
    content: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "block_type": self.block_type,
            "order": self.order,
            "content": dict(self.content),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WebsiteBlock":
        return cls(**d)


@dataclass
class Website:
    blocks: list[WebsiteBlock] = field(default_factory=list)

    def conversion_bonus(self) -> float:
        """Bonus do konwersji klientów z marketingu. Zakres 0.0 - 0.5.

        Liczony z liczby i rodzaju bloków na stronie.
        """
        bonus = 0.0
        for block in self.blocks:
            if block.block_type == "hero":
                bonus += 0.05
            elif block.block_type == "pricing":
                bonus += 0.10
            elif block.block_type == "reviews":
                bonus += 0.08
            elif block.block_type == "status":
                bonus += 0.05
            elif block.block_type == "faq":
                bonus += 0.04
            elif block.block_type == "contact":
                bonus += 0.04
            elif block.block_type == "chat":
                bonus += 0.06
            elif block.block_type == "blog":
                bonus += 0.03
        return min(bonus, 0.5)

    def to_dict(self) -> dict[str, Any]:
        return {"blocks": [b.to_dict() for b in self.blocks]}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Website":
        return cls(blocks=[WebsiteBlock.from_dict(b) for b in d.get("blocks", [])])


@dataclass
class GameState:
    day: int = 1
    cash: float = 5000.0
    reputation: float = 50.0       # 0-100
    regions: list[Region] = field(default_factory=list)
    servers: list[Server] = field(default_factory=list)
    products: list[ProductPlan] = field(default_factory=list)
    customers: list[CustomerAggregate] = field(default_factory=list)
    employees: list[Employee] = field(default_factory=list)
    failures_active: list[Failure] = field(default_factory=list)
    failures_history: list[Failure] = field(default_factory=list)
    # Realne usługi na serwerach (VPS/WWW/dedyk) — faktyczni klienci
    services: list[ServiceInstance] = field(default_factory=list)
    # Tickety supportu
    tickets: list[Ticket] = field(default_factory=list)
    marketing_budget_daily: float = 0.0
    website: Website = field(default_factory=Website)
    tickets_open: int = 0
    tickets_resolved_today: int = 0
    unlocked_milestones: list[str] = field(default_factory=list)
    rng_seed: int = 0
    version: str = "0.1.0"
    # Tryb gry (sandbox | career | hardcore)
    game_mode: str = "sandbox"
    # Modyfikator awaryjności (z trybu gry, domyślnie 1.0)
    failure_multiplier: float = 1.0
    # Czy samouczek już pokazany (False = pokaż przy nowej grze)
    tutorial_shown: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "day": self.day,
            "cash": self.cash,
            "reputation": self.reputation,
            "regions": [r.to_dict() for r in self.regions],
            "servers": [s.to_dict() for s in self.servers],
            "products": [p.to_dict() for p in self.products],
            "customers": [c.to_dict() for c in self.customers],
            "employees": [e.to_dict() for e in self.employees],
            "failures_active": [f.to_dict() for f in self.failures_active],
            "failures_history": [f.to_dict() for f in self.failures_history],
            "services": [s.to_dict() for s in self.services],
            "tickets": [t.to_dict() for t in self.tickets],
            "marketing_budget_daily": self.marketing_budget_daily,
            "website": self.website.to_dict(),
            "tickets_open": self.tickets_open,
            "tickets_resolved_today": self.tickets_resolved_today,
            "unlocked_milestones": list(self.unlocked_milestones),
            "rng_seed": self.rng_seed,
            "version": self.version,
            "game_mode": self.game_mode,
            "failure_multiplier": self.failure_multiplier,
            "tutorial_shown": self.tutorial_shown,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "GameState":
        return cls(
            day=d.get("day", 1),
            cash=d.get("cash", 5000.0),
            reputation=d.get("reputation", 50.0),
            regions=[Region.from_dict(r) for r in d.get("regions", [])],
            servers=[Server.from_dict(s) for s in d.get("servers", [])],
            products=[ProductPlan.from_dict(p) for p in d.get("products", [])],
            customers=[CustomerAggregate.from_dict(c) for c in d.get("customers", [])],
            employees=[Employee.from_dict(e) for e in d.get("employees", [])],
            failures_active=[Failure.from_dict(f) for f in d.get("failures_active", [])],
            failures_history=[Failure.from_dict(f) for f in d.get("failures_history", [])],
            services=[ServiceInstance.from_dict(s) for s in d.get("services", [])],
            tickets=[Ticket.from_dict(t) for t in d.get("tickets", [])],
            marketing_budget_daily=d.get("marketing_budget_daily", 0.0),
            website=Website.from_dict(d.get("website", {})),
            tickets_open=d.get("tickets_open", 0),
            tickets_resolved_today=d.get("tickets_resolved_today", 0),
            unlocked_milestones=list(d.get("unlocked_milestones", [])),
            rng_seed=d.get("rng_seed", 0),
            version=d.get("version", "0.1.0"),
            game_mode=d.get("game_mode", "sandbox"),
            failure_multiplier=d.get("failure_multiplier", 1.0),
            tutorial_shown=d.get("tutorial_shown", False),
        )