/*
 * Blowfish algorithm implementation
 * Author:   Gleb Getmanenko
 * Date:     02.05.16
 * Language: C (dmc compiler)
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <windows.h>

#include "blowfishPS.c"

typedef struct {
    uint32_t P[18];
    uint32_t S[4][256];
} KEY;

void __stdcall __declspec(dllexport)
    EncryptChunk( uint8_t* chunkptr , uint32_t nblocks , KEY* key);
void __stdcall __declspec(dllexport)
    DecryptChunk( uint8_t* chunkptr , uint32_t nblocks , KEY* key);
KEY* __stdcall __declspec(dllexport) gen_key192( uint8_t* skey );
KEY* __stdcall __declspec(dllexport) _gen_key192( uint8_t* skey , KEY* key );

void encrypt( uint8_t* data , KEY* key );
void decrypt( uint8_t* data , KEY* key );
uint32_t F( uint32_t R, KEY* key );

void __stdcall EncryptChunk( uint8_t* chunkptr , uint32_t nblocks , KEY* key)
{
    uint8_t* data = (uint8_t*)malloc(8);
    for ( uint32_t i = 0; i < nblocks; i++ )
    {
        memcpy(data,&chunkptr[i*8],8);
        encrypt(data,key);
        memcpy(&chunkptr[i*8],data,8);
    }
}

void __stdcall DecryptChunk( uint8_t* chunkptr , uint32_t nblocks , KEY* key)
{
    uint8_t* data = (uint8_t*)malloc(8);
    for ( uint32_t i = 0; i < nblocks; i++ )
    {
        memcpy(data,&chunkptr[i*8],8);
        decrypt(data,key);
        memcpy(&chunkptr[i*8],data,8);
    }
}

void encrypt( uint8_t* data , KEY* key )
{
    uint32_t L = ((uint32_t*)data)[1];
    uint32_t R = ((uint32_t*)data)[0];
    uint32_t t;
    
    for ( uint8_t i = 0; i < 16; i++ )
    {
        t = R;
        R = L ^ key->P[i];
        L = t ^ F(R,key);
    }
    
    t = L ^ key->P[16];
    L = R ^ key->P[17];
    R = t;
    
    ((uint32_t*)data)[1] = L;
    ((uint32_t*)data)[0] = R;
}

void decrypt( uint8_t* data , KEY* key )
{
    uint32_t L = ((uint32_t*)data)[1];
    uint32_t R = ((uint32_t*)data)[0];
    uint32_t t;
    
    for ( uint8_t i = 17; i > 1; i-- )
    {
        t = R;
        R = L ^ key->P[i];
        L = t ^ F(R,key);
    }
    
    t = L ^ key->P[1];
    L = R ^ key->P[0];
    R = t;
    
    ((uint32_t*)data)[1] = L;
    ((uint32_t*)data)[0] = R;
}

uint32_t F(uint32_t R, KEY* key)
{
    uint8_t* r = (uint8_t*)&R;
    uint32_t q[4];
    
    q[0] = key->S[3][ r[0] ];
    q[1] = key->S[2][ r[1] ];
    q[2] = key->S[1][ r[2] ];
    q[3] = key->S[0][ r[3] ];
    
    q[2] += q[3];
    q[1] ^= q[2];
    q[0] += q[1];
    
    return q[0];
}

KEY* __stdcall gen_key192( uint8_t* skey )
{
    KEY* key = (KEY*)malloc(sizeof(KEY));
    _gen_key192(skey,key);
    return key;
}

KEY* __stdcall __declspec(dllexport) _gen_key192( uint8_t* skey , KEY* key )
{
    /* Function generates P keys and S tables from a 192 bit secret key */
    uint32_t* skey32 = (uint32_t*)skey;
    
    // Initialize P and S
    memcpy((void*)key->P,(void*)&P_INIT,sizeof(uint32_t)*18);
    memcpy((void*)key->S,(void*)&S_INIT,sizeof(uint32_t)*4*256);
    
    // XOR P keys with secret key
    for ( int i = 0; i < 18; i++ ) key->P[i] ^= skey32[i%6];
    
    // Encipher P keys and S tables
    uint8_t* data = (uint8_t*)malloc(8);
    uint32_t* data32 = (uint32_t*)data;
    memset(data,0,8);
    
    for ( int i = 0; i < 18; i+=2 )
    {
        encrypt(data,key);
        key->P[i] = data32[0];
        key->P[i+1] = data32[1];
    }
    for ( int i = 0; i < 4; i++ )
    {
        for ( int j = 0; j < 256; j+=2 )
        {
            encrypt(data,key);
            key->S[i][j] = data32[0];
            key->S[i][j+1] = data32[1];
        }
    }
    
    return key;
}

bool __stdcall __declspec(dllexport) APIENTRY DllMain(
    HANDLE hModule, DWORD fdwReason, LPVOID lpvReserved
)
{
    return TRUE;
}
