"""Ekran Pracownicy — zatrudnianie i zwalnianie."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from core.game import Game
from core.models import Employee
from data import balance
from data.names import random_employee_name
from data.products import PRODUCT_TYPES
import random as _r

ROLE_LABELS = {
    "support": "Support",
    "sysadmin": "Sysadmin",
    "neteng": "Network engineer",
    "sales": "Sales",
    "marketing": "Marketing",
}


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

        info = QLabel(
            "Pracownicy automatycznie wykonują swoje role:\n"
            "• Support — zamyka tickety\n"
            "• Sysadmin — naprawia awarie sprzętowe\n"
            "• Network engineer — naprawia awarie sieciowe / DDoS\n"
            "• Sales — zwiększa konwersję klientów\n"
            "• Marketing — zwiększa efektywność wydatków marketingowych\n\n"
            f"Pensja dzienna = poziom × ${balance.EMPLOYEE_SALARY_PER_LEVEL:.0f}"
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        # Sekcja: zatrudnij nowego
        hire_box = QHBoxLayout()
        hire_box.setSpacing(8)

        hire_box.addWidget(QLabel("Rola:"))
        from PySide6.QtWidgets import QComboBox
        self.role_combo = QComboBox()
        for rid, label in ROLE_LABELS.items():
            self.role_combo.addItem(label, rid)
        hire_box.addWidget(self.role_combo)

        hire_box.addWidget(QLabel("Poziom (1-5):"))
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 5)
        self.level_spin.setValue(1)
        self.level_spin.valueChanged.connect(self._update_hire_cost)
        hire_box.addWidget(self.level_spin)

        self.hire_cost_label = QLabel("")
        self.hire_cost_label.setStyleSheet("color: #facc15;")
        hire_box.addWidget(self.hire_cost_label)

        hire_box.addStretch()

        self.btn_hire = QPushButton("Zatrudnij")
        self.btn_hire.setObjectName("primary")
        self.btn_hire.clicked.connect(self._on_hire)
        hire_box.addWidget(self.btn_hire)

        layout.addLayout(hire_box)

        # Tabela pracowników
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Imię", "Rola", "Poziom", "Pensja/dzień", "Akcja"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

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
        self.table.setRowCount(0)
        for i, emp in enumerate(self.game.state.employees):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(emp.name))
            self.table.setItem(i, 1, QTableWidgetItem(ROLE_LABELS.get(emp.role, emp.role)))
            self.table.setItem(i, 2, QTableWidgetItem(str(emp.level)))
            self.table.setItem(i, 3, QTableWidgetItem(f"${emp.salary_daily:.2f}"))

            btn = QPushButton("Zwolnij")
            btn.setObjectName("danger")
            btn.clicked.connect(lambda checked=False, e=emp: self._on_fire(e))
            self.table.setCellWidget(i, 4, btn)

        # Zablokuj edycję komórek
        for r in range(self.table.rowCount()):
            for c in range(4):
                item = self.table.item(r, c)
                if item:
                    item.setFlags(Qt.ItemFlags(item.flags()) & ~Qt.ItemFlag.ItemIsEditable)  # ~ItemIsEditable

    def _on_fire(self, emp: Employee) -> None:
        if emp in self.game.state.employees:
            self.game.state.employees.remove(emp)
            self.refresh()