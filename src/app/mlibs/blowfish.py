import sys
import os.path
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
    def __init__(self,skey=None):
        if not isinstance(skey,bytes):
            raise TypeError('Key must be bytes')
        if len(skey) < self.skeylength:
            raise ValueError('Key size must be at least %i bytes'%self.skeylength)

        if getattr(sys, 'frozen', False):
            path = os.path.dirname(os.path.realpath(sys.executable))
        else:
            path = os.path.dirname(os.path.realpath(sys.argv[0]))
        libpath = os.path.join(path,'mlibs','win32','blowfish.dll')

        self.dll = WinDLL(libpath)

        self.skey = create_string_buffer(skey)
        self.key  = create_string_buffer(self.keylength)

        self.dll._gen_key192(self.skey,self.key)
    def __del__(self):
        try:
            del self.key
            libHandle = self.dll._handle
            del self.dll
            windll.kernel32.FreeLibrary(libHandle)
        except:
            pass
    def Encrypt(self,data):
        _data = create_string_buffer(data)
        self.dll.Encrypt( _data , self.key )
        return _data.raw[:-1]
    def Decrypt(self,data):
        _data = create_string_buffer(data)
        self.dll.Decrypt( _data , self.key )
        return _data.raw[:-1]
    def EncryptChunk(self,chunk,clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.dll.EncryptChunk( _chunk, _clen , self.key )
        return _chunk.raw[:-1]
    def DecryptChunk(self,chunk,clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.dll.DecryptChunk( _chunk, _clen , self.key )
        return _chunk.raw[:-1]
