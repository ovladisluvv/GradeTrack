# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for the GradeTrack PyQt6 desktop app.
# Build:  pyinstaller GradeTrack.spec   (run from the repository root)
# Produces a single-file, windowed executable; on macOS also a GradeTrack.app bundle.
import sys

# Resources bundled into the executable. At runtime they are unpacked under
# sys._MEIPASS, which utils.resource_path() resolves. Source path -> path inside bundle.
datas = [
    ("data", "data"),          # university_structure.yaml, test_grades.html, in_diploma/**
    ("config", "config"),      # config.yaml (URLs only, no secrets)
    ("src/gui/fonts", "fonts"),  # bundled fonts, loaded via theme.get_source_path("fonts", ...)
]

a = Analysis(
    ["src/gui/app.py"],
    pathex=["src"],            # absolute imports (from gui import ...) need src on sys.path
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="GradeTrack",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX can trip Windows antivirus false positives
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,             # windowed GUI app, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="GradeTrack.app",
        icon=None,
        bundle_identifier="ru.msu.gradetrack",
        info_plist={"NSHighResolutionCapable": True},
    )
