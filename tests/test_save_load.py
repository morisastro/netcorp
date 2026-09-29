"""Testy save/load."""
from __future__ import annotations

from pathlib import Path

import pytest

from core.game import Game
from persistence import save_load


def test_save_and_load_roundtrip(tmp_path, monkeypatch):
    """Zapis i odczyt gry zachowuje stan."""
    # Mock save_dir na tymczasowy katalog
    monkeypatch.setattr(save_load, "save_dir", lambda: tmp_path)

    game = Game.new_game()
    game.state.cash = 1234.56
    save_load.save_game(game, "test_save")

    loaded = save_load.load_game("test_save")
    assert loaded.state.cash == 1234.56
    assert loaded.state.day == game.state.day


def test_list_saves_returns_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(save_load, "save_dir", lambda: tmp_path)

    game = Game.new_game()
    save_load.save_game(game, "partia1")
    save_load.save_game(game, "partia2")

    saves = save_load.list_saves()
    names = {s["name"] for s in saves}
    assert "partia1" in names
    assert "partia2" in names


def test_autosave_uses_special_name(tmp_path, monkeypatch):
    monkeypatch.setattr(save_load, "save_dir", lambda: tmp_path)

    game = Game.new_game()
    save_load.autosave(game)

    saves = save_load.list_saves()
    autosaves = [s for s in saves if s["is_autosave"]]
    assert len(autosaves) == 1