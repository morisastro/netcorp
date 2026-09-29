"""System samouczka — prowadzi gracza przez pierwsze kroki.

Tutorial to lista kroków. Każdy krok ma: tytuł, opis, warunek ukończenia.
Pokazywany jako modal z przyciskami Dalej/Pomiń.
"""
from __future__ import annotations

from typing import Any, Callable

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


# Kroki samouczka. Każdy krok: (tytuł, treść HTML, wskazówka co zrobić)
TUTORIAL_STEPS: list[dict] = [
    {
        "title": "Witaj w NetCorp Tycoon!",
        "body": """
        <h2>🎮 Witaj!</h2>
        <p>Zbudujesz tu własną firmę hostingową — od garażowego home labu
        do międzynarodowego cloud providera.</p>
        <p>Grupa działa w <b>turniach dziennych</b>: planujesz, klikasz
        <b>"Następny dzień"</b>, system symuluje 24h.</p>
        <p>Jedyny warunek przegranej: <b>bankructwo</b> (brak gotówki).</p>
        <p>Kliknij <b>Dalej</b>, aby przejść przez samouczek.</p>
        """,
    },
    {
        "title": "Krok 1: Zatrudnij pracownika",
        "body": """
        <h2>👤 Zatrudnij pierwszego pracownika</h2>
        <p>Przejdź do <b>Pracownicy</b> w menu po lewej.</p>
        <p>Wybierz rolę <b>Support</b> (zamyka tickety klientów) i poziom 1.</p>
        <p>Koszt: <b>$50/dzień</b>. To inwestycja — bez supportu klienci będą
        niezadowoleni i szybciej odejdą.</p>
        """,
    },
    {
        "title": "Krok 2: Stwórz plan produktu",
        "body": """
        <h2>📦 Stwórz pierwszy plan</h2>
        <p>Przejdź do <b>Produkty</b> i kliknij <b>+ Dodaj plan</b>.</p>
        <p>Wybierz <b>VPS</b>, nazwij plan, ustaw parametry (2 vCPU, 4GB RAM, 50GB)
        i cenę np. <b>$9.99/mies</b>.</p>
        <p>Bez planów <b>nie ma klientów</b> — to kluczowy krok!</p>
        """,
    },
    {
        "title": "Krok 3: Zainwestuj w marketing",
        "body": """
        <h2>📢 Marketing</h2>
        <p>Przejdź do <b>Marketing</b> i ustaw budżet dzienny np. <b>$100</b>.</p>
        <p>Każde $15 wydan na marketing przynosi ~1 nowego klienta.</p>
        <p>Bez marketingu klientów przybywa bardzo powoli (tylko z reputacji).</p>
        """,
    },
    {
        "title": "Krok 4: Zbuduj stronę firmy",
        "body": """
        <h2>🌐 Strona firmy</h2>
        <p>Przejdź do <b>Strona firmy</b>. Przeciągnij bloki z paleti po lewej
        na stronę pośrodku.</p>
        <p>Każdy blok daje <b>bonus do konwersji</b> klientów z marketingu.</p>
        <p>Najmocniejsze: <b>Cennik (+10%)</b>, <b>Opinie (+8%)</b>,
        <b>Live chat (+6%)</b>.</p>
        """,
    },
    {
        "title": "Krok 5: Kolejny dzień",
        "body": """
        <h2>▶️ Następny dzień</h2>
        <p>Kliknij <b>Następny dzień</b> w prawym górnym rogu.</p>
        <p>System zasymuluje 24h: przychody, koszty, awarie, nowych klientów.</p>
        <p>Pojawi się <b>raport dzienny</b> z podsumowaniem.</p>
        <p>Im więcej dni przebiegnie, tym więcej klientów i... awarii.</p>
        """,
    },
    {
        "title": "Awarie i decyzje",
        "body": """
        <h2>⚠️ Awarie</h2>
        <p>Sprzęt czasem pada. Każda awaria wymaga <b>decyzji</b>:</p>
        <ul>
        <li><b>Restart</b> — szybkie, ale problem może wrócić</li>
        <li><b>Wymiana</b> — kosztuje $, ale trwale naprawia</li>
        <li><b>Failover</b> — przełącza na backup</li>
        <li><b>Ignoruj</b> — tanie, ale klienci cierpią</li>
        </ul>
        <p><b>Tani sprzęt = częstsze awarie</b>. Premium tier = drogi ale niezawodny.</p>
        """,
    },
    {
        "title": "Rozwój firmy",
        "body": """
        <h2>🚀 Rozwój</h2>
        <p>Kamienie milowe odblokowują nowe możliwości:</p>
        <ul>
        <li><b>50 klientów</b> → wynajem małej serwerowni</li>
        <li><b>500 klientów</b> → pełne DC</li>
        <li><b>2000 klientów</b> → drugi region</li>
        </ul>
        <p>Kupuj lepsze serwery, zatrudniaj więcej ludzi, rozszerzaj ofertę.</p>
        <p><b>Powodzenia!</b> 🎯</p>
        """,
    },
]


class TutorialDialog(QDialog):
    """Modal samouczka — pokazuje kroki jeden po drugim."""

    def __init__(self, on_finished: Callable[[], None], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Samouczek")
        self.resize(560, 420)
        self._step = 0
        self._on_finished = on_finished
        self._build_ui()
        self._show_step()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.title_label = QLabel("")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #60a5fa;")
        layout.addWidget(self.title_label)

        # Pasek postępu
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #6a6a6a; font-size: 11px;")
        layout.addWidget(self.progress_label)

        self.body = QTextBrowser()
        self.body.setStyleSheet("background: #1a1a1a; border: none;")
        layout.addWidget(self.body, 1)

        # Przyciski
        btn_row_layout = __import__("PySide6.QtWidgets", fromlist=["QHBoxLayout"]).QHBoxLayout()

        self.btn_skip = QPushButton("Pomiń samouczek")
        self.btn_skip.clicked.connect(self._skip)
        btn_row_layout.addWidget(self.btn_skip)
        btn_row_layout.addStretch()

        self.btn_prev = QPushButton("← Wstecz")
        self.btn_prev.clicked.connect(self._prev)
        btn_row_layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("Dalej →")
        self.btn_next.setObjectName("primary")
        self.btn_next.clicked.connect(self._next)
        btn_row_layout.addWidget(self.btn_next)

        layout.addLayout(btn_row_layout)

    def _show_step(self) -> None:
        if self._step >= len(TUTORIAL_STEPS):
            self._finish()
            return
        step = TUTORIAL_STEPS[self._step]
        self.title_label.setText(step["title"])
        self.progress_label.setText(f"Krok {self._step + 1} / {len(TUTORIAL_STEPS)}")
        self.body.setHtml(step["body"])
        # Przyciski
        self.btn_prev.setEnabled(self._step > 0)
        self.btn_next.setText("Zakończ ✓" if self._step == len(TUTORIAL_STEPS) - 1 else "Dalej →")

    def _next(self) -> None:
        self._step += 1
        self._show_step()

    def _prev(self) -> None:
        if self._step > 0:
            self._step -= 1
        self._show_step()

    def _skip(self) -> None:
        self._finish()

    def _finish(self) -> None:
        self._on_finished()
        self.accept()