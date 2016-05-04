import os
from ctypes import *
from timeit import timeit
import traceback

KEY_LENGTH = 18*4 + 4*256*4

see = WinDLL('seeblowfish.dll')
asm = WinDLL('asmblowfish.dll')

skey = create_string_buffer(b'0x42'*24)
asmkey = create_string_buffer(KEY_LENGTH)
seekey = create_string_buffer(KEY_LENGTH)

asm._gen_key192(skey,asmkey)
see._gen_key192(skey,seekey)

nchunks = 8*1024
x = create_string_buffer(nchunks*8)

print('\nASM Encryption')
number = 2000
print('nbytes',number*nchunks*8)
t = timeit(lambda: asm.EncryptChunk(x,nchunks,asmkey),number=number)
print('time',t)
print('speed',number*nchunks*8/t/1024/1024,'MB/S')

print('\nASM Decryption')
number = 2000
print('nbytes',number*nchunks*8)
t = timeit(lambda: asm.DecryptChunk(x,nchunks,asmkey),number=number)
print('time',t)
print('speed',number*nchunks*8/t/1024/1024,'MB/S')

print('\nC Encryption')
number = 2000
print('nbytes',number*nchunks*8)
t = timeit(lambda: see.EncryptChunk(x,nchunks,seekey),number=number)
print('time',t)
print('speed',number*nchunks*8/t/1024/1024,'MB/S')

print('\nC Decryption')
number = 2000
print('nbytes',number*nchunks*8)
t = timeit(lambda: see.DecryptChunk(x,nchunks,seekey),number=number)
print('time',t)
print('speed',number*nchunks*8/t/1024/1024,'MB/S')

