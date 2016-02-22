#!/usr/bin/env python3
from sys import argv as _argv
import input_constrain as _ic

_p = _ic._writer

def getch(*a):
    _p(ord(_ic._Getch()))


def readkey(*a):
    _p(ord(_ic._read_keypress()))


def raw_readkey(*a):
    _p(ord(_ic._read_keypress(raw=True)))

def writer(*a):
    if a:
        _ic._writer(*a)

if __name__ == "__main__":
    try:
        _arg  = _argv[1]
        _rest = tuple(_argv[2:])
    except IndexError:
        _g = globals()
        _funcs = [
            i for i in _g
            if not list(_g.keys())[list(_g.keys())
                .index(i)]
                .startswith("_")
        ]
        print("names:\t" + "\n\t".join(i for i in _funcs))
    else:
        globals()[_arg](*_rest)
