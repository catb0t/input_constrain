#!/usr/bin/env python3
from sys import executable as py, maxsize as mxsz
import subprocess as sp
import unittest

import input_constrain

TEST_HELP = "_tests_helper.py"


class TestKPReader(unittest.TestCase):

    def test_parsenum(self):
        nums = (-mxsz, -122, -1, 0, 8, 88, 888880, mxsz)
        for idx, elem in enumerate(nums):
            result = input_constrain.parsenum(elem)
            expect = mxsz if elem < 0 else elem
            self.assertEqual(result, expect)

    def test_parsenum_complex(self):
        with self.assertRaises(TypeError):
            input_constrain.parsenum(8j)

    def test_getch(self):
        for ch in range(4, 128):
            p = sp.Popen(
                [py, "-u", TEST_HELP, "getch"],
                stdin=sp.PIPE,
                stdout=sp.PIPE,
                stderr=sp.PIPE,
                bufsize=1
            )
            out, err = p.communicate(input=bytes(chr(ch), "ascii"))

if __name__ == '__main__':
    unittest.main()