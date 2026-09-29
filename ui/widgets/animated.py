"""Animowane widgety tekstowe — fade-in, slide-in, pulse, count-up.

QPropertyAnimation + QGraphicsOpacityEffect / QPropertyAnimation na geometry / pos.
"""
from __future__ import annotations

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QTimer,
    Qt,
)
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QWidget


def fade_in(widget: QWidget, duration_ms: int = 300, start: float = 0.0, end: float = 1.0) -> QPropertyAnimation:
    """Animacja pojawienia się widgetu (fade-in opacity)."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(start)
    anim.setEndValue(end)
    anim.setEasingCurve(QEasingCurve.InOutQuad)
    anim.start(QPropertyAnimation.DeleteWhenStopped)
    return anim


def slide_in(widget: QWidget, duration_ms: int = 350, offset_x: int = 24, offset_y: int = 0) -> QPropertyAnimation:
    """Animacja wjazdu widgetu (slide-in)."""
    start_pos = widget.pos()
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(start_pos + widget.rect().topLeft() - widget.rect().topLeft().translated(offset_x, offset_y))
    anim.setEndValue(start_pos)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    anim.start(QPropertyAnimation.DeleteWhenStopped)
    return anim


class AnimatedLabel(QLabel):
    """QLabel z efektem fade-in przy ustawianiu tekstu + pulse przy alertach."""

    def __init__(self, text: str = "", parent=None, animate_on_set: bool = True) -> None:
        super().__init__(text, parent)
        self._animate_on_set = animate_on_set
        self._effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._effect)
        self._effect.setOpacity(1.0)
        self._pulse_anim: QPropertyAnimation | None = None

    def setText(self, text: str) -> None:  # noqa: N802
        if self._animate_on_set and self.text() != text:
            # Fade-out → zmiana → fade-in
            anim_out = QPropertyAnimation(self._effect, b"opacity", self)
            anim_out.setDuration(150)
            anim_out.setStartValue(1.0)
            anim_out.setEndValue(0.0)
            anim_out.setEasingCurve(QEasingCurve.InQuad)

            def _swap():
                super(AnimatedLabel, self).setText(text)
                anim_in = QPropertyAnimation(self._effect, b"opacity", self)
                anim_in.setDuration(250)
                anim_in.setStartValue(0.0)
                anim_in.setEndValue(1.0)
                anim_in.setEasingCurve(QEasingCurve.OutQuad)
                anim_in.start(QPropertyAnimation.DeleteWhenStopped)

            anim_out.finished.connect(_swap)
            anim_out.start(QPropertyAnimation.DeleteWhenStopped)
        else:
            super().setText(text)

    def pulse(self, color: str = "#facc15", duration_ms: int = 600) -> None:
        """Animacja pulsowania kolorem (alert)."""
        original = self.palette().color(QPalette.WindowText)
        target = QColor(color)
        anim = QPropertyAnimation(self, b"color", self)  # type: ignore[arg-type]
        # QPropertyAnimation na "color" nie działa na QLabel; używamy stylesheet
        # Zamiast: zmiana stylesheet z animacją przez timer
        QTimer.singleShot(0, lambda: self.setStyleSheet(f"color: {color};"))
        QTimer.singleShot(duration_ms // 2, lambda: self.setStyleSheet(""))
        self._pulse_anim = anim


class HoverLabel(QLabel):
    """QLabel z efektem hover — zmiana koloru + subtelny glow (text-shadow).

    Używa eventy mouseEnter/mouseLeave + stylesheet do animacji koloru.
    Można ustawić property hover_color i glow_color.
    """

    def __init__(self, text: str = "", hover_color: str = "#60a5fa", parent=None) -> None:
        super().__init__(text, parent)
        self._hover_color = hover_color
        self._base_color = self.palette().color(self.foregroundRole()).name()
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event) -> None:  # noqa: N802
        self.setStyleSheet(
            f"color: {self._hover_color}; "
            f"transition: color 200ms ease;"
        )
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self.setStyleSheet("")
        super().leaveEvent(event)


class ScreenTitleLabel(QLabel):
    """Tytuł ekranu z efektem hover (kolor + glow)."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("screen-title")
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event) -> None:  # noqa: N802
        self.setStyleSheet(
            "QLabel#screen-title { color: #60a5fa; }"
        )
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self.setStyleSheet("")
        super().leaveEvent(event)


class SectionTitleLabel(QLabel):
    """Podtytuł sekcji z efektem hover."""

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setObjectName("section-title")
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event) -> None:  # noqa: N802
        self.setStyleSheet("QLabel#section-title { color: #60a5fa; }")
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:  # noqa: N802
        self.setStyleSheet("")
        super().leaveEvent(event)


class CountUpLabel(QLabel):
    """QLabel animujący liczbę od starej do nowej wartości (count-up)."""

    def __init__(self, prefix: str = "", suffix: str = "", duration_ms: int = 600, parent=None) -> None:
        super().__init__(parent)
        self._prefix = prefix
        self._suffix = suffix
        self._duration = duration_ms
        self._current = 0
        self._target = 0
        self._anim: QPropertyAnimation | None = None
        self.setText(f"{prefix}{0}{suffix}")

    def set_value(self, value: int) -> None:
        old = self._current
        self._target = value
        if old == value:
            self.setText(f"{self._prefix}{value}{self._suffix}")
            return
        # Animuj przez self (używamy property "value" dummy)
        self._current = value
        # Prosty count-up przez QTimer (zamiast QPropertyAnimation na int)
        steps = max(self._duration // 30, 1)
        delta = (value - old) / steps
        self._animate_count(old, value, delta, 0, steps)

    def _animate_count(self, start: int, end: int, delta: float, step: int, total: int) -> None:
        current = int(start + delta * step)
        if step >= total:
            current = end
            self.setText(f"{self._prefix}{end}{self._suffix}")
            return
        self.setText(f"{self._prefix}{current}{self._suffix}")
        QTimer.singleShot(30, lambda: self._animate_count(start, end, delta, step + 1, total))