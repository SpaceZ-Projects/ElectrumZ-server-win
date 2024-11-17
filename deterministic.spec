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

binaries = [('env/Lib/site-packages/winloop/*', 'winloop')]

hiddenimports = collect_submodules('pythonnet')
hiddenimports += collect_submodules('aiohttp')
hiddenimports += collect_submodules('plyvel')
hiddenimports += collect_submodules('aiorpcx')
hiddenimports += collect_submodules('attrs')
hiddenimports += collect_submodules('cryptography')
hiddenimports += collect_submodules('OpenSSL')
hiddenimports += collect_submodules('winloop')
hiddenimports += collect_submodules('objgraph')
hiddenimports += collect_submodules('rapidjson-stubs')
hiddenimports += collect_submodules('ujson')
hiddenimports += collect_submodules('blake256')
hiddenimports += collect_submodules('Cryptodome')

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

conexe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='ElectrumZ-Server',
    debug=False,
    strip=False,
    upx=False,
    console=True,
    icon='icons/electrumz.ico'
)

coll = COLLECT(conexe,
            a.binaries,
            a.datas,
            strip=False,
            upx=False,
            name=os.path.join('dist', 'electrumz-server'))