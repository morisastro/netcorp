"""Ekran Finanse — przychody, koszty, historia, pożyczka."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from data import balance


# Parametry pożyczki
LOAN_RATE = 0.5       # $ pożyczki per utracony klient (za każdy klienta dostajesz $0.50)
LOAN_MIN_CLIENTS = 5  # minimum klientów żeby wziąć pożyczkę
LOAN_INTEREST_DAILY = 0.001  # 0.1% dziennie odsetek


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
        self.summary_label.setStyleSheet("color: #d4d4d4; font-size: 14px; padding: 12px; background: #1f1f1f; border-radius: 4px;")
        layout.addWidget(self.summary_label)

        # ---- Sekcja pożyczki ----
        loan_title = QLabel("💵 Pożyczka (w zamian za część klientów)")
        loan_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #facc15; margin-top: 8px;")
        layout.addWidget(loan_title)

        loan_info = QLabel(
            f"Możesz wziąć pożyczkę — dostajesz ${LOAN_RATE:.2f} za każdego utraconego klienta.\n"
            f"Koszt: {LOAN_INTEREST_DAILY*100:.1f}% odsetek dziennie (rosnący dług).\n"
            f"Minimum: {LOAN_MIN_CLIENTS} klientów."
        )
        loan_info.setStyleSheet("color: #9a9a9a;")
        loan_info.setWordWrap(True)
        layout.addWidget(loan_info)

        # Aktualny dług
        self.debt_label = QLabel("")
        self.debt_label.setStyleSheet("color: #f87171; font-weight: bold; padding: 8px; background: #2a1a1a; border-radius: 4px;")
        layout.addWidget(self.debt_label)

        # Input: ilu klientów oddać
        loan_row = QHBoxLayout()
        loan_row.setSpacing(8)
        loan_row.addWidget(QLabel("Klienci do oddania:"))
        self.loan_customers_spin = QDoubleSpinBox()
        self.loan_customers_spin.setRange(0, 100000)
        self.loan_customers_spin.setDecimals(0)
        self.loan_customers_spin.setSingleStep(5)
        self.loan_customers_spin.valueChanged.connect(self._update_loan_amount)
        loan_row.addWidget(self.loan_customers_spin)

        self.loan_amount_label = QLabel("")
        self.loan_amount_label.setStyleSheet("color: #4ade80; font-weight: bold;")
        loan_row.addWidget(self.loan_amount_label)
        loan_row.addStretch()

        self.btn_take_loan = QPushButton("Weź pożyczkę")
        self.btn_take_loan.setObjectName("primary")
        self.btn_take_loan.clicked.connect(self._on_take_loan)
        loan_row.addWidget(self.btn_take_loan)
        layout.addLayout(loan_row)

        # Spłata długu
        repay_row = QHBoxLayout()
        repay_row.setSpacing(8)
        repay_row.addWidget(QLabel("Spłać $:"))
        self.repay_spin = QDoubleSpinBox()
        self.repay_spin.setRange(0, 1000000)
        self.repay_spin.setDecimals(2)
        self.repay_spin.setSingleStep(100)
        repay_row.addWidget(self.repay_spin)

        self.btn_repay = QPushButton("Spłać dług")
        self.btn_repay.clicked.connect(self._on_repay)
        repay_row.addWidget(self.btn_repay)
        repay_row.addStretch()
        layout.addLayout(repay_row)

        layout.addStretch()
        self._update_loan_amount()

    def _update_loan_amount(self) -> None:
        customers = int(self.loan_customers_spin.value())
        amount = customers * LOAN_RATE
        self.loan_amount_label.setText(f"Dostaniesz: ${amount:.2f}")

    def _on_take_loan(self) -> None:
        customers = int(self.loan_customers_spin.value())
        if customers < LOAN_MIN_CLIENTS:
            QMessageBox.warning(self, "Za mało", f"Minimum {LOAN_MIN_CLIENTS} klientów.")
            return
        total_active = self.game.total_customers()
        if customers > total_active:
            QMessageBox.warning(self, "Brak klientów", f"Masz {total_active} klientów, nie możesz oddać {customers}.")
            return
        amount = customers * LOAN_RATE
        reply = QMessageBox.question(
            self, "Pożyczka",
            f"Wziąć pożyczkę?\n\n"
            f"Klienci do oddania: {customers}\n"
            f"Kwota pożyczki: ${amount:.2f}\n"
            f"Odsetki: {LOAN_INTEREST_DAILY*100:.1f}% dziennie\n\n"
            f"Pozostanie klientów: {total_active - customers}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        # Usuń klientów (losowo z usług)
        from core.models import ServiceInstance
        import random
        active = [s for s in self.game.state.services if s.status == "active"]
        rng = random.Random(self.game.state.day)
        to_remove = rng.sample(active, min(customers, len(active))) if active else []
        for svc in to_remove:
            self.game.state.services.remove(svc)
        # Jeśli usunęliśmy mniej niż customers (bo mniej usług), dopasuj kwotę
        actual_removed = len(to_remove)
        amount = actual_removed * LOAN_RATE
        self.game.state.cash += amount
        self.game.state.debt += amount
        self.game.state.debt_daily_interest = LOAN_INTEREST_DAILY
        # Sync CustomerAggregate
        for cust in self.game.state.customers:
            if cust.product_type != "domain":
                cust.count = sum(1 for s in self.game.state.services if s.product_type == cust.product_type and s.status == "active")
        QMessageBox.information(
            self, "Pożyczka wzięta",
            f"Dostajesz ${amount:.2f}\n"
            f"Utracono {actual_removed} klientów\n"
            f"Aktualny dług: ${self.game.state.debt:.2f}",
        )
        self.refresh()

    def _on_repay(self) -> None:
        amount = self.repay_spin.value()
        if amount <= 0:
            return
        if self.game.state.debt <= 0:
            QMessageBox.information(self, "Brak długu", "Nie masz długu do spłaty.")
            return
        if amount > self.game.state.cash:
            QMessageBox.warning(self, "Brak środków", f"Potrzeba ${amount:.2f}, masz ${self.game.state.cash:.2f}.")
            return
        repay = min(amount, self.game.state.debt, self.game.state.cash)
        self.game.state.cash -= repay
        self.game.state.debt -= repay
        QMessageBox.information(self, "Spłacono", f"Spłacono ${repay:.2f}\nZostało długu: ${self.game.state.debt:.2f}")
        self.refresh()

    def refresh(self) -> None:
        state = self.game.state
        daily_salary = sum(e.salary_daily for e in state.employees)
        daily_rent = sum(r.rent_daily for r in state.regions)
        daily_licenses = balance.LICENSE_DAILY
        daily_power = sum(r.power_kw_used * balance.POWER_PRICE_PER_KWH * 24 for r in state.regions)
        daily_interest = state.debt * state.debt_daily_interest if state.debt > 0 else 0
        daily_expenses_est = daily_salary + daily_rent + daily_licenses + daily_power + daily_interest

        from core.services import generate_revenue
        daily_income_est = generate_revenue(state)

        self.summary_label.setText(
            f"Gotówka: ${state.cash:,.2f}    "
            f"Przychód/dzień: ${daily_income_est:,.2f}    "
            f"Koszty/dzień: ${daily_expenses_est:,.2f}    "
            f"Saldo/dzień: ${daily_income_est - daily_expenses_est:,.2f}\n"
            f"Pensje: ${daily_salary:.2f}  |  Prąd: ${daily_power:.2f}  |  "
            f"Wynajem: ${daily_rent:.2f}  |  Licencje: ${daily_licenses:.2f}  |  "
            f"Odsetki: ${daily_interest:.2f}"
        )

        if state.debt > 0:
            self.debt_label.setText(
                f"💰 Aktualny dług: ${state.debt:,.2f}  "
                f"(odsetki ${state.debt * state.debt_daily_interest:.2f}/dzień)"
            )
        else:
            self.debt_label.setText("Brak długu. ✅")
            self.debt_label.setStyleSheet("color: #4ade80; font-weight: bold; padding: 8px; background: #1a2a1a; border-radius: 4px;")

        self.repay_spin.setMaximum(max(state.cash, 0))