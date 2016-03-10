#!/usr/bin/env python3

import sys
import struct
from platform import system
SYSTEM = system().lower()
DEBUG  = True

class CHAR:
    """essentially an enum, to avoid clouding the ns"""
    NUL = chr(0)
    INT = chr(3)
    EOF = chr(4)
    BEL = chr(7)
    BKS = chr(8)
    LFD = chr(10)
    CRR = chr(13)
    ESC = chr(27)
    SPC = chr(32)
    DEL = chr(127)

    CONDS = [
        (lambda i, chars: i in chars),
        (lambda i, chars: i not in chars),
        (lambda *args, **kwargs: False),
    ]


def init(TERM_BUFSIZE=4096):
    """module initialiser: calls constructors so you don't have to
    you must call this before other functions!"""
    global reader
    reader = read_class(TERMCTL_SPECIAL_BUFSIZE=TERM_BUFSIZE)


def checkinit(func, *args, **kwargs):
    from functools import wraps

    @wraps(func)
    def isdefined(*args, **kwargs):
        if "reader" not in globals().keys():
            print("\n\tfatal: init() not called\n")
            msg = "must call init() first, or call init() again before {}()".format(func.__name__)
            raise TypeError(msg)

        return func(*args, **kwargs)

    return isdefined


class _nt_reader():

    def __init__(self, *args, **kwargs):
        """reader on nt"""

        self.NAME = "NT"

        if SYSTEM != "windows":
            util.writer("\n\there be dragons; ye COWER in the SHADOW of", self.NAME, "\n\n")

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


class _posix_reader():

    def __init__(self, TERMCTL_SPECIAL_BUFSIZE=4096):
        """reader on posix"""

        self.NAME = "POSIX"

        if SYSTEM == "windows":
            util.writer("\n\there be dragons; ye COWER in the SHADOW of", self.NAME, "\n\n")

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
            fl = self.fcntl.fcntl(fd, self.fcntl.F_GETFL)
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

read_class = {
    "windows": _nt_reader,
}.get(
    SYSTEM,
    _posix_reader  # default
)


class util():
    """utilities"""

    @staticmethod
    def parsenum(num):
        """sys.maxsize if num is negative"""
        num = int(num)
        return sys.maxsize if num < 0 else num

    @staticmethod
    def writer(*args, fd=sys.stdout, flush=True):
        """write a string to file descriptor and flush.
        should be used by all stdout-writing"""

        if not args:
            raise TypeError("writer requires at least one argument")

        if len(args) > 1:
            args = " ".join(str(i) for i in args).strip(" ")
        else:
            args = "".join(str(i) for i in args)

        def wflush(fd, args):
            fd.write(args)
            if flush:
                fd.flush()

        if not isinstance(fd, (tuple, list)):
            wflush(fd, args)

        elif isinstance(fd, (tuple, list)):
            for s in fd:
                wflush(s, args)

        else:
            raise TypeError("file descriptors not provided in a sane format")

    @staticmethod
    def debug_fmt(
            level,
            cframe = {
                "FILE": None,
                "FUNC": None,
                "LINE": None,
            }
        ):

        import inspect
        callerframercrd = inspect.stack()[2]
        frame = callerframercrd[0]
        info  = inspect.getframeinfo(frame)
        FILE, FUNC, LINE = info.filename, info.function, info.lineno

        assert level not in (None, ""), "level must not be None or EmptyString"
        level = level.upper()
        return "[ " + {
            "INFO":  "{}1;32mINFO{}",     # info  = green
            "WARN":  "{}1;31mWARN{}",     # warn  = light red
            "ERROR": "{}1;31mERROR{}",    # error = red
            "FATAL": "{}1;31mFATAL{}",    # fatal = red
            "RANGE": "{}1;33mRANGE_VIOLATION{}",  # over / underflow = yellow
            "DEBUG": "{}1;36mDEBUG{}",    # debug = blue
        }.get(
            level, "{}1;36m" + level + "{}"
        ).format(
            CHAR.ESC + "[",
            CHAR.ESC + "[m"
        ) + " ] line {}, function {}, file {} ::".format(
            cframe["LINE"] or LINE,
            cframe["FUNC"] or FUNC,
            cframe["FILE"] or FILE,
        )

    @staticmethod
    def debug_write(
            *args,
            level  = "INFO",
            fd     = sys.stdout,
            cframe = {
                "FILE": None,
                "FUNC": None,
                "LINE": None,
            }
        ):

        import inspect
        callerframercrd = inspect.stack()[1]
        frame = callerframercrd[0]
        info  = inspect.getframeinfo(frame)
        FILE, FUNC, LINE = info.filename, info.function, info.lineno

        if DEBUG:
            util.writer(
                util.debug_fmt(
                    level,
                    cframe = {
                        "FILE": cframe["FILE"] or FILE,
                        "FUNC": cframe["FUNC"] or FUNC,
                        "LINE": cframe["LINE"] or LINE,
                    }
                ),
                *args,
                fd=fd
            )

    @staticmethod
    def esc_filter(c, y):
        """append x to y as long as x is not DEL or backspace or esc"""
        if c in (CHAR.DEL, CHAR.BKS):
            try: y.pop()
            except IndexError: pass
            return y

        """elif c.startswith("\x1b["):
            y.idx += {
                "D": -1,
                "C": 1
            }.get(c[-1], (lambda: None))"""

        y.append(c)
        return y


@checkinit
def readkey(raw=False):
    """interface for getch + drain_buf
    if raw, behave like getch but with flushing for multibyte inputs"""
    ch = reader.getch()
    more = reader.drain_buf()

    if raw:
        return ch + more

    # cooked

    if ch == CHAR.INT: raise KeyboardInterrupt
    if ch == CHAR.EOF: raise EOFError

    if ch in (CHAR.BKS, CHAR.DEL):
        util.writer(CHAR.BKS + CHAR.SPC + CHAR.BKS)
        return CHAR.BKS

    elif ch in (CHAR.CRR, CHAR.LFD):
        return (CHAR.CRR if SYSTEM == "Windows" else "") + CHAR.LFD

    elif ch == CHAR.ESC:
        if more:
            sp = more[1:]
            if sp in ("3~", "A", "B", "C", "D"):
                util.writer(CHAR.BEL)
            return CHAR.SPC  # CHAR.ESC + more

    ch += more
    return ch


@checkinit
def raw_readkey():
    """alias for readkey(raw=True)"""
    return readkey(raw=True)


@checkinit
def pretty_press(raw=False):
    """literally just read any fancy char from stdin let caller do whatever"""
    y = []
    i = readkey(raw=raw)
    if (not raw) and (i not in (CHAR.BKS, CHAR.DEL, CHAR.ESC)):
        util.writer(i)
    return util.esc_filter(i, y)


@checkinit
def _do_condition(
        end_chars,
        end_condition,
        count,
        ignore_chars=(),
        ignore_condition=CHAR.CONDS[True + 1],  # always false
        raw=False
    ):
    """singular interface to reading strings from readkey, to minimise duplication"""
    y = []
    count = util.parsenum(count)
    while len(y) <= count:
        i = readkey(raw=raw)
        if end_condition(i, end_chars):
            break
        if not ignore_condition(i, ignore_chars):
            if (not raw) and (i not in (CHAR.BKS, CHAR.DEL)):
                util.writer(i)
            y = util.esc_filter(i, y)
    return "".join(y)


@checkinit
def thismany(count, raw=False):
    """read exactly count chars"""

    return _do_condition(
        "",
        CHAR.CONDS[True + 1],  # more than true == never expires :D
        count,
        raw=raw
    )


@checkinit
def until(chars, invert=False, count=-1, raw=False):
    """get chars of stdin until any of chars is read,
    or until count chars have been read, whichever comes first"""

    return _do_condition(
        chars,
        CHAR.CONDS[invert],
        count,
        raw=raw
    )


@checkinit
def until_not(chars, count=-1, raw=False):
    """read stdin until any of chars stop being read,
    or until count chars have been read; whichever comes first"""

    return until(
        chars,
        invert=True,
        count=count,
        raw=raw
    )


@checkinit
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
        CHAR.CONDS[not end_cond],
        count,
        ignore_chars=ignore_these,
        ignore_condition=CHAR.CONDS[invert],
        raw=raw
    )


@checkinit
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
