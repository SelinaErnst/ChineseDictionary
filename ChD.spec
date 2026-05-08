# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path
from PyInstaller.utils.hooks import collect_all

datas = [('appdata', 'appdata'), ('packages', 'packages')]
binaries = []
hiddenimports = []
tmp_ret = collect_all('kivymd')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    # pathex=['/home/selina/Applications/conda/miniconda_24.3.0/envs/kivydev_env/lib/python3.12/site-packages'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    # hookspath=[],
    hookspath=[kivymd_hooks_path],
    # hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    # optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)], # <-- ADD THIS LINE
    # [],
    name='ChD',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False, # Disabling UPX often fixes DLL load failures
    # upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)