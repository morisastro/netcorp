"""System modów — ładuje pliki JSON z folderu mods/ obok gry.

Mody to pliki .json w folderze mods/. Każdy mod może nadpisywać:
  - balance (stałe balansu)
  - server_models (katalog serwerów)
  - tlds (domeny)
  - names (imiona)

Mody są opcjonalne — brak folderu/modów = gra domyślna.

Format pliku mod.json:
{
  "name": "Mój mod",
  "version": "1.0",
  "author": "autor",
  "balance": {
    "FAILURE_BASE_DAILY": 0.05,
    "MARKETING_COST_PER_NEW_CUSTOMER": 10.0
  },
  "server_models": [
    { "id": "custom_server", "name": "Mój serwer", "cpu_cores": 99, ... }
  ]
}

Modding API — mody nie modyfikują kodu gry, tylko dane JSON.
Zgodne z licencją CC BY-ND 4.0 (mody to osobne pakiety, nie derivative work).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def mods_dir() -> Path:
    """Folder mods/ — obok exe (PyInstaller) lub w katalogu projektu (dev)."""
    import sys
    if hasattr(sys, '_MEIPASS') or getattr(sys, 'frozen', False):
        # PyInstaller — mods obok exe (gracz może tam dodawać mody)
        base = Path(sys.executable).parent / "mods"
    else:
        # Dev mode — mods w katalogu projektu
        base = Path(__file__).resolve().parent.parent / "mods"
    base.mkdir(parents=True, exist_ok=True)
    return base


def list_mods() -> list[dict[str, Any]]:
    """Zwraca listę zainstalowanych modów z folderu mods/.

    Każdy wpis: {name, version, author, file, enabled, description}
    """
    mods: list[dict[str, Any]] = []
    for path in sorted(mods_dir().glob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            mods.append({
                "name": data.get("name", path.stem),
                "version": data.get("version", "1.0"),
                "author": data.get("author", "nieznany"),
                "file": path.name,
                "enabled": data.get("enabled", True),
                "description": data.get("description", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return mods


def load_mods() -> dict[str, Any]:
    """Ładuje wszystkie włączone mody i zwraca scalone dane.

    Zwraca dict z kluczami: balance, server_models, tlds, names
    (każdy klucz jest opcjonalny — brak = brak nadpisania).
    """
    merged: dict[str, Any] = {
        "balance": {},
        "server_models": [],
        "tlds": [],
        "names": {},
    }
    for mod_info in list_mods():
        if not mod_info.get("enabled", True):
            continue
        path = mods_dir() / mod_info["file"]
        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # Scal balance (nadpisz klucze)
            if "balance" in data:
                merged["balance"].update(data["balance"])
            # Dodaj server_models (dodaj do listy)
            if "server_models" in data:
                merged["server_models"].extend(data["server_models"])
            # Dodaj tlds
            if "tlds" in data:
                merged["tlds"].extend(data["tlds"])
            # Nadpisz names
            if "names" in data:
                merged["names"].update(data["names"])
        except (json.JSONDecodeError, OSError):
            continue
    return merged