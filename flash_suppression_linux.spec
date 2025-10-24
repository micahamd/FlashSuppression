# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for CFS Task - Linux Version
Creates a single-file Linux executable with bundled dependencies

Build command: pyinstaller flash_suppression_linux.spec
Output: dist/CFS_Task
"""

block_cipher = None

a = Analysis(
    ['display_file.py'],  # Main entry point
    pathex=[],
    binaries=[],
    datas=[
        # Configuration files
        ('config.json', '.'),
        ('config_ui_settings.json', '.'),
        
        # Required image resources
        ('grey.png', '.'),
        ('temp_checkerboard.png', '.'),
        
        # Python helper modules
        ('packaging_helper.py', '.'),
    ],
    hiddenimports=[
        # Pillow-Tkinter integration
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL._imaging',
        
        # Tkinter components
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.constants',
        
        # Standard library modules used
        'csv',
        'json',
        'time',
        'functools',
        'subprocess',
        'random',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CFS_Task',                          # Output executable name (no .exe on Linux)
    debug=False,                              # Set to True for debugging
    bootloader_ignore_signals=False,
    strip=True,                               # Strip symbols on Linux (reduces size)
    upx=True,                                 # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                            # Hide console window (GUI app)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
