"""Ekran Strona firmy — lepszy drag & drop builder.

Layout: paleta bloków (lewa) | lista bloków strony (środek, drag & drop reorder) | podgląd HTML (prawa)
"""
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
from ui.website_renderer import WebsiteRenderer

BLOCK_TYPES = [
    ("hero", "Hero / Nagłówek", "Duży nagłówek z hasłem firmy", "+5%"),
    ("pricing", "Cennik", "Tabela cen planów — silny wpływ na konwersję", "+10%"),
    ("reviews", "Opinie klientów", "Recenzje zadowolonych klientów", "+8%"),
    ("status", "Status serwerów", "Live status infrastruktury", "+5%"),
    ("faq", "FAQ", "Najczęstsze pytania klientów", "+4%"),
    ("contact", "Kontakt", "Dane kontaktowe", "+4%"),
    ("chat", "Live chat", "Czat na żywo — bonus do konwersji", "+6%"),
    ("blog", "Blog", "Artykuły techniczne", "+3%"),
]

BLOCK_BONUS = {
    "hero": 0.05, "pricing": 0.10, "reviews": 0.08, "status": 0.05,
    "faq": 0.04, "contact": 0.04, "chat": 0.06, "blog": 0.03,
}


class PaletteBlock(QFrame):
    """Blok w palecie (do przeciągnięcia na stronę)."""

    def __init__(self, block_type: str, label: str, desc: str, bonus: str, on_drag_start, parent=None) -> None:
        super().__init__(parent)
        self.block_type = block_type
        self.on_drag_start = on_drag_start
        self.setObjectName("card")
        self.setFixedHeight(64)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QFrame#card { background-color: #1f1f1f; border: 1px solid #3a3a3a; border-radius: 6px; }"
            "QFrame#card:hover { border-color: #2563eb; background-color: #232323; }"
        )
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 8, 12, 8)
        v.setSpacing(2)

        header = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #d4d4d4; font-weight: bold; font-size: 13px;")
        header.addWidget(lbl)
        header.addStretch()
        bonus_lbl = QLabel(bonus)
        bonus_lbl.setStyleSheet("color: #4ade80; font-size: 11px; font-weight: bold;")
        header.addWidget(bonus_lbl)
        v.addLayout(header)

        d = QLabel(desc)
        d.setStyleSheet("color: #6a6a6a; font-size: 11px;")
        v.addWidget(d)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.on_drag_start(self.block_type)


class PlacedBlock(QFrame):
    """Blok na liście strony (można usunąć)."""

    def __init__(self, block: WebsiteBlock, on_remove, parent=None) -> None:
        super().__init__(parent)
        self.block = block
        self.setObjectName("card")
        self.setStyleSheet(
            "QFrame#card { background-color: #1e3a5f; border: 1px solid #2563eb; border-radius: 6px; }"
            "QFrame#card:hover { background-color: #234b6e; }"
        )
        h = QHBoxLayout(self)
        h.setContentsMargins(12, 8, 12, 8)
        label = next((l for t, l, d, b in BLOCK_TYPES if t == block.block_type), block.block_type)
        lbl = QLabel(f"✓  {label}")
        lbl.setStyleSheet("color: #93c5fd; font-weight: bold;")
        h.addWidget(lbl)
        h.addStretch()
        bonus = BLOCK_BONUS.get(block.block_type, 0)
        bonus_lbl = QLabel(f"+{bonus*100:.0f}%")
        bonus_lbl.setStyleSheet("color: #4ade80; font-size: 11px; font-weight: bold;")
        h.addWidget(bonus_lbl)

        btn = QPushButton("Usuń")
        btn.setStyleSheet(
            "QPushButton { background-color: #7f1d1d; color: #ffffff; "
            "border: none; padding: 3px 10px; border-radius: 3px; font-weight: bold; }"
            "QPushButton:hover { background-color: #991b1b; }"
        )
        btn.clicked.connect(lambda: on_remove(block))
        h.addWidget(btn)


class _DropFrame(QFrame):
    """QFrame akceptujący drop bloków."""

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

        # Nagłówek + bonus
        header = QHBoxLayout()
        title = QLabel("Strona firmy")
        title.setObjectName("screen-title")
        header.addWidget(title)
        header.addStretch()
        self.bonus_label = QLabel("Bonus do konwersji: 0%")
        self.bonus_label.setStyleSheet(
            "color: #facc15; font-weight: bold; padding: 6px 12px; "
            "background: #1f1f1f; border-radius: 4px;"
        )
        header.addWidget(self.bonus_label)
        layout.addLayout(header)

        info = QLabel(
            "Przeciągnij bloki z paleti na stronę. Lepsza strona = większy bonus do konwersji klientów."
        )
        info.setStyleSheet("color: #9a9a9a;")
        layout.addWidget(info)

        # Trzy kolumny
        cols = QHBoxLayout()
        cols.setSpacing(12)

        # Kolumna 1: paleta bloków (scroll)
        palette_col = QVBoxLayout()
        pal_title = QLabel("📋  Paleta bloków")
        pal_title.setStyleSheet("color: #60a5fa; font-weight: bold; padding: 4px;")
        palette_col.addWidget(pal_title)

        palette_scroll = QScrollArea()
        palette_scroll.setWidgetResizable(True)
        palette_scroll.setFrameShape(QFrame.NoFrame)
        palette_inner = QWidget()
        palette_inner.setStyleSheet("background: #111111; border: 1px solid #3a3a3a; border-radius: 4px;")
        pal_layout = QVBoxLayout(palette_inner)
        pal_layout.setContentsMargins(8, 8, 8, 8)
        pal_layout.setSpacing(6)
        for bt, label, desc, bonus in BLOCK_TYPES:
            pal_layout.addWidget(
                PaletteBlock(bt, label, desc, bonus, on_drag_start=self._start_drag)
            )
        pal_layout.addStretch()
        palette_scroll.setWidget(palette_inner)
        palette_col.addWidget(palette_scroll)
        cols.addLayout(palette_col, 1)

        # Kolumna 2: strona (drop target) — lista bloków
        page_col = QVBoxLayout()
        page_title = QLabel("🌐  Twoja strona")
        page_title.setStyleSheet("color: #60a5fa; font-weight: bold; padding: 4px;")
        page_col.addWidget(page_title)

        self.page_frame = _DropFrame(on_drop=self._on_drop_block)
        self.page_frame.setStyleSheet(
            "background: #111111; border: 2px dashed #3a3a3a; border-radius: 6px;"
        )
        self.page_layout = QVBoxLayout(self.page_frame)
        self.page_layout.setContentsMargins(12, 12, 12, 12)
        self.page_layout.setSpacing(6)

        self.empty_label = QLabel("⬅  Przeciągnij bloki tutaj")
        self.empty_label.setStyleSheet("color: #6a6a6a; padding: 32px; font-size: 14px;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.page_layout.addWidget(self.empty_label)

        self.blocks_container = QWidget()
        self.blocks_layout = QVBoxLayout(self.blocks_container)
        self.blocks_layout.setContentsMargins(0, 0, 0, 0)
        self.blocks_layout.setSpacing(6)
        self.page_layout.addWidget(self.blocks_container)
        self.page_layout.addStretch()

        page_scroll = QScrollArea()
        page_scroll.setWidgetResizable(True)
        page_scroll.setFrameShape(QFrame.NoFrame)
        page_scroll.setWidget(self.page_frame)
        page_col.addWidget(page_scroll)
        cols.addLayout(page_col, 1)

        # Kolumna 3: podgląd HTML
        renderer_col = QVBoxLayout()
        renderer_title = QLabel("👁️  Podgląd strony")
        renderer_title.setStyleSheet("color: #60a5fa; font-weight: bold; padding: 4px;")
        renderer_col.addWidget(renderer_title)
        self.renderer = WebsiteRenderer()
        self.renderer.render(self.game.state.website.blocks)
        renderer_col.addWidget(self.renderer, 1)
        cols.addLayout(renderer_col, 2)

        layout.addLayout(cols, 1)

    def _start_drag(self, block_type: str) -> None:
        """Rozpoczyna drag & drop bloku (MIME = block_type)."""
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(block_type)
        drag.setMimeData(mime)
        drag.exec_(Qt.CopyAction)

    def refresh(self) -> None:
        # Wyczyść listę bloków
        while self.blocks_layout.count():
            item = self.blocks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        blocks = self.game.state.website.blocks
        if blocks:
            self.empty_label.setVisible(False)
            sorted_blocks = sorted(blocks, key=lambda b: b.order)
            for block in sorted_blocks:
                w = PlacedBlock(block, on_remove=self._on_remove_block)
                self.blocks_layout.addWidget(w)
        else:
            self.empty_label.setVisible(True)

        # Bonus
        bonus = self.game.state.website.conversion_bonus()
        self.bonus_label.setText(f"Bonus do konwersji: {bonus*100:.0f}%")

        # Odśwież podgląd
        self.renderer.render(self.game.state.website.blocks)

    def _on_remove_block(self, block: WebsiteBlock) -> None:
        if block in self.game.state.website.blocks:
            self.game.state.website.blocks.remove(block)
            self.refresh()

    def _on_drop_block(self, block_type: str) -> None:
        existing = [b for b in self.game.state.website.blocks if b.block_type == block_type]
        if existing:
            return
        order = len(self.game.state.website.blocks)
        block = WebsiteBlock(block_type=block_type, order=order, content={})
        self.game.state.website.blocks.append(block)
        self.refresh()