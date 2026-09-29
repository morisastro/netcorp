"""Ekran menu głównego (startowego) — nowa gra, wczytaj, ustawienia, wyjście.

Pokazywany przed otwarciem okna gry. Tutaj gracz wybiera:
- Nowa gra (start od garażu)
- Wczytaj partię (lista zapisów)
- Ustawienia (licencja, o programie)
- Wyjście
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.settings import APP_DISPLAY_NAME, APP_VERSION, save_dir
from app.update_checker import check_for_update
from persistence import save_load


GAME_MODES = [
    {
        "id": "sandbox",
        "name": "Sandbox",
        "desc": "Tryb otwarty — buduj firmę bez limitów, bez przegrania.",
        "cash": 5000.0,
        "reputation": 50.0,
        "failure_mult": 1.0,
    },
    {
        "id": "career",
        "name": "Kariera",
        "desc": "Tryb z bankructwem — od garażu do providera, jedyny fail = brak gotówki.",
        "cash": 3000.0,
        "reputation": 40.0,
        "failure_mult": 1.2,
    },
    {
        "id": "hardcore",
        "name": "Hardcore",
        "desc": "Minimalny kapitał, wyższa awaryjność, szybsze tempo. Dla weteranów.",
        "cash": 1500.0,
        "reputation": 30.0,
        "failure_mult": 1.8,
    },
]


class MainMenuWindow(QWidget):
    """Menu startowe. Emituje sygnał gdy gracz wybierze partię do załadowania."""

    def __init__(self, on_start_game, parent=None) -> None:
        super().__init__(parent)
        self.on_start_game = on_start_game  # callback(game: Game)
        self.setWindowTitle(f"{APP_DISPLAY_NAME}")
        from ui.screen_info import recommended_menu_size
        menu_w, menu_h = recommended_menu_size()
        self.resize(menu_w, menu_h)
        self.setMinimumSize(760, 520)
        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Lewa kolumna — menu akcji
        left = QFrame()
        left.setFixedWidth(260)
        left.setStyleSheet("background-color: #111111; border-right: 1px solid #333333;")
        llayout = QVBoxLayout(left)
        llayout.setContentsMargins(0, 0, 0, 0)
        llayout.setSpacing(0)

        logo = QLabel(APP_DISPLAY_NAME)
        logo.setStyleSheet(
            "color: #60a5fa; font-size: 20px; font-weight: bold; "
            "padding: 24px; background: transparent;"
        )
        llayout.addWidget(logo)

        subtitle = QLabel("Cloud provider tycoon")
        subtitle.setStyleSheet("color: #6a6a6a; padding: 0 24px 24px 24px; background: transparent;")
        llayout.addWidget(subtitle)

        self.btn_new = QPushButton("➕  Nowa gra")
        self.btn_load = QPushButton("📂  Wczytaj partię")
        self.btn_settings = QPushButton("⚙️  Ustawienia / O programie")
        self.btn_exit = QPushButton("🚪  Wyjście")

        for btn in (self.btn_new, self.btn_load, self.btn_settings, self.btn_exit):
            btn.setStyleSheet(
                "background: transparent; border: none; text-align: left; "
                "padding: 14px 24px; color: #9a9a9a; font-size: 14px;"
            )
            llayout.addWidget(btn)

        llayout.addStretch()

        ver = QLabel(f"v{APP_VERSION}")
        ver.setStyleSheet("color: #6a6a6a; padding: 16px 24px; font-size: 11px;")
        llayout.addWidget(ver)

        self.btn_new.clicked.connect(self._on_show_modes)
        self.btn_load.clicked.connect(self._on_show_load)
        self.btn_settings.clicked.connect(self._on_show_settings)
        self.btn_exit.clicked.connect(self.close)

        # Prawa kolumna — stacked (powitanie / wczytaj / ustawienia)
        right = QFrame()
        rlayout = QVBoxLayout(right)
        rlayout.setContentsMargins(0, 0, 0, 0)
        rlayout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_welcome())
        self.stack.addWidget(self._build_modes_panel())
        self.stack.addWidget(self._build_load_panel())
        self.stack.addWidget(self._build_settings_panel())
        rlayout.addWidget(self.stack)

        root.addWidget(left, 0)
        root.addWidget(right, 1)

        # Sprawdź aktualizację w tle
        self._check_update_async()

    def _build_welcome(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QLabel("Witaj w NetCorp Tycoon")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)

        desc = QLabel(
            "Zbuduj własną firmę hostingową — od garażowego home labu "
            "do międzynarodowego cloud providera.\n\n"
            "Kliknij „+ Nowa gra” po lewej, aby zacząć nową partię, "
            "lub „Wczytaj partię”, aby wrócić do zapisanej gry."
        )
        desc.setStyleSheet("color: #9a9a9a; font-size: 14px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addStretch()

        # Banner aktualizacji
        self.update_banner = QLabel("")
        self.update_banner.setStyleSheet(
            "color: #93c5fd; background-color: #1e3a5f; "
            "padding: 12px; border-radius: 4px;"
        )
        self.update_banner.setWordWrap(True)
        self.update_banner.setVisible(False)
        layout.addWidget(self.update_banner)

        return w

    def _build_modes_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QLabel("Wybierz tryb gry")
        title.setObjectName("screen-title")
        layout.addWidget(title)

        hint = QLabel("Wybierz tryb, który określa kapitał startowy i trudność:")
        hint.setStyleSheet("color: #6a6a6a;")
        layout.addWidget(hint)

        # Panel nickname / nazwa firmy (powolne wprowadzanie do MP)
        from PySide6.QtWidgets import QFrame, QLineEdit, QHBoxLayout
        nick_frame = QFrame()
        nick_frame.setObjectName("card")
        nick_frame.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 4px; }"
        )
        nick_layout = QVBoxLayout(nick_frame)
        nick_layout.setContentsMargins(16, 12, 16, 12)
        nick_layout.setSpacing(6)

        nick_title = QLabel("👤 Twój nickname / nazwa firmy")
        nick_title.setStyleSheet("color: #60a5fa; font-weight: bold;")
        nick_layout.addWidget(nick_title)

        nick_hint = QLabel("W przyszłości (multiplayer) inni gracze zobaczą tę nazwę w rankingach.")
        nick_hint.setStyleSheet("color: #6a6a6a; font-size: 11px;")
        nick_hint.setWordWrap(True)
        nick_layout.addWidget(nick_hint)

        nick_row = QHBoxLayout()
        nick_row.setSpacing(8)
        nick_row.addWidget(QLabel("Nickname:"))
        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("np. morisastro")
        self.nick_input.setMaximumWidth(200)
        nick_row.addWidget(self.nick_input)
        nick_row.addStretch()
        nick_layout.addLayout(nick_row)

        comp_row = QHBoxLayout()
        comp_row.setSpacing(8)
        comp_row.addWidget(QLabel("Firma:"))
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("np. NetCorp")
        self.company_input.setMaximumWidth(200)
        self.company_input.setText("NetCorp")
        comp_row.addWidget(self.company_input)
        comp_row.addStretch()
        nick_layout.addLayout(comp_row)

        layout.addWidget(nick_frame)

        from PySide6.QtWidgets import QFrame, QPushButton as QP
        self.mode_buttons: dict[str, QP] = {}
        for mode in GAME_MODES:
            card = QFrame()
            card.setObjectName("card")
            card.setStyleSheet(
                "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 4px; }"
                "QFrame#card:hover { border-color: #2563eb; }"
            )
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 12, 16, 12)
            c_layout.setSpacing(4)

            name_lbl = QLabel(f"🎯 {mode['name']}")
            name_lbl.setStyleSheet("color: #60a5fa; font-size: 16px; font-weight: bold;")
            c_layout.addWidget(name_lbl)

            desc_lbl = QLabel(mode["desc"])
            desc_lbl.setStyleSheet("color: #9a9a9a;")
            desc_lbl.setWordWrap(True)
            c_layout.addWidget(desc_lbl)

            stats_lbl = QLabel(
                f"Kapitał startowy: ${mode['cash']:,.0f}    "
                f"Reputacja: {mode['reputation']:.0f}/100    "
                f"Awaryjność: ×{mode['failure_mult']}"
            )
            stats_lbl.setStyleSheet("color: #facc15; font-size: 12px;")
            c_layout.addWidget(stats_lbl)

            btn = QP("Rozpocznij ten tryb →")
            btn.setObjectName("primary")
            btn.clicked.connect(lambda checked=False, m=mode: self._on_start_mode(m))
            c_layout.addWidget(btn)

            self.mode_buttons[mode["id"]] = btn
            layout.addWidget(card)

        layout.addStretch()
        return w

    def _build_load_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QLabel("Wczytaj partię")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)

        hint = QLabel("Wybierz zapis z listy poniżej:")
        hint.setStyleSheet("color: #6a6a6a;")
        layout.addWidget(hint)

        self.saves_list = QListWidget()
        self.saves_list.setStyleSheet(
            "QListWidget { background-color: #1f1f1f; border: 1px solid #333333; }"
            "QListWidget::item { padding: 12px; border-bottom: 1px solid #2a2a2a; }"
            "QListWidget::item:selected { background-color: #2563eb; color: white; }"
        )
        self.saves_list.itemDoubleClicked.connect(self._on_load_selected)
        layout.addWidget(self.saves_list, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.btn_load_selected = QPushButton("Wczytaj zaznaczone")
        self.btn_load_selected.setObjectName("primary")
        self.btn_load_selected.clicked.connect(self._on_load_selected)
        btn_row.addWidget(self.btn_load_selected)
        self.btn_delete_save = QPushButton("Usuń zapis")
        self.btn_delete_save.setObjectName("danger")
        self.btn_delete_save.clicked.connect(self._on_delete_save)
        btn_row.addWidget(self.btn_delete_save)
        self.btn_refresh_saves = QPushButton("Odśwież")
        self.btn_refresh_saves.clicked.connect(self._refresh_saves)
        btn_row.addWidget(self.btn_refresh_saves)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.empty_saves_label = QLabel("Brak zapisów. Rozpocznij nową grę.")
        self.empty_saves_label.setStyleSheet("color: #6a6a6a; padding: 12px;")
        layout.addWidget(self.empty_saves_label)

        return w

    def _build_settings_panel(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(12)

        title = QLabel("Ustawienia / O programie")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(10)

        info_lines = [
            f"NetCorp Tycoon v{APP_VERSION}",
            "",
            "Gra management/tycoon o prowadzeniu firmy hostingowej / cloud providera.",
            "",
            "Licencja: CC BY-ND 4.0 (gra darmowa).",
            "Modyfikacje (mody) dozwolone przez oficjalny modding API.",
            "",
            f"Zapisy: {save_dir()}",
            "",
            "Sprawdzanie aktualizacji: na starcie (GitHub releases).",
        ]
        for line in info_lines:
            lbl = QLabel(line)
            lbl.setStyleSheet("color: #d4d4d4;")
            lbl.setWordWrap(True)
            inner_layout.addWidget(lbl)

        # Sekcja licencji
        lic_title = QLabel("Licencja")
        lic_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #60a5fa; margin-top: 16px;")
        inner_layout.addWidget(lic_title)
        lic_body = QLabel(
            "Creative Commons Attribution-NoDerivatives 4.0 International.\n"
            "Możesz kopiować i dystrybuować grę z atrybucją.\n"
            "Nie wolno redystrybuować zmodyfikowanej wersji kodu.\n"
            "Mody jako osobne pakiety są dozwolone."
        )
        lic_body.setStyleSheet("color: #9a9a9a;")
        lic_body.setWordWrap(True)
        inner_layout.addWidget(lic_body)

        inner_layout.addStretch()
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        self.btn_check_update = QPushButton("Sprawdź aktualizacje teraz")
        self.btn_check_update.clicked.connect(self._on_check_update_manual)
        layout.addWidget(self.btn_check_update)

        return w

    # ---- akcje ----

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._refresh_saves()

    def _on_start_mode(self, mode: dict) -> None:
        from core.game import Game
        import uuid
        game = Game.new_game()
        # Dostosuj do trybu
        game.state.cash = mode["cash"]
        game.state.reputation = mode["reputation"]
        game.state.game_mode = mode["id"]
        game.state.failure_multiplier = mode["failure_mult"]
        # Nickname / nazwa firmy
        nick = self.nick_input.text().strip() or "Player"
        company = self.company_input.text().strip() or "NetCorp"
        game.state.player_nick = nick
        game.state.company_name = company
        game.state.player_id = uuid.uuid4().hex  # unikalne ID (do MP w przyszłości)
        # Autosave nowej gry
        try:
            save_load.autosave(game)
        except Exception:
            pass
        self.on_start_game(game)
        self.close()

    def _on_show_modes(self) -> None:
        self.stack.setCurrentIndex(1)

    def _on_show_load(self) -> None:
        self.stack.setCurrentIndex(2)
        self._refresh_saves()

    def _on_show_settings(self) -> None:
        self.stack.setCurrentIndex(3)

    def _refresh_saves(self) -> None:
        self.saves_list.clear()
        saves = save_load.list_saves()
        if not saves:
            self.empty_saves_label.setVisible(True)
            return
        self.empty_saves_label.setVisible(False)
        for s in saves:
            tag = "  [AUTOSAVE] " if s["is_autosave"] else "  "
            label = (
                f"{tag}{s['name']}    "
                f"Dzień {s['day']}    "
                f"${s['cash']:,.2f}    "
                f"Klienci: {s['customers']}    "
                f"({s['saved_at']})"
            )
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, s)
            self.saves_list.addItem(item)

    def _on_load_selected(self, item=None) -> None:
        if item is None:
            item = self.saves_list.currentItem()
        if item is None:
            return
        s = item.data(Qt.UserRole)
        try:
            game = save_load.load_from_path(Path(s["path"]))
            self.on_start_game(game)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Błąd wczytywania", f"Nie udało się wczytać zapisu:\n{e}")

    def _on_delete_save(self) -> None:
        item = self.saves_list.currentItem()
        if item is None:
            return
        s = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "Usuń zapis",
            f"Czy na pewno usunąć zapis „{s['name']}”?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                Path(s["path"]).unlink()
            except OSError:
                pass
            self._refresh_saves()

    def _on_check_update_manual(self) -> None:
        info = check_for_update()
        if info is None:
            QMessageBox.information(self, "Aktualizacje", "Masz najnowszą wersję.")
            return
        # Zbuduj listę plików do pobrania
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

    def _check_update_async(self) -> None:
        import threading
        from PySide6.QtCore import QTimer

        def worker():
            info = check_for_update()
            if info:
                QTimer.singleShot(0, lambda: self._show_update_banner(info))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _show_update_banner(self, info: dict) -> None:
        self.update_banner.setText(
            f"⬆ Dostępna nowa wersja: {info['tag']} — {info.get('name', '')}\n"
            f"Pobierz z: {info.get('url', '')}"
        )
        self.update_banner.setVisible(True)

    def _apply_theme(self) -> None:
        from ui.theme import DARK_QSS
        self.setStyleSheet(DARK_QSS)