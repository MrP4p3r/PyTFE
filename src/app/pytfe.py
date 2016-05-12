#! /usr/bin/python3.4
#  encoding=utf8

import sys
import os
from mlibs.inter import Main

def main():
    path = os.path.dirname(os.path.realpath(__file__))
    main = Main(path)
    main.show()
    sys.exit(main.app.exec_())

if __name__ == "__main__":
    main()
