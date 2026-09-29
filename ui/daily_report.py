"""Modal raportu dziennego — podsumowanie po kliknięciu 'Następny dzień'."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class DailyReportDialog(QDialog):
    """Pokazuje raport z symulacji jednego dnia."""

    def __init__(self, report: dict, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Raport — dzień {report['day']}")
        self.resize(460, 380)
        self._build_ui(report)

    def _build_ui(self, report: dict) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        title = QLabel(f"📅 Dzień {report['day']}")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #d4d4d4;")
        layout.addWidget(title)

        # Wiersze raportu
        rows = [
            ("Przychód", f"${report['income']:,.2f}", "#4ade80"),
            ("Koszty", f"${report['expenses']:,.2f}", "#f87171"),
            ("Saldo", f"${report['income'] - report['expenses']:,.2f}",
             "#4ade80" if report['income'] - report['expenses'] >= 0 else "#f87171"),
            ("Gotówka", f"${report['cash']:,.2f}", "#d4d4d4"),
            ("Nowi klienci", f"+{report['new_customers']}", "#4ade80"),
            ("Odeszli (churn)", f"-{report['churned']}", "#f87171"),
            ("Nowe awarie", f"{len(report['new_failures'])}",
             "#f87171" if report['new_failures'] else "#9a9a9a"),
            ("Rozwiązane awarie", f"{len(report['resolved_failures'])}", "#9a9a9a"),
            ("Tickety rozwiązane", f"{report['tickets_resolved']}", "#9a9a9a"),
        ]

        # Klienci którzy nie kupili (brak serwera)
        unplaced = report.get("unplaced", 0)
        if unplaced > 0:
            rows.append(("⚠ Nie kupili (brak miejsca)", f"{unplaced}", "#facc15"))

        for label, value, color in rows:
            line = QLabel(f"{label}: {value}")
            line.setStyleSheet(f"color: {color}; font-size: 14px;")
            layout.addWidget(line)

        # Kamienie milowe
        if report.get("milestones_unlocked"):
            layout.addSpacing(8)
            ms_title = QLabel("🏆 Kamienie milowe:")
            ms_title.setStyleSheet("font-weight: bold; color: #facc15;")
            layout.addWidget(ms_title)
            for ms in report["milestones_unlocked"]:
                ms_label = QLabel(f"   • {ms}")
                ms_label.setStyleSheet("color: #facc15;")
                layout.addWidget(ms_label)

        # Nowe awarie
        if report["new_failures"]:
            layout.addSpacing(8)
            fail_title = QLabel("⚠ Nowe awarie:")
            fail_title.setStyleSheet("font-weight: bold; color: #f87171;")
            layout.addWidget(fail_title)
            from ui.failures import FAILURE_LABELS
            for f in report["new_failures"]:
                label = FAILURE_LABELS.get(f.type, f.type)
                srv = f.server_id or "DC"
                fail_label = QLabel(f"   • {label} — serwer {srv}")
                fail_label.setStyleSheet("color: #f87171;")
                layout.addWidget(fail_label)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)