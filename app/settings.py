"""Ustawienia aplikacji i ścieżki."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "netcorp-tycoon"
APP_VERSION = "0.2.6"
APP_DISPLAY_NAME = "NetCorp Tycoon"

# Repo GitHub do sprawdzania aktualizacji
GITHUB_REPO = "morisastro/netcorp"  # owner/repo
GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_ISSUES_URL = f"https://github.com/{GITHUB_REPO}/issues"
GITHUB_REPO_URL = f"https://github.com/{GITHUB_REPO}"

# Debug mode — włączane w Ustawieniach (zapisywane w pliku)
def is_debug() -> bool:
    """Zwraca True jeśli debug mode włączony."""
    try:
        import json
        path = app_data_dir() / "settings.json"
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f).get("debug", False)
    except Exception:
        pass
    return False

def set_debug(enabled: bool) -> bool:
    """Włącza/wyłącza debug mode (zapis w settings.json)."""
    try:
        import json
        path = app_data_dir() / "settings.json"
        data = {}
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        data["debug"] = enabled
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f)
        return True
    except Exception:
        return False


def save_dir() -> Path:
    """Katalog na zapisy gry: ~/.netcorp-tycoon/saves/"""
    home = Path.home()
    base = home / ".netcorp-tycoon" / "saves"
    base.mkdir(parents=True, exist_ok=True)
    return base


def app_data_dir() -> Path:
    """Katalog danych aplikacji: ~/.netcorp-tycoon/"""
    base = Path.home() / ".netcorp-tycoon"
    base.mkdir(parents=True, exist_ok=True)
    return base


def app_icon_path() -> str:
    """Zwraca ścieżkę logo.ico — działa w dev i w bundlu PyInstaller."""
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, 'assets', 'logo.ico')
    # Dev mode: katalog projektu / assets / logo.ico
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, '..', 'assets', 'logo.ico'))