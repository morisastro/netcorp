"""Save/load stanu gry do plików JSON w ~/.netcorp-tycoon/saves/.

Każda partia = osobny plik .json z nazwą zapisu.
Multi-slot, autosave na koniec dnia (_autosave.json), manualny save pod nazwą.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.settings import save_dir
from core.game import Game
from core.models import GameState
from persistence.schemas import CURRENT_SCHEMA_VERSION, migrate

AUTOSAVE_NAME = "_autosave"


def _save_path(name: str) -> Path:
    """Pełna ścieżka pliku zapisu."""
    safe_name = name.replace("/", "_").replace("\\", "_").strip()
    return save_dir() / f"{safe_name}.json"


def save_game(game: Game, name: str) -> Path:
    """Zapisuje stan gry do pliku .json. Zwraca ścieżkę pliku."""
    state_dict = game.state.to_dict()
    state_dict["schema_version"] = CURRENT_SCHEMA_VERSION
    state_dict["saved_at"] = datetime.now().isoformat(timespec="seconds")
    state_dict["save_name"] = name
    path = _save_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state_dict, f, ensure_ascii=False, indent=2)
    return path


def autosave(game: Game) -> Path:
    """Zapis automatyczny (nadpisuje _autosave.json)."""
    return save_game(game, AUTOSAVE_NAME)


def load_game(name: str) -> Game:
    """Wczytuje stan gry z pliku .json."""
    path = _save_path(name)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data = migrate(data)
    state = GameState.from_dict(data)
    return Game(state=state)


def load_from_path(path: Path) -> Game:
    """Wczytuje stan gry z konkretnej ścieżki."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    data = migrate(data)
    state = GameState.from_dict(data)
    return Game(state=state)


def list_saves() -> list[dict[str, Any]]:
    """Zwraca listę zapisów z metadanymi (do ekranu ładowania).

    Każdy wpis: {name, path, day, cash, customers, saved_at, is_autosave}
    """
    saves: list[dict[str, Any]] = []
    for path in save_dir().glob("*.json"):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            saves.append({
                "name": data.get("save_name", path.stem),
                "path": str(path),
                "day": data.get("day", 0),
                "cash": data.get("cash", 0.0),
                "customers": sum(c.get("count", 0) for c in data.get("customers", [])),
                "saved_at": data.get("saved_at", ""),
                "is_autosave": path.stem == AUTOSAVE_NAME,
            })
        except (json.JSONDecodeError, OSError):
            # Pomiń uszkodzone pliki
            continue
    # Sortuj: najnowsze najpierw
    saves.sort(key=lambda s: s["saved_at"], reverse=True)
    return saves


def delete_save(name: str) -> bool:
    """Usuwa plik zapisu. Zwraca True jeśli usunięto."""
    path = _save_path(name)
    if path.exists():
        path.unlink()
        return True
    return False