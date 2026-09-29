"""Karta KPI — mała kafelek z tytułem i wartością."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class KpiCard(QFrame):
    """Karta KPI: tytuł (mały, szary) + wartość (duży, bold)."""

    def __init__(self, title: str, value: str = "—", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("card-title")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("card-value")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def set_status(self, status: str) -> None:
        """status: 'ok' | 'warn' | 'error' | 'down' — zmienia kolor wartości."""
        # Usuń poprzednie statusy
        for s in ("status-ok", "status-warn", "status-error", "status-down"):
            self.value_label.objectName()  # noop
        self.value_label.setProperty("status", status)
        self.style().unpolish(self.value_label)
        self.style().polish(self.value_label)