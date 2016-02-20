#!/usr/bin/env python3

import sys
import string
import input_constrain


def _until_demo():
    """
    demonstrate the until function
    """

    print("get until what?")
    char = input_constrain._read_keypress()
    input_constrain._writer(char + "\n")
    y = input_constrain.until(char)
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
    y = input_constrain.thismany(kps)
    print("\n" + y)


def _can_you_vote():
    """
    a practical example:
    test if a user can vote based purely on keypresses
    """

    input_constrain._writer("can you vote? age : ")
    x = int("0" + until_not("0123456789"))
    if not x:
        print("\nsorry, age can only consist of digits.")
        return
    print(
        "your age is", x, "\nYou can vote!"
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

    input_constrain._writer("demo FORTH repl \n> ")
    firstchar = input_constrain._read_keypress()
    input_constrain._writer(firstchar)
    if firstchar != ":":
        print("\nreturned because first char wasn't ':'")
        return
    defn = firstchar + input_constrain.until(";") + ";"
    input_constrain._writer("\nrepl got:\n" + defn + "\n")


def _get_paragraphs():
    from string import printable as ALLOWED_CHARS
    print("\nPress CTRL-C or CTRL-D to stop reading.")
    textwriterCommand = input_constrain.until_not(ALLOWED_CHARS, count=500, raw=True)
    input_constrain._writer("\n\n")
    return input_constrain._writer("you typed:" + textwriterCommand)

if __name__ == "__main__":
    _get_paragraphs()
