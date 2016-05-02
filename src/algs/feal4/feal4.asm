format PE GUI 4.0 DLL
entry DllMain

include 'win32a.inc'

; ------------------------------

section '.text' code readable executable

proc DllMain hinstDLL, fdwReason, lpvReserved
    mov eax, TRUE
    ret
endp

proc EncryptChunk chunkptr,nblocks,keyptr
    pusha
    mov edi,[chunkptr]
    mov esi,[keyptr]
    mov ecx,[nblocks]
    @@:
        push ecx ; save ecx
        push edi ; save edi
        push esi ; save esi
        push dword [esi+4]    ; key[63:32]
        push dword [esi]      ; key[31:0]
        push dword [edi+4]    ; block[63:32]
        push dword [edi]      ; block[31:0]
        
        call _encrypt
        
        add esp,4*4
        pop esi ; restore esi
        pop edi ; restore edi
        pop ecx ; restore ecx
        mov [edi+4],edx ; save encrypted block[63:32]
        mov [edi],eax   ; save encrypted block[31:0]
        add edi,8
    loop @b
    popa
    mov eax,0
    ret
endp

proc DecryptChunk chunkptr,nblocks,keyptr
    pusha
    mov edi,[chunkptr]
    mov esi,[keyptr]
    mov ecx,[nblocks]
    @@:
        push ecx ; save ecx
        push edi ; save edi
        push esi ; save esi
        push dword [esi+4]    ; key[63:32]
        push dword [esi]      ; key[31:0]
        push dword [edi+4]    ; block[63:32]
        push dword [edi]      ; block[31:0]
        
        call _decrypt
        
        add esp,4*4
        pop esi ; restore esi
        pop edi ; restore edi
        pop ecx ; restore ecx
        mov [edi+4],edx ; save decrypted block[63:32]
        mov [edi],eax   ; save decrypted block[31:0]
        add edi,8
    loop @b
    popa
    mov eax,0
    ret
endp

proc encrypt dataptr,keyptr,resptr
    mov edi,[keyptr]
    push dword [edi+4]
    push dword [edi]
    mov edi,[dataptr]
    push dword [edi+4]
    push dword [edi]
    call _encrypt
    
    mov edi,[resptr]
    mov dword [edi],eax
    mov dword [edi+4],edx
    mov eax,0
    ret
endp

proc decrypt dataptr,keyptr,resptr
    mov edi,[keyptr]
    push dword [edi+4]
    push dword [edi]
    mov edi,[dataptr]
    push dword [edi+4]
    push dword [edi]
    call _decrypt
    
    mov edi,[resptr]
    mov dword [edi],eax
    mov dword [edi+4],edx
    mov eax,0
    ret
endp

F:
    ; sdata : eax     : bh:bl:ah:al
    ; key16 : cx
    push ebp
    mov ebp, esp
    
    ; eax -> bh:bl:ah:al
    ror eax,16
    mov bx,ax
    rol eax,16
    
    xor ah, cl
    xor bl, ch
    xor ah, al
    xor bl, bh
    
    add ah, bl
    add ah, 1
    rol ah, 2
    
    add bl, ah
    rol bl, 2
    
    add al, ah
    rol al, 2
    
    add bh, bl
    add bh, 1
    rol bh, 2
    
    ; bh:bl:ah:al -> eax
    ror eax,16
    mov ax,bx
    rol eax,16
    
    pop ebp
    ret
_encrypt:
    ; data : [ebp+8]  : edx:eax
    ; key  : [ebp+16]
    push ebp
    mov ebp, esp
    
    ; load data to edx:eax
    mov eax, [ebp+8]  ; right data
    mov edx, [ebp+12] ; left data
    
    ; data xor key
    xor eax, [ebp+16]
    xor edx, [ebp+20]
    
    ; left xor right
    xor eax, edx
    
    repeat 3 ;;;
        push eax ; temp right
        mov cx, word [ebp+(22-(%-1)*2)] ; key16
        call F ; F
        xor eax, edx ; RIGHT = F(right,key16) xor left
        pop edx ; LEFT = temp right
    end repeat ;;;
    
    push eax ; temp right
    mov cx, word [ebp+16] ; key16
    call F
    xor edx, eax ; LEFT = F(right,key16) xor left
    pop eax ; RIGHT = temp right
    
    ; left xor right
    xor eax, edx
    
    ; data xor key
    xor eax, [ebp+16]
    xor edx, [ebp+20]
    
    pop ebp
    ret
_decrypt:
    ; data : [ebp+8]  : edx:eax
    ; key  : [ebp+16]
    push ebp
    mov ebp, esp
    
    ; load data to edx:eax
    mov eax, [ebp+8]  ; right data
    mov edx, [ebp+12] ; left data
    
    ; data xor key
    xor eax, [ebp+16]
    xor edx, [ebp+20]
    
    ; left xor right
    xor eax, edx
    
    repeat 3 ;;;
        push eax ; temp right
        mov cx, word [ebp+(16+(%-1)*2)] ; key16
        call F ; F
        xor eax, edx ; RIGHT = F(right,key16) xor left
        pop edx ; LEFT = temp right
    end repeat ;;;
    
    push eax ; temp right
    mov cx, word [ebp+22] ; key16
    call F
    xor edx, eax ; LEFT = F(right,key16) xor left
    pop eax ; RIGHT = temp right
    
    ; left xor right
    xor eax, edx
    
    ; data xor key
    xor eax, [ebp+16]
    xor edx, [ebp+20]
    
    pop ebp
    ret

mov eax,EncryptChunk ; force relocation

section '.edata' export data readable
 
export 'FEAL4.DLL',\
    encrypt, 'encrypt',\
    EncryptChunk, 'EncryptChunk',\
    decrypt, 'decrypt',\
    DecryptChunk, 'DecryptChunk'

section '.reloc' fixups data readable discardable
