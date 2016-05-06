blowfish.c compilation was executed with gcc:

    gcc -std=c99 -O3 -c blowfish.c
    gcc -s -shared -o seeblowfish.dll blowfish.o -Wl,--out-implib,libblowfish.a,--subsystem,windows

blowfish.asm compilation was executed with Flat Assembler (fasm):

    fasm blowfish.asm asmblowfish.dll
