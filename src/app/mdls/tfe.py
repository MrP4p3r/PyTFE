import os
import sys
import traceback

from hashlib import md5

from .pbkdf2 import PBKDF2 as pbkdf2

from .feal4      import feal4
from .blowfish   import blowfish

algtab = {
    "FEAL 4": {
        "module"    : feal4,
        "genkey"    : lambda pas,salt: pbkdf2(pas,salt).read(8),
        "blocksize" : 8,
        "chunksize" : 8*8*1024, # 64K
        "id"        : 1,
    },
    "Blowfish": {
        "module"    : blowfish,
        "genkey"    : lambda pas,salt: pbkdf2(pas,salt).read(24),
        "blocksize" : 8,
        "chunksize" : 8*8*1024, # 64K
        "id"        : 2,
    },
}

hashtab = {
    "MD5": {
        "function" : lambda x: md5(x).digest(),
        "id"       : 1,
        "length"   : 16,
    }
}

FILE_SIG = b'tfe\x42'
HEADER_LENGTH = 16
HASH_DATA_LENGTH = 512
SALT_LENGTH = 16

def buildheader(**kwargs):
    header = b''
    #file signature
    header += FILE_SIG
    flds = [ ('algorithm',1),('hashtype',1),('offset',2),('filesize',8) ]
    for fld,n in flds:
        q = kwargs[fld]
        b = q.to_bytes(n,sys.byteorder)
        header += b
    if len(header)!=16: raise
    return header

def buildemptyheader(**kwargs):
    header = b''
    #file signature
    header += FILE_SIG
    flds = [ ('algorithm',1),('hashtype',1),('offset',2),('filesize',8) ]
    for fld,n in flds:
        q = kwargs[fld]
        b = q.to_bytes(n,sys.byteorder)
        header += b
    if len(header)!=16: raise
    return header

def parseheader(header):
    if header[0:4] != FILE_SIG: raise ValueError('Not valid file')
    hdr = []
    #flds = [ ('algorithm',1),('hashtype',1),('offset',2),('filesize',8) ]
    algid    = header[4]
    hashid   = header[5]
    offset   = int.from_bytes(header[6:8],sys.byteorder)
    filesize = int.from_bytes(header[8:16],sys.byteorder)
    #find alg
    for a in algtab:
        if algtab[a]['id']==algid: algorithm = a
    #find hash
    for h in hashtab:
        if hashtab[h]['id']==hashid: hashtype = h
    return algorithm,hashtype,offset,filesize

def readchunk(bi,bls,chunksize):
    res = bi.read(chunksize)
    L = len(res)
    if L == 0: return b'',0
    if L%bls != 0:
        q = (bls - L%bls)%bls
        res = res + b'\x42'*q
    return res,len(res)//bls

def EncryptBuffer(bi,bo,blength,pas,alg="FEAL 4",hasht="MD5"):
    #alg
    _alg   = algtab[alg]
    _bls   = _alg['blocksize']
    _chs   = _alg['chunksize']
    salt = os.urandom(SALT_LENGTH)
    _key   = _alg['genkey'](pas,salt)
    _enc   = _alg['module'](_key)
    _algid = _alg['id']
    #hash
    _hashf   = hashtab[hasht]["function"]
    _hashid  = hashtab[hasht]["id"]
    _hashlen = hashtab[hasht]["length"]
    #header
    bleft = blength
    chunk,clen = readchunk(bi,_bls,min(_chs,bleft))
    bleft -= len(chunk)
    if clen == 0:
        # no data in buffer
        header = buildheader(
            algorithm = _algid,
            hashtype  = _hashid,
            offset    = 0,
            filesize  = 0
        )
        bo.write(header)
        del _enc
        return
    hash = _hashf( chunk[:HASH_DATA_LENGTH] )
    _offset = HEADER_LENGTH + len(hash) + SALT_LENGTH
    header = buildheader(
        algorithm = _algid,
        hashtype  = _hashid,
        offset    = _offset,
        filesize  = blength
    )
    #write header and first chunk
    bo.write(header)
    bo.write(hash)
    bo.write(salt)
    echunk = _enc.EncryptChunk(chunk,clen)
    bo.write(echunk)
    #encrypt remaining chunks
    while bleft > 0:
        chunk,clen = readchunk(bi,_bls,min(_chs,bleft))
        bleft -= len(chunk)
        if clen == 0: break
        echunk = _enc.EncryptChunk(chunk,clen)
        bo.write(echunk)
    del _enc
    if bleft > 0:
        raise Exception('Buffer size specified is greater than actual data')

def DecryptBuffer(bi,bo,pas):
    BEG = bi.tell()
    header = bi.read(HEADER_LENGTH)
    alg,hasht,offset,blength = parseheader(header)
    if blength == 0: return
    #init hash
    _hashf   = hashtab[hasht]["function"]
    _hashid  = hashtab[hasht]["id"]
    _hashlen = hashtab[hasht]["length"]
    #read hash and salt
    bi.seek(BEG+HEADER_LENGTH,0)
    hashA = bi.read(_hashlen)
    salt  = bi.read(SALT_LENGTH)
    bi.seek(BEG+offset,0)
    #init alg
    _alg = algtab[alg]
    _bls = _alg['blocksize']
    _chs = _alg['chunksize']
    _key = _alg['genkey'](pas,salt)
    _dec = _alg['module'](_key)
    # decr
    bleft = blength + (_bls - blength%_bls)%_bls
    echunk,clen = readchunk(bi,_bls,min(_chs,bleft))
    bleft -= len(echunk)
    chunk = _dec.DecryptChunk(echunk,clen)
    # check hash
    hashD = _hashf( chunk[:HASH_DATA_LENGTH] )
    if hashA != hashD:
        raise ValueError('Bad key')
    bo.write(chunk[:blength])
    blength -= len(echunk)
    
    while bleft > 0:
        echunk,clen = readchunk(bi,_bls,min(_chs,bleft))
        bleft -= len(echunk)
        if clen == 0: break
        chunk = _dec.DecryptChunk(echunk,clen)
        bo.write(echunk[:blength])
        blength -= len(echunk)
    del _dec

def isTfeFile(path):
    f = open(path,'rb')
    try:
        header = f.read(HEADER_LENGTH)
        f.close()
        alg,hasht,offset,blength = parseheader(header)
        if alg in algtab and hasht in hashtab:
            return True
        else:
            return False
    except:
        print('ошибочка')
        traceback.print_exc()
        return False


# ---------- ФУНКЦИИ ДЛЯ ФАЙЛОВ ----------

def EncryptFile(alg,pas,filenameIN,filenameOUT=None,r=False):
    if filenameOUT == None:
        if r:
            filenameOUT = filenameIN+'$temp$'
        else:
            fn,ext = os.path.splitext(filenameIN)
            filenameOUT = fn + '_enc' + ext
    if filenameOUT == filenameIN: filenameOUT += '$temp$'; r = True
    try: fi = open(filenameIN,'rb')
    except Exception as e: raise e
    try: fo = open(filenameOUT,'wb')
    except: fi.close(); raise e
    filesize = os.path.getsize(filenameIN)
    try: EncryptBuffer(fi,fo,filesize,pas,alg)
    except Exception as e:
        fi.close()
        fo.close()
        os.remove(filenameOUT)
        raise e
    fi.close()
    fo.close()
    if r:
        os.remove(filenameIN)
        os.rename(filenameOUT,filenameIN)

def DecryptFile(pas,filenameIN,filenameOUT=None,r=False):
    if filenameOUT == None:
        if r:
            filenameOUT = filenameIN+'$temp$'
        else:
            fn,ext = os.path.splitext(filenameIN)
            filenameOUT = fn + '_dec' + ext
    if filenameOUT == filenameIN: filenameOUT += '$temp$'; r = True
    try: fi = open(filenameIN,'rb')
    except Exception as e: raise e
    try: fo = open(filenameOUT,'wb')
    except: fi.close(); raise e
    try: DecryptBuffer(fi,fo,pas)
    except Exception as e:
        fi.close()
        fo.close()
        os.remove(filenameOUT)
        raise e
    fi.close()
    fo.close()
    if r:
        os.remove(filenameIN)
        os.rename(filenameOUT,filenameIN)

