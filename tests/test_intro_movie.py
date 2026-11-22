"""Tests for tools/intro_movie.py on a made-up movie (ffmpeg test source, no retail data)."""
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import intro_movie  # noqa: E402

HAVE_FFMPEG = shutil.which("ffmpeg") is not None


def make_movie(path, seconds=2, size="256x128"):
    """A silent 2:1 RoQ movie plus its .mp3 soundtrack beside it, the way MOHAA ships intro.RoQ."""
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "lavfi", "-i", "testsrc=size=%s:rate=30:duration=%d" % (size, seconds),
         "-an", "-c:v", "roq", path], check=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=%d" % seconds,
         "-ac", "2", "-c:a", "libmp3lame", os.path.splitext(path)[0] + ".mp3"], check=True)


def decode_gcvid(path):
    """Replay a GCV2 stream the way avi_gc.c AVI_DecodeFrame does; return (header, frames)."""
    data = open(path, "rb").read()
    assert data[:4] == b"GCV2"
    w, h, fps_num, fps_den, count, flags = struct.unpack_from("<6I", data, 4)
    offsets = struct.unpack_from("<%dI" % count, data, 28)
    base = 28 + 4 * count
    tiles_x = w // 8
    frame = bytearray(w * h * 2)
    frames = []
    for off in offsets:
        p = base + off
        tag = data[p]
        if tag == 0:
            frame[:] = data[p + 1:p + 1 + len(frame)]
        else:
            assert tag == 1
            n = struct.unpack_from("<H", data, p + 1)[0]
            q = p + 3
            assert n <= tiles_x * (h // 8)
            for _ in range(n):
                idx = struct.unpack_from("<H", data, q)[0]
                tile = data[q + 2:q + 2 + 128]
                q += 130
                tx, ty = idx % tiles_x, idx // tiles_x
                for r in range(8):
                    d = ((ty * 8 + r) * w + tx * 8) * 2
                    frame[d:d + 16] = tile[r * 16:r * 16 + 16]
        frames.append(bytes(frame))
    return (w, h, fps_num, fps_den, count, flags), frames


@unittest.skipUnless(HAVE_FFMPEG, "needs ffmpeg")
class IntroMovieTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_find_intro_prefers_named_cinematic(self):
        main = os.path.join(self.tmp, "MOHAA", "main", "video")
        os.makedirs(main)
        for name, size in (("eaintro.roq", 5000), ("2015logo.roq", 4000), ("intro.roq", 100)):
            with open(os.path.join(main, name), "wb") as fh:
                fh.write(b"\0" * size)
        path, entry = intro_movie.find_intro([os.path.join(self.tmp, "MOHAA")])
        self.assertTrue(path.endswith("video/intro.roq"))
        self.assertEqual(os.path.basename(entry), "intro.roq")

    def test_find_intro_in_pk3_and_none(self):
        pk3 = os.path.join(self.tmp, "pak9.pk3")
        with zipfile.ZipFile(pk3, "w") as z:
            z.writestr("video/intro.roq", b"x")
        path, entry = intro_movie.find_intro([pk3])
        self.assertEqual(path, "video/intro.roq")
        self.assertIsInstance(entry, tuple)
        empty = os.path.join(self.tmp, "empty")
        os.makedirs(empty)
        self.assertIsNone(intro_movie.find_intro([empty]))

    def test_stage_writes_engine_streams(self):
        video = os.path.join(self.tmp, "install", "main", "video")
        os.makedirs(video)
        make_movie(os.path.join(video, "intro.RoQ"))
        make_movie(os.path.join(video, "EAlogo.RoQ"), seconds=1)
        sd = os.path.join(self.tmp, "sd")
        game_root = os.path.join(sd, "xash3d", "mohaa")
        written = intro_movie.convert_intro([os.path.join(self.tmp, "install")], game_root, log=lambda *_: None)
        media = os.path.join(sd, "xash3d", "mohaa", "media")
        self.assertEqual(written, [os.path.join(media, "mohaa_intro.gcvid"), os.path.join(media, "mohaa_intro.gcpcm")])

        (w, h, fps_num, fps_den, count, flags), frames = decode_gcvid(written[0])
        self.assertEqual((w, h, fps_num, fps_den, flags), (320, 160, 15, 1, 8))  # 2:1 kept
        self.assertTrue(28 <= count <= 32, count)  # 2 s at 15 fps

        # The decoded frames track the source within the lowest bit per channel.
        ref = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", os.path.join(video, "intro.RoQ"), "-an",
             "-vf", "fps=15,scale=320:160:flags=lanczos", "-pix_fmt", "rgb565le", "-f", "rawvideo", "-"],
            capture_output=True, check=True).stdout
        fs = w * h * 2
        for i in (0, count // 2, count - 1):
            src, got = ref[i * fs:(i + 1) * fs], frames[i]
            worst = 0
            for a, b in zip(struct.unpack("<%dH" % (fs // 2), src), struct.unpack("<%dH" % (fs // 2), got)):
                worst = max(worst, abs((a >> 11) - (b >> 11)), abs(((a >> 5) & 63) - ((b >> 5) & 63)), abs((a & 31) - (b & 31)))
            self.assertLessEqual(worst, 1, "frame %d" % i)

        pcm = open(written[1], "rb").read()
        self.assertEqual(pcm[:4], b"GCPA")
        rate, ch, width, n = struct.unpack_from("<IHHI", pcm, 4)
        self.assertEqual((rate, ch, width), (48000, 2, 2))
        self.assertEqual(len(pcm) - 16, n)
        self.assertAlmostEqual(n / (rate * ch * width), 2.0, delta=0.1)

    def test_converter_movie_stage(self):
        import io
        from contextlib import redirect_stdout
        import mohaa_sd
        game, sd = os.path.join(self.tmp, "MOHAA"), os.path.join(self.tmp, "sd")
        video = os.path.join(game, "main", "video")
        os.makedirs(video)
        with zipfile.ZipFile(os.path.join(game, "main", "pak0.pk3"), "w") as z:
            z.writestr("maps/t1.scr", "main:\nend\n")
        make_movie(os.path.join(video, "intro.RoQ"), seconds=1)
        self.assertEqual(mohaa_sd.CD_GROUPS["Video Files"], "video")
        out = io.StringIO()
        with redirect_stdout(out):
            rc = mohaa_sd.main(["--mohaa", game, "--sd", sd, "--gamedir", "mohaa", "--stages", "movie", "--list"])
        self.assertEqual(rc, 0, out.getvalue())
        self.assertIn("xash3d/mohaa/media/mohaa_intro.gcvid", out.getvalue())
        self.assertIn("xash3d/mohaa/media/mohaa_intro.gcpcm", out.getvalue())

    def test_exact_mode_is_lossless_and_static_frames_cost_nothing(self):
        src = os.path.join(self.tmp, "still.avi")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red:size=320x240:rate=15:duration=1",
                        "-c:v", "rawvideo", "-pix_fmt", "rgb565le", src], check=True)
        out = os.path.join(self.tmp, "still.gcvid")
        frames, keys, size = intro_movie.encode_gcvid(src, out, exact=True)
        self.assertEqual(keys, 1)
        # One keyframe, then 3-byte empty deltas.
        self.assertEqual(size, 28 + 4 * frames + 1 + 320 * 240 * 2 + 3 * (frames - 1))

    def test_no_intro_is_not_an_error(self):
        empty = os.path.join(self.tmp, "nothing")
        os.makedirs(empty)
        self.assertEqual(intro_movie.stage_intro([empty], os.path.join(self.tmp, "game"), [], self.tmp), [])
        self.assertEqual(intro_movie.main([empty, "--sd", os.path.join(self.tmp, "sd")]), 2)


if __name__ == "__main__":
    unittest.main()
