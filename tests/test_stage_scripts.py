"""Tests for tools/stage_scripts.py, on made-up scripts (no retail data)."""
import os
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import stage_scripts  # noqa: E402


class StageScriptsTest(unittest.TestCase):
    def test_closure_and_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = os.path.join(tmp, "main"), os.path.join(tmp, "out")
            os.makedirs(src)
            with zipfile.ZipFile(os.path.join(src, "pak0.pk3"), "w") as z:
                z.writestr("maps/t1.scr", 'main:\n\texec global/spawner.scr\n\tthread global/Disc.scr::go\nend\n')
                z.writestr("maps/t1_precache.scr", "main:\nend\n")
                z.writestr("global/spawner.scr", 'main:\n\twaitthread global/entsound.scr::x\n\texec global/gone.scr\nend\n')
                z.writestr("global/disc.scr", "go:\nend\n")
                z.writestr("global/entsound.scr", "x:\n\texec global/spawner.scr\nend\n")
                z.writestr("global/unused.scr", "main:\nend\n")
            self.assertEqual(stage_scripts.main([src, "--out", out, "--maps", "t1"]), 0)
            got = sorted(os.path.relpath(os.path.join(d, f), out) for d, _, fs in os.walk(out) for f in fs)
            self.assertEqual(got, ["global/disc.scr", "global/entsound.scr", "global/spawner.scr",
                                   "maps/t1.scr", "maps/t1_precache.scr"])
            _, missing = stage_scripts.closure(stage_scripts.collect([src], (".scr",)), "t1")
            self.assertEqual(missing, ["global/gone.scr"])
            self.assertEqual(stage_scripts.main([src, "--out", out, "--maps", "nope"]), 1)


if __name__ == "__main__":
    unittest.main()
