from os.path import abspath,dirname,realpath,join
from ctypes import *

class blowfish:
    key  = None
    skey = None
    keylength  = 18*4 + 4*256*4
    skeylength = 192//8 # 192 bits = 24 bytes
    blocksize  = 8
    def __init__(self,skey=None):
        if not isinstance(skey,bytes):
            raise TypeError('Key must be bytes')
        if len(skey) < self.skeylength:
            raise ValueError('Key size must be at least %i bytes'%self.skeylength)
        
        self.dll = WinDLL( join(dirname(realpath(__file__)),'blowfish.dll'))
        self.skey = create_string_buffer(skey)
        self.key  = create_string_buffer(self.keylength)
        
        self.dll._gen_key192(self.skey,self.key)
    def __del__(self):
        del self.key
        try:
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

