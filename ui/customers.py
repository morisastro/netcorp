"""Ekran Klienci — karty per produkt + segmenty."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from data.products import product_name
from ui.icons import PRODUCT_ICONS


class CustomerCard(QFrame):
    """Karta klientów danego produktu."""

    def __init__(self, cust, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 6px; }"
            "QFrame#card:hover { border-color: #2563eb; }"
        )
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        # Nagłówek: ikona + nazwa produktu
        icon = PRODUCT_ICONS.get(cust.product_type, "📦")
        header = QHBoxLayout()
        name_lbl = QLabel(f"{icon}  {product_name(cust.product_type)}")
        name_lbl.setStyleSheet("color: #d4d4d4; font-size: 15px; font-weight: bold;")
        header.addWidget(name_lbl)
        header.addStretch()
        count_lbl = QLabel(f"👥 {cust.count}")
        count_lbl.setStyleSheet("color: #60a5fa; font-size: 18px; font-weight: bold;")
        header.addWidget(count_lbl)
        v.addLayout(header)

        # Segment
        seg_lbl = QLabel(f"Segment: {cust.segment}")
        seg_lbl.setStyleSheet("color: #9a9a9a; font-size: 12px;")
        v.addWidget(seg_lbl)

        # Metryki
        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        metrics.addWidget(self._metric("Churn/mies", f"{cust.churn_monthly*100:.1f}%", "#facc15"))
        metrics.addWidget(self._metric("SLA naruszenia", f"{cust.sla_breaches_this_month}",
                                       "#f87171" if cust.sla_breaches_this_month else "#4ade80"))
        metrics.addWidget(self._metric("Pobyt (dni)", f"{cust.avg_stay_days}", "#9a9a9a"))
        v.addLayout(metrics)

    def _metric(self, label: str, value: str, color: str) -> QFrame:
        box = QFrame()
        box.setStyleSheet("background: #2a2a2a; border-radius: 4px;")
        v = QVBoxLayout(box)
        v.setContentsMargins(8, 6, 8, 6)
        v.setSpacing(2)
        l = QLabel(label)
        l.setStyleSheet("color: #6a6a6a; font-size: 10px;")
        v.addWidget(l)
        val = QLabel(value)
        val.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 13px;")
        v.addWidget(val)
        return box


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

        info = QLabel(
            "Klienci są grupowani per produkt. Każdy klient zostaje 1-7 dni, "
            "po czym odchodzi (chyba że go zatrzyma dobra jakość usług)."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        # Karty w scrollu
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(8)
        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll, 1)

    def refresh(self) -> None:
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from ui.screen_info import is_small_screen
        cols = 1 if is_small_screen() else 2
        for i, cust in enumerate(self.game.state.customers):
            card = CustomerCard(cust)
            self.cards_grid.addWidget(card, i // cols, i % cols)

        if not self.game.state.customers:
            empty = QLabel("Brak klientów. Dodaj plany i zrób marketing.")
            empty.setStyleSheet("color: #6a6a6a; padding: 24px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, cols)