"""Wspólny styl dark pro-operator dla całej aplikacji."""
from __future__ import annotations

DARK_QSS = """
* {
    font-family: "Consolas", "Cascadia Mono", "Menlo", "DejaVu Sans Mono", monospace;
    font-size: 13px;
    color: #d4d4d4;
}

QWidget {
    background-color: #1a1a1a;
    color: #d4d4d4;
}

QMainWindow {
    background-color: #1a1a1a;
}

/* Sidebar */
#sidebar {
    background-color: #111111;
    border-right: 1px solid #333333;
}

#sidebar QPushButton {
    background-color: transparent;
    border: none;
    text-align: left;
    padding: 10px 16px;
    color: #9a9a9a;
    font-size: 13px;
}

#sidebar QPushButton:hover {
    background-color: #222222;
    color: #d4d4d4;
    /* animacja hover */
    transition: background-color 120ms ease, color 120ms ease;
}

#sidebar QPushButton:checked {
    background-color: #2563eb;
    color: #ffffff;
    border-left: 3px solid #60a5fa;
}

#sidebar QLabel#logo {
    padding: 16px;
    font-size: 15px;
    font-weight: bold;
    color: #60a5fa;
    background-color: transparent;
}

/* Top bar */
#topbar {
    background-color: #1a1a1a;
    border-bottom: 1px solid #333333;
}

#topbar QLabel {
    color: #9a9a9a;
    padding: 8px 16px;
}

#topbar QLabel#kpi {
    color: #d4d4d4;
    font-size: 13px;
    padding: 8px 12px;
}

/* Przyciski */
QPushButton {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    padding: 6px 14px;
    border-radius: 3px;
    color: #d4d4d4;
}

QPushButton:hover {
    background-color: #333333;
    border-color: #555555;
    transition: background-color 120ms ease, border-color 120ms ease;
}

QPushButton:pressed {
    background-color: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
}

QPushButton#primary {
    background-color: #2563eb;
    border-color: #2563eb;
    color: #ffffff;
    font-weight: bold;
}

QPushButton#primary:hover {
    background-color: #3b82f6;
    border-color: #3b82f6;
    transition: background-color 120ms ease, border-color 120ms ease;
}

QPushButton#danger {
    background-color: #7f1d1d;
    border-color: #991b1b;
    color: #ffffff;
}

/* Tabele */
QTableWidget {
    background-color: #1f1f1f;
    alternate-background-color: #232323;
    gridline-color: #333333;
    border: 1px solid #333333;
    selection-background-color: #2563eb;
}

QHeaderView::section {
    background-color: #2a2a2a;
    color: #9a9a9a;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #333333;
    font-weight: bold;
}

QTableWidget::item {
    padding: 6px 10px;
}

/* Karty / panele */
QFrame#card {
    background-color: #1f1f1f;
    border: 1px solid #333333;
    border-radius: 4px;
}

QFrame#card QLabel#card-title {
    color: #9a9a9a;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 8px 12px 4px 12px;
}

QFrame#card QLabel#card-value {
    color: #d4d4d4;
    font-size: 22px;
    font-weight: bold;
    padding: 0 12px 10px 12px;
}

/* Status */
QLabel#status-ok { color: #4ade80; }
QLabel#status-warn { color: #facc15; }
QLabel#status-error { color: #f87171; }
QLabel#status-down { color: #ef4444; font-weight: bold; }

/* Paski obciążenia */
QProgressBar {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 2px;
    text-align: center;
    color: #d4d4d4;
    height: 16px;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 2px;
    /* animacja ładowania */
    transition: width 200ms ease;
}

QProgressBar::chunk[warn="true"] { background-color: #facc15; }
QProgressBar::chunk[crit="true"] { background-color: #ef4444; }

/* Input */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    padding: 5px 8px;
    border-radius: 3px;
    color: #d4d4d4;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #2563eb;
}

/* Scrollbar */
QScrollBar:vertical {
    background-color: #1a1a1a;
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #3a3a3a;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Powiadomienie o aktualizacji */
QFrame#update-banner {
    background-color: #1e3a5f;
    border-bottom: 1px solid #2563eb;
}

QFrame#update-banner QLabel {
    color: #93c5fd;
    padding: 6px 12px;
}

QFrame#update-banner QLabel#update-title {
    font-weight: bold;
    color: #bfdbfe;
}
"""