"""Schemat save'ów i wersjonowanie."""
from __future__ import annotations

CURRENT_SCHEMA_VERSION = 1


def migrate(state_dict: dict) -> dict:
    """Migruje stan save'a do aktualnej wersji schematu.

    Na razie v1 — bez migracji. W przyszłości: sprawdzić state["schema_version"]
    i aplikować migracje krok po kroku.
    """
    v = state_dict.get("schema_version", 0)
    if v < 1:
        # Dodaj pola wymagane w v1 jeśli brakuje
        state_dict.setdefault("schema_version", CURRENT_SCHEMA_VERSION)
    return state_dict