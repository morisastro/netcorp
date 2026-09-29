"""Ekran Infrastruktura — serwerownia (sloty SVG), katalog serwerów, zasoby DC."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from core.models import Server
from data import balance
from data.server_models import SERVER_CATALOG, get_model, get_price
from ui.widgets.kpi_card import KpiCard


class InfrastructureScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Infrastruktura")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        # Karty zasobów DC
        region = self.game.state.regions[0] if self.game.state.regions else None
        if region:
            resources_row = QHBoxLayout()
            resources_row.setSpacing(8)

            self.card_region = KpiCard("Region", region.name)
            self.card_slots = KpiCard("Sloty", f"{region.slots_used}/{region.slots_total}")
            self.card_power = KpiCard("Prąd", f"{region.power_kw_used:.1f}/{region.power_kw_total:.1f} kW")
            self.card_net = KpiCard("Sieć", f"{region.network_gbps:.1f} Gbps ({region.uplinks}×)")
            self.card_cool = KpiCard("Chłodzenie", f"{region.cooling_factor:.2f}")
            for c in (self.card_region, self.card_slots, self.card_power, self.card_net, self.card_cool):
                resources_row.addWidget(c)
            layout.addLayout(resources_row)

            # Paski obciążenia
            bars_row = QHBoxLayout()
            bars_row.setSpacing(12)

            self.bar_power = self._make_bar("Obciążenie prądu")
            self.bar_slots = self._make_bar("Zajętość slotów")
            bars_row.addWidget(self.bar_power)
            bars_row.addWidget(self.bar_slots)
            layout.addLayout(bars_row)

        # Sekcja: serwerownia SVG
        rack_title = QLabel("Serwerownia — wizualizacja slotów")
        rack_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9a9a9a; margin-top: 8px;")
        layout.addWidget(rack_title)

        self.rack_svg = QSvgWidget()
        self.rack_svg.setMinimumHeight(280)
        layout.addWidget(self.rack_svg, 1)

        # Przyciski: kup serwer + kup slot
        btn_row = QHBoxLayout()
        self.btn_buy_slot = QPushButton("➕ Kup slot")
        self.btn_buy_slot.setToolTip("Rozbuduj serwerownię — dodatkowy slot na serwer")
        self.btn_buy_slot.clicked.connect(self._on_buy_slot)
        btn_row.addWidget(self.btn_buy_slot)

        self.btn_buy = QPushButton("🖥️ Kup serwer")
        self.btn_buy.setObjectName("primary")
        self.btn_buy.clicked.connect(self._on_buy_server)
        btn_row.addWidget(self.btn_buy)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Serwery jako karty w scrollu
        servers_title = QLabel("🖥️ Serwery")
        servers_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9a9a9a; margin-top: 8px;")
        layout.addWidget(servers_title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.cards_container = QWidget()
        from PySide6.QtWidgets import QGridLayout
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(8)
        self.scroll.setWidget(self.cards_container)
        layout.addWidget(self.scroll, 1)

    def _make_bar(self, label: str) -> QFrame:
        box = QFrame()
        v = QVBoxLayout(box)
        v.setContentsMargins(8, 8, 8, 8)
        v.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #9a9a9a; font-size: 11px;")
        v.addWidget(lbl)
        bar = QProgressBar()
        bar.setRange(0, 100)
        v.addWidget(bar)
        box.bar = bar  # type: ignore[attr-defined]
        return box

    def refresh(self) -> None:
        state = self.game.state
        if not state.regions:
            return
        region = state.regions[0]

        self.card_region.set_value(region.name)
        self.card_slots.set_value(f"{region.slots_used}/{region.slots_total}")
        self.card_power.set_value(f"{region.power_kw_used:.1f}/{region.power_kw_total:.1f} kW")
        self.card_net.set_value(f"{region.network_gbps:.1f} Gbps ({region.uplinks}×)")
        self.card_cool.set_value(f"{region.cooling_factor:.2f}")

        # Paski
        power_pct = int((region.power_kw_used / max(region.power_kw_total, 0.01)) * 100)
        slots_pct = int((region.slots_used / max(region.slots_total, 1)) * 100)
        self.bar_power.bar.setValue(power_pct)
        self.bar_slots.bar.setValue(slots_pct)

        # SVG slotów
        self.rack_svg.load(self._build_svg(region, state.servers).encode("utf-8"))

        # Serwery jako karty
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from ui.icons import server_icon
        cols = 3
        for i, s in enumerate(state.servers):
            model = get_model(s.model_id)
            model_name = model["name"] if model else s.model_id
            card = self._build_server_card(s, model_name)
            self.cards_grid.addWidget(card, i // cols, i % cols)

        if not state.servers:
            from PySide6.QtCore import Qt
            empty = QLabel("Brak serwerów. Kup pierwszy serwer powyżej.")
            empty.setStyleSheet("color: #6a6a6a; padding: 24px;")
            empty.setAlignment(Qt.AlignCenter)
            self.cards_grid.addWidget(empty, 0, 0, 1, cols)

    def _build_server_card(self, server, model_name: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 6px; }"
            "QFrame#card:hover { border-color: #2563eb; }"
        )
        v = QVBoxLayout(card)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)

        # Nagłówek: ikona + model + status badge
        from ui.icons import server_icon
        header = QHBoxLayout()
        name_lbl = QLabel(f"{server_icon(server.status)}  {model_name}")
        name_lbl.setStyleSheet("color: #d4d4d4; font-size: 14px; font-weight: bold;")
        header.addWidget(name_lbl)
        header.addStretch()

        status_text = {"ok": "OK", "down": "DOWN", "maintenance": "SERWIS"}.get(server.status, server.status)
        status_colors = {"ok": "#16a34a", "down": "#dc2626", "maintenance": "#ca8a04"}
        status_bg = status_colors.get(server.status, "#3a3a3a")
        status_lbl = QLabel(status_text)
        status_lbl.setStyleSheet(
            f"background: {status_bg}; color: white; padding: 2px 10px; "
            f"border-radius: 8px; font-weight: bold; font-size: 11px;"
        )
        header.addWidget(status_lbl)
        v.addLayout(header)

        # Tier badge
        tier_label = {"budget": "⬇️ Budget", "standard": "▶️ Standard", "premium": "⭐ Premium"}.get(
            server.quality_tier, server.quality_tier
        )
        tier_lbl = QLabel(tier_label)
        tier_lbl.setStyleSheet("color: #facc15; font-size: 12px;")
        v.addWidget(tier_lbl)

        # Parametry
        params_lbl = QLabel(
            f"⚙️ {server.cpu_cores}c   🔋 {server.ram_gb}GB   "
            f"💾 {server.disk_gb}GB {server.disk_type}   📅 {server.age_days} dni"
        )
        params_lbl.setStyleSheet("color: #9a9a9a; font-size: 11px;")
        v.addWidget(params_lbl)

        # Obciążenie (paski)
        if server.load_cpu > 0 or server.load_ram > 0:
            load_lbl = QLabel(f"Obciążenie: CPU {server.load_cpu*100:.0f}%  RAM {server.load_ram*100:.0f}%")
            color = "#4ade80"
            if server.load_cpu > 0.8:
                color = "#f87171"
            elif server.load_cpu > 0.6:
                color = "#facc15"
            load_lbl.setStyleSheet(f"color: {color}; font-size: 11px;")
            v.addWidget(load_lbl)

        # Przycisk sprzedaj/usuń serwer (zwrot części kosztów)
        from data.server_models import get_model, get_price
        model = get_model(server.model_id)
        if model:
            base_price = get_price(server.model_id, server.quality_tier) or 0
            age_factor = max(0.1, 1.0 - server.age_days / 1000)
            sell_value = base_price * 0.3 * age_factor
        else:
            sell_value = 0
        sell_text = f"Sprzedaj (${sell_value:.0f})" if sell_value > 0 else "Usuń"

        actions = QHBoxLayout()
        actions.addStretch()
        btn_sell = QPushButton(sell_text)
        btn_sell.setStyleSheet(
            "QPushButton { background-color: #7f1d1d; color: #ffffff; "
            "border: none; padding: 4px 12px; border-radius: 3px; font-weight: bold; }"
            "QPushButton:hover { background-color: #991b1b; }"
        )
        btn_sell.clicked.connect(lambda checked=False, s=server, val=sell_value: self._on_sell_server(s, val))
        actions.addWidget(btn_sell)
        v.addLayout(actions)

        return card

    def _on_sell_server(self, server, sell_value: float) -> None:
        """Sprzedaje/usuwa serwer (zwrot części kosztów)."""
        from PySide6.QtWidgets import QMessageBox
        msg = f"Czy na pewno sprzedać serwer {server.id}?\n"
        if sell_value > 0:
            msg += f"Zwrot: ${sell_value:.2f}"
        else:
            msg += "Brak zwrotu (stary serwer)."
        reply = QMessageBox.question(
            self, "Sprzedaż serwera", msg, QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        if server in self.game.state.servers:
            self.game.state.servers.remove(server)
            self.game.state.cash += sell_value
            for region in self.game.state.regions:
                if region.id == server.region_id:
                    region.slots_used = max(0, region.slots_used - 1)
                    model = get_model(server.model_id)
                    if model:
                        region.power_kw_used = max(0, region.power_kw_used - (model.get("tdp_w", 200) / 1000.0))
                    break
            self.refresh()

    def _build_svg(self, region, servers) -> str:
        """Buduje SVG serwerowni z slotami."""
        cols = 4  # liczba kolumn slotów
        slot_w = 120
        slot_h = 80
        padding = 12
        margin = 16
        rows = (region.slots_total + cols - 1) // cols
        width = margin * 2 + cols * (slot_w + padding) - padding
        height = margin * 2 + rows * (slot_h + padding) - padding + 40

        # Mapuj slot_id → serwer
        slot_map = {s.slot_id: s for s in servers}

        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" style="background:#1a1a1a;">',
            f'<text x="{margin}" y="24" fill="#9a9a9a" font-family="monospace" font-size="13">'
            f'{region.name} — {region.slots_used}/{region.slots_total} slotów</text>',
        ]

        for i in range(region.slots_total):
            col = i % cols
            row = i // cols
            x = margin + col * (slot_w + padding)
            y = 40 + margin + row * (slot_h + padding)
            slot_id = f"slot_{i}"
            server = slot_map.get(slot_id)

            if server:
                # Kolor wg statusu
                if server.status == "ok":
                    color = "#2563eb"
                    border = "#60a5fa"
                    label = "ON"
                    label_color = "#4ade80"
                elif server.status == "down":
                    color = "#7f1d1d"
                    border = "#ef4444"
                    label = "DOWN"
                    label_color = "#ef4444"
                else:
                    color = "#713f12"
                    border = "#facc15"
                    label = "MAINT"
                    label_color = "#facc15"

                model = get_model(server.model_id)
                model_name = model["name"] if model else server.model_id
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{slot_w}" height="{slot_h}" rx="4" '
                    f'fill="{color}" stroke="{border}" stroke-width="2"/>'
                )
                parts.append(
                    f'<text x="{x+8}" y="{y+18}" fill="#d4d4d4" font-family="monospace" font-size="10">'
                    f'{slot_id}</text>'
                )
                parts.append(
                    f'<text x="{x+8}" y="{y+34}" fill="#d4d4d4" font-family="monospace" font-size="9">'
                    f'{model_name[:18]}</text>'
                )
                parts.append(
                    f'<text x="{x+8}" y="{y+48}" fill="#9a9a9a" font-family="monospace" font-size="9">'
                    f'{server.cpu_cores}c {server.ram_gb}GB</text>'
                )
                parts.append(
                    f'<text x="{x+slot_w-8}" y="{y+slot_h-8}" text-anchor="end" '
                    f'fill="{label_color}" font-family="monospace" font-size="10" font-weight="bold">'
                    f'{label}</text>'
                )
            else:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{slot_w}" height="{slot_h}" rx="4" '
                    f'fill="#1f1f1f" stroke="#3a3a3a" stroke-width="1" stroke-dasharray="4 4"/>'
                )
                parts.append(
                    f'<text x="{x+slot_w/2}" y="{y+slot_h/2+4}" text-anchor="middle" '
                    f'fill="#3a3a3a" font-family="monospace" font-size="11">{slot_id}</text>'
                )

        parts.append("</svg>")
        return "\n".join(parts)

    def _slot_price(self, region: Any) -> float:
        """Cena zakupu kolejnego slotu (rośnie z liczbą slotów)."""
        from data import balance
        return balance.SLOT_BUY_BASE_PRICE + region.slots_total * balance.SLOT_BUY_STEP

    def _on_buy_slot(self) -> None:
        """Kupuje dodatkowy slot w serwerowni."""
        if not self.game.state.regions:
            return
        region = self.game.state.regions[0]
        price = self._slot_price(region)
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Kup slot",
            f"Kupić dodatkowy slot w '{region.name}'?\n"
            f"Cena: ${price:.2f}\n"
            f"Aktualnie: {region.slots_total} slotów ({region.slots_used} zajętych)\n"
            f"Po zakupie: {region.slots_total + 1} slotów\n"
            f"Gotówka: ${self.game.state.cash:.2f}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        if self.game.state.cash < price:
            QMessageBox.warning(self, "Brak środków", f"Potrzeba ${price:.2f}, masz ${self.game.state.cash:.2f}.")
            return
        self.game.state.cash -= price
        region.slots_total += 1
        from data import balance
        region.power_kw_total += balance.SLOT_POWER_KW
        QMessageBox.information(
            self, "Slot kupiony",
            f"Serwerownia rozbudowana do {region.slots_total} slotów.\n"
            f"Pojemność prądu: +{balance.SLOT_POWER_KW} kW (teraz {region.power_kw_total} kW)."
        )
        self.refresh()

    def _on_buy_server(self) -> None:
        dlg = BuyServerDialog(self.game, parent=self)
        if dlg.exec() == QDialog.Accepted:
            spec = dlg.get_spec()
            if spec is None:
                return
            model_id, tier, slot_id = spec
            model = get_model(model_id)
            if model is None:
                return
            price = get_price(model_id, tier)
            if price is None:
                return
            if self.game.state.cash < price:
                QMessageBox.warning(self, "Brak środków", f"Potrzeba ${price:.2f}, masz ${self.game.state.cash:.2f}.")
                return
            region = self.game.state.regions[0]
            if region.slots_used >= region.slots_total:
                QMessageBox.warning(self, "Brak slotów", "Wszystkie sloty zajęte. Rozbuduj serwerownię.")
                return

            self.game.state.cash -= price
            server = Server(
                id=f"srv_{len(self.game.state.servers)+1}_{model_id}_{tier}",
                model_id=model_id,
                quality_tier=tier,
                cpu_cores=model["cpu_cores"],
                ram_gb=model["ram_gb"],
                disk_gb=model["disk_gb"],
                disk_type=model["disk_type"],
                slot_id=slot_id,
                region_id=region.id,
                mtbf_base=balance.TIER_MTBF.get(tier, 10000.0),
            )
            self.game.state.servers.append(server)
            region.slots_used += 1
            region.power_kw_used += (model.get("tdp_w", 200) / 1000.0)
            self.refresh()


class BuyServerDialog(QDialog):
    """Dialog kupna serwera — wybór modelu, tieru, slotu."""

    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self.setWindowTitle("Kup serwer")
        self.resize(420, 360)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Model
        layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        for m in SERVER_CATALOG:
            self.model_combo.addItem(f"{m['name']}  ({m['cpu_cores']}c/{m['ram_gb']}GB/{m['disk_gb']}GB {m['disk_type']})", m["id"])
        layout.addWidget(self.model_combo)

        # Tier
        layout.addWidget(QLabel("Tier jakości:"))
        self.tier_combo = QComboBox()
        for tier in ("budget", "standard", "premium"):
            mult = balance.TIER_FAILURE_MULTIPLIER[tier]
            self.tier_combo.addItem(f"{tier} (awaryjność ×{mult})", tier)
        layout.addWidget(self.tier_combo)

        # Slot
        layout.addWidget(QLabel("Slot w serwerowni:"))
        self.slot_combo = QComboBox()
        self._refresh_slots()
        layout.addWidget(self.slot_combo)

        # Cena
        self.price_label = QLabel("")
        self.price_label.setStyleSheet("color: #facc15; font-weight: bold; padding: 8px;")
        layout.addWidget(self.price_label)

        # Aktualizuj cenę przy zmianie
        self.model_combo.currentIndexChanged.connect(self._update_price)
        self.tier_combo.currentIndexChanged.connect(self._update_price)
        self._update_price()

        # Saldo
        self.balance_label = QLabel(f"Gotówka: ${self.game.state.cash:,.2f}")
        layout.addWidget(self.balance_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _refresh_slots(self) -> None:
        self.slot_combo.clear()
        region = self.game.state.regions[0]
        used_slots = {s.slot_id for s in self.game.state.servers}
        for i in range(region.slots_total):
            slot_id = f"slot_{i}"
            if slot_id not in used_slots:
                self.slot_combo.addItem(slot_id, slot_id)

    def _update_price(self) -> None:
        model_id = self.model_combo.currentData()
        tier = self.tier_combo.currentData()
        price = get_price(model_id, tier) if model_id and tier else 0.0
        self.price_label.setText(f"Cena: ${price:.2f}")
        if price > self.game.state.cash:
            self.price_label.setStyleSheet("color: #f87171; font-weight: bold; padding: 8px;")
        else:
            self.price_label.setStyleSheet("color: #facc15; font-weight: bold; padding: 8px;")

    def get_spec(self) -> tuple[str, str, str] | None:
        model_id = self.model_combo.currentData()
        tier = self.tier_combo.currentData()
        slot_id = self.slot_combo.currentData()
        if not model_id or not tier or not slot_id:
            return None
        return model_id, tier, slot_id