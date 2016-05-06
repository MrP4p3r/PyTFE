from os.path import abspath,dirname,realpath,join
from ctypes import *

class feal4:
    key = None
    keylength = 8
    blocksize = 8
    def __init__(self,key=None):
        if not isinstance(key,bytes):
            raise TypeError('Key must be bytes')
        if len(key) < self.keylength:
            raise ValueError('Key size must be at least %i bytes'%self.keylength)
        
        self.key = create_string_buffer(key)
        self.dll = WinDLL( join(dirname(realpath(__file__)),'feal4.dll'))
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
    
if __name__=='__main__':
    f = feal4(b'\x01\x02\x03\x04\x05\x06\x07\x08')



