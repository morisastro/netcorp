"""Główny obiekt gry — stan + akcje + symulacja tury.

UI wywołuje metody na obiekcie Game i czyta stan przez get_state_snapshot().
Game jest jedynym źródłem prawdy o stanie gry.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from core.models import (
    CustomerAggregate,
    GameState,
    Region,
    Server,
)
from core.rng import GameRNG


# Domyślny start: garaż / home lab
DEFAULT_CASH = 5000.0
DEFAULT_REPUTATION = 50.0
DEFAULT_RNG_SEED = 42


def _new_garage_region() -> Region:
    """Początkowy region — garaż z 1 starym serwerem i ograniczonymi zasobami."""
    return Region(
        id="region_garage",
        name="Garaż (home lab)",
        slots_total=3,
        slots_used=1,
        power_kw_total=2.0,
        power_kw_used=0.3,
        network_gbps=0.1,
        uplinks=1,
        cooling_factor=0.6,      # słabe chłodzenie w garażu
        ddos_protection=False,
        rent_daily=0.0,          # garaż bezczynszowy
    )


def _new_default_server(region_id: str) -> Server:
    """Początkowy stary serwer — tier budget."""
    return Server(
        id="srv_initial",
        model_id="old_rack_server",
        quality_tier="budget",
        cpu_cores=4,
        ram_gb=8,
        disk_gb=500,
        disk_type="hdd",
        slot_id="slot_0",
        region_id=region_id,
        age_days=0,
        mtbf_base=4000.0,        # budget tier = niski MTBF
        load_cpu=0.0,
        load_ram=0.0,
        status="ok",
        host_of=[],
    )


class Game:
    """Główny obiekt gry."""

    def __init__(self, state: GameState | None = None) -> None:
        if state is None:
            state = self._initial_state()
        self.state = state
        self.rng = GameRNG(state.rng_seed or DEFAULT_RNG_SEED)

    # ---- inicjalizacja ----

    @staticmethod
    def _initial_state() -> GameState:
        region = _new_garage_region()
        server = _new_default_server(region.id)
        # Domyślni klienci per produkt (puste na start)
        customers = [
            CustomerAggregate(product_type="www", segment="hobbyist", count=0),
            CustomerAggregate(product_type="vps", segment="hobbyist", count=0),
            CustomerAggregate(product_type="dedicated", segment="small_biz", count=0),
            CustomerAggregate(product_type="domain", segment="hobbyist", count=0),
        ]
        return GameState(
            day=1,
            cash=DEFAULT_CASH,
            reputation=DEFAULT_REPUTATION,
            regions=[region],
            servers=[server],
            customers=customers,
            rng_seed=DEFAULT_RNG_SEED,
        )

    @classmethod
    def new_game(cls) -> "Game":
        return cls()

    # ---- snapshot dla UI ----

    def get_state_snapshot(self) -> dict[str, Any]:
        """Zwraca widok stanu do wyświetlenia w UI."""
        return self.state.to_dict()

    # ---- akcje gracza (placeholder do rozszerzenia) ----

    def next_day(self) -> dict[str, Any]:
        """Symuluje jeden dzień. Zwraca raport dzienny."""
        from core.simulation import simulate_day
        report = simulate_day(self.state, self.rng)
        self.state.day += 1
        # Wiek serwerów +1 dzień
        for s in self.state.servers:
            s.age_days += 1
        return report

    # ---- KPI helpers ----

    def total_customers(self) -> int:
        return sum(c.count for c in self.state.customers)

    def cash(self) -> float:
        return self.state.cash

    def day(self) -> int:
        return self.state.day

    def reputation(self) -> float:
        return self.state.reputation

    def date_label(self) -> str:
        """Etykieta daty w grze (dzień + data kalendarzowa)."""
        start = date(2030, 1, 1)
        current = date.fromordinal(start.toordinal() + (self.state.day - 1))
        return f"Dzień {self.state.day} • {current.isoformat()}"