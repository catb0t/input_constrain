#!/usr/bin/env python3
import unittest
import subprocess as sp
from sys import executable as py, maxsize as MAXSIZE, version_info as VERINFO
from os import getcwd

TESTMOD_INFO = ("pmlr", getcwd() + "/../pmlr/pmlr/pmlr.py")

TEST_HELP = getcwd() + "/../pmlr/test/_tests_helper.py"


if VERINFO.major == 2:
    import imp
    pmlr = imp.load_source(*TESTMOD_INFO)

elif VERINFO.major == 3:
    if VERINFO.minor < 5:
        from importlib.machinery import SourceFileLoader
        pmlr = SourceFileLoader(*TESTMOD_INFO).load_module()

    elif VERINFO.minor >= 5:
        import importlib.util
        spec = importlib.util.spec_from_file_location(*TESTMOD_INFO)
        pmlr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pmlr)

    else:
        raise NotImplementedError(VERINFO.minor)
else:
    raise NotImplementedError(VERINFO.major)


class TestKPReader(unittest.TestCase):

    def setUp(self):
        pmlr.init()

    def test_parsenum(self):
        """test parsenum"""
        nums = (-MAXSIZE, -122, -1, 0, 8, 88, 888880, MAXSIZE)
        for elem in nums:
            result = pmlr.util.parsenum(elem)
            expect = MAXSIZE if elem < 0 else elem
            self.assertEqual(result, expect)

    def test_parsenum_complex(self):
        """test parsenum failure"""
        with self.assertRaises(TypeError):
            pmlr.util.parsenum(8j)

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
        specials = {  # special cases
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