"""Tests for tools/music.py, on made-up .mus tables and scripts (no retail data)."""
import os
import shutil
import sys
import tempfile
import unittest
import wave
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import music  # noqa: E402

MUS = """// a comment
path sound/music
normal  Calm_01.mp3
!normal volume 0.7
!normal loop
aux1    fight.mp3
!aux1   fadetime 1.5
aux2    sting.wav
"""

SCR = """main:
\t$player stufftext "tmstartloop sound/music/mus_tank.mp3"
\t$player stufftext "tmstop; tmstart sound/music/mus_win.mp3"
end
"""


class MusicTest(unittest.TestCase):
    def test_parse(self):
        folder, moods = music.parse_mus(MUS)
        self.assertEqual(folder, "sound/music")
        self.assertEqual(moods["normal"], ["Calm_01.mp3", 0.7, 1, 0.0])
        self.assertEqual(moods["aux1"], ["fight.mp3", 1.0, 0, 1.5])
        self.assertEqual(music.sample_name("sound/music/Calm_01.mp3"), "mohaa/music/calm_01.wav")
        self.assertEqual(music.cues(SCR), [("sound/music/mus_tank.mp3", True), ("sound/music/mus_win.mp3", False)])

    def test_tables_and_convert(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = os.path.join(tmp, "main"), os.path.join(tmp, "out")
            os.makedirs(os.path.join(src, "sound", "music"))
            with zipfile.ZipFile(os.path.join(src, "pak0.pk3"), "w") as z:
                z.writestr("music/t1.mus", MUS)
                z.writestr("maps/t1.scr", SCR)
            # the music sits loose beside the paks, as a retail install has it
            with wave.open(os.path.join(src, "sound", "music", "sting.wav"), "wb") as w:
                w.setnchannels(2)
                w.setsampwidth(2)
                w.setframerate(44100)
                w.writeframes(bytes(4 * 4410))
            argv = [src, "--out", out]
            if shutil.which("ffmpeg"):
                argv.append("--convert")
            self.assertEqual(music.main(argv), 0)
            with open(os.path.join(out, "music", "t1.mood")) as fh:
                rows = [l.split() for l in fh if not l.startswith("#")]
            self.assertEqual(rows, [
                ["normal", "mohaa/music/calm_01.wav", "0.70", "1", "0.0"],
                ["aux1", "mohaa/music/fight.wav", "1.00", "0", "1.5"],
                ["aux2", "mohaa/music/sting.wav", "1.00", "0", "0.0"],
            ])
            if shutil.which("ffmpeg"):
                with wave.open(os.path.join(out, "sound", "mohaa", "music", "sting.wav")) as w:
                    self.assertEqual((w.getnchannels(), w.getsampwidth(), w.getframerate()), (1, 2, 22050))
                    self.assertAlmostEqual(w.getnframes(), 2205, delta=64)
                self.assertFalse(os.path.exists(os.path.join(out, "sound", "mohaa", "music", "calm_01.wav")))


if __name__ == "__main__":
    unittest.main()
