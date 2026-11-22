#!/usr/bin/env python3
"""Run a command and record it as progress media: a terminal-style screenshot (PNG) and a short replay video.

    python3 tools/capture_run.py --out /mnt/project-files/media/2026-11-22-vehicles --name dod_mohaa_test \
        --title "Script VM: vehicle drive tests" -- ./dm

The command's output (stdout and stderr together) is recorded with timings, then replayed in a headless browser
page that looks like a terminal: the video shows the lines arriving (sped up to at most --max-seconds), and the
screenshot shows the final screen. It writes <name>.log, <name>.png and <name>.mp4 (or .webm without ffmpeg).
The exit status is the command's own, so it can stand in for the command in a test script.
"""
import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
body{margin:0;background:#0d1117;color:#c9d1d9;font:15px/1.45 "DejaVu Sans Mono",monospace}
.bar{background:#161b22;padding:10px 16px;color:#8b949e;border-bottom:1px solid #30363d}
.bar b{color:#e6edf3}
pre{margin:0;padding:14px 16px;white-space:pre-wrap;word-break:break-all}
.cmd{color:#7ee787}.err{color:#ff7b72}.ok{color:#7ee787}.st{padding:0 16px 16px;color:#8b949e}
</style></head><body><div class="bar"><b>%TITLE%</b> &nbsp; %WHEN%</div>
<pre id="t"><span class="cmd">$ %CMD%</span>
</pre><div class="st" id="s"></div><script>
const lines=%LINES%, scale=%SCALE%, status=%STATUS%, t=document.getElementById('t');
function cls(s){return /PASSED| ok$|\d+ passed|: ok/.test(s)&&!/FAILED|\d+ failed/.test(s)?'ok':/fail|error|assert|abort/i.test(s)?'err':''}
let i=0;function next(){
  if(i>=lines.length){document.getElementById('s').textContent=status===0?'exit 0':'exit '+status;
    document.title='done';return}
  const [at,s]=lines[i++],e=document.createElement('span');e.className=cls(s);e.textContent=s+'\\n';t.appendChild(e);
  window.scrollTo(0,document.body.scrollHeight);
  const wait=i<lines.length?Math.min(400,(lines[i][0]-at)*scale*1000):0;setTimeout(next,Math.max(15,wait))}
setTimeout(next,600);
</script></body></html>"""


RECORD = r"""
const [page, png, dir, timeout] = process.argv.slice(1);
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const size = { width: 1280, height: 720 };
  const ctx = await b.newContext({ viewport: size, deviceScaleFactor: 2, recordVideo: { dir, size } });
  const pg = await ctx.newPage();
  await pg.goto('file://' + page);
  await pg.waitForFunction(() => document.title === 'done', null, { timeout: +timeout });
  await pg.waitForTimeout(1500);   // hold the last frame
  await pg.screenshot({ path: png, fullPage: true });
  const v = pg.video();
  await ctx.close();
  await v.saveAs(dir + '/video.webm');
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
"""


def run(cmd):
    lines, start = [], time.monotonic()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    for line in p.stdout:
        sys.stdout.write(line)
        lines.append([time.monotonic() - start, line.rstrip("\n")])
    return p.wait(), lines, time.monotonic() - start


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="directory for the media")
    ap.add_argument("--name", required=True, help="file name stem")
    ap.add_argument("--title", default="", help="heading shown above the output")
    ap.add_argument("--max-seconds", type=float, default=12.0, help="longest replay (default 12)")
    ap.add_argument("--keep-lines", type=int, default=400, help="replay only the last N lines (default 400)")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd[:1] == ["--"] else a.cmd
    if not cmd:
        ap.error("no command")
    os.makedirs(a.out, exist_ok=True)
    status, lines, took = run(cmd)
    stem = os.path.join(a.out, a.name)
    with open(stem + ".log", "w") as f:
        f.write("$ %s\n" % " ".join(cmd) + "\n".join(s for _, s in lines) + "\nexit %d\n" % status)
    shown = lines[-a.keep_lines:]
    span = (shown[-1][0] - shown[0][0]) if len(shown) > 1 else 0.0
    page = (PAGE.replace("%TITLE%", html.escape(a.title or a.name))
            .replace("%WHEN%", html.escape(time.strftime("%Y-%m-%d %H:%M") + " · %.1fs" % took))
            .replace("%CMD%", html.escape(" ".join(cmd)))
            .replace("%LINES%", json.dumps(shown))
            .replace("%SCALE%", repr(min(1.0, a.max_seconds / span) if span > 0 else 1.0))
            .replace("%STATUS%", str(status)))
    # the browser side runs in Node: the image ships Playwright for Node (require('playwright')), not for Python
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "page.html"), "w") as f:
            f.write(page)
        subprocess.run(["node", "-e", RECORD, os.path.join(tmp, "page.html"), stem + ".png", tmp,
                        str(int((a.max_seconds + 30) * 1000))], check=True)
        video = os.path.join(tmp, "video.webm")
        if shutil.which("ffmpeg"):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", stem + ".mp4"], check=True)
        else:
            shutil.copy(video, stem + ".webm")
    print("media: %s.png, %s.%s" % (stem, stem, "mp4" if shutil.which("ffmpeg") else "webm"), file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main())
