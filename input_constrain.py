#!/usr/bin/env python3

def read_single_keypress() -> str:
    """Waits for a single keypress on stdin.

    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.

    Returns the character of the key that was pressed (zero on
    KeyboardInterrupt which can happen when a signal gets handled)

    -- from :: http://stackoverflow.com/a/6599441/4532996
    """

    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save) # copy the stored version to update
    # iflag
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                  | termios.ISTRIP | termios.INLCR | termios. IGNCR
                  | termios.ICRNL | termios.IXON )
    # oflag
    attrs[1] &= ~termios.OPOST
    # cflag
    attrs[2] &= ~(termios.CSIZE | termios. PARENB)
    attrs[2] |= termios.CS8
    # lflag
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    # read a single keystroke
    try:
        ret = sys.stdin.read(1) # returns a single character
    except KeyboardInterrupt:
        ret = 0
    finally:
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret

def until(char) -> str:
    """get chars of stdin until char is read"""
    import sys
    y = ""
    sys.stdout.flush()
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i == char:
            break
        y += i
    return y

def thismany(count) -> str:
    """get exactly count chars of stdin"""
    import sys
    y = ""
    sys.stdout.flush()
    for _ in range(count):
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        y += i
    return y

def until_multi(chars) -> str:
    """read stdin until any of a set of chars are read"""
    import sys
    chars = list(chars)
    y = ""
    sys.stdout.flush()
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i in chars:
            break
        y += i
    return y

def until_not(char) -> str:
    """read stdin until char stops being read"""
    import sys
    y = ""
    sys.stdout.flush()
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i != char:
            break
        y += i
    return y

def until_not_multi(chars) -> str:
    """read stdin until !(chars)"""
    import sys
    chars = list(chars)
    y = ""
    sys.stdout.flush()
    while True:
        i = read_single_keypress()
        _ = sys.stdout.write(i)
        sys.stdout.flush()
        if i not in chars:
            break
        y += i
    return y
