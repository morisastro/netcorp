"""Ekran Produktów — karty planów + tworzenie/edycja."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from core.models import ProductPlan
from data.products import PRODUCT_TYPES, product_name
from ui.icons import PRODUCT_ICONS

PRODUCT_LABELS = {p["id"]: p["name"] for p in PRODUCT_TYPES}

PRODUCT_FIELDS = {
    "www":       {"cpu", "ram", "disk", "bw", "price", "sla"},
    "vps":       {"cpu", "ram", "disk", "bw", "price", "sla"},
    "dedicated": {"cpu", "ram", "disk", "bw", "price", "sla"},
    "domain":    {"price", "sla"},
}


class PlanDialog(QDialog):
    """Dialog tworzenia/edycji planu."""

    def __init__(self, plan: ProductPlan | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Plan produktu")
        self.resize(380, 360)
        self._build_ui(plan)

    def _build_ui(self, plan: ProductPlan | None) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.product = QComboBox()
        for pid, label in PRODUCT_LABELS.items():
            self.product.addItem(f"{PRODUCT_ICONS[pid]} {label}", pid)
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

        self.setup = QDoubleSpinBox()
        self.setup.setRange(0, 9999)
        self.setup.setDecimals(2)
        self.setup.setSuffix(" $")
        self.setup.setToolTip("Jednorazowa opłata setup (zastrzyk gotówki przy nowym kliencie)")
        form.addRow("Opłata setup:", self.setup)

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
            self.setup.setValue(plan.setup_fee)
            self.sla.setValue(plan.sla_target)
        self._update_field_visibility()

    def _update_field_visibility(self) -> None:
        product_type = self.product.currentData()
        fields = PRODUCT_FIELDS.get(product_type, set())
        for fname, widget in [
            ("cpu", self.cpu), ("ram", self.ram), ("disk", self.disk), ("bw", self.bw),
        ]:
            widget.setVisible(fname in fields)
        self.adjustSize()

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
            setup_fee=self.setup.value(),
        )


class PlanCard(QFrame):
    """Karta pojedynczego planu produktu."""

    def __init__(self, plan: ProductPlan, on_edit, on_delete, parent=None) -> None:
        super().__init__(parent)
        self.plan = plan
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 6px; }"
            "QFrame#card:hover { border-color: #2563eb; }"
        )
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        # Nagłówek: ikona + nazwa produktu
        icon = PRODUCT_ICONS.get(plan.product_type, "📦")
        header = QHBoxLayout()
        name_lbl = QLabel(f"{icon}  {product_name(plan.product_type)}")
        name_lbl.setStyleSheet("color: #d4d4d4; font-size: 15px; font-weight: bold;")
        header.addWidget(name_lbl)
        header.addStretch()
        price_lbl = QLabel(f"${plan.price_monthly:.2f}/mies")
        price_lbl.setStyleSheet("color: #4ade80; font-weight: bold; font-size: 14px;")
        header.addWidget(price_lbl)
        if plan.setup_fee > 0:
            setup_lbl = QLabel(f"+${plan.setup_fee:.0f} setup")
            setup_lbl.setStyleSheet("color: #facc15; font-size: 11px;")
            header.addWidget(setup_lbl)
        v.addLayout(header)

        # Nazwa planu
        plan_name_lbl = QLabel(plan.name)
        plan_name_lbl.setStyleSheet("color: #60a5fa; font-size: 12px;")
        v.addWidget(plan_name_lbl)

        # Parametry
        params = []
        fields = PRODUCT_FIELDS.get(plan.product_type, set())
        if "cpu" in fields:
            params.append(f"⚙️ {plan.cpu_cores} vCPU")
        if "ram" in fields:
            params.append(f"🔋 {plan.ram_gb} GB RAM")
        if "disk" in fields:
            params.append(f"💾 {plan.disk_gb} GB")
        if "bw" in fields:
            params.append(f"🌐 {plan.bandwidth_mbps} Mbps")
        params.append(f"🎯 SLA {plan.sla_target}%")
        params_lbl = QLabel("   •   ".join(params))
        params_lbl.setStyleSheet("color: #9a9a9a; font-size: 11px;")
        params_lbl.setWordWrap(True)
        v.addWidget(params_lbl)

        # Akcje
        actions = QHBoxLayout()
        actions.addStretch()
        btn_edit = QPushButton("Edytuj")
        btn_edit.setStyleSheet(
            "QPushButton { background-color: #2a2a2a; color: #d4d4d4; "
            "border: 1px solid #3a3a3a; padding: 4px 12px; border-radius: 3px; }"
            "QPushButton:hover { background-color: #333333; }"
        )
        btn_edit.clicked.connect(lambda: on_edit(plan))
        actions.addWidget(btn_edit)

        btn_del = QPushButton("Usuń")
        btn_del.setStyleSheet(
            "QPushButton { background-color: #7f1d1d; color: #ffffff; "
            "border: none; padding: 4px 12px; border-radius: 3px; font-weight: bold; }"
            "QPushButton:hover { background-color: #991b1b; }"
        )
        btn_del.clicked.connect(lambda: on_delete(plan))
        actions.addWidget(btn_del)
        v.addLayout(actions)


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

        # Nagłówek + przycisk dodaj
        header = QHBoxLayout()
        title = QLabel("Produkty i plany")
        title.setObjectName("screen-title")
        header.addWidget(title)
        header.addStretch()

        self.btn_add = QPushButton("➕ Dodaj plan")
        self.btn_add.setObjectName("primary")
        self.btn_add.clicked.connect(self._on_add_plan)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        info = QLabel(
            "Twórz własne plany dla każdego produktu. "
            "Klienci kupują plany zależnie od ceny, reputacji i marketingu."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        # Karty planów w scrollu
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(8)
        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll, 1)

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
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from ui.screen_info import is_small_screen
        cols = 2 if is_small_screen() else 3
        for i, plan in enumerate(self.game.state.products):
            card = PlanCard(plan, on_edit=self._on_edit_plan, on_delete=self._on_delete_plan)
            self.cards_grid.addWidget(card, i // cols, i % cols)

        if not self.game.state.products:
            empty = QLabel("Brak planów. Dodaj pierwszy plan, aby zacząć sprzedawać.")
            empty.setStyleSheet("color: #6a6a6a; padding: 24px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, cols)