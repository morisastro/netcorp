"""Ekran Strona firmy — drag & drop builder sekcji."""
from __future__ import annotations

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.game import Game
from core.models import WebsiteBlock

# Dostępne bloki do przeciągania
BLOCK_TYPES = [
    ("hero", "Hero / Nagłówek", "Duży nagłówek z hasłem firmy"),
    ("pricing", "Cennik", "Tabela cen planów — silny wpływ na konwersję"),
    ("reviews", "Opinie klientów", "Recenzje zadowolonych klientów"),
    ("status", "Status serwerów", "Live status infrastruktury"),
    ("faq", "FAQ", "Najczęstsze pytania klientów"),
    ("contact", "Kontakt", "Dane kontaktowe"),
    ("chat", "Live chat", "Czat na żywo — bonus do konwersji"),
    ("blog", "Blog", "Artykuły techniczne"),
]

BLOCK_BONUS = {
    "hero": 0.05, "pricing": 0.10, "reviews": 0.08, "status": 0.05,
    "faq": 0.04, "contact": 0.04, "chat": 0.06, "blog": 0.03,
}


class BlockWidget(QFrame):
    """Pojedynczy blok na liście (dragable)."""

    def __init__(self, block_type: str, label: str, desc: str, parent=None) -> None:
        super().__init__(parent)
        self.block_type = block_type
        self.setObjectName("card")
        self.setFixedHeight(56)
        self.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 4px; }"
            "QFrame#card:hover { border-color: #2563eb; }"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #d4d4d4; font-weight: bold;")
        layout.addWidget(lbl)
        d = QLabel(desc)
        d.setStyleSheet("color: #6a6a6a;")
        layout.addWidget(d, 1)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.block_type)
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)


class PlacedBlockWidget(QFrame):
    """Blok już dodany do strony (z przyciskiem usuń)."""

    def __init__(self, block: WebsiteBlock, on_remove, parent=None) -> None:
        super().__init__(parent)
        self.block = block
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { background-color: #1e3a5f; border: 1px solid #2563eb; border-radius: 4px; }"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        label = next((l for t, l, d in BLOCK_TYPES if t == block.block_type), block.block_type)
        lbl = QLabel(f"✓ {label}  (+{BLOCK_BONUS.get(block.block_type, 0)*100:.0f}%)")
        lbl.setStyleSheet("color: #93c5fd; font-weight: bold;")
        layout.addWidget(lbl)
        layout.addStretch()
        btn = QPushButton("Usuń")
        btn.setObjectName("danger")
        btn.clicked.connect(lambda: on_remove(block))
        layout.addWidget(btn)


class _DropFrame(QFrame):
    """QFrame akceptujący drop bloków (text mime = block_type)."""
    def __init__(self, on_drop, parent=None) -> None:
        super().__init__(parent)
        self._on_drop = on_drop
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        self._on_drop(event.mimeData().text())


class WebsiteScreen(QWidget):
    def __init__(self, game: Game, parent=None) -> None:
        super().__init__(parent)
        self.game = game
        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title = QLabel("Strona firmy")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel(
            "Przeciągnij bloki z lewej na stronę po prawej. "
            "Lepsza strona = większy bonus do konwersji klientów z marketingu."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        # Wskaźnik bonusu
        self.bonus_label = QLabel("Bonus do konwersji: 0%")
        self.bonus_label.setStyleSheet("color: #facc15; font-weight: bold; padding: 8px; background: #1f1f1f; border-radius: 4px;")
        layout.addWidget(self.bonus_label)

        # Dwie kolumny: paleta bloków | strona
        cols = QHBoxLayout()
        cols.setSpacing(12)

        # Paleta bloków (po lewej)
        palette_frame = QFrame()
        palette_frame.setStyleSheet("background: #1a1a1a; border: 1px solid #3a3a3a; border-radius: 4px;")
        pal_layout = QVBoxLayout(palette_frame)
        pal_layout.setContentsMargins(8, 8, 8, 8)
        pal_layout.setSpacing(6)
        pal_title = QLabel("📋 Paleta bloków (przeciągnij →)")
        pal_title.setStyleSheet("color: #9a9a9a; font-weight: bold;")
        pal_layout.addWidget(pal_title)
        for bt, label, desc in BLOCK_TYPES:
            pal_layout.addWidget(BlockWidget(bt, label, desc))
        pal_layout.addStretch()
        cols.addWidget(palette_frame, 1)

        # Strona (drop target)
        self.page_frame = _DropFrame(on_drop=self._on_drop_block)
        self.page_frame.setStyleSheet(
            "background: #111111; border: 2px dashed #3a3a3a; border-radius: 4px; min-height: 200px;"
        )
        self.page_layout = QVBoxLayout(self.page_frame)
        self.page_layout.setContentsMargins(12, 12, 12, 12)
        self.page_layout.setSpacing(6)

        page_title = QLabel("🌐 Twoja strona (upuść bloki tutaj)")
        page_title.setStyleSheet("color: #60a5fa; font-weight: bold; padding: 8px;")
        self.page_layout.addWidget(page_title)

        self.empty_label = QLabel("Upuść bloki tutaj, aby zbudować stronę firmy.")
        self.empty_label.setStyleSheet("color: #6a6a6a; padding: 24px;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.page_layout.addWidget(self.empty_label)

        self.page_layout.addStretch()
        cols.addWidget(self.page_frame, 2)

        layout.addLayout(cols, 1)

    def refresh(self) -> None:
        # Wyczyść listę bloków (zostaw tytuł i empty_label)
        while self.page_layout.count() > 3:  # tytuł + empty_label + stretch
            item = self.page_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        blocks = self.game.state.website.blocks
        if blocks:
            self.empty_label.setVisible(False)
            # Sortuj wg order
            sorted_blocks = sorted(blocks, key=lambda b: b.order)
            for block in sorted_blocks:
                w = PlacedBlockWidget(block, on_remove=self._on_remove_block)
                # Wstaw przed stretch
                self.page_layout.insertWidget(self.page_layout.count() - 1, w)
        else:
            self.empty_label.setVisible(True)

        # Bonus
        bonus = self.game.state.website.conversion_bonus()
        self.bonus_label.setText(f"Bonus do konwersji: {bonus*100:.0f}%")

    def _on_remove_block(self, block: WebsiteBlock) -> None:
        if block in self.game.state.website.blocks:
            self.game.state.website.blocks.remove(block)
            self.refresh()

    def _on_drop_block(self, block_type: str) -> None:
        # Sprawdź czy już jest
        existing = [b for b in self.game.state.website.blocks if b.block_type == block_type]
        if existing:
            return  # Nie duplikuj
        order = len(self.game.state.website.blocks)
        block = WebsiteBlock(block_type=block_type, order=order, content={})
        self.game.state.website.blocks.append(block)
        self.refresh()