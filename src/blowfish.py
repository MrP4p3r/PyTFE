from os.path import abspath,dirname,realpath,join
from ctypes import *

class blowfish:
    key = b''
    keylength = 192//8 # 192 bits
    blocksize = 8
    def __init__(self,key=None):
        if not isinstance(key,bytes):
            raise TypeError('Key must be bytes')
        if len(key) < self.keylength:
            raise ValueError('Key size must be at least %i bytes'%self.keylength)
        self.key = key[:self.keylength]
        
        self.dll = WinDLL( join(dirname(realpath(__file__)),'blowfish.dll'))
        _sk = create_string_buffer(self.key)
        self._key = self.dll.gen_key192(byref(_sk))
    def __del__(self):
        try:
            libHandle = self.dll._handle
            del self.dll
            windll.kernel32.FreeLibrary(libHandle)
        except:
            pass
    def Encrypt(self,data):
        raise NotImplementedError
        #_data = create_string_buffer(data)
        #_res  = create_string_buffer(self.blocksize)
        #self.dll.Encrypt( byref(_data) , self._key , byref(_res) )
    def Decrypt(self,data):
        raise NotImplementedError
        #_data = create_string_buffer(data)
        #_res  = create_string_buffer(self.blocksize)
        #self.dll.Decrypt( byref(_data) , self._key , byref(_res) )
    def EncryptChunk(self,chunk,clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.dll.EncryptChunk( byref(_chunk), _clen , self._key )
        return _chunk.raw[:-1]
    def DecryptChunk(self,chunk,clen):
        _chunk = create_string_buffer(chunk)
        _clen  = c_ulong(clen)
        self.dll.DecryptChunk( byref(_chunk), _clen , self._key )
        return _chunk.raw[:-1]
