"""Ekran Pracownicy — karty pracowników zatrudnianie/zwalnianie."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from core.models import Employee
from data import balance
from data.names import random_employee_name
from ui.icons import ROLE_ICONS
import random as _r

ROLE_LABELS = {
    "support": "Support",
    "sysadmin": "Sysadmin",
    "neteng": "Network engineer",
    "sales": "Sales",
    "marketing": "Marketing",
}

ROLE_DESC = {
    "support": "Zamyka tickety klientów",
    "sysadmin": "Naprawia awarie sprzętowe",
    "neteng": "Naprawia awarie sieci / DDoS",
    "sales": "Zwiększa konwersję klientów",
    "marketing": "Zwiększa ROI marketingu",
}


class EmployeeCard(QFrame):
    """Karta pojedynczego pracownika."""

    def __init__(self, employee: Employee, on_fire, parent=None) -> None:
        super().__init__(parent)
        self.employee = employee
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 6px; }"
            "QFrame#card:hover { border-color: #2563eb; }"
        )
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        # Nagłówek: ikona + imię
        icon = ROLE_ICONS.get(employee.role, "👤")
        name_row = QHBoxLayout()
        name_lbl = QLabel(f"{icon}  {employee.name}")
        name_lbl.setStyleSheet("color: #d4d4d4; font-size: 15px; font-weight: bold;")
        name_row.addWidget(name_lbl)
        name_row.addStretch()
        # Level badge
        level_lbl = QLabel(f"Lv {employee.level}")
        level_lbl.setStyleSheet(
            "background: #2563eb; color: white; padding: 2px 8px; border-radius: 8px; font-weight: bold;"
        )
        name_row.addWidget(level_lbl)
        v.addLayout(name_row)

        # Rola + opis
        role_lbl = QLabel(ROLE_LABELS.get(employee.role, employee.role))
        role_lbl.setStyleSheet("color: #60a5fa; font-size: 12px;")
        v.addWidget(role_lbl)

        desc_lbl = QLabel(ROLE_DESC.get(employee.role, ""))
        desc_lbl.setStyleSheet("color: #6a6a6a; font-size: 11px;")
        v.addWidget(desc_lbl)

        # Stopka: pensja + zwolnij
        footer = QHBoxLayout()
        salary_lbl = QLabel(f"💵 ${employee.salary_daily:.2f}/dzień")
        salary_lbl.setStyleSheet("color: #facc15; font-size: 12px;")
        footer.addWidget(salary_lbl)
        footer.addStretch()

        btn_fire = QPushButton("Zwolnij")
        btn_fire.setStyleSheet(
            "QPushButton { background-color: #7f1d1d; color: #ffffff; "
            "border: none; padding: 4px 12px; border-radius: 3px; font-weight: bold; }"
            "QPushButton:hover { background-color: #991b1b; }"
        )
        btn_fire.clicked.connect(lambda: on_fire(employee))
        footer.addWidget(btn_fire)
        v.addLayout(footer)


class EmployeesScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Pracownicy")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        # Panel zatrudniania
        hire_frame = QFrame()
        hire_frame.setObjectName("card")
        hire_frame.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 6px; }"
        )
        hire_layout = QVBoxLayout(hire_frame)
        hire_layout.setContentsMargins(16, 12, 16, 12)
        hire_layout.setSpacing(8)

        hire_title = QLabel("➕ Zatrudnij nowego pracownika")
        hire_title.setStyleSheet("color: #60a5fa; font-weight: bold; font-size: 14px;")
        hire_layout.addWidget(hire_title)

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(QLabel("Rola:"))
        self.role_combo = QComboBox()
        for rid, label in ROLE_LABELS.items():
            self.role_combo.addItem(f"{ROLE_ICONS[rid]} {label}", rid)
        row.addWidget(self.role_combo)

        row.addWidget(QLabel("Poziom:"))
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(1)
        self.level_spin.valueChanged.connect(self._update_hire_cost)
        row.addWidget(self.level_spin)

        self.hire_cost_label = QLabel("")
        self.hire_cost_label.setStyleSheet("color: #facc15; font-weight: bold;")
        row.addWidget(self.hire_cost_label)
        row.addStretch()

        self.btn_hire = QPushButton("Zatrudnij")
        self.btn_hire.setObjectName("primary")
        self.btn_hire.clicked.connect(self._on_hire)
        row.addWidget(self.btn_hire)
        hire_layout.addLayout(row)
        layout.addWidget(hire_frame)

        # Lista pracowników jako karty w scrollu
        list_title = QLabel(f"👤 Zatrudnieni pracownicy")
        list_title.setStyleSheet("color: #9a9a9a; font-weight: bold; margin-top: 8px;")
        layout.addWidget(list_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(8)
        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll, 1)

        self._update_hire_cost()

    def _update_hire_cost(self) -> None:
        level = self.level_spin.value()
        cost = level * balance.EMPLOYEE_SALARY_PER_LEVEL
        self.hire_cost_label.setText(f"Koszt/dzień: ${cost:.2f}")

    def _on_hire(self) -> None:
        role = self.role_combo.currentData()
        level = self.level_spin.value()
        salary = level * balance.EMPLOYEE_SALARY_PER_LEVEL
        name = random_employee_name()
        emp = Employee(
            id=f"emp_{len(self.game.state.employees) + 1}_{_r.randint(1000, 9999)}",
            name=name,
            role=role,
            level=level,
            salary_daily=salary,
            hired_day=self.game.state.day,
        )
        self.game.state.employees.append(emp)
        self.refresh()

    def refresh(self) -> None:
        # Wyczyść grid
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = 3
        for i, emp in enumerate(self.game.state.employees):
            card = EmployeeCard(emp, on_fire=self._on_fire)
            self.cards_grid.addWidget(card, i // cols, i % cols)

        if not self.game.state.employees:
            empty = QLabel("Brak pracowników. Zatrudnij kogoś powyżej.")
            empty.setStyleSheet("color: #6a6a6a; padding: 24px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, cols)

    def _on_fire(self, emp: Employee) -> None:
        if emp in self.game.state.employees:
            self.game.state.employees.remove(emp)
            self.refresh()