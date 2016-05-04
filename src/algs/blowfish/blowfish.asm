;
; Blowfish algorithm implementation
; Author:   Gleb Getmanenko
; Date:     02.05.16
; Language: asm (fasm)
;

format PE GUI 4.0 DLL
entry DllMain

include 'win32a.inc'

include 'blowfishPS.asm'

struct KEY
    P  dd 18  dup (?)
    S1 dd 256 dup (?)
    S2 dd 256 dup (?)
    S3 dd 256 dup (?)
    S4 dd 256 dup (?)
ends

section '.text' code readable executable

proc DllMain hinstDLL, fdwReason, lpvReserved
    mov eax, TRUE
    ret
endp

encrypt:
    ; encrypt a block of data
    ; [esp+4] - pointer to data
    ; [esp+8] - pointer to key
    
    mov edi, [esp+4]
    mov eax, [edi+0]
    mov edx, [edi+4]
    
    mov edi, [esp+8]
    
    repeat 16  ;;;
        push eax
        mov eax, edx
        xor eax, [edi+KEY.P+(%-1)*4]
        pop edx
        call F
    end repeat ;;;
    
    mov ebx, edx
    xor ebx, [edi+KEY.P+16*4]
    mov edx, eax
    xor edx, [edi+KEY.P+17*4]
    mov eax, ebx
    
    mov edi, [esp+4]
    mov [edi+0], eax
    mov [edi+4], edx
    
    ret

decrypt:
    ; decrypt a block of data
    ; [esp+4] - pointer to data
    ; [esp+8] - pointer to key
    
    mov edi, [esp+4]
    mov eax, [edi+0]
    mov edx, [edi+4]
    
    mov edi, [esp+8]
    
    repeat 16  ;;;
        push eax
        mov eax, edx
        xor eax, [edi+KEY.P+(17-(%-1))*4]
        pop edx
        call F
    end repeat ;;;
    
    mov ebx, edx
    xor ebx, [edi+KEY.P+1*4]
    mov edx, eax
    xor edx, [edi+KEY.P+0*4]
    mov eax, ebx
    
    mov edi, [esp+4]
    mov [edi+0], eax
    mov [edi+4], edx
    
    ret

F:
    push eax
    push edx
    
    movzx eax, byte [esp+4+0]
    movzx ebx, byte [esp+4+1]
    movzx ecx, byte [esp+4+2]
    movzx edx, byte [esp+4+3]
    
    mov eax, [edi+KEY.S4+eax*4]
    mov ebx, [edi+KEY.S3+ebx*4]
    mov ecx, [edi+KEY.S2+ecx*4]
    mov edx, [edi+KEY.S1+edx*4]
    
    add ecx, edx
    xor ebx, ecx
    add eax, ebx
    
    pop edx
    xor edx, eax
    pop eax
    ret

proc Encrypt dataptr,keyptr
    pusha
    pushd [keyptr]
    pushd [dataptr]
    call encrypt
    add esp,8
    popa
    mov eax,0
    ret
endp

proc Decrypt dataptr,keyptr
    pusha
    pushd [keyptr]
    pushd [dataptr]
    call decrypt
    add esp,8
    popa
    mov eax,0
    ret
endp

proc EncryptChunk chunkptr,nblocks,keyptr
    pushad
    
    mov edi, [chunkptr]
    ;mov esi, [keyptr]
    mov ecx, [nblocks]
    @@:
        push ecx      ; save counter
        push [keyptr] ; key ptr
        push edi      ; data ptr
        call encrypt
        add esp, 2*4
        pop ecx
        add edi, 8
    loop @b
    
    popad
    mov eax,0
    ret
endp

proc DecryptChunk chunkptr,nblocks,keyptr
    pushad
    
    mov edi, [chunkptr]
    ;mov esi, [keyptr]
    mov ecx, [nblocks]
    @@:
        push ecx      ; save counter
        push [keyptr] ; key ptr
        push edi      ; data ptr
        call decrypt
        add esp, 2*4
        pop ecx
        add edi, 8
    loop @b
    
    popad
    mov eax,0
    ret
endp

proc _gen_key192 skey,key
    pushad
    
    ; init P keys and S tables
    pushd 18*4+4*256*4 ; length of initial key
    push PS_INIT
    push [key]
    call mmemcpy
    add esp, 12
    
    ; cycled xor with skey (24 bytes)
    mov edi, [skey]
    mov esi, [key]
    mov ecx, 0
    @@:
        ; key->P[i] ^= skey32[i%6]
        mov eax, ecx
        ; eax = eax % 6
        ror eax, 16
        mov dx, ax
        rol eax, 16
        mov bx, 6
        div bx
        movsx eax, dx
        ;
        mov eax, [edi+4*eax]
        xor [esi+4*ecx], eax
        inc ecx
        cmp ecx, 18
    jnae @b
    
    ; encipher P keys and S tables
    ; init zero block
    pushd 0
    pushd 0
    mov eax, esp ; pointer to zero block
    ; for ( int i = 0; i < 1042; i+=2 )
    xor ecx, ecx ; int i = 0
    @@:
        push ecx
        ; encrypt(data,key);
        push esi ; key pointer
        push eax ; data pointer
        call encrypt
        
        ; update key
        pop eax ; data pointer
        pop esi ; key pointer
        pop ecx ; i
        mov ebx, [eax+0]
        mov [esi+ecx*4+0], ebx
        mov ebx, [eax+4]
        mov [esi+ecx*4+4], ebx
        
        add ecx, 2
        cmp ecx, 1042
    jnae @b
    add esp, 8
    
    popad
    mov eax, [key]
    ret
endp

mmemcpy:
    ; copy [ebp+16] bytes from *[ebp+12] to *[ebp+8]
    push ebp
    mov ebp, esp
    
    mov ecx, [ebp+16]
    cmp ecx, 0
    jz endloop
    mov edi, [ebp+12]
    mov esi, [ebp+8]
    @@:
        mov al, [edi]
        mov [esi], al
        inc edi
        inc esi
    loop @b
    endloop:
    
    mov esp, ebp
    pop ebp
    ret

mov eax, encrypt ; force relocation

section '.edata' export data readable

export 'blowfish.dll',\
    Encrypt, 'encrypt',\
    Decrypt, 'decrypt',\
    EncryptChunk, 'EncryptChunk',\
    DecryptChunk, 'DecryptChunk',\
    _gen_key192, '_gen_key192'

section '.reloc' fixups data readable discardable
