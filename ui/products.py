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

# Pola wymagane per typ produktu (reszta ukryta w dialogu)
PRODUCT_FIELDS = {
    "www":       {"cpu", "ram", "disk", "bw", "price", "sla"},
    "vps":       {"cpu", "ram", "disk", "bw", "price", "sla"},
    "dedicated": {"cpu", "ram", "disk", "bw", "price", "sla"},
    "domain":    {"price", "sla"},  # domena nie ma dysku/CPU/RAM
}


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
        self.product.currentIndexChanged.connect(self._update_field_visibility)
        form.addRow("Produkt:", self.product)

        self.name = QLineEdit()
        form.addRow("Nazwa planu:", self.name)

        self.cpu = QSpinBox()
        self.cpu.setRange(0, 64)
        self.cpu_row = form.addRow("vCPU:", self.cpu)

        self.ram = QSpinBox()
        self.ram.setRange(0, 256)
        self.ram_row = form.addRow("RAM (GB):", self.ram)

        self.disk = QSpinBox()
        self.disk.setRange(0, 8000)
        self.disk_row = form.addRow("Dysk (GB):", self.disk)

        self.bw = QSpinBox()
        self.bw.setRange(0, 10000)
        self.bw_row = form.addRow("Przepustowość (Mbps):", self.bw)

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
        self._update_field_visibility()

    def _update_field_visibility(self) -> None:
        """Ukrywa pola niepotrzebne dla danego produktu (np. domena bez dysku)."""
        product_type = self.product.currentData()
        fields = PRODUCT_FIELDS.get(product_type, set())
        # Mapa: nazwa pola → (widget, wiersz formularza)
        widgets = {
            "cpu": (self.cpu, self.cpu_row),
            "ram": (self.ram, self.ram_row),
            "disk": (self.disk, self.disk_row),
            "bw": (self.bw, self.bw_row),
            "price": (self.price, None),
            "sla": (self.sla, None),
        }
        for fname, (widget, row) in widgets.items():
            visible = fname in fields
            widget.setVisible(visible)
            if row is not None:
                # Ukryj label i widget w wierszu formularza
                label_item = self._row_label(row)
                if label_item is not None:
                    label_item.setVisible(visible)
                field_item = self._row_field(row)
                if field_item is not None:
                    field_item.setVisible(visible)
        self.adjustSize()

    def _row_label(self, row):
        # QFormLayout nie ujawnia łatwo labela; ukrywamy przez parent layout geometry
        return None

    def _row_field(self, row):
        return None

    def to_plan(self, plan_id: str) -> ProductPlan:
        product_type = self.product.currentData()
        fields = PRODUCT_FIELDS.get(product_type, set())
        return ProductPlan(
            id=plan_id,
            product_type=product_type,
            name=self.name.text() or "Plan",
            cpu_cores=self.cpu.value() if "cpu" in fields else 0,
            ram_gb=self.ram.value() if "ram" in fields else 0,
            disk_gb=self.disk.value() if "disk" in fields else 0,
            bandwidth_mbps=self.bw.value() if "bw" in fields else 0,
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
            "Produkt", "Nazwa planu", "vCPU", "RAM", "Dysk", "Mbps", "Cena/mies", "Akcje"
        ])
        # Kolumny: produkty i nazwa rozciągane, reszta po treści
        from PySide6.QtWidgets import QHeaderView
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for c in range(2, 7):
            self.table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
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
            from ui.icons import product_icon
            self.table.setItem(i, 0, QTableWidgetItem(f"{product_icon(plan.product_type)}  {product_name(plan.product_type)}"))
            self.table.setItem(i, 1, QTableWidgetItem(plan.name))
            self.table.setItem(i, 2, QTableWidgetItem(f"{plan.cpu_cores}" if plan.cpu_cores else "—"))
            self.table.setItem(i, 3, QTableWidgetItem(f"{plan.ram_gb} GB" if plan.ram_gb else "—"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{plan.disk_gb} GB" if plan.disk_gb else "—"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{plan.bandwidth_mbps}" if plan.bandwidth_mbps else "—"))
            self.table.setItem(i, 6, QTableWidgetItem(f"${plan.price_monthly:.2f}"))

            cell = QWidget()
            h = QHBoxLayout(cell)
            h.setContentsMargins(4, 4, 4, 4)
            h.setSpacing(4)
            btn_edit = QPushButton("✏️")
            btn_edit.setToolTip("Edytuj plan")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda checked=False, p=plan: self._on_edit_plan(p))
            btn_del = QPushButton("🗑️")
            btn_del.setToolTip("Usuń plan")
            btn_del.setObjectName("danger")
            btn_del.setFixedSize(32, 28)
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