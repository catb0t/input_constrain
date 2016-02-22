#!/usr/bin/env python3

import sys
import string
import pmlr


def _until_demo():
    """
    demonstrate the until function
    """

    print("get until what?")
    char = pmlr._read_keypress()
    pmlr._writer(char + "\n")
    y = pmlr.until(char)
    print("\n" + y)


def _thismany_demo():
    """
    demonstrate the thismany function
    """

    print("get how many chars?")
    kps = input()
    try:
        kps = int(kps)
    except ValueError:
        print("not a number, sorry")
        return
    print("getting", str(kps))
    y = pmlr.thismany(kps)
    print("\n" + y)


def _can_you_vote():
    """
    a practical example:
    test if a user can vote based purely on keypresses
    """

    pmlr._writer("can you vote? age : ")
    x = int("0" + pmlr.ignore_not("0123456789", "0123456789", end_cond=True, count=2))
    if not x:
        print("\nsorry, age can only consist of digits.")
        return
    print(
        "\nyour age is", x, "\nYou can vote!"
        if x >= 18
        else "Sorry! you can't vote"
    )


def _forth_syntax_test():
    """
    in the programming language Forth,
    `function` definitons start at the beginning of a line with a `:` colon
    and go until the next semicolon.

    this is an example of how this module can be used
    in a Forth REPL to compile statements specially;
    it's implemented in catb0t/microcat as well.
    """

    pmlr._writer("demo FORTH repl \n> ")
    firstchar = pmlr._read_keypress()
    pmlr._writer(firstchar)
    if firstchar != ":":
        print("\nreturned because first char wasn't ':'")
        return
    defn = firstchar + pmlr.until(";") + ";"
    pmlr._writer("\nrepl got:\n" + defn + "\n")


def _get_paragraphs():
    from string import printable as ALLOWED_CHARS
    print("\nPress CTRL-C or CTRL-D to stop reading.")
    textwriterCommand = pmlr.until_not(ALLOWED_CHARS, count=500, raw=True)
    pmlr._writer("\n\n")
    return pmlr._writer("you typed:" + textwriterCommand)
