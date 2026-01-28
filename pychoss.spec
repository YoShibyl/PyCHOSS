# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pychoss.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['ttkbootstrap', 'obs-websocket-py', 'PIL._tkinter_finder', 'pygithub'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='pychoss',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='64bit',
    codesign_identity=None,
    entitlements_file=None,
)
