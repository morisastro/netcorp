"""Ekran Klienci — agregaty per produkt + status."""
from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from data.products import product_name
from ui.widgets.kpi_card import KpiCard


class CustomersScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Klienci")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        # Karty KPI per produkt
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(8)
        layout.addLayout(self.cards_layout)
        self.cards: list[KpiCard] = []

        # Tabela szczegółowa
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Produkt", "Segment", "Klienci", "Churn/mies", "SLA naruszenia"])
        from PySide6.QtWidgets import QHeaderView
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        # Odśwież karty
        for c in self.cards:
            c.deleteLater()
        self.cards.clear()

        for cust in self.game.state.customers:
            card = KpiCard(product_name(cust.product_type), f"{cust.count}")
            self.cards.append(card)
            self.cards_layout.addWidget(card)

        # Tabela
        self.table.setRowCount(0)
        from ui.icons import product_icon
        for i, cust in enumerate(self.game.state.customers):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(f"{product_icon(cust.product_type)}  {product_name(cust.product_type)}"))
            self.table.setItem(i, 1, QTableWidgetItem(cust.segment))
            self.table.setItem(i, 2, QTableWidgetItem(f"👥 {cust.count}"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{cust.churn_monthly*100:.1f}%"))
            sla = cust.sla_breaches_this_month
            sla_item = QTableWidgetItem(f"{'⚠️ ' if sla else ''}{sla}")
            if sla:
                sla_item.setForeground(QColor("#f87171"))
            self.table.setItem(i, 4, sla_item)