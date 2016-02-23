#!/usr/bin/env python3
from sys import argv as _argv

from tests import pmlr as _ic

_p = _ic.util.writer


def getch(*a):
    _ic.init()
    _p(ord(_ic.reader.getch()))


def readkey(*a):
    _ic.init()
    _p(ord(_ic.readkey()))


def raw_readkey(*a):
    _ic.init()
    _p(ord(_ic.raw_readkey()))


def writer(*a):
    if a:
        _p(*a)

if __name__ == "__main__":
    try:
        _arg  = _argv[1]
        _rest = tuple(_argv[2:])
    except IndexError:
        _g = globals().copy()
        _funcs = [
            i for i in _g
            if not list(_g.keys())[list(_g.keys())
                .index(i)]
                .startswith("_")
        ]
        print("names:\t" + "\n\t".join(i for i in _funcs))
    else:
        globals()[_arg](*_rest)
