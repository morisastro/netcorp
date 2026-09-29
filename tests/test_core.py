"""Testy logiki core — uruchamiane przez pytest, bez Qt."""
from __future__ import annotations

from core.game import Game
from core.models import Employee, CustomerAggregate


def test_new_game_starts_with_garage():
    game = Game.new_game()
    assert game.state.cash > 0
    assert len(game.state.regions) == 1
    # Nazwa może być zmieniona przez mod (game_settings.start_region_name)
    assert "garaż" in game.state.regions[0].name.lower() or "garaz" in game.state.regions[0].name.lower()
    assert len(game.state.servers) == 1
    assert game.state.servers[0].quality_tier == "budget"


def test_new_game_has_empty_customer_aggregates():
    game = Game.new_game()
    assert len(game.state.customers) == 4
    assert all(c.count == 0 for c in game.state.customers)
    product_types = {c.product_type for c in game.state.customers}
    assert product_types == {"www", "vps", "dedicated", "domain"}


def test_next_day_advances_day():
    game = Game.new_game()
    initial_day = game.state.day
    game.next_day()
    assert game.state.day == initial_day + 1


def test_next_day_ages_servers():
    game = Game.new_game()
    initial_age = game.state.servers[0].age_days
    game.next_day()
    assert game.state.servers[0].age_days == initial_age + 1


def test_next_day_with_employees_pays_salary():
    game = Game.new_game()
    initial_cash = game.state.cash
    game.state.employees.append(
        Employee(id="e1", name="Test Person", role="support", level=2, salary_daily=100.0)
    )
    game.next_day()
    # Gotówka powinna spaść o pensję (plus inne koszty stałe)
    assert game.state.cash < initial_cash


def test_next_day_deterministic_with_seed():
    """Ten sam seed → ta sama sekwencja zdarzeń losowych."""
    game1 = Game.new_game()
    game2 = Game.new_game()
    for _ in range(10):
        r1 = game1.next_day()
        r2 = game2.next_day()
        assert r1 == r2


def test_state_serialization_roundtrip():
    """Stan gry można serializować i deserializować."""
    game = Game.new_game()
    game.state.cash = 9999.0
    game.state.employees.append(
        Employee(id="e1", name="Test Person", role="sysadmin", level=3)
    )
    state_dict = game.state.to_dict()
    from core.models import GameState
    restored = GameState.from_dict(state_dict)
    assert restored.cash == 9999.0
    assert len(restored.employees) == 1
    assert restored.employees[0].name == "Test Person"


def test_total_customers_aggregates_all_segments():
    game = Game.new_game()
    # Teraz total_customers liczy z aktywnych usług + domen
    # Dodajemy usługi ręcznie
    from core.models import ServiceInstance
    for i in range(10):
        game.state.services.append(
            ServiceInstance(
                id=f"svc_{i}", product_type="www", plan_id="p", server_id="srv_initial",
                segment="hobbyist", arrived_day=1, stay_days=5, monthly_price=10,
            )
        )
    game.state.customers[3].count = 5  # domeny (product_type=domain na idx 3)
    assert game.total_customers() == 15