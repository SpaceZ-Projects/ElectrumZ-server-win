# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

datas = [
    ('electrumz_server', '.'),
    ('electrumz_rpc', '.'),
    ('electrumz_compact_history', '.'),
    ('electrumz/*', 'electrumz'),
    ('icons/*', 'icons'),
    ('electrumz.conf', '.')
]

binaries = []

hiddenimports = []

hiddenimports += collect_submodules('aiohttp')
hiddenimports += collect_submodules('plyvel')
hiddenimports += collect_submodules('aiorpcx')
hiddenimports += collect_submodules('attrs')
hiddenimports += collect_submodules('cryptography')
hiddenimports += collect_submodules('OpenSSL')
hiddenimports += collect_submodules('objgraph')
hiddenimports += collect_submodules('rapidjson-stubs')
hiddenimports += collect_submodules('ujson')
hiddenimports += collect_submodules('blake256')
hiddenimports += collect_submodules('Cryptodome')
hiddenimports += collect_submodules('pythonnet')

excludes=['__pycache__']

a = Analysis(
    ['electrumz_server'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=excludes
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ElectrumZ-Server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icons/electrumz.ico'
)