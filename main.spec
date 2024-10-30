# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['electrumz_server'],
    pathex=['.'],
    binaries=[('env/Lib/site-packages/winloop/*', 'winloop')],
    datas=[
        ('electrumz_server', '.'),
        ('electrumz_rpc', '.'),
        ('electrumz_compact_history', '.'),
        ('electrumz/*', 'electrumz'),
        ('img/*', 'img')
    ],
    hiddenimports=[
        'aiorpcx',
        'attrs',
        'plyvel',
        'aiohttp',
        'cryptography',
        'OpenSSL',
        'winloop',
        'objgraph',
        'rapidjson-stubs',
        'ujson',
        'blake256',
        'Cryptodome'],

    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0
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
    icon='img/electrumz.ico'
)