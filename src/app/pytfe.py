#! /usr/bin/python3.4
# -*- coding: utf-8 -*-

import sys
import os
from mlibs.inter import Main

def main():
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(os.path.realpath(sys.executable))
    else:
        path = os.path.dirname(os.path.realpath(__file__))
    main = Main(path)
    # main.show()
    sys.exit(main.app.exec_())

if __name__ == "__main__":
    main()
