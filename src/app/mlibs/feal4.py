import sys
import os.path
from ctypes import *

class feal4:
    key = None
    # key length = 64 bits = 8 bytes
    keylength = 8
    # block length = 64 bits = 8 bytes
    blocksize = 8
    def __init__(self,key=None):
        if not isinstance(key,bytes):
            raise TypeError('Key must be bytes')
        if len(key) < self.keylength:
            raise ValueError('Key size must be at least %i bytes'%self.keylength)

        if getattr(sys, 'frozen', False):
            path = os.path.dirname(os.path.realpath(sys.executable))
        else:
            path = os.path.dirname(os.path.realpath(sys.argv[0]))
        libpath = os.path.join(path,'mlibs','win32','feal4.dll')
        self.dll = WinDLL(libpath)
        
        self.key = create_string_buffer(key)
    def __del__(self):
        try:
            libHandle = self.dll._handle
            del self.dll
            windll.kernel32.FreeLibrary(libHandle)
        except:
            pass
    def Encrypt(self,data):
        _data = create_string_buffer(data)
        self.dll.Encrypt(_data,self.key)
        return _data.raw[:-1]
    def Decrypt(self,data):
        _data = create_string_buffer(data)
        self.dll.Decrypt(_data,self.key)
        return _data.raw[:-1]
    def EncryptChunk(self,chunk,clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.dll.EncryptChunk(_chunk,_clen,self.key)
        return _chunk.raw[:-1]
    def DecryptChunk(self,chunk,clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.dll.DecryptChunk(_chunk,_clen,self.key)
        return _chunk.raw[:-1]
