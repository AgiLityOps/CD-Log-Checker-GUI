# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for CD Log Checker GUI. Build on Windows (x64) with:
#     pyinstaller --clean --noconfirm hbcl_gui.spec
# Produces a single-file, windowed (no console) dist/CD-Log-Checker-GUI.exe.
# Set the environment variable HBCL_GUI_ONEDIR=1 to build a folder instead:
#     dist/CD-Log-Checker-GUI/CD-Log-Checker-GUI.exe (+ _internal/)
import os
import platform

import tkinterdnd2
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = []
# hbcl's resources (EAC/XLD translation + pattern JSON, drives.db)
datas += collect_data_files("heybrochecklog")
# version metadata so the status bar can show the bundled hbcl version
datas += copy_metadata("heybrochecklog")

# tkdnd native binaries. tkinterdnd2 ships its own PyInstaller hook that picks
# the right folder; we add the Windows x64 folder explicitly as well so drag
# and drop can never silently go missing from the exe.
if platform.system() == "Windows":
    tkdnd_dir = os.path.join(os.path.dirname(tkinterdnd2.__file__), "tkdnd", "win-x64")
    for name in os.listdir(tkdnd_dir):
        datas.append((os.path.join(tkdnd_dir, name), "tkinterdnd2/tkdnd/win-x64"))

# Ship the licence/notice inside the bundle too (they also go next to the exe).
datas += [("LICENSE", "."), ("NOTICE", "."), ("assets/app.ico", "assets")]

ONEDIR = os.environ.get("HBCL_GUI_ONEDIR") == "1"
NAME = "CD-Log-Checker-GUI"

a = Analysis(
    ["run_hbcl_gui.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=["hbcl_gui", "hbcl_gui.app", "hbcl_gui.core", "hbcl_gui.render"],
    hookspath=[],
    runtime_hooks=[],
    # pprp pulls these in as install deps but they are never used at runtime
    excludes=["nose", "coverage", "pytest", "IPython", "numpy"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

common = dict(
    name=NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX makes antivirus false positives worse
    console=False,
    disable_windowed_traceback=False,
    icon="assets/app.ico",
    version="version_info.txt",
    manifest="assets/app.manifest",
    uac_admin=False,
)

if ONEDIR:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, **common)
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=NAME)
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], runtime_tmpdir=None, **common)
