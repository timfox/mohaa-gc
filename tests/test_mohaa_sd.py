"""Tests for tools/mohaa_sd.py on a made-up install and made-up CDs (no retail data)."""
import io
import os
import shutil
import stat
import sys
import tempfile
import unittest
import wave
import zipfile
from contextlib import redirect_stdout
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import mohaa_sd  # noqa: E402

MUS = "path sound/music\nnormal sting.wav\n!normal loop\n"
SCR = "main:\n\tprintln \"hi\"\nend\n"


def pak(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("music/t1.mus", MUS)
        z.writestr("maps/t1.scr", SCR)


def wav(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(bytes(4 * 4410))


def run(argv):
    out = io.StringIO()
    with redirect_stdout(out):
        rc = mohaa_sd.main(argv)
    return rc, out.getvalue()


class MohaaSdTest(unittest.TestCase):
    def test_install_to_sd_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "Main"))   # Windows installs capitalise it
            pak(os.path.join(game, "Main", "pak0.pk3"))
            wav(os.path.join(game, "Main", "sound", "music", "sting.wav"))
            self.assertEqual(mohaa_sd.find_main(game), os.path.join(game, "Main"))
            stages = "music,scripts" if shutil.which("ffmpeg") else "scripts"
            rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", stages, "--list"])
            self.assertEqual(rc, 0)
            root = os.path.join(sd, "xash3d", "dod")
            self.assertTrue(os.path.isfile(os.path.join(root, "maps", "t1.scr")))
            if shutil.which("ffmpeg"):
                self.assertTrue(os.path.isfile(os.path.join(root, "music", "t1.mood")))
                with wave.open(os.path.join(root, "sound", "mohaa", "music", "sting.wav")) as w:
                    self.assertEqual((w.getnchannels(), w.getframerate()), (1, 22050))
            self.assertIn("== scripts:", log)

    def test_cds_are_unpacked_once_with_unshield(self):
        with tempfile.TemporaryDirectory() as tmp:
            cd1, cd2, sd, bin_ = (os.path.join(tmp, n) for n in ("cd1", "cd2", "sd", "bin"))
            for d in (cd1, cd2, bin_):
                os.makedirs(d)
            for name, d in (("DATA1.HDR", cd1), ("DATA1.CAB", cd1), ("DATA2.CAB", cd1), ("DATA3.CAB", cd2)):
                open(os.path.join(d, name), "w").close()
            # a stand-in unshield: writes the groups as the real one does (one flat folder per group)
            src = os.path.join(tmp, "payload")
            os.makedirs(src)
            pak(os.path.join(src, "pak0.pk3"))
            wav(os.path.join(src, "sting.wav"))
            fake = os.path.join(bin_, "unshield")
            with open(fake, "w") as f:
                f.write("#!/bin/sh\n"
                        "while [ $# -gt 0 ]; do case $1 in -d) shift; out=$1;; *.CAB) cab=$1;; esac; shift; done\n"
                        "test -e \"$(dirname \"$cab\")/DATA3.CAB\" || exit 3\n"
                        "mkdir -p \"$out/Music Files\" \"$out/Data Files Complete\" \"$out/Help Files EN-US\"\n"
                        "cp '%s' \"$out/Music Files/\"\n"
                        "cp '%s' \"$out/Data Files Complete/PAK0.PK3\"\n"
                        "echo x > \"$out/Help Files EN-US/readme.txt\"\n"
                        "echo ran >> '%s'\n" % (os.path.join(src, "sting.wav"), os.path.join(src, "pak0.pk3"),
                                               os.path.join(tmp, "runs")))
            os.chmod(fake, os.stat(fake).st_mode | stat.S_IEXEC)
            with mock.patch.dict(os.environ, {"PATH": bin_ + os.pathsep + os.environ["PATH"]}):
                for _ in range(2):
                    rc, _log = run(["--cd", cd1, cd2, "--sd", sd, "--maps", "t1", "--stages", "scripts"])
                    self.assertEqual(rc, 0)
            main = os.path.join(sd, ".mohaa-work", "cd", "main")
            self.assertTrue(os.path.isfile(os.path.join(main, "pak0.pk3")))
            self.assertTrue(os.path.isfile(os.path.join(main, "sound", "music", "sting.wav")))
            self.assertFalse(os.path.exists(os.path.join(main, "readme.txt")))
            with open(os.path.join(tmp, "runs")) as f:
                self.assertEqual(f.read().count("ran"), 1)   # the second run reuses the unpacked set
            self.assertTrue(os.path.isfile(os.path.join(sd, "xash3d", "dod", "maps", "t1.scr")))

    def test_a_failing_stage_does_not_stop_the_rest(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "main"))
            pak(os.path.join(game, "main", "pak0.pk3"))   # no ubersound aliases: the sounds stage fails
            rc, log = run(["--mohaa", game, "--sd", sd, "--maps", "t1", "--stages", "sounds,scripts"])
            self.assertEqual(rc, 1)
            self.assertIn("== sounds: FAILED", log)
            self.assertIn("failed stages: sounds", log)
            self.assertTrue(os.path.isfile(os.path.join(sd, "xash3d", "dod", "maps", "t1.scr")))

    def test_needs_a_source(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit):
                with mock.patch("sys.stderr", io.StringIO()):
                    mohaa_sd.main(["--sd", tmp])


if __name__ == "__main__":
    unittest.main()
