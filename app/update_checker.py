"""Sprawdzanie aktualizacji — porównanie wersji z najnowszym release na GitHub.

Nie pobiera automatycznie — tylko wyświetla powiadomienie z linkiem do release.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional

from app.settings import APP_VERSION, GITHUB_RELEASES_API


def fetch_latest_release(timeout: float = 5.0) -> Optional[dict]:
    """Pobiera informacje o najnowszym release z GitHub API.

    Zwraca słownik z kluczami: tag_name, name, html_url, body, published_at.
    Zwraca None przy błędzie (brak sieci, timeout, brak release).
    """
    req = urllib.request.Request(
        GITHUB_RELEASES_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "netcorp-tycoon-updater",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def parse_version(version: str) -> tuple[int, ...]:
    """Parsuje 'v0.1.2' lub '0.1.2' do krotki (0, 1, 2)."""
    v = version.lstrip("vV").strip()
    parts: list[int] = []
    for part in v.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            break
    return tuple(parts)


def is_newer(latest: str, current: str) -> bool:
    """Zwraca True jeśli latest > current wg semver."""
    return parse_version(latest) > parse_version(current)


def check_for_update() -> Optional[dict]:
    """Sprawdza aktualizacje. Zwraca dict powiadomienia jeśli jest nowsza wersja.

    Dict: {tag, url, name, body}. None jeśli brak lub błąd.
    """
    release = fetch_latest_release()
    if release is None:
        return None
    latest_tag = release.get("tag_name", "")
    if not latest_tag:
        return None
    if not is_newer(latest_tag, APP_VERSION):
        return None
    return {
        "tag": latest_tag,
        "url": release.get("html_url", ""),
        "name": release.get("name", latest_tag),
        "body": release.get("body", ""),
    }