#!/usr/bin/env python3

class _Getch:
    """Gets a single character from standard input."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty

    def __call__(self):
        , tty, termios
        fd = stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


def read_single_keypress():
    getch = _Getch()
    x = getch.__call__()
    if ord(x) == 27 or ord(x) == 127:
        sys.stdout.write(chr(8))
    elif ord(x) == 3:
        raise KeyboardInterrupt
    elif ord(x) == 4:
        raise EOFError
    return x

def nbsp(x, y):
    """append x to y as long as x is not DEL or backspace"""
    if ord(x) == 27 or ord(x) == 127:
        y.pop()
        return y
    y.append(x)
    return y

def thismany(count) -> str:
    """get exactly count chars of stdin"""
    y = []
    for _ in range(count):
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        y = nbsp(i, y)
    return "".join(y)


def until(char) -> str:
    """get chars of stdin until char is read"""
    y = []
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i == char:
            break
        y = nbsp(i, y)
    return "".join(y)


def until_multi(chars) -> str:
    """read stdin until any of a set of chars are read"""
    chars = list(chars)
    y = []
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i in chars:
            break
        y = nbsp(i, y)
    return "".join(y)


def until_not(char) -> str:
    """read stdin until char stops being read"""
    y = []
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i != char:
            break
        y = nbsp(i, y)
    return "".join(y)


def until_not_multi(chars) -> str:
    """read stdin until !(chars)"""
    chars = list(chars)
    y = []
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i not in chars:
            break
        y = nbsp(i, y)
    return "".join(y)
