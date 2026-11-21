"""Tests for the Morpheus (.scr) script VM in script/.

Builds out/msrun with the system C compiler, runs each tests/scripts/*.scr
against the mock world and compares output with the .expected file next to it.
Regenerate an expected file after an intended change with:
    out/msrun tests/scripts/NAME.scr > tests/scripts/NAME.expected
"""
import os
import shutil
import subprocess
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(HERE, "scripts")
MSRUN = os.path.join(ROOT, "out", "msrun")

# scripts that are expected to report script errors (msrun exits 3)
EXPECT_ERRORS = {"errors"}


def run(*args, cwd=None):
    return subprocess.run([MSRUN, *args], capture_output=True, text=True, cwd=cwd)


@unittest.skipUnless(shutil.which(os.environ.get("CC", "cc")) and shutil.which("make"), "needs a C compiler")
class ScriptVMTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(["make", "-s", "-C", os.path.join(ROOT, "script")], check=True)

    def check(self, name):
        r = run(os.path.join(SCRIPTS, name + ".scr"))
        with open(os.path.join(SCRIPTS, name + ".expected")) as fh:
            expected = fh.read()
        self.assertEqual(r.stdout, expected)
        self.assertEqual(r.returncode, 3 if name in EXPECT_ERRORS else 0, r.stdout + r.stderr)

    def test_basics(self):
        self.check("basics")

    def test_mission(self):
        self.check("mission")

    def test_errors(self):
        self.check("errors")

    def test_compile_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.scr")
            with open(path, "w") as fh:
                fh.write("main:\n\tif (1 {\nend\n")
            r = run(path)
            self.assertEqual(r.returncode, 1)
            self.assertIn("bad.scr:2:", r.stdout)

    def test_memory_budget(self):
        r = run("-mem", os.path.join(SCRIPTS, "mission.scr"))
        last = r.stdout.strip().splitlines()[-1]
        peak = int(last.split(",")[1].split()[0])
        self.assertLess(peak, 64 * 1024, last)
        # a budget too small to load the script fails cleanly instead of crashing
        r = run("-budget", "2000", os.path.join(SCRIPTS, "mission.scr"))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("error", r.stdout)

    def test_wait_scheduling(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "w.scr")
            with open(path, "w") as fh:
                fh.write("main:\n\tthread a\n\twait 1\n\tprintln \"main\"\nend\n"
                         "a:\n\twaitframe\n\tprintln \"a\"\n\twait 0.5\n\tprintln \"a2\"\nend\n")
            r = run(path)
            self.assertEqual(r.stdout.splitlines(), ["  0.05 a", "  0.55 a2", "  1.00 main"])

    def test_check_scripts_tool(self):
        with tempfile.TemporaryDirectory() as tmp:
            pk3 = os.path.join(tmp, "pak0.pk3")
            with zipfile.ZipFile(pk3, "w") as z:
                z.write(os.path.join(SCRIPTS, "basics.scr"), "maps/basics.scr")
                z.writestr("maps/broken.scr", "main:\n\t$ \nend\n")
            r = subprocess.run(["python3", os.path.join(ROOT, "tools", "check_scripts.py"), pk3],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("maps/broken.scr:2:", r.stdout)
            self.assertIn("1 of 2 scripts compile", r.stdout)


if __name__ == "__main__":
    unittest.main()
