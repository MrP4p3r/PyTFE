# -*- coding: utf-8 -*-

import sys
import os
from ctypes import *

class blowfish:
    key  = None
    skey = None
    # key length = (18 keys)x(32 bits) + (4 tables)x(256 values)x(32 bits)
    keylength  = 18*4 + 4*256*4
    # secret key length = 192 bits = 24 bytes
    skeylength = 192//8
    # block length = 64 bits = 8 bytes
    blocksize  = 8

    def __init__(self, skey=None):
        if not isinstance(skey, bytes):
            raise TypeError('Key must be bytes')
        if len(skey) < self.skeylength:
            raise ValueError('Key size must be at least %i bytes'%self.skeylength)

        if getattr(sys, 'frozen', False):
            path = os.path.dirname(os.path.realpath(sys.executable))
        else:
            path = os.path.dirname(os.path.realpath(sys.argv[0]))

        if os.name == 'posix':
            libpath = os.path.join(path, 'mlibs', 'linux', 'blowfish.so')
            self.lib = CDLL(libpath)
        else:
            libpath = os.path.join(path, 'mlibs', 'win32', 'blowfish.dll')
            self.lib = WinDLL(libpath)

        self.skey = create_string_buffer(skey)
        self.key  = create_string_buffer(self.keylength)

        self.lib._gen_key192(self.skey, self.key)

    def __del__(self):
        try:
            if os.name != 'posix':
                del self.key
                libHandle = self.lib._handle
                del self.lib
                windll.kernel32.FreeLibrary(libHandle)
        except:
            pass

    def Encrypt(self, data):
        _data = create_string_buffer(data)
        self.lib.Encrypt(_data, self.key)
        return _data.raw[:-1]

    def Decrypt(self, data):
        _data = create_string_buffer(data)
        self.lib.Decrypt(_data, self.key)
        return _data.raw[:-1]

    def EncryptChunk(self, chunk, clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.lib.EncryptChunk(_chunk, _clen, self.key)
        return _chunk.raw[:-1]

    def DecryptChunk(self, chunk, clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.lib.DecryptChunk(_chunk, _clen, self.key)
        return _chunk.raw[:-1]

