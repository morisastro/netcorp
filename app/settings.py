"""Ustawienia aplikacji i ścieżki."""
from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "netcorp-tycoon"
APP_VERSION = "0.2.4"
APP_DISPLAY_NAME = "NetCorp Tycoon"

# Repo GitHub do sprawdzania aktualizacji
GITHUB_REPO = "morisastro/netcorp"  # owner/repo
GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


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