# -*- mode: python ; coding: utf-8 -*-
# DevBuddy AI – PyInstaller Build Spec
# Build: pyinstaller devbuddy.spec

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets',  'assets'),      # icons, avatar images
        ('config.json', '.'),       # default config (if present)
    ],
    hiddenimports=[
        'pystray._win32',
        'PIL._tkinter_finder',
        'onnxruntime',
        'rembg',
        'schedule',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
    ],
    hookspath=[],
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
    name='DevBuddyAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/tray_icon.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DevBuddyAI',
)
