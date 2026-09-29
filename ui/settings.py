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

        # Otwórz foldery
        folders_row = QHBoxLayout()
        self.btn_open_saves = QPushButton("📂  Otwórz folder zapisów")
        self.btn_open_saves.clicked.connect(self._on_open_saves_folder)
        folders_row.addWidget(self.btn_open_saves)
        self.btn_open_mods = QPushButton("🧩  Otwórz folder modów")
        self.btn_open_mods.clicked.connect(self._on_open_mods_folder)
        folders_row.addWidget(self.btn_open_mods)
        self.btn_open_game = QPushButton("🎮  Otwórz folder gry")
        self.btn_open_game.clicked.connect(self._on_open_game_folder)
        folders_row.addWidget(self.btn_open_game)
        folders_row.addStretch()
        layout.addLayout(folders_row)

        # Sekcja: zainstalowane mody
        mods_title = QLabel("🧩 Zainstalowane mody")
        mods_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 12px;")
        layout.addWidget(mods_title)
        self.mods_label = QLabel("—")
        self.mods_label.setStyleSheet("color: #9a9a9a; padding: 8px; background: #1f1f1f; border-radius: 4px;")
        self.mods_label.setWordWrap(True)
        layout.addWidget(self.mods_label)

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

        # Sekcja: Debug mode
        debug_title = QLabel("🐛 Debug mode")
        debug_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #facc15; margin-top: 12px;")
        layout.addWidget(debug_title)
        debug_info = QLabel(
            "Włącz debug mode aby zobaczyć dodatkowe informacje w konsoli\n"
            "(liczba klientów, usługi, awarie, obciążenie serwerów)."
        )
        debug_info.setStyleSheet("color: #9a9a9a;")
        debug_info.setWordWrap(True)
        layout.addWidget(debug_info)

        from PySide6.QtWidgets import QCheckBox
        from app.settings import is_debug, set_debug
        self.debug_checkbox = QCheckBox("Włącz debug mode (wymaga restartu)")
        self.debug_checkbox.setChecked(is_debug())
        self.debug_checkbox.stateChanged.connect(lambda state: set_debug(state == 2))  # 2 = Checked
        layout.addWidget(self.debug_checkbox)

        # Sekcja: Błędy / Issues
        bugs_title = QLabel("🐞 Zgłaszanie błędów")
        bugs_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #f87171; margin-top: 12px;")
        layout.addWidget(bugs_title)
        bugs_info = QLabel(
            "Znalazłeś błąd? Masz propozycję? Zgłoś to na GitHub:\n"
            "https://github.com/morisastro/netcorp/issues\n\n"
            "Opisz co się stało, jakie kroki wykonałeś, i screen jeśli możliwe."
        )
        bugs_info.setStyleSheet("color: #9a9a9a;")
        bugs_info.setWordWrap(True)
        layout.addWidget(bugs_info)

        bugs_row = QHBoxLayout()
        self.btn_open_issues = QPushButton("🐞  Otwórz GitHub Issues")
        self.btn_open_issues.clicked.connect(lambda: self._open_url("https://github.com/morisastro/netcorp/issues"))
        bugs_row.addWidget(self.btn_open_issues)
        bugs_row.addStretch()
        layout.addLayout(bugs_row)

        layout.addStretch()

    def _on_save(self) -> None:
        from PySide6.QtWidgets import QDialog
        from ui.save_dialog import SaveDialog
        dlg = SaveDialog(default_name=f"partia-dzien-{self.game.state.day}", parent=self)
        if dlg.exec() != QDialog.Accepted:
            return
        name = dlg.chosen_name()
        if not name:
            return
        saves = {s["name"] for s in save_load.list_saves()}
        if name in saves:
            reply = QMessageBox.question(
                self, "Nadpisać zapis?",
                f"Zapis „{name}” już istnieje. Nadpisać?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return
        try:
            save_load.save_game(self.game, name)
            QMessageBox.information(self, "Zapisano", f"Partia zapisana jako „{name}”.")
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
        # Pokaż zainstalowane mody
        try:
            from core.mods import list_mods
            mods = list_mods()
            if not mods:
                self.mods_label.setText("Brak zainstalowanych modów. Dodaj plik .json do folderu mods/.")
            else:
                lines = []
                for m in mods:
                    status = "✅" if m.get("enabled", True) else "❌"
                    lines.append(f"{status}  {m['name']} v{m['version']}  ({m['author']})")
                    if m.get("description"):
                        lines.append(f"      {m['description']}")
                self.mods_label.setText("\n".join(lines))
        except Exception:
            self.mods_label.setText("Błąd ładowania modów.")

    def _open_url(self, url: str) -> None:
        if not url:
            return
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl(url))

    def _open_path(self, path) -> None:
        """Otwiera folder w explorerze (tworzy jeśli brak)."""
        from pathlib import Path
        import subprocess, sys
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(p)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p)])

    def _on_open_saves_folder(self) -> None:
        from app.settings import save_dir
        self._open_path(save_dir())

    def _on_open_mods_folder(self) -> None:
        from core.mods import mods_dir
        self._open_path(mods_dir())

    def _on_open_game_folder(self) -> None:
        """Otwórz folder, w którym jest uruchomiona gra (.exe lub main.py)."""
        import sys, os
        from pathlib import Path
        if getattr(sys, "frozen", False):
            # PyInstaller — folder obok exe
            p = Path(sys.executable).parent
        else:
            # Dev — katalog projektu
            p = Path(__file__).resolve().parent.parent
        self._open_path(p)