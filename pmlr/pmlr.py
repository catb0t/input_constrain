#!/usr/bin/env python3

import sys
import struct
from platform import system
SYSTEM = system()

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


class _nt_reader():

    def __init__(self, *args, **kwargs):
        """reader on nt"""

        self.NAME = "NT"

        self.msvcrt = __import__("msvcrt")
        self.ctypes = __import__("ctypes")
        try:
            self.colorama  = __import__("colorama")
            self.colorama.init()
        except (AttributeError, ImportError):
            print(
            """
            you must install colorama to use this module on windows
            do this by:
            $ cd colorama
            $ python setup.py install
            """
            )
            exit(2)


    def getch(self):
        """use msvcrt to get a char"""
        return self.msvcrt.getch()

    def drain_buf(self):
        """while buffer, pseudo-nonblocking read bytes from buffer using msvcrt"""
        y = []
        while self.msvcrt.kbhit():
            y.append(self.msvcrt.getch())
        return "".join(y)

    def term_size(self, details=False):
        """get terminal winsize on nt"""
        # https://gist.github.com/jtriley/1108174#file-terminalsize-py-L31
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h    = self.ctypes.windll.kernel32.GetStdHandle(-12)
        csbi = self.ctypes.create_string_buffer(22)
        res  = self.ctypes.windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            juicy_data = struct.unpack("hhhhHhhhhhh", csbi.raw)
            (
                bufx, bufy,
                curx, cury,
                wattr,
                left, top,
                right, bottom,
                maxx, maxy
            ) = juicy_data
            sizex = right - left + 1
            sizey = bottom - top + 1
            ret = sizex, sizey, sizex * sizey, juicy_data
            return ret if details else ret[:len(ret) - 1]
        else:
            raise ValueError(
                "ctypes.windll.kernel32.GetConsoleScreenBufferInfo: "
                + repr(res)
            )

class _posix_reader():

    def __init__(self, TERMCTL_SPECIAL_BUFSIZE=4096):
        """reader on posix"""

        self.NAME = "POSIX"

        self.tty     = __import__("tty")
        self.termios = __import__("termios")
        self.fcntl   = __import__("fcntl")

        self.O_NONBLOCK = __import__("os").O_NONBLOCK

        self.TERM_BUFSIZE = TERMCTL_SPECIAL_BUFSIZE


    def getch(self):
        """use old fashioned termios to getch"""
        if sys.stdin.isatty():  # fixes "Inappropriate ioctl for device"
            fd = sys.stdin.fileno()
            old_settings = self.termios.tcgetattr(fd)
            try:
                self.tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old_settings)
                return ch
        else:
            return sys.stdin.read(1)

    def drain_buf(self):
        """read TERM_BUFSIZE of waiting keypresses"""
        if sys.stdin.isatty():
            fd = sys.stdin.fileno()
            fl = self.fcntl.fcntl(fd, fcntl.F_GETFL)
            self.fcntl.fcntl(fd, self.fcntl.F_SETFL, fl | self.O_NONBLOCK)
            try:
                # if nothing is waiting on sys.stdin, then TypeError
                # because "can't concat NoneType and str"
                chars = sys.stdin.read(self.TERM_BUFSIZE)
            except TypeError:
                chars = ""
            finally:
                self.fcntl.fcntl(fd, self.fcntl.F_SETFL, fl) # restore settings
                return chars
        else:
            return sys.stdin.read(self.TERM_BUFSIZE)  # ???

    def term_size(self):
        """get terminal size on posix"""
        h, w, hp, wp = struct.unpack(
            'HHHH',
            self.fcntl.ioctl(
                0, self.termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)
            )
        )
        return w, h, w * h

read_class = {
    "Windows": _nt_reader,
}.get(
    SYSTEM,
    _posix_reader  # default
)


class xyctl_class(read_class): # only inheriting to get at term_size without passing an instance

    def __init__(self):
        """x/y control"""
        self.UP = chr(65)  # A
        self.DN = chr(66)
        self.LT = chr(67)
        self.RT = chr(68)  # D

        self.DIRS = frozenset([self.UP, self.DN, self.LT, self.RT])  # membership

        self.DIRCALC = {
            self.UP: (0, 1),
            self.DN: (0, -1),
            self.LT: (-1, 0),
            self.RT: (1, 0),
        }
        self.saved = []

    def _abs_matrix_calc(self, adj_x, adj_y):
        cur_x, cur_y = xyctl.getter()
        new_x, new_y = (
            (cur_x + adj_x),
            (cur_y + adj_y)
        )

        if (new_x * new_y) < (self.term_size()[2]):
            return new_x, new_y
        else:
            _writer(CHAR_BEL)
            raise ValueError

    def getter(self):
        """return cursor's position in terminal"""
        _writer(CHAR_ESC + "[6n")
        pos = until("R", raw=True)
        _writer(CHAR_CRR + CHAR_NUL * (len(pos) + 1) + CHAR_CRR)
        pos = pos[2:].split(";")
        pos[0], pos[1] = int(pos[1]), int(pos[0])
        return pos

    def absolute_setter(self, new_x, new_y):
        """set cursor position by absolute coords"""
        _writer(CHAR_ESC + "[{};{}H".format(new_x, new_y))

    def adjust_xy(self, adj_x, adj_y):
        """adjust cursor by increments"""
        new_x, new_y = xyctl._abs_matrix_calc(adj_x, adj_y)
        xyctl.absolute_setter(new_x, new_y)

    def savepos(self):
        """save the cursor's position by appending it to a list"""
        coords = self.getter()
        self.saved.append(coords)
        return coords

    def popsaved(self, idx=-1):
        """get last saved cursor pos by popping from list, or idx"""
        new = self.saved.pop(idx)
        if new:
            self.absolute_setter(*tuple(new))
            return new

    def process_arrowkey(self, seq):
        pass
        


class util():
    """utilities"""
    def parsenum(num):
        """sys.maxsize if num is negative"""
        num = int(num)
        return sys.maxsize if num < 0 else num

    def writer(*args):
        """write a string to stdout and flush.
        should be used by all stdout-writing"""
        if not args:
            raise TypeError("_writer requires at least one argument")
        args = " ".join(str(i) for i in args).strip()
        sys.stdout.write(args)
        sys.stdout.flush()


def init(TERM_BUFSIZE=4096):
    """module initialiser: calls constructors so you don't have to
    you must call this before other functions!"""
    global reader, xyctl
    reader = read_class(TERMCTL_SPECIAL_BUFSIZE=TERM_BUFSIZE)
    xyctl  = xyctl_class()



def readkey(raw=False):
    """interface for getch + drain_buf
    if raw, behave like getch but with flushing for multibyte inputs"""
    ch = reader.getch()
    more = reader.drain_buf()
    if raw:
        return ch + more

    # cooked

    if ch == CHAR_INT: raise KeyboardInterrupt
    if ch == CHAR_EOF: raise EOFError

    if ch in (CHAR_BKS, CHAR_DEL):
        _writer(CHAR_BKS)
        _writer(CHAR_SPC)  # hacky? indeed. does it *work*? hell yeah!

    elif ch in (CHAR_CRR, CHAR_LFD):
        _writer(CHAR_CRR if SYSTEM == "Windows" else "")
        _writer(CHAR_LFD)
        return CHAR_LFD

    elif ch == CHAR_ESC:
        if more[0] == "[":
            sp = more[1:]
            if sp in xyctl.DIRS:
                xyctl.process_arrowkey(sp)
            else:
                return CHAR_ESC + more

    return ch + more


def raw_readkey():
    """alias for readkey(raw=True)"""
    return readkey(raw=True)


def _nbsp(x, y):
    """append x to y as long as x is not DEL or backspace"""
    if x in (CHAR_DEL, CHAR_BKS, CHAR_ESC):
        try:
            y.pop()
        except IndexError:
            pass
        return y
    y.append(x)
    return y


def pretty_press(raw=False):
    """literally just read any fancy char from stdin let caller do whatever"""
    y = []
    i = readkey(raw=raw)
    if (not raw) and (i not in (CHAR_BKS, CHAR_DEL)):
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
    """singular interface to reading strings from readkey, to minimise duplication"""
    y = []
    count = parsenum(count)
    while len(y) <= count:
        i = readkey(raw=raw)
        if not ignore_condition(i, ignore_chars):
            if (not raw) and (i not in (CHAR_BKS, CHAR_DEL)):
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
