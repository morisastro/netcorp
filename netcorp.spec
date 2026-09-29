# -*- mode: python ; coding: utf-8 -*-
"""Spec PyInstaller dla NetCorp Tycoon.

Build:  pyinstaller netcorp.spec
Wynik:  dist/netcorp-tycoon/netcorp-tycoon.exe (jednoklik, działa offline)
"""
import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Brak zewnętrznych danych — wszystko w Pythonie
        ('data', 'data'),
        ('LICENSE', '.'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PySide6.QtSvgWidgets',
        'PySide6.QtSvg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Pomijamy moduły nieużywane (mniejszy bundle)
        'tkinter',
        'unittest',
        'pydoc',
        'doctest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='netcorp-tycoon',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX może wyzwalać fałszywe alarmy AV — wyłączamy
    console=False,  # Bez okna konsoli (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='netcorp-tycoon',
)