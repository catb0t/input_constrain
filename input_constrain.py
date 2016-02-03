#!/usr/bin/env python3

import sys
from platform import system

if system == "Windows":
    import msvcrt

    def _Getch():
        return msvcrt.getch()

else:
    import tty, termios

    def _Getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch


def parsenum(num):
    return sys.maxsize if 0 > num else num

CHAR_INT = chr(3)
CHAR_EOF = chr(4)
CHAR_BKS = chr(8)
CHAR_ESC = chr(27)
CHAR_SPC = chr(32)
CHAR_DEL = chr(127)


def _read_keypress():
    """interface for _Getch that interprets backspace and DEL properly"""
    c = _Getch()

    if c in (CHAR_BKS, CHAR_DEL, CHAR_ESC):
        sys.stdout.write(CHAR_BKS)
        sys.stdout.write(CHAR_SPC)  # hacky? indeed. does it *work*? hell yeah!
        sys.stdout.write(CHAR_BKS)

    elif c == CHAR_INT: raise KeyboardInterrupt
    elif c == CHAR_EOF: raise EOFError

    return c


def _nbsp(x, y):
    """append x to y as long as x is not DEL or backspace"""
    if x in (CHAR_DEL, CHAR_BKS):
        try:
            y.pop()
        except IndexError:
            pass
        return y
    y.append(x)
    return y


def _writer(i):
    sys.stdout.write(i)
    sys.stdout.flush()


def pretty_press() -> str:
    """literally just read any fancy char from stdin let caller do whatever"""
    i = _read_keypress()
    _writer(i)
    return _nbsp(i, y)


def thismany(count=-1) -> str:
    """get exactly count chars of stdin"""
    y = []
    count = parsenum(count)
    while len(y) <= count:
        i = _read_keypress()
        _writer(i)
        y = _nbsp(i, y)
    return "".join(y)


def _until_condition(chars, condition, count) -> str:
    y = []
    while len(y) <= count:
        i = _read_keypress()
        _writer(i)
        if condition(i, chars):
            break
        y = _nbsp(i, y)
    return "".join(y)


def until(chars, count=-1) -> str:
    """get chars of stdin until any of chars is read,
    or until count chars have been read, whichever comes first"""

    return _until_condition(
        chars, lambda i, chars: i in chars, parsenum(count)
    )


def until_not(chars, count=-1) -> str:
    """read stdin until any of chars stop being read,
    or until count chars have been read; whichever comes first"""

    return _until_condition(
        chars, lambda i, chars: i not in chars, parsenum(count)
    )
