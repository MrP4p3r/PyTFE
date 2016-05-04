blowfish.c compilation was executed with Digital Mars C compiler (dmc):

    dmc -o+all -WD blowfish.c kernel32.lib

blowfish.asm compilation was executed with Flat Assembler (fasm):

    fasm blowfish.asm

testbf.py measures speed of chunk encryption/decryption functions of
libraries produced by C and ASM code: seeblowfish.dll and asmblowfish.dll
