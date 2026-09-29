"""Okno główne aplikacji — sidebar + topbar + centralny ekran."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.settings import APP_DISPLAY_NAME, APP_VERSION
from app.update_checker import check_for_update
from core.game import Game
from ui.dashboard import DashboardScreen
from ui.placeholder import PlaceholderScreen
from ui.theme import DARK_QSS


# (id, etykieta PL) pozycji w sidebar
SIDEBAR_ITEMS = [
    ("dashboard", "Przegląd"),
    ("infrastructure", "Infrastruktura"),
    ("products", "Produkty"),
    ("customers", "Klienci"),
    ("failures", "Awarie"),
    ("employees", "Pracownicy"),
    ("marketing", "Marketing"),
    ("website", "Strona firmy"),
    ("finances", "Finanse"),
    ("settings", "Ustawienia"),
]


class MainWindow(QWidget):
    """Główne okno aplikacji (bez ramki QMainWindow — używamy QWidget + własny układ).

    Layout: [sidebar | (topbar / stacked screens)]
    """

    def __init__(self) -> None:
        super().__init__()
        self.game: Game = Game.new_game()
        self._current_screen_id: str = "dashboard"
        self._build_ui()
        self._apply_theme()
        self._check_update_async()

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{APP_DISPLAY_NAME} v{APP_VERSION}")
        self.resize(1280, 800)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = self._build_sidebar()
        root.addWidget(sidebar, 0)

        # Prawa kolumna: topbar + stacked
        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.topbar = self._build_topbar()
        right.addWidget(self.topbar, 0)

        self.stack = QStackedWidget()
        self.screens: dict[str, QWidget] = {}
        self._build_screens()
        right.addWidget(self.stack, 1)

        root.addLayout(right, 1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(200)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QLabel(APP_DISPLAY_NAME)
        logo.setObjectName("logo")
        layout.addWidget(logo)

        self.nav_buttons: dict[str, QPushButton] = {}
        for sid, label in SIDEBAR_ITEMS:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, s=sid: self._switch_screen(s))
            layout.addWidget(btn)
            self.nav_buttons[sid] = btn

        layout.addStretch()

        # Stopka sidebar
        footer = QLabel(f"v{APP_VERSION}")
        footer.setStyleSheet("color: #6a6a6a; padding: 12px; font-size: 11px;")
        layout.addWidget(footer)

        return sidebar

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setObjectName("topbar")
        bar.setFixedHeight(48)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        self.date_label = QLabel("Dzień 1 • 2030-01-01")
        self.date_label.setObjectName("kpi")
        layout.addWidget(self.date_label)

        layout.addStretch()

        self.kpi_cash = QLabel("Gotówka: $5,000.00")
        self.kpi_cash.setObjectName("kpi")
        layout.addWidget(self.kpi_cash)

        self.kpi_customers = QLabel("Klienci: 0")
        self.kpi_customers.setObjectName("kpi")
        layout.addWidget(self.kpi_customers)

        self.kpi_reputation = QLabel("Reputacja: 50/100")
        self.kpi_reputation.setObjectName("kpi")
        layout.addWidget(self.kpi_reputation)

        layout.addStretch()

        self.btn_next_day = QPushButton("▶ Następny dzień")
        self.btn_next_day.setObjectName("primary")
        self.btn_next_day.clicked.connect(self._on_next_day)
        layout.addWidget(self.btn_next_day)

        # Banner aktualizacji (ukryty domyślnie)
        self.update_banner = QFrame()
        self.update_banner.setObjectName("update-banner")
        self.update_banner.setFixedHeight(0)
        ub_layout = QHBoxLayout(self.update_banner)
        ub_layout.setContentsMargins(12, 4, 12, 4)
        self.update_title = QLabel("")
        self.update_title.setObjectName("update-title")
        self.update_msg = QLabel("")
        self.update_link = QPushButton("Otwórz release →")
        self.update_link.setStyleSheet("background: transparent; border: none; color: #93c5fd;")
        ub_layout.addWidget(self.update_title)
        ub_layout.addWidget(self.update_msg, 1)
        ub_layout.addWidget(self.update_link)
        ub_layout.addStretch()

        # Wrapper z bannerem nad topbarem
        wrapper = QFrame()
        wrapper.setObjectName("topbar")
        wlayout = QVBoxLayout(wrapper)
        wlayout.setContentsMargins(0, 0, 0, 0)
        wlayout.setSpacing(0)
        wlayout.addWidget(self.update_banner)
        wlayout.addWidget(bar)
        return wrapper

    def _build_screens(self) -> None:
        # Dashboard — zaimplementowany
        self.screens["dashboard"] = DashboardScreen(self.game)
        # Pozostałe — placeholder z opisem
        placeholders = {
            "infrastructure": ("Infrastruktura", "Serwerownia, sloty, katalog serwerów, zasoby DC (prąd/sieć/chłodzenie)."),
            "products": ("Produkty", "Tworzenie planów i cen dla hostingu WWW, VPS, dedyków, domen."),
            "customers": ("Klienci", "Agregaty klientów per produkt, churn, status SLA."),
            "failures": ("Awarie", "Aktywne awarie, wybór akcji (restart/wymiana/failover/ignore), historia."),
            "employees": ("Pracownicy", "Zatrudnianie i zwalnianie: Support, Sysadmin, NetEng, Sales, Marketing."),
            "marketing": ("Marketing", "Budżet dzienny, ROI, przyrost klientów."),
            "website": ("Strona firmy", "Drag & drop builder sekcji strony — bonus do konwersji klientów."),
            "finances": ("Finanse", "Przychody i koszty dzienne, wykres gotówki."),
            "settings": ("Ustawienia", "Zapis/wczytanie gry, licencja, sprawdź aktualizacje, o programie."),
        }
        for sid, (title, desc) in placeholders.items():
            self.screens[sid] = PlaceholderScreen(title, desc)

        for sid, widget in self.screens.items():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)
            scroll.setFrameShape(QFrame.NoFrame)
            self.stack.addWidget(scroll)

        self._switch_screen("dashboard")

    def _switch_screen(self, screen_id: str) -> None:
        self._current_screen_id = screen_id
        self.stack.setCurrentWidget(self.stack.widget(list(self.screens.keys()).index(screen_id) if False else self._index_of(screen_id)))
        for sid, btn in self.nav_buttons.items():
            btn.setChecked(sid == screen_id)
        # Odśwież ekran jeśli ma metodę refresh()
        widget = self.screens.get(screen_id)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _index_of(self, screen_id: str) -> int:
        for i in range(self.stack.count()):
            scroll = self.stack.widget(i)
            if scroll.widget() is self.screens.get(screen_id):
                return i
        return 0

    def _on_next_day(self) -> None:
        """Symulacja jednego dnia."""
        report = self.game.next_day()
        self._refresh_all()

    def _refresh_all(self) -> None:
        """Odświeża topbar i aktywny ekran."""
        state = self.game.state
        self.date_label.setText(self.game.date_label())
        self.kpi_cash.setText(f"Gotówka: ${state.cash:,.2f}")
        self.kpi_customers.setText(f"Klienci: {self.game.total_customers()}")
        self.kpi_reputation.setText(f"Reputacja: {state.reputation:.0f}/100")

        widget = self.screens.get(self._current_screen_id)
        if hasattr(widget, "refresh"):
            widget.refresh()

    def _apply_theme(self) -> None:
        self.setStyleSheet(DARK_QSS)

    def _check_update_async(self) -> None:
        """Sprawdza aktualizację w tle i pokazuje banner jeśli nowsza wersja."""
        import threading

        def worker():
            info = check_for_update()
            if info:
                # Aktualizuj UI w wątku głównym
                from PySide6.QtCore import QTimer
                QTimer.singleShot(0, lambda: self._show_update_banner(info))

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _show_update_banner(self, info: dict) -> None:
        self.update_title.setText(f"Dostępna nowa wersja: {info['tag']}")
        self.update_msg.setText(info.get("name", ""))
        self.update_link.clicked.connect(lambda: self._open_url(info.get("url", "")))
        self.update_banner.setFixedHeight(32)

    def _open_url(self, url: str) -> None:
        if not url:
            return
        from PySide6.QtGui import QDesktopServices
        from PySide6.QtCore import QUrl
        QDesktopServices.openUrl(QUrl(url))