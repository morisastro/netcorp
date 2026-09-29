"""NetCorp Tycoon — punkt wejścia aplikacji.

Najpierw pokazuje menu startowe (nowa gra / wczytaj / ustawienia),
dopiero po wybraniu partii otwiera główne okno gry.
"""
import os
import sys

# Wymuś UTF-8 na wszystkich platformach (głównie dla Windows console)
os.environ.setdefault("PYTHONUTF8", "1")
# W aplikacji okienkowej (.exe bez konsoli) sys.stdout/stderr mogą być None
_stdout = getattr(sys, "stdout", None)
if _stdout is not None and getattr(_stdout, "encoding", "") and _stdout.encoding.lower() != "utf-8":
    try:
        _stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
_stderr = getattr(sys, "stderr", None)
if _stderr is not None and getattr(_stderr, "encoding", "") and _stderr.encoding.lower() != "utf-8":
    try:
        _stderr.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

from PySide6.QtWidgets import QApplication

from ui.main_menu import MainMenuWindow
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("NetCorp Tycoon")
    app.setOrganizationName("NetCorpTycoon")

    # Ikona aplikacji (pasek zadań, okno)
    from app.settings import app_icon_path
    from PySide6.QtGui import QIcon
    if os.path.exists(app_icon_path()):
        app.setWindowIcon(QIcon(app_icon_path()))

    # Główne okno gry tworzone na żądanie po wybraniu partii
    game_window: list[MainWindow] = []

    def start_game(game):
        win = MainWindow(game)
        win.show()
        game_window.append(win)

    menu = MainMenuWindow(on_start_game=start_game)
    menu.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())