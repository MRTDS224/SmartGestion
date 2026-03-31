# -*- mode: python ; coding: utf-8 -*-
from kivymd import hooks_path as kivymd_hooks_path

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/screens/*.kv', 'ui/screens'),
        ('assets/*', 'assets'),
        ('smart_gestion.db', '.') # Include local DB if present, though ideally it's created on run
    ],
    hiddenimports=['psycopg2', 'kivymd.uix.datatables', 'kivymd.uix.dialog', 'kivymd.uix.boxlayout'],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='SmartGestion1.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Set to True to see errors for now, False for production
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SmartGestion',
)
