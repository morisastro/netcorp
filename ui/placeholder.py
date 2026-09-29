"""Ekran placeholder — używany dla ekranów nie zaimplementowanych jeszcze."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PlaceholderScreen(QWidget):
    """Prosty ekran 'w budowie'."""

    def __init__(self, title: str, description: str = "", parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        t = QLabel(title)
        t.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(t)

        d = QLabel(description or "Ten ekran zostanie zaimplementowany w kolejnej fazie.")
        d.setStyleSheet("color: #6a6a6a;")
        d.setWordWrap(True)
        layout.addWidget(d)
        layout.addStretch()