#! /usr/bin/python3.4
# -*- coding: utf-8 -*-

import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    'packages': [
        'sys', 'os', 'subprocess', 'hashlib', 'traceback', 'io',
        'ctypes', 'random', 'struct', 'string', 'hmac',
        'PySide.QtCore', 'PySide.QtGui',
        'chardet', 'mlibs'
    ],
    'excludes': [ 'tkinter' ],
    'include_files': [
        'icon.png',
        ('tr/com.qm', 'tr/com.qm'),
        ('tr/tr_en.qm', 'tr/tr_en.qm'),
        ('tr/qt_ru.qm', 'tr/qt_ru.qm'),
        ('tr/tr_ru.qm', 'tr/tr_ru.qm'),
        ('mlibs/win32/feal4.dll', 'mlibs/win32/feal4.dll'),
        ('mlibs/win32/blowfish.dll', 'mlibs/win32/blowfish.dll'),
    ],
    'include_msvcr': True,
    'zip_includes': [],
    'bin_excludes': [],
    'create_shared_zip': False
}

base = None

if sys.platform == 'win32':
    base = 'Win32GUI'
    pass

target = Executable('pytfete.py', base=base, icon='icon.ico')

setup( name = "PyTFE",
       version = "1.0.3",
       description = "",
       options = { "build_exe": build_exe_options },
       executables = [ target ] )
