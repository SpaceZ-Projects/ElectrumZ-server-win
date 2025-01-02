
import re
import struct
from dataclasses import dataclass
from decimal import Decimal
from functools import partial
from hashlib import sha256
from typing import Sequence, Tuple

import electrumz.lib.util as util
from electrumz.lib.hash import Base58, double_sha256, hash_to_hex_str
from electrumz.lib.hash import HASHX_LEN
from electrumz.lib.script import ScriptPubKey
import electrumz.lib.tx as lib_tx
from electrumz.lib.tx import Tx

import electrumz.server.block_processor as block_proc
import electrumz.server.daemon as daemon
from electrumz.server.session import ElectrumZ


@dataclass
class Block:
    __slots__ = "raw", "header", "transactions"
    raw: bytes
    header: bytes
    transactions: Sequence[Tuple[Tx, bytes]]


class CoinError(Exception):
    '''Exception raised for coin-related errors.'''


class Coin:
    '''Base class of coin hierarchy.'''

    REORG_LIMIT = 200
    # Not sure if these are coin-specific
    RPC_URL_REGEX = re.compile('.+@(\\[[0-9a-fA-F:]+\\]|[^:]+)(:[0-9]+)?')
    VALUE_PER_COIN = 100000000
    CHUNK_SIZE = 2016
    BASIC_HEADER_SIZE = 80
    STATIC_BLOCK_HEADERS = True
    SESSIONCLS = ElectrumZ
    DEFAULT_MAX_SEND = 1000000
    DESERIALIZER = lib_tx.Deserializer
    DAEMON = daemon.Daemon
    BLOCK_PROCESSOR = block_proc.BlockProcessor
    HEADER_VALUES = ('version', 'prev_block_hash', 'merkle_root', 'timestamp',
                     'bits', 'nonce')
    HEADER_UNPACK = struct.Struct('< I 32s 32s I I I').unpack_from
    P2PKH_VERBYTE = bytes.fromhex("00")
    P2SH_VERBYTES = (bytes.fromhex("05"),)
    XPUB_VERBYTES = bytes('????', 'utf-8')
    XPRV_VERBYTES = bytes('????', 'utf-8')
    WIF_BYTE = bytes.fromhex("80")
    ENCODE_CHECK = Base58.encode_check
    DECODE_CHECK = Base58.decode_check
    GENESIS_HASH = ('000000000019d6689c085ae165831e93'
                    '4ff763ae46a2a6c172b3f1b60a8ce26f')
    GENESIS_ACTIVATION = 100_000_000

    MEMPOOL_HISTOGRAM_REFRESH_SECS = 500
    # first bin size in vbytes. smaller bins mean more precision but also bandwidth:
    MEMPOOL_COMPACT_HISTOGRAM_BINSIZE = 30_000

    # Peer discovery
    PEER_DEFAULT_PORTS = {'t': '50001', 's': '50002'}
    PEERS = []
    CRASH_CLIENT_VER = None
    BLACKLIST_URL = None
    ESTIMATEFEE_MODES = (None, 'CONSERVATIVE', 'ECONOMICAL')

    RPC_PORT: int
    NAME: str
    NET: str

    # only used for initial db sync ETAs:
    TX_COUNT_HEIGHT: int  # at a given snapshot of the chain,
    TX_COUNT: int         # there have been this many txs so far,
    TX_PER_BLOCK: int     # and from that height onwards, we guess this many txs per block

    @classmethod
    def lookup_coin_class(cls, name, net):
        '''Return a coin class given name and network.

        Raise an exception if unrecognised.'''
        req_attrs = ('TX_COUNT', 'TX_COUNT_HEIGHT', 'TX_PER_BLOCK')
        for coin in util.subclasses(Coin):
            if (coin.NAME.lower() == name.lower() and
                    coin.NET.lower() == net.lower()):
                missing = [
                    attr
                    for attr in req_attrs
                    if not hasattr(coin, attr)
                ]
                if missing:
                    raise CoinError(
                        f'coin {name} missing {missing} attributes'
                    )
                return coin
        raise CoinError(f'unknown coin {name} and network {net} combination')

    @classmethod
    def sanitize_url(cls, url):
        # Remove surrounding ws and trailing /s
        url = url.strip().rstrip('/')
        match = cls.RPC_URL_REGEX.match(url)
        if not match:
            raise CoinError(f'invalid daemon URL: "{url}"')
        if match.groups()[1] is None:
            url = f'{url}:{cls.RPC_PORT:d}'
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        return url + '/'

    @classmethod
    def max_fetch_blocks(cls, height):
        if height < 130000:
            return 1000
        return 100

    @classmethod
    def genesis_block(cls, block):
        '''Check the Genesis block is the right one for this coin.

        Return the block less its unspendable coinbase.
        '''
        header = cls.block_header(block, 0)
        header_hex_hash = hash_to_hex_str(cls.header_hash(header))
        if header_hex_hash != cls.GENESIS_HASH:
            raise CoinError(f'genesis block has hash {header_hex_hash} '
                            f'expected {cls.GENESIS_HASH}')

        return header + b'\0'

    @classmethod
    def hashX_from_script(cls, script):
        '''Returns a hashX from a script.'''
        return sha256(script).digest()[:HASHX_LEN]

    @staticmethod
    def lookup_xverbytes(verbytes):
        '''Return a (is_xpub, coin_class) pair given xpub/xprv verbytes.'''
        # Order means BTC testnet will override NMC testnet
        for coin in util.subclasses(Coin):
            if verbytes == coin.XPUB_VERBYTES:
                return True, coin
            if verbytes == coin.XPRV_VERBYTES:
                return False, coin
        raise CoinError('version bytes unrecognised')

    @classmethod
    def address_to_hashX(cls, address):
        '''Return a hashX given a coin address.'''
        return cls.hashX_from_script(cls.pay_to_address_script(address))

    @classmethod
    def hash160_to_P2PKH_script(cls, hash160):
        return ScriptPubKey.P2PKH_script(hash160)

    @classmethod
    def hash160_to_P2PKH_hashX(cls, hash160):
        return cls.hashX_from_script(cls.hash160_to_P2PKH_script(hash160))

    @classmethod
    def pay_to_address_script(cls, address):
        '''Return a pubkey script that pays to a pubkey hash.

        Pass the address (either P2PKH or P2SH) in base58 form.
        '''
        raw = cls.DECODE_CHECK(address)

        # Require version byte(s) plus hash160.
        verbyte = -1
        verlen = len(raw) - 20
        if verlen > 0:
            verbyte, hash160 = raw[:verlen], raw[verlen:]

        if verbyte == cls.P2PKH_VERBYTE:
            return cls.hash160_to_P2PKH_script(hash160)
        if verbyte in cls.P2SH_VERBYTES:
            return ScriptPubKey.P2SH_script(hash160)

        raise CoinError(f'invalid address: {address}')

    @classmethod
    def privkey_WIF(cls, privkey_bytes, compressed):
        '''Return the private key encoded in Wallet Import Format.'''
        payload = bytearray(cls.WIF_BYTE + privkey_bytes)
        if compressed:
            payload.append(0x01)
        return cls.ENCODE_CHECK(payload)

    @classmethod
    def header_hash(cls, header):
        '''Given a header return hash'''
        return double_sha256(header)

    @classmethod
    def header_prevhash(cls, header):
        '''Given a header return previous hash'''
        return header[4:36]

    @classmethod
    def static_header_offset(cls, height):
        '''Given a header height return its offset in the headers file.

        If header sizes change at some point, this is the only code
        that needs updating.'''
        assert cls.STATIC_BLOCK_HEADERS
        return height * cls.BASIC_HEADER_SIZE

    @classmethod
    def static_header_len(cls, height):
        '''Given a header height return its length.'''
        return (cls.static_header_offset(height + 1)
                - cls.static_header_offset(height))

    @classmethod
    def block_header(cls, block, height):
        '''Returns the block header given a block and its height.'''
        return block[:cls.static_header_len(height)]

    @classmethod
    def block(cls, raw_block, height):
        '''Return a Block namedtuple given a raw block and its height.'''
        header = cls.block_header(raw_block, height)
        txs = cls.DESERIALIZER(raw_block, start=len(header)).read_tx_block()
        return Block(raw_block, header, txs)

    @classmethod
    def decimal_value(cls, value):
        '''Return the number of standard coin units as a Decimal given a
        quantity of smallest units.

        For example 1 BTC is returned for 100 million satoshis.
        '''
        return Decimal(value) / cls.VALUE_PER_COIN

    @classmethod
    def warn_old_client_on_tx_broadcast(cls, _client_ver):
        return False

    @classmethod
    def bucket_estimatefee_block_target(cls, n: int) -> int:
        '''For caching purposes, it might be desirable to restrict the
        set of values that can be queried as an estimatefee block target.
        '''
        return n


class EquihashMixin:
    STATIC_BLOCK_HEADERS = False
    BASIC_HEADER_SIZE = 140  # Excluding Equihash solution
    DESERIALIZER = lib_tx.DeserializerEquihash
    HEADER_VALUES = ('version', 'prev_block_hash', 'merkle_root', 'reserved',
                     'timestamp', 'bits', 'nonce')
    HEADER_UNPACK = struct.Struct('< I 32s 32s 32s I I 32s').unpack_from

    @classmethod
    def block_header(cls, block, height):
        '''Return the block header bytes'''
        deserializer = cls.DESERIALIZER(block)
        return deserializer.read_header(cls.BASIC_HEADER_SIZE)



class BitcoinZ(EquihashMixin, Coin):
    NAME = "BitcoinZ"
    SHORTNAME = "BTCZ"
    NET = "mainnet"
    GENESIS_HASH = ('f499ee3d498b4298ac6a64205b8addb7'
                    'c43197e2a660229be65db8a4534d75c1')

    P2PKH_VERBYTE = bytes.fromhex("1CB8")
    P2SH_VERBYTES = [bytes.fromhex("1CBD")]
    WIF_BYTE = bytes.fromhex("80")
    DESERIALIZER = lib_tx.DeserializerZcash

    BASIC_HEADER_SIZE = 243
    HEADER_SIZE_NO_SOLUTION = 140

    TX_COUNT = 171976
    TX_COUNT_HEIGHT = 81323
    TX_PER_BLOCK = 3
    RPC_PORT = 1979
    REORG_LIMIT = 800
    PEERS = [
        'electrum1.btcz.rocks s t',
        'electrum2.btcz.rocks s t',
        'electrum3.btcz.rocks s t'
    ]    

    @classmethod
    def block_header(cls, block, height):
        '''Return the block header bytes'''
        deserializer = cls.DESERIALIZER(block)
        return deserializer.read_header(cls.HEADER_SIZE_NO_SOLUTION)