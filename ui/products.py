"""Ekran Produktów — tworzenie/edycja planów i cen."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

from core.game import Game
from core.models import ProductPlan
from data.products import PRODUCT_TYPES, product_name

PRODUCT_LABELS = {p["id"]: p["name"] for p in PRODUCT_TYPES}


class PlanDialog(QDialog):
    """Dialog tworzenia/edycji planu."""

    def __init__(self, plan: ProductPlan | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Plan produktu")
        self.resize(380, 320)
        self._build_ui(plan)

    def _build_ui(self, plan: ProductPlan | None) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.product = QComboBox()
        for pid, label in PRODUCT_LABELS.items():
            self.product.addItem(label, pid)
        form.addRow("Produkt:", self.product)

        self.name = QLineEdit()
        form.addRow("Nazwa planu:", self.name)

        self.cpu = QSpinBox()
        self.cpu.setRange(0, 64)
        form.addRow("vCPU:", self.cpu)

        self.ram = QSpinBox()
        self.ram.setRange(0, 256)
        form.addRow("RAM (GB):", self.ram)

        self.disk = QSpinBox()
        self.disk.setRange(0, 8000)
        form.addRow("Dysk (GB):", self.disk)

        self.bw = QSpinBox()
        self.bw.setRange(0, 10000)
        form.addRow("Przepustowość (Mbps):", self.bw)

        self.price = QDoubleSpinBox()
        self.price.setRange(0, 9999)
        self.price.setDecimals(2)
        self.price.setSuffix(" $/mies")
        form.addRow("Cena miesięczna:", self.price)

        self.sla = QDoubleSpinBox()
        self.sla.setRange(80, 100)
        self.sla.setDecimals(1)
        self.sla.setSuffix(" %")
        form.addRow("Cel SLA:", self.sla)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        if plan is not None:
            for i in range(self.product.count()):
                if self.product.itemData(i) == plan.product_type:
                    self.product.setCurrentIndex(i)
                    break
            self.name.setText(plan.name)
            self.cpu.setValue(plan.cpu_cores)
            self.ram.setValue(plan.ram_gb)
            self.disk.setValue(plan.disk_gb)
            self.bw.setValue(plan.bandwidth_mbps)
            self.price.setValue(plan.price_monthly)
            self.sla.setValue(plan.sla_target)

    def to_plan(self, plan_id: str) -> ProductPlan:
        return ProductPlan(
            id=plan_id,
            product_type=self.product.currentData(),
            name=self.name.text() or "Plan",
            cpu_cores=self.cpu.value(),
            ram_gb=self.ram.value(),
            disk_gb=self.disk.value(),
            bandwidth_mbps=self.bw.value(),
            price_monthly=self.price.value(),
            sla_target=self.sla.value(),
        )


class ProductsScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Produkty i plany")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        info = QLabel(
            "Twórz własne plany dla każdego produktu. "
            "Klienci kupują plany zależnie od ceny, reputacji i marketingu."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("+ Dodaj plan")
        self.btn_add.setObjectName("primary")
        self.btn_add.clicked.connect(self._on_add_plan)
        btn_row.addWidget(self.btn_add)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Produkt", "Nazwa", "vCPU", "RAM", "Dysk", "Mbps", "Cena/mies", "Akcja"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

    def _on_add_plan(self) -> None:
        dlg = PlanDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            import uuid
            plan = dlg.to_plan(f"plan_{uuid.uuid4().hex[:8]}")
            self.game.state.products.append(plan)
            self.refresh()

    def _on_edit_plan(self, plan: ProductPlan) -> None:
        dlg = PlanDialog(plan=plan, parent=self)
        if dlg.exec() == QDialog.Accepted:
            updated = dlg.to_plan(plan.id)
            idx = self.game.state.products.index(plan)
            self.game.state.products[idx] = updated
            self.refresh()

    def _on_delete_plan(self, plan: ProductPlan) -> None:
        if plan in self.game.state.products:
            self.game.state.products.remove(plan)
            self.refresh()

    def refresh(self) -> None:
        self.table.setRowCount(0)
        for i, plan in enumerate(self.game.state.products):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(product_name(plan.product_type)))
            self.table.setItem(i, 1, QTableWidgetItem(plan.name))
            self.table.setItem(i, 2, QTableWidgetItem(str(plan.cpu_cores)))
            self.table.setItem(i, 3, QTableWidgetItem(f"{plan.ram_gb} GB"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{plan.disk_gb} GB"))
            self.table.setItem(i, 5, QTableWidgetItem(str(plan.bandwidth_mbps)))
            self.table.setItem(i, 6, QTableWidgetItem(f"${plan.price_monthly:.2f}"))

            cell = QWidget()
            h = QHBoxLayout(cell)
            h.setContentsMargins(2, 2, 2, 2)
            btn_edit = QPushButton("Edytuj")
            btn_edit.clicked.connect(lambda checked=False, p=plan: self._on_edit_plan(p))
            btn_del = QPushButton("Usuń")
            btn_del.setObjectName("danger")
            btn_del.clicked.connect(lambda checked=False, p=plan: self._on_delete_plan(p))
            h.addWidget(btn_edit)
            h.addWidget(btn_del)
            self.table.setCellWidget(i, 7, cell)

        if self.table.rowCount() == 0:
            self.table.insertRow(0)
            empty = QTableWidgetItem("Brak planów. Dodaj pierwszy plan, aby zacząć sprzedawać.")
            empty.setFlags(Qt.ItemFlags(empty.flags()) & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setSpan(0, 0, 1, 8)
            self.table.setItem(0, 0, empty)