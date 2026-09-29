"""Skrypt do tworzenia nowej wersji release.

Użycie:
    python new_version.py 0.2.0
    python new_version.py 1.0.0

Co robi:
1. Aktualizuje APP_VERSION w app/settings.py
2. Commit: "Bump version to X.Y.Z"
3. Tworzy tag vX.Y.Z
4. Pcha commit + tag → CI automatycznie buduje release

Po wypchnięciu tagu GitHub Actions buduje 3 platformy (Win/Linux/macOS)
i tworzy release z plikami ZIP do pobrania.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
SETTINGS = ROOT / "app" / "settings.py"


def update_version(new_version: str) -> None:
    """Aktualizuje APP_VERSION w app/settings.py."""
    content = SETTINGS.read_text(encoding="utf-8")
    pattern = r'^APP_VERSION\s*=\s*"[^"]*"'
    replacement = f'APP_VERSION = "{new_version}"'
    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)
    if count == 0:
        print(f"BŁĄD: nie znaleziono APP_VERSION w {SETTINGS}")
        sys.exit(1)
    SETTINGS.write_text(new_content, encoding="utf-8")
    print(f"✓ Zaktualizowano APP_VERSION → {new_version}")


def run(cmd: list[str], check: bool = True) -> int:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.call(cmd, cwd=str(ROOT))
    if check and result != 0:
        print(f"BŁĄD: komenda nie powiodła się: {' '.join(cmd)}")
        sys.exit(result)
    return result


def main() -> int:
    if len(sys.argv) != 2:
        print("Użycie: python new_version.py <wersja>")
        print("Przykład: python new_version.py 0.2.0")
        return 1

    version = sys.argv[1].strip().lstrip("vV")
    if not re.match(r"^\d+\.\d+\.\d+$", version):
        print(f"BŁĄD: wersja musi być w formacie X.Y.Z (np. 0.2.0), dostałem: {version}")
        return 1

    tag = f"v{version}"
    print(f"=== Tworzenie nowej wersji {tag} ===")

    # 1. Aktualizuj APP_VERSION
    update_version(version)

    # 2. Commit
    run(["git", "add", "app/settings.py"])
    run(["git", "commit", "-m", f"Bump version to {version}"])

    # 3. Tag
    # Usuń stary tag jeśli istnieje (lokalnie)
    run(["git", "tag", "-d", tag], check=False)
    run(["git", "tag", "-a", tag, "-m", f"NetCorp Tycoon {tag}"])

    # 4. Push commit + tag
    run(["git", "push", "origin", "main"])
    run(["git", "push", "origin", tag])

    print()
    print("=== GOTOWE ===")
    print(f"Wersja: {version}")
    print(f"Tag: {tag}")
    print()
    print("GitHub Actions automatycznie:")
    print("  1. Zbuduje 3 platformy (Windows, Linux, macOS)")
    print("  2. Spakuje do ZIP")
    print("  3. Utworzy release z plikami do pobrania")
    print()
    print(f"Sprawdź: https://github.com/morisastro/netcorp/actions")
    print(f"Release:  https://github.com/morisastro/netcorp/releases/tag/{tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())