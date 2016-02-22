#!/usr/bin/env python3
import unittest
import subprocess as sp
from sys import executable as py, maxsize as mxsz

import input_constrain

TEST_HELP = "_tests_helper.py"

class TestKPReader(unittest.TestCase):

    def test_parsenum(self):
        """test parsenum"""
        nums = (-mxsz, -122, -1, 0, 8, 88, 888880, mxsz)
        for idx, elem in enumerate(nums):
            result = input_constrain.parsenum(elem)
            expect = mxsz if elem < 0 else elem
            self.assertEqual(result, expect)

    def test_parsenum_complex(self):
        """test parsenum failure"""
        with self.assertRaises(TypeError):
            input_constrain.parsenum(8j)

    def test_getch(self):
        """test getch (patience)"""
        for ch in range(128):
            p = sp.Popen(
                [py, TEST_HELP, "getch"],
                stdin=sp.PIPE,
                stdout=sp.PIPE,
            )
            out, _ = p.communicate(input=bytes(chr(ch), "utf-8"))
            self.assertEqual(
                out, bytes('{}'.format(ch), "utf-8")  # ewww
            )

    def test_read_keypress(self):
        """test readkey (patience)"""
        specials = { # special cases
            3: "KeyboardInterrupt",
            4: "EOFError",
            8: b'\x08\x088',
            13: b'10',
            27: b'\x08\x0827',
            127: '',
        }
        for ch in range(128):
            p = sp.Popen(
                [py, TEST_HELP, "readkey"],
                stdin=sp.PIPE,
                stdout=sp.PIPE,
                stderr=sp.PIPE
            )
            out, err = p.communicate(input=bytes(chr(ch), "utf-8"))
            if ch in specials.keys():
                res = (  # magic
                    err
                        .decode("utf-8")
                        .strip()
                        .split("\n")[-1]
                    if ch not in (8, 13, 27)
                    else out
                )
                self.assertEqual(
                    specials[ch], res
                )
            else:
                self.assertEqual(
                    out, bytes('{}'.format(ch), "utf-8")
                )

    def test_read_keypress_raw(self):
        """read raw keypress (patience)"""
        specials = { # special cases
            8: b'\x08\x088',
            13: b'10',
            27: b'\x08\x0827',
            127: b'\x08\x08127',
        }
        for ch in range(128):
            p = sp.Popen(
                [py, TEST_HELP, "raw_readkey"],
                stdin=sp.PIPE,
                stdout=sp.PIPE,
                stderr=sp.PIPE
            )
            out, err = p.communicate(input=bytes(chr(ch), "utf-8"))
            if ch in specials.keys():
                self.assertEqual(
                    specials[ch], out
                )
            else:
                self.assertEqual(
                    out, bytes('{}'.format(ch), "utf-8")
                )


if __name__ == '__main__':
    from os import stat
    try:
        stat(TEST_HELP)
    except FileNotFoundError as e:
        print(e)
        print("stat: cannot stat '{}': no such file or directory".format(TEST_HELP))
        exit(2)
    else:
        unittest.main(verbosity = 3)