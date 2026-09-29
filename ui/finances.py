"""Ekran Finanse — przychody, koszty, historia dni."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from core.game import Game
from data import balance


class FinancesScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Finanse")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        # Podsumowanie bieżące
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #d4d4d4; font-size: 14px;")
        layout.addWidget(self.summary_label)

        # Tabela dziennych przychodów/kosztów (placeholder — na razie lista dni)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Dzień", "Przychód", "Koszty", "Saldo"])
        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        state = self.game.state
        # Szacunkowe koszty dzienne (gdyby trwał dzień)
        daily_salary = sum(e.salary_daily for e in state.employees)
        daily_rent = sum(r.rent_daily for r in state.regions)
        daily_licenses = balance.LICENSE_DAILY
        daily_expenses_est = daily_salary + daily_rent + daily_licenses
        daily_income_est = (sum(c.count for c in state.customers) * 15.0) / 30.0

        self.summary_label.setText(
            f"Gotówka: ${state.cash:,.2f}    "
            f"Przychód/dzień: ${daily_income_est:,.2f}    "
            f"Koszty/dzień: ${daily_expenses_est:,.2f}    "
            f"Saldo/dzień: ${daily_income_est - daily_expenses_est:,.2f}"
        )

        # Tabela: historia ostatnich dni (placeholder, wypełnij przy symulacji)
        self.table.setRowCount(0)
        # Na razie pusta — symulacja zacznie wypełniać historię w przyszłości
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem("—"))
        self.table.setItem(0, 1, QTableWidgetItem("—"))
        self.table.setItem(0, 2, QTableWidgetItem("—"))
        self.table.setItem(0, 3, QTableWidgetItem("—"))