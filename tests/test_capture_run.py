"""tools/capture_run.py records a command as a PNG and a video, and passes its exit status through."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def have_browser():
    if not shutil.which("node"):
        return False
    return subprocess.run(["node", "-e", "require('playwright')"], capture_output=True).returncode == 0


@unittest.skipUnless(have_browser(), "needs Node with Playwright")
class CaptureRunTest(unittest.TestCase):
    def test_records_media_and_keeps_status(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run([sys.executable, str(ROOT / "tools/capture_run.py"), "--out", out, "--name", "t",
                                "--max-seconds", "1", "--", sys.executable, "-c",
                                "print('step one ok'); print('it failed'); raise SystemExit(3)"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 3, r.stderr)
            self.assertIn("step one ok", r.stdout)
            self.assertIn("it failed", Path(out, "t.log").read_text())
            self.assertGreater(os.path.getsize(Path(out, "t.png")), 1000)
            video = Path(out, "t.mp4") if shutil.which("ffmpeg") else Path(out, "t.webm")
            self.assertGreater(os.path.getsize(video), 1000)


if __name__ == "__main__":
    unittest.main()
