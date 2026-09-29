"""Ekran Awarie — aktywne awarie + wybór akcji."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.game import Game

FAILURE_LABELS = {
    "disk": "Awaria dysku",
    "cpu_overload": "Przeciążenie CPU",
    "overheat": "Przegrzanie",
    "power": "Awaria zasilania",
    "network": "Awaria sieci",
    "ddos": "Atak DDoS",
}

ACTION_LABELS = [
    ("restart", "Restart"),
    ("replace", "Wymiana komponentu"),
    ("failover", "Failover na backup"),
    ("ignore", "Zignoruj"),
]


class FailuresScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Awarie")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        self.list_container = QVBoxLayout()
        self.list_container.setSpacing(8)
        layout.addLayout(self.list_container)

        self.empty_label = QLabel("Brak aktywnych awarii. ✅")
        self.empty_label.setStyleSheet("color: #4ade80; padding: 12px;")
        layout.addWidget(self.empty_label)

        # Historia
        layout.addSpacing(8)
        hist_title = QLabel("Historia awarii (ostatnie)")
        hist_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #9a9a9a;")
        layout.addWidget(hist_title)
        self.history_label = QLabel("—")
        self.history_label.setStyleSheet("color: #6a6a6a;")
        self.history_label.setWordWrap(True)
        layout.addWidget(self.history_label)

        layout.addStretch()

    def refresh(self) -> None:
        # Wyczyść listę aktywnych
        while self.list_container.count():
            item = self.list_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        failures = self.game.state.failures_active
        if not failures:
            self.empty_label.setVisible(True)
        else:
            self.empty_label.setVisible(False)
            for f in failures:
                card = self._build_failure_card(f)
                self.list_container.addWidget(card)

        # Historia
        hist = self.game.state.failures_history[-10:]
        if hist:
            lines = [
                f"{FAILURE_LABELS.get(f.type, f.type)} — serwer {f.server_id or 'DC'} "
                f"— dzień {f.started_day} — {f.status}"
                for f in reversed(hist)
            ]
            self.history_label.setText("\n".join(lines))
        else:
            self.history_label.setText("Brak historii awarii.")

    def _build_failure_card(self, failure) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet(
            "QFrame#card { background-color: #2a1f1f; border: 1px solid #7f1d1d; border-radius: 4px; }"
        )
        v = QVBoxLayout(card)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(6)

        header = QLabel(f"⚠ {FAILURE_LABELS.get(failure.type, failure.type)}")
        header.setStyleSheet("color: #f87171; font-weight: bold; font-size: 15px;")
        v.addWidget(header)

        details = QLabel(
            f"Serwer: {failure.server_id or 'całe DC'}    "
            f"Region: {failure.region_id}    "
            f"Trwa: {failure.duration_hours}h    "
            f"Od dnia: {failure.started_day}"
        )
        details.setStyleSheet("color: #9a9a9a;")
        v.addWidget(details)

        # Przyciski akcji
        actions_row = QHBoxLayout()
        actions_row.setSpacing(6)
        for action_id, label in ACTION_LABELS:
            btn = QPushButton(label)
            if action_id == "ignore":
                btn.setObjectName("danger")
            else:
                btn.setObjectName("primary")
            btn.clicked.connect(lambda checked=False, f=failure, a=action_id: self._on_action(f, a))
            actions_row.addWidget(btn)
        actions_row.addStretch()
        v.addLayout(actions_row)
        return card

    def _on_action(self, failure, action: str) -> None:
        failure.actions_taken.append(action)
        if action == "ignore":
            failure.status = "ignored"
        else:
            failure.status = "resolved"
        # Przenieś do historii
        if failure in self.game.state.failures_active:
            self.game.state.failures_active.remove(failure)
            self.game.state.failures_history.append(failure)
        self.refresh()