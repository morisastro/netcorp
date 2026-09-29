"""Wykrywanie rozmiaru ekranu i skalowanie UI."""
from __future__ import annotations

import os


def screen_size() -> tuple[int, int]:
    """Zwraca (szerokość, wysokość) ekranu w pikselach."""
    try:
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            geo = screen.geometry()
            return geo.width(), geo.height()
    except Exception:
        pass
    return 1920, 1080  # domyślnie


def recommended_window_size() -> tuple[int, int]:
    """Rekomendowany rozmiar okna gry (85% ekranu, max 1600x1000)."""
    w, h = screen_size()
    # 85% ekranu, ale nie mniej niż 1024x640
    win_w = max(1024, min(1600, int(w * 0.85)))
    win_h = max(640, min(1000, int(h * 0.85)))
    return win_w, win_h


def recommended_menu_size() -> tuple[int, int]:
    """Rekomendowany rozmiar menu startowego (60% ekranu, max 900x600)."""
    w, h = screen_size()
    win_w = max(760, min(900, int(w * 0.6)))
    win_h = max(520, min(600, int(h * 0.6)))
    return win_w, win_h


def is_small_screen() -> bool:
    """True jeśli ekran jest mały (mniej niż 1400px szerokości)."""
    w, _ = screen_size()
    return w < 1400


def grid_columns_for_width(width: int, min_cols: int = 2, max_cols: int = 4) -> int:
    """Liczy liczbę kolumn w gridzie dla danej szerokości."""
    # ~280px na kolumnę
    cols = max(min_cols, min(max_cols, width // 280))
    return cols


def svg_height_for_screen() -> int:
    """Wysokość SVG serwerowni dostosowana do ekranu."""
    _, h = screen_size()
    if h <= 800:
        return 160
    if h <= 1000:
        return 200
    return 240