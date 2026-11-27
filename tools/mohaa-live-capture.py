#!/usr/bin/env python3
"""Capture periodic guest-window stills and optional silent Dolphin video."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import signal
import shutil
import subprocess
import time
from pathlib import Path


def sh(*args: str) -> subprocess.CompletedProcess[str]:
	return subprocess.run(args, capture_output=True, text=True)


def alive(pid: int) -> bool:
	try:
		os.kill(pid, 0)
		return True
	except OSError:
		return False


def find_window(runtime_dir: Path) -> str | None:
	tree = sh("xwininfo", "-root", "-tree").stdout
	for line in tree.splitlines():
		if not ('("dolphin-emu" "GameCube")' in line or '("xash-gc-dolphin" "GameCube")' in line):
			continue
		if "640x480" not in line and "854x480" not in line:
			continue
		parts = line.split()
		if not parts or not parts[0].startswith("0x"):
			continue
		pid_text = sh("xprop", "-id", parts[0], "_NET_WM_PID").stdout
		try:
			pid = int(pid_text.split("=", 1)[1].strip())
		except (IndexError, ValueError):
			continue
		args = sh("ps", "-p", str(pid), "-o", "args=").stdout
		if str(runtime_dir) in args:
			return parts[0]
	return None


def main() -> int:
	p = argparse.ArgumentParser(description=__doc__)
	p.add_argument("--probe-pid", type=int, required=True)
	p.add_argument("--runtime-dir", type=Path, required=True)
	p.add_argument("--shot-root", type=Path, required=True)
	p.add_argument("--video", type=Path)
	p.add_argument("--interval", type=float, default=8.0)
	p.add_argument("--route", required=True)
	p.add_argument("--repo", required=True)
	p.add_argument("--engine", required=True)
	p.add_argument("--iso", required=True)
	a = p.parse_args()

	shot_deadline = time.monotonic() + 15
	a.shot_dir = None
	while time.monotonic() < shot_deadline:
		matches = sorted(a.shot_root.glob(f"*-{a.route}"), key=lambda path: path.stat().st_mtime if path.is_dir() else 0)
		if matches:
			a.shot_dir = matches[-1]
			break
		time.sleep(0.25)
	if a.shot_dir is None:
		print("live capture: probe screenshot folder not found")
		return 0

	a.shot_dir.mkdir(parents=True, exist_ok=True)
	frames = a.shot_dir / "frames"
	frames.mkdir(exist_ok=True)
	deadline = time.monotonic() + 90
	win = None
	while alive(a.probe_pid) and time.monotonic() < deadline:
		win = find_window(a.runtime_dir)
		if win:
			break
		time.sleep(0.5)
	if not win:
		print("live capture: guest window not found; milestone captures remain available")
		return 0

	ff = None
	ff_log = None
	ff_log_handle = None
	if a.video and shutil.which("ffmpeg"):
		mkv = a.video.with_suffix(".mkv")
		ff_log = a.video.with_suffix(".ffmpeg.log")
		ff_log_handle = ff_log.open("w", encoding="utf-8")
		ff = subprocess.Popen(
			[
				"ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
				"-thread_queue_size", "512", "-f", "x11grab", "-draw_mouse", "0",
				"-framerate", "30", "-window_id", win, "-i", os.environ.get("DISPLAY", ":0"),
				"-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264",
				"-preset", "veryfast", "-crf", "27", "-pix_fmt", "yuv420p",
				"-movflags", "+faststart", str(mkv),
			],
			stdin=subprocess.DEVNULL,
			stdout=subprocess.DEVNULL,
			stderr=ff_log_handle,
		)

	start = time.monotonic()
	next_frame = start
	frame_num = 0
	while alive(a.probe_pid):
		now = time.monotonic()
		if now >= next_frame:
			frame_num += 1
			path = frames / f"frame-{frame_num:04d}-{int(now - start):04d}s.png"
			shot = sh("import", "-window", win, str(path))
			if shot.returncode != 0 or (path.is_file() and path.stat().st_size < 1024):
				path.unlink(missing_ok=True)
				frame_num -= 1
			next_frame += max(1.0, a.interval)
			time.sleep(0.1)
		else:
			time.sleep(min(0.5, next_frame - now))

	if ff and ff.poll() is None:
		ff.send_signal(signal.SIGINT)
		try:
			ff.wait(timeout=20)
		except subprocess.TimeoutExpired:
			ff.kill()
			ff.wait()
	if ff_log_handle:
		ff_log_handle.close()

	if a.video:
		mkv = a.video.with_suffix(".mkv")
		if mkv.is_file() and mkv.stat().st_size > 0:
			conv = sh("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mkv), "-c", "copy", "-movflags", "+faststart", str(a.video))
			if conv.returncode == 0 and a.video.is_file() and a.video.stat().st_size:
				mkv.unlink()
				probe = sh("ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name", "-of", "json", str(a.video))
				try:
					data = json.loads(probe.stdout)
				except ValueError:
					data = {}
				streams = [f"{s.get('codec_type')}:{s.get('codec_name')}" for s in data.get("streams", [])]
				stamp_text = a.shot_dir.name[:15]
				stamp = dt.datetime.strptime(stamp_text, "%Y%m%d-%H%M%S").isoformat(timespec="seconds")
				meta = {
					"file": a.video.name,
					"date": stamp,
					"commit": a.repo,
					"engine_commit": a.engine,
					"route": a.route,
					"disc": a.iso,
					"duration_s": round(float((data.get("format") or {}).get("duration") or 0), 1),
					"streams": streams,
					"size_mb": round(a.video.stat().st_size / 1e6, 1),
					"project": "mohaa-gc",
					"audio": "silent screen capture (forced or PulseAudio unavailable)",
				}
				a.video.with_suffix(".json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
		else:
			print("live capture: no video stream was written")
	print(f"live capture: saved {frame_num} periodic screenshots under {frames}")
	return 0
if __name__ == "__main__":
	raise SystemExit(main())
