"""Ekran Dashboard — KPI, alerty, podsumowanie."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from data.products import product_name
from ui.widgets.kpi_card import KpiCard


class DashboardScreen(QWidget):
    """Ekran główny — przegląd firmy."""

    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        title = QLabel("Przegląd firmy")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4d4d4;")
        outer.addWidget(title)

        # Rząd KPI
        kpi_row = QGridLayout()
        kpi_row.setSpacing(12)
        outer.addLayout(kpi_row)

        self.card_cash = KpiCard("Gotówka")
        self.card_customers = KpiCard("Klienci (łącznie)")
        self.card_reputation = KpiCard("Reputacja")
        self.card_servers = KpiCard("Serwery")
        self.card_failures = KpiCard("Aktywne awarie")
        self.card_tickets = KpiCard("Otwarte tickety")

        cards = [
            self.card_cash,
            self.card_customers,
            self.card_reputation,
            self.card_servers,
            self.card_failures,
            self.card_tickets,
        ]
        for i, card in enumerate(cards):
            kpi_row.addWidget(card, i // 3, i % 3)

        # Sekcja: klienci per produkt
        outer.addSpacing(8)
        section_title = QLabel("Klienci per produkt")
        section_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9a9a9a;")
        outer.addWidget(section_title)

        self.customers_grid = QGridLayout()
        self.customers_grid.setSpacing(8)
        outer.addLayout(self.customers_grid)

        # Sekcja: ostatnie awarie / alerty
        outer.addSpacing(8)
        alerts_title = QLabel("Alerty / ostatnie awarie")
        alerts_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9a9a9a;")
        outer.addWidget(alerts_title)

        self.alerts_box = QLabel("Brak aktywnych awarii.")
        self.alerts_box.setStyleSheet("color: #4ade80; padding: 8px;")
        outer.addWidget(self.alerts_box)

        outer.addStretch()

    def refresh(self) -> None:
        """Odświeża dane z Game."""
        state = self.game.state

        self.card_cash.set_value(f"${state.cash:,.2f}")
        self.card_customers.set_value(f"{self.game.total_customers()}")
        self.card_reputation.set_value(f"{state.reputation:.0f}/100")
        self.card_servers.set_value(f"{len(state.servers)}")
        self.card_failures.set_value(f"{len(state.failures_active)}")
        self.card_tickets.set_value(f"{state.tickets_open}")

        # Statusy kolorystyczne
        if state.cash < 1000:
            self.card_cash.set_status("error")
        elif state.cash < 5000:
            self.card_cash.set_status("warn")
        else:
            self.card_cash.set_status("ok")

        if state.reputation >= 70:
            self.card_reputation.set_status("ok")
        elif state.reputation >= 40:
            self.card_reputation.set_status("warn")
        else:
            self.card_reputation.set_status("error")

        if state.failures_active:
            self.card_failures.set_status("error")
            self.card_failures.set_value(f"{len(state.failures_active)} ⚠")
        else:
            self.card_failures.set_status("ok")

        if state.tickets_open > 0:
            self.card_tickets.set_status("warn")
        else:
            self.card_tickets.set_status("ok")

        # Klienci per produkt
        self._refresh_customers_grid()

        # Alerty
        if state.failures_active:
            lines = []
            for f in state.failures_active:
                lines.append(f"⚠ Awarria typu {f.type} — serwer {f.server_id or 'DC'}")
            self.alerts_box.setText("\n".join(lines))
            self.alerts_box.setStyleSheet("color: #f87171; padding: 8px;")
        else:
            self.alerts_box.setText("Brak aktywnych awarii.")
            self.alerts_box.setStyleSheet("color: #4ade80; padding: 8px;")

    def _refresh_customers_grid(self) -> None:
        # Wyczyść
        while self.customers_grid.count():
            item = self.customers_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, cust in enumerate(self.game.state.customers):
            name = product_name(cust.product_type)
            card = KpiCard(name, f"{cust.count}")
            self.customers_grid.addWidget(card, i // 4, i % 4)