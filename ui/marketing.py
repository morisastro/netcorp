"""Ekran Marketing — budżet dzienny, ROI, przyrost klientów."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from data import balance


class MarketingScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Marketing")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        info = QLabel(
            "Marketing przyciąga nowych klientów. Im więcej wydajesz, tym więcej klientów dziennie.\n"
            f"Koszt pozyskania: ~${balance.MARKETING_COST_PER_NEW_CUSTOMER:.0f} / nowy klient.\n"
            "Dobra strona firmy (bonus) zwiększa efektywność marketingu."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        # Ustawienie budżetu
        budget_row = QHBoxLayout()
        budget_row.setSpacing(8)
        budget_row.addWidget(QLabel("Budżet dzienny: $"))
        self.budget_spin = QDoubleSpinBox()
        self.budget_spin.setRange(0, 100000)
        self.budget_spin.setDecimals(2)
        self.budget_spin.setSingleStep(50)
        self.budget_spin.setValue(self.game.state.marketing_budget_daily)
        budget_row.addWidget(self.budget_spin)
        self.btn_apply = QPushButton("Zastosuj")
        self.btn_apply.setObjectName("primary")
        self.btn_apply.clicked.connect(self._on_apply_budget)
        budget_row.addWidget(self.btn_apply)
        budget_row.addStretch()
        layout.addLayout(budget_row)

        # Szybkie przyciski
        quick_row = QHBoxLayout()
        for amount in (0, 100, 500, 1000, 5000):
            btn = QPushButton(f"${amount}")
            btn.clicked.connect(lambda checked=False, a=amount: self._quick_set(a))
            quick_row.addWidget(btn)
        quick_row.addStretch()
        layout.addLayout(quick_row)

        # KPI
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(8)
        self.card_budget = _info_card("Budżet dzienny", "$0")
        self.card_estimate = _info_card("Szacunkowo nowych/dzień", "0")
        self.card_cost = _info_card("Koszt / klient", f"${balance.MARKETING_COST_PER_NEW_CUSTOMER:.0f}")
        for c in (self.card_budget, self.card_estimate, self.card_cost):
            kpi_row.addWidget(c)
        layout.addLayout(kpi_row)

        layout.addStretch()

    def _quick_set(self, amount: float) -> None:
        self.budget_spin.setValue(amount)
        self._on_apply_budget()

    def _on_apply_budget(self) -> None:
        self.game.state.marketing_budget_daily = self.budget_spin.value()
        self.refresh()

    def refresh(self) -> None:
        budget = self.game.state.marketing_budget_daily
        self.card_budget.set_value(f"${budget:,.2f}")
        est_new = int(budget / balance.MARKETING_COST_PER_NEW_CUSTOMER)
        self.card_estimate.set_value(f"~{est_new}/dzień")
        self.budget_spin.setValue(budget)


def _info_card(title: str, value: str) -> QFrame:
    from ui.widgets.kpi_card import KpiCard
    return KpiCard(title, value)