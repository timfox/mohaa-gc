"""Tests for tools/ubersound.py, on made-up aliases and scripts (no retail data)."""
import os
import subprocess
import sys
import tempfile
import unittest
import wave
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ubersound  # noqa: E402

UBER = """main:
local.master = spawn ScriptMaster
// a comment aliascache ignored ignored
local.master aliascache door_open1 sound/mechanics/Door_01.wav soundparms 0.8 0.2 1.0 0.1 160 1600 auto loaded maps "t1"
local.master aliascache door_open2 sound/mechanics/door_02.wav soundparms 0.7 0.2 1.0 0.1 200 1600 auto loaded maps "t1"
local.master aliascache alarm sound/alarm.wav soundparms 1.0 0.0 1.0 0.0 600 3000 item loaded maps "t1"
local.master alias unused sound/unused.wav
local.master aliascache door_open2 sound/mechanics/door_02.wav soundparms 0.7 0.2 1.0 0.1 200 1600 auto loaded maps "t2"
local.master aliascache door_open3 sound/null.wav soundparms 0.7 0.2 1.0 0.1 200 1600 auto loaded maps "t1"
end
"""

MAP = """main:
\t$door playsound door_open
\texec global/siren.scr
end
"""

SIREN = """main:
\tlocal.s loopsound "alarm"
\tself playsound nothing_like_this
end
"""


def stereo_wav(path, rate, frames):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        data = bytearray()
        for i in range(frames):
            data += (1000).to_bytes(2, "little", signed=True) + (3000).to_bytes(2, "little", signed=True)
        w.writeframes(bytes(data))


class UbersoundTest(unittest.TestCase):
    def test_parse(self):
        a = ubersound.parse_aliases(UBER)
        self.assertEqual(sorted(a), ["alarm", "door_open1", "door_open2", "door_open3", "unused"])
        self.assertEqual(a["door_open1"], [("sound/mechanics/Door_01.wav", 0.8, 160.0, "auto")])
        self.assertEqual(a["unused"], [("sound/unused.wav", 1.0, 160.0, "auto")])
        # numbered variants stand in for a missing exact alias; a path listed twice and null.wav are dropped
        self.assertEqual([p for p, *_ in ubersound.resolve(a, "door_open")],
                         ["sound/mechanics/Door_01.wav", "sound/mechanics/door_02.wav"])
        self.assertEqual(ubersound.resolve(a, "door"), [])
        self.assertEqual(ubersound.sample_name("sound/mechanics/Door_01.wav"), "mohaa/mechanics/door_01.wav")

    def test_map_table_and_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = os.path.join(tmp, "main"), os.path.join(tmp, "out")
            os.makedirs(src)
            wav = os.path.join(tmp, "door.wav")
            stereo_wav(wav, 44100, 441)
            with zipfile.ZipFile(os.path.join(src, "pak0.pk3"), "w") as z:
                z.writestr("ubersound/ubersound.scr", UBER)
                z.writestr("maps/t1.scr", MAP)
                z.writestr("global/siren.scr", SIREN)
                z.write(wav, "sound/mechanics/door_01.wav")
                z.write(wav, "sound/alarm.wav")
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "ubersound.py"), src, "--out", out,
                                "--wav"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("t1: 3 aliases, 3 samples, 2 scripts read, 1 unresolved: nothing_like_this", r.stdout)
            with open(os.path.join(out, "maps", "t1.snd")) as fh:
                rows = [l.split() for l in fh if not l.startswith("#")]
            self.assertEqual(rows, [
                ["alarm", "mohaa/alarm.wav", "1.00", "600", "item"],
                ["door_open", "mohaa/mechanics/door_01.wav", "0.80", "160", "auto"],
                ["door_open", "mohaa/mechanics/door_02.wav", "0.70", "200", "auto"],
            ])
            # two samples converted (the pak has them), one listed as missing
            self.assertIn("converted 2 samples, skipped 1", r.stdout)
            with open(os.path.join(out, "sound", "mohaa", "alarm.wav"), "rb") as fh:
                looped = fh.read()
            self.assertIn(b"cue ", looped)      # loopsound: GoldSrc repeats a wav with a cue point
            with open(os.path.join(out, "sound", "mohaa", "mechanics", "door_01.wav"), "rb") as fh:
                self.assertNotIn(b"cue ", fh.read())
            with wave.open(os.path.join(out, "sound", "mohaa", "mechanics", "door_01.wav")) as w:
                self.assertEqual((w.getnchannels(), w.getsampwidth(), w.getframerate()), (1, 2, 22050))
                self.assertEqual(w.getnframes(), 221)
                self.assertEqual(int.from_bytes(w.readframes(1), "little", signed=True), 2000)


    def test_ima_adpcm(self):
        # one mono block: header (predictor 0, index 0), then 4 bytes = 8 samples, low nibble first
        block = (0).to_bytes(2, "little", signed=True) + bytes([0, 0]) + bytes([0x77, 0x00, 0x08, 0x80])
        out = ubersound.decode_ima(block, 1, len(block))
        # 7: +step*(1/8+1/4+1/2+1) = +11 at step 7, index -> 8; 7 again at step 16 = +30
        self.assertEqual(out[:3], [0, 11, 41])
        self.assertEqual(len(out), 9)
        fmt = (0x11).to_bytes(2, "little") + (1).to_bytes(2, "little") + (11025).to_bytes(4, "little") + \
            (0).to_bytes(4, "little") + len(block).to_bytes(2, "little") + (4).to_bytes(2, "little")
        riff = b"WAVE" + b"fmt " + len(fmt).to_bytes(4, "little") + fmt + b"data" + len(block).to_bytes(4, "little") + block
        ch, rate, samples = ubersound.read_wav(b"RIFF" + len(riff).to_bytes(4, "little") + riff)
        self.assertEqual((ch, rate, samples), (1, 11025, out))


if __name__ == "__main__":
    unittest.main()
