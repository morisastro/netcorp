"""Dialog zapisu gry — wybór istniejącego zapisu (nadpisanie) lub nowa nazwa."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
)

from persistence import save_load


class SaveDialog(QDialog):
    """Dialog zapisu: lista istniejących zapisów + pole nowej nazwy."""

    def __init__(self, default_name: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Zapisz grę")
        self.resize(420, 400)
        self._chosen_name = ""
        self._build_ui(default_name)

    def _build_ui(self, default_name: str) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Istniejące zapisy
        existing_label = QLabel("📂 Istniejące zapisy (kliknij, aby nadpisać):")
        existing_label.setStyleSheet("color: #9a9a9a; font-weight: bold;")
        layout.addWidget(existing_label)

        self.saves_list = QListWidget()
        self.saves_list.setStyleSheet(
            "QListWidget { background-color: #1f1f1f; border: 1px solid #333333; }"
            "QListWidget::item { padding: 10px; border-bottom: 1px solid #2a2a2a; }"
            "QListWidget::item:selected { background-color: #2563eb; color: white; }"
        )
        self.saves_list.itemClicked.connect(self._on_select_existing)
        layout.addWidget(self.saves_list)

        # Pasek info
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #facc15; padding: 4px;")
        layout.addWidget(self.info_label)

        # Nowa nazwa
        new_label = QLabel("✏️ Lub wpisz nową nazwę:")
        new_label.setStyleSheet("color: #9a9a9a; font-weight: bold; margin-top: 8px;")
        layout.addWidget(new_label)

        name_row = QHBoxLayout()
        self.name_input = QLineEdit(default_name)
        self.name_input.textChanged.connect(self._on_name_changed)
        name_row.addWidget(self.name_input)
        layout.addLayout(name_row)

        # Przyciski
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setText("💾 Zapisz")
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._refresh_saves()

    def _refresh_saves(self) -> None:
        self.saves_list.clear()
        saves = save_load.list_saves()
        for s in saves:
            tag = "[AUTOSAVE] " if s["is_autosave"] else ""
            label = (
                f"{tag}{s['name']}    "
                f"Dzień {s['day']}    "
                f"${s['cash']:,.2f}    "
                f"Klienci: {s['customers']}"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, s["name"])
            self.saves_list.addItem(item)

    def _on_select_existing(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.UserRole)
        self.name_input.setText(name)
        self.info_label.setText(f"Nadpiszesz istniejący zapis: {name}")

    def _on_name_changed(self, text: str) -> None:
        # Sprawdź czy nazwa istnieje
        saves = {s["name"] for s in save_load.list_saves()}
        if text.strip() in saves:
            self.info_label.setText(f"Nadpiszesz istniejący zapis: {text.strip()}")
        else:
            self.info_label.setText("Nowy zapis")

    def _on_save(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            return
        self._chosen_name = name
        self.accept()

    def chosen_name(self) -> str:
        return self._chosen_name