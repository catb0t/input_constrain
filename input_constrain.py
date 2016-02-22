#!/usr/bin/env python3

import sys
from platform import system

if system() == "Windows":
    import msvcrt
    import colorama
    try:
        colorama.init()
    except AttributeError:
        print("""
        you must install colorama to use this module on windows
        do this by:
        $ cd colorama
        $ python setup.py install""")
        exit(2)

    def _Getch():
        return msvcrt.getch()

else:
    import tty, termios

    def _Getch():
        if sys.stdin.isatty():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch
        else:
            return sys.stdin.read(1)


def parsenum(num):
    num = int(num)
    return sys.maxsize if num < 0 else num

CHAR_NUL = chr(0)
CHAR_INT = chr(3)
CHAR_EOF = chr(4)
CHAR_BEL = chr(7)
CHAR_BKS = chr(8)
CHAR_LFD = chr(10)
CHAR_CRR = chr(13)
CHAR_ESC = chr(27)
CHAR_SPC = chr(32)
CHAR_DEL = chr(127)

CONDS = [
    (lambda i, chars: i in chars),
    (lambda i, chars: i not in chars),
    (lambda *args, **kwargs: False),
]


def _read_keypress(raw=False):
    """interface for _Getch that interprets backspace and DEL properly"""
    c = _Getch()

    if c in (CHAR_BKS, CHAR_DEL, CHAR_ESC):
        _writer(CHAR_BKS)
        _writer(CHAR_SPC)  # hacky? indeed. does it *work*? hell yeah!
        _writer(CHAR_BKS)

    elif c in (CHAR_CRR, CHAR_LFD):
        _writer(CHAR_LFD if system == "Windows" else "")
        _writer(CHAR_CRR)
        return CHAR_LFD

    if not raw:
        if c == CHAR_INT:
            raise KeyboardInterrupt
        if c == CHAR_EOF:
            raise EOFError

        if c == CHAR_ESC:
            d, e = _Getch(), _Getch()
            #if d == "[" and e in xyctl.DIRS:
            #    adj_x, adj_y = xyctl.DIRCALC[e]
            #    _writer("going " + str(adj_x) + str(adj_y))
                # xyctl.adjust(adj_x, adj_y)

    return c


def _writer(*args):
    """
    write a string to stdout and flush.
    should be used by all stdout-writing
    """
    if not args:
        raise TypeError("_writer requires at least one argument")
    args = " ".join(str(i) for i in args).strip()
    sys.stdout.write(args)
    sys.stdout.flush()


def _nbsp(x, y):
    """
    append x to y as long as x is not DEL or backspace
    """
    if x in (CHAR_DEL, CHAR_BKS, CHAR_ESC):
        try:
            y.pop()
        except IndexError:
            pass
        return y
    y.append(x)
    return y


def pretty_press():
    """
    literally just read any fancy char from stdin let caller do whatever
    """
    y = []
    i = _read_keypress()
    _writer(i)
    return _nbsp(i, y)


def _do_condition(
        end_chars,
        end_condition,
        count,
        ignore_chars=(),
        ignore_condition=CONDS[True + 1],
        raw=False
    ):
    y = []
    count = parsenum(count)
    while len(y) <= count:
        i = _read_keypress(raw)
        if not ignore_condition(i, ignore_chars):
            _writer(i)
        if end_condition(i, end_chars):
            break
        if not ignore_condition(i, ignore_chars):
            y = _nbsp(i, y)
    return "".join(y)


def thismany(count, raw=False):
    """read exactly count chars"""

    return _do_condition(
        "",
        CONDS[True + 1],  # more than true == never expires :D
        count,
        raw=raw
    )


def until(chars, invert=False, count=-1, raw=False):
    """get chars of stdin until any of chars is read,
    or until count chars have been read, whichever comes first"""

    return _do_condition(
        chars,
        CONDS[invert],
        count,
        raw=raw
    )


def until_not(chars, count=-1, raw=False):
    """read stdin until any of chars stop being read,
    or until count chars have been read; whichever comes first"""

    return until(
        chars,
        invert=True,
        count=count,
        raw=raw
    )


def ignore(
        ignore_these,
        end_on,
        end_cond=True,
        count=-1,
        raw=False,
        invert=False
    ):
    """ignore_these keypresses, and stop reading at end_on or count,
    whichever comes first"""

    return _do_condition(
        end_on,
        CONDS[end_cond],
        count,
        ignore_chars=ignore_these,
        ignore_condition=CONDS[invert],
        raw=raw
    )


def ignore_not(
        ignore_these,
        end_on,
        end_cond=True,
        count=-1,
        raw=False
    ):
    """ignore everything that isn't these keypresses
    and stop reading at end_on or count, whichever comes first"""

    return ignore(
        ignore_these,
        end_on,
        end_cond=end_cond,
        count=count,
        raw=raw,
        invert=True
    )


class xyctl:
    UP = chr(65)
    DN = chr(66)
    LT = chr(67)
    RT = chr(68)

    DIRS = frozenset([UP, DN, LT, RT])

    DIRCALC = {
        UP: (0, 1),
        DN: (0, -1),
        LT: (-1, 0),
        RT: (1, 0),
    }

    def _terminal_size():
        import fcntl, struct
        h, w, hp, wp = struct.unpack('HHHH',
            fcntl.ioctl(0, termios.TIOCGWINSZ,
            struct.pack('HHHH', 0, 0, 0, 0)))
        return w, h, w * h

    def _matrix_calc(adj_x, adj_y):
        cur_x, cur_y = xyctl.getter()
        new_x, new_y = (
            (cur_x + adj_x),
            (cur_y + adj_y)
        )

        if (new_x * new_y) < (xyctl._terminal_size()[2]):
            return new_x, new_y
        else:
            _writer(CHAR_BEL)

    def getter():
        _writer(CHAR_ESC + "[6n")
        pos = until("R", raw=True)
        _writer(CHAR_CRR + CHAR_NUL * (len(pos) + 1) + CHAR_CRR)
        pos = pos[2:].split(";")
        pos[0], pos[1] = int(pos[1]), int(pos[0])
        return pos

    def setter(new_x, new_y):
        _writer(CHAR_ESC + "[{};{}H".format(new_x, new_y))

    def adjust(adj_x, adj_y):
        new_x, new_y = xyctl._matrix_calc(adj_x, adj_y)
        xyctl.setter(new_x, new_y)

#if __name__ == "__main__":
#    print(hex(ord(_read_keypress())))
