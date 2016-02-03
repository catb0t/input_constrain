#!/usr/bin/env python3

import sys
from input_constrain import *

def _until_demo() -> None:
    """demonstrate the until function"""
    print("get until what?")
    char = read_single_keypress()
    _ = sys.stdout.write(char + "\n")
    sys.stdout.flush()
    y = until(char)
    print("\n" + y)


def _thismany_demo() -> None:
    """demonstrate the thismany function"""
    print("get how many chars?")
    kps = input()
    try:
        kps = int(kps)
    except ValueError:
        print("not a number, sorry")
        return
    print("getting", str(kps))
    y = thismany(kps)
    print("\n" + y)


def _can_you_vote() -> str:
    """a practical example:
    test if a user can vote based purely on keypresses"""
    _ = sys.stdout.write("can you vote? age : ")
    sys.stdout.flush()
    x = int("0" + until_not("0123456789"))
    if not x:
        print("\nsorry, age can only consist of digits.")
        return
    print(
        "your age is", x, "\nYou can vote!"
        if x >= 18
        else "Sorry! you can't vote"
    )


def _forth_syntax_test() -> str:
    """
    in the programming language Forth,
    `function` definitons start at the beginning of a line with a `:` colon
    and go until the next semicolon.

    this is an example of how this module can be used
    in a Forth REPL to compile statements specially;
    it's implemented in catb0t/microcat as well.
    """
    sys.stdout.write("demo FORTH repl \n> ")
    firstchar = read_single_keypress()
    _ = sys.stdout.write(firstchar)
    if firstchar != ":":
        return print("first char wasn't ':'")
    defn = firstchar + until(";") + ";"
    sys.stdout.write("\nrepl got:\n" + defn + "\n")
    return


if __name__ == "__main__":
    _forth_syntax_test()
