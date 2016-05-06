/*
 * FEAL4 algorithm implementation
 * Author:   Gleb Getmanenko
 * Date:     06.05.16
 * Language: C
 * 
 * win32:
 * gcc -std=c99 -O3 -c feal4.c
 * gcc -s -shared -o feal4.dll feal4.o -Wl,--out-implib,libfeal4.a,--subsystem,windows
 *
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <windows.h>

void __stdcall __declspec(dllexport)
    _EncryptChunk( uint8_t* chunkptr, uint32_t nblocks, uint8_t* key);
void __stdcall __declspec(dllexport)
    _DecryptChunk( uint8_t* chunkptr, uint32_t nblocks, uint8_t* key);
void __stdcall __declspec(dllexport)
    _encrypt( uint8_t* data, uint8_t* key );
void __stdcall __declspec(dllexport)
    _decrypt( uint8_t* data, uint8_t* key );

void encrypt( uint8_t* data, uint8_t* key );
void decrypt( uint8_t* data, uint8_t* key );
uint32_t F( uint32_t sd, uint16_t sk );
uint8_t S0( uint8_t a, uint8_t b );
uint8_t S1( uint8_t a, uint8_t b );
uint8_t rol2( uint8_t a );


bool __stdcall __declspec(dllexport) APIENTRY
    DllMain( HANDLE hModule, DWORD fdwReason, LPVOID lpvReserved )
{
    return TRUE;
}

void __stdcall __declspec(dllexport)
    _EncryptChunk( uint8_t* chunkptr, uint32_t nblocks, uint8_t* key)
{
    for ( uint32_t i = 0; i < nblocks; i++ ) encrypt(&chunkptr[i*8],key);
}

void __stdcall __declspec(dllexport)
    _DecryptChunk( uint8_t* chunkptr , uint32_t nblocks , uint8_t* key)
{
    for ( uint32_t i = 0; i < nblocks; i++ ) decrypt(&chunkptr[i*8],key);
}

void __stdcall __declspec(dllexport)
    _encrypt( uint8_t* data , uint8_t* key )
{
    encrypt(data,key);
}

void __stdcall __declspec(dllexport)
    _decrypt( uint8_t* data , uint8_t* key )
{
    decrypt(data,key);
}


uint8_t S0( uint8_t a, uint8_t b ) { return rol2(a+b); }
uint8_t S1( uint8_t a, uint8_t b ) { return rol2(a+b+1); }
uint8_t rol2( uint8_t a ) { return ((a>>6)|(a<<2)); }

void encrypt( uint8_t* data , uint8_t* key )
{
    uint32_t L = ((uint32_t*)data)[1];
    uint32_t R = ((uint32_t*)data)[0];
    uint32_t t;
    
    L ^= ((uint32_t*)key)[1];
    R ^= ((uint32_t*)key)[0];
    R ^= L;
    for ( uint8_t i = 3; i > 0; i-- )
    {
        t = R;
        R = L ^ F(R,((uint16_t*)key)[i]);
        L = t;
    }
    L = L ^ F(R,((uint16_t*)key)[0]);
    R ^= L;
    L ^= ((uint32_t*)key)[1];
    R ^= ((uint32_t*)key)[0];
    
    ((uint32_t*)data)[1] = L;
    ((uint32_t*)data)[0] = R;
}

void decrypt( uint8_t* data , uint8_t* key )
{
    uint32_t L = ((uint32_t*)data)[1];
    uint32_t R = ((uint32_t*)data)[0];
    uint32_t t;
    
    L ^= ((uint32_t*)key)[1];
    R ^= ((uint32_t*)key)[0];
    R ^= L;
    for ( uint8_t i = 0; i < 3; i++ )
    {
        t = R;
        R = L ^ F(R,((uint16_t*)key)[i]);
        L = t;
    }
    L = L ^ F(R,((uint16_t*)key)[3]);
    R ^= L;
    L ^= ((uint32_t*)key)[1];
    R ^= ((uint32_t*)key)[0];
    
    ((uint32_t*)data)[1] = L;
    ((uint32_t*)data)[0] = R;
}

uint32_t F( uint32_t sd , uint16_t sk )
{
    uint8_t* ssd = (uint8_t*)&sd;
    uint8_t* ssk = (uint8_t*)&sk;
    
    ssd[1] ^= ssk[0];
    ssd[2] ^= ssk[1];
    ssd[1] ^= ssd[0];
    ssd[2] ^= ssd[3];
    
    ssd[1] = S1(ssd[1],ssd[2]);
    ssd[2] = S0(ssd[2],ssd[1]);
    ssd[0] = S0(ssd[0],ssd[1]);
    ssd[3] = S1(ssd[3],ssd[2]);
    
    return sd;
}
