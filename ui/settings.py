"""Ekran Ustawienia — zapis, licencja, o programie, aktualizacje."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.settings import APP_DISPLAY_NAME, APP_VERSION, save_dir
from app.update_checker import check_for_update
from core.game import Game
from persistence import save_load


class SettingsScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Ustawienia")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        # Sekcja: zapis
        save_title = QLabel("Zapis / wczytanie")
        save_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 8px;")
        layout.addWidget(save_title)

        save_row = QHBoxLayout()
        self.btn_save = QPushButton("💾 Zapisz partię pod nazwą")
        self.btn_save.setObjectName("primary")
        self.btn_save.clicked.connect(self._on_save)
        save_row.addWidget(self.btn_save)
        self.btn_autosave = QPushButton("💾 Zapisz jako autosave")
        self.btn_autosave.clicked.connect(self._on_autosave)
        save_row.addWidget(self.btn_autosave)
        save_row.addStretch()
        layout.addLayout(save_row)

        # Sekcja: aktualizacje
        up_title = QLabel("Aktualizacje")
        up_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 12px;")
        layout.addWidget(up_title)
        self.btn_check = QPushButton("Sprawdź aktualizacje teraz")
        self.btn_check.clicked.connect(self._on_check_update)
        layout.addWidget(self.btn_check)

        # Sekcja: GitHub
        gh_title = QLabel("GitHub")
        gh_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 12px;")
        layout.addWidget(gh_title)
        gh_row = QHBoxLayout()
        self.btn_github_repo = QPushButton("📂  Repozytorium")
        self.btn_github_repo.clicked.connect(lambda: self._open_url("https://github.com/morisastro/netcorp"))
        gh_row.addWidget(self.btn_github_repo)
        self.btn_github_releases = QPushButton("🏷️  Releases")
        self.btn_github_releases.clicked.connect(lambda: self._open_url("https://github.com/morisastro/netcorp/releases"))
        gh_row.addWidget(self.btn_github_releases)
        self.btn_github_issues = QPushButton("🐛  Zgłoś problem")
        self.btn_github_issues.clicked.connect(lambda: self._open_url("https://github.com/morisastro/netcorp/issues"))
        gh_row.addWidget(self.btn_github_issues)
        gh_row.addStretch()
        layout.addLayout(gh_row)

        # Sekcja: licencja
        lic_title = QLabel("Licencja")
        lic_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 12px;")
        layout.addWidget(lic_title)
        lic_body = QLabel(
            f"{APP_DISPLAY_NAME} v{APP_VERSION}\n"
            "Licencja: CC BY-ND 4.0 (gra darmowa).\n"
            "Możesz kopiować i dystrybuować grę z atrybucją.\n"
            "Nie wolno redystrybuować zmodyfikowanej wersji kodu.\n"
            "Mody jako osobne pakiety są dozwolone."
        )
        lic_body.setStyleSheet("color: #9a9a9a;")
        lic_body.setWordWrap(True)
        layout.addWidget(lic_body)

        # Sekcja: info
        info_title = QLabel("O programie")
        info_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 12px;")
        layout.addWidget(info_title)
        info = QLabel(
            f"Wersja: {APP_VERSION}\n"
            f"Zapisy: {save_dir()}\n"
            "Sprawdzanie aktualizacji: automatyczne przy starcie (GitHub releases)."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        layout.addStretch()

    def _on_save(self) -> None:
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Zapisz grę", "Nazwa zapisu:", text=f"partia-dzien-{self.game.state.day}")
        if not ok or not name.strip():
            return
        try:
            save_load.save_game(self.game, name.strip())
            QMessageBox.information(self, "Zapisano", f"Partia zapisana jako „{name.strip()}”.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się zapisać:\n{e}")

    def _on_autosave(self) -> None:
        try:
            save_load.autosave(self.game)
            QMessageBox.information(self, "Zapisano", "Autosave zapisany.")
        except Exception as e:
            QMessageBox.critical(self, "Błąd zapisu", f"Nie udało się zapisać:\n{e}")

    def _on_check_update(self) -> None:
        info = check_for_update()
        if info is None:
            QMessageBox.information(self, "Aktualizacje", "Masz najnowszą wersję.")
            return
        assets = info.get("assets", [])
        win_asset = next((a for a in assets if "win" in a["name"].lower()), None)
        lines = [f"Nowa wersja: {info['tag']}"]
        lines.append(info.get("name", ""))
        lines.append("")
        if win_asset:
            lines.append(f"Pobierz Windows: {win_asset['name']} ({win_asset['size_mb']} MB)")
            lines.append(f"  {win_asset['url']}")
        else:
            lines.append("Pobierz z:")
            lines.append(info.get("url", ""))
        lines.append("")
        lines.append("Wszystkie pliki:")
        for a in assets:
            lines.append(f"  • {a['name']} ({a['size_mb']} MB)")
        QMessageBox.information(self, "Dostępna aktualizacja", "\n".join(lines))

    def refresh(self) -> None:
        pass  # ustawienia statyczne

    def _open_url(self, url: str) -> None:
        if not url:
            return
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(url))