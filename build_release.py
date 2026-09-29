"""Buduje release do dystrybucji.

Kroki:
1. PyInstaller buduje onedir (dist/netcorp-tycoon/)
2. Kopiuje LICENSE
3. Pakuje dist/netcorp-tycoon/ do ZIP
4. Wynik: release/netcorp-tycoon-v<wersja>-win.zip

Uruchom: python build_release.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Wymuś UTF-8
os.environ.setdefault("PYTHONUTF8", "1")

ROOT = Path(__file__).parent.resolve()
DIST = ROOT / "dist"
APP_DIR = DIST / "netcorp-tycoon"
RELEASE = ROOT / "release"

# Pobierz wersję z app/settings.py
def get_version() -> str:
    settings = (ROOT / "app" / "settings.py").read_text(encoding="utf-8")
    for line in settings.splitlines():
        if line.startswith("APP_VERSION"):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return "0.1.0"


def main() -> int:
    version = get_version()
    print(f"=== Budowanie release v{version} ===")

    # 1. Wyczyść stare buildy
    for p in (DIST, ROOT / "build", RELEASE):
        if p.exists():
            print(f"Usuwanie {p}...")
            shutil.rmtree(p)
    RELEASE.mkdir(parents=True, exist_ok=True)

    # 2. PyInstaller
    print("Uruchamianie PyInstaller...")
    ret = subprocess.call([
        sys.executable, "-m", "PyInstaller",
        "netcorp.spec",
        "--noconfirm",
        "--clean",
    ], cwd=str(ROOT))
    if ret != 0:
        print("BŁĄD: PyInstaller nie powiódł się")
        return ret

    if not APP_DIR.exists():
        print(f"BŁĄD: {APP_DIR} nie istnieje")
        return 1

    # 3. Skopiuj LICENSE
    shutil.copy(ROOT / "LICENSE", APP_DIR / "LICENSE")

    # 4. Usuń zbędne pliki z dist (np. Qt pluginy nieużywane)
    #    (można doprecyzować, na razie zostawiamy wszystko)

    # 5. ZIP
    zip_name = f"netcorp-tycoon-v{version}-win"
    zip_path = RELEASE / f"{zip_name}.zip"
    print(f"Pakowanie do {zip_path}...")
    shutil.make_archive(str(RELEASE / zip_name), "zip", root_dir=str(DIST), base_dir="netcorp-tycoon")

    # 6. Podsumowanie
    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print()
    print("=== GOTOWE ===")
    print(f"Release ZIP: {zip_path}")
    print(f"Rozmiar: {size_mb:.1f} MB")
    print(f"Rozpakuj i uruchom: netcorp-tycoon\\netcorp-tycoon.exe")
    return 0


if __name__ == "__main__":
    sys.exit(main())