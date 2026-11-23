#!/usr/bin/env python3
"""Bake the model tags and animation lengths MOHAA's scripted cutscenes read, for one or more maps.

    python3 tools/mohaa_tags.py "/path/to/MOHAA/main" --out <game root> --maps m1l1,m3l2

MOHAA plays its in-game cutscenes with the level running: m1l1's opening ride moves the truck, the
squad and the player's camera every frame from the tags of an animated path model
(vehicles/gmctruckpath_opening.tik: "tag_camera", "truck dummy", "Captain01 origin" ...), read with
gettagposition / gettagangles, and it waits for actors' animations with "waittill animdone". The
GameCube side has no skeletal animation, so this writes what those scripts ask for into
maps/<map>.tags:

* for every .tik the level's scripts name whose skeleton has a bone the scripts ask for by name,
  each animation's frames of those bones, in model space (the .tik's scale applied);
* the length in seconds of every animation name the scripts mention, so "waittill animdone"
  wakes when the animation would have ended.

Bone channels are relative to the parent bone and turn the way MOHAA's skeletor applies them (see
mohaa_skd._rotate). Human skeletons are left out: they are large and scripts only read a head tag
from them. Written from the file layout, not from any game or GPL source.

File layout (little-endian):
    "MTAG" u32 version (1)
    u32 durations; each: u8 len, name (lowercase), f32 seconds
    u32 models;    each: u8 len, model path (lowercase, relative to models/)
                         u8 tags; each: u8 len, tag name (lowercase)
                         u8 anims; each: u8 len, anim name (lowercase), f32 frame time, u16 frames,
                                         f32 position step; then frames x tags x
                                         (i16 position[3] in steps, i16 quaternion x y z w * 32767)
The quaternion turns tag axes into model axes (textbook q v q*); the tag's forward is its x axis.

Files over 16 KiB use a 20-byte MTGC manifest at maps/<map>.tags and 4 KiB pieces named
maps/<map>.tags.000, .001, ... . The GameCube runtime reassembles these original MTAG bytes
in its reserved map arena, loading only one small piece from the fragmented engine heap at a time.

The output is retail data: write it outside the repository and never commit it.
"""
from __future__ import annotations

import argparse
import math
import os
import re
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mohaa_skd as skd  # noqa: E402
from ubersound import collect, read  # noqa: E402

MAGIC = b"MTAG"
VERSION = 1
CHUNK_MAGIC = b"MTGC"
CHUNK_SIZE = 4096
CHUNK_THRESHOLD = 16 * 1024
MAX_TAG_FRAMES = 4096
SKIP_TREES = ("models/human/", "models/animal/")
TOKEN = re.compile(r'"([^"]*)"|([^\s(){}\[\]=+\-*/,;"]+)')


# ---------------------------------------------------------------- skeletons and animations

def skeleton(data: bytes, name: str = ""):
	"""[(bone name, parent name)] from an SKMD file, names as stored."""
	if len(data) < skd.HEADER.size:
		raise skd.SkdError(f"{name}: too short for an SKMD header")
	ident, _ver, _n, _ns, nb, ob, _os, _oe = skd.HEADER.unpack_from(data, 0)
	if ident != skd.SKD_IDENT or not 0 <= nb <= 512:
		raise skd.SkdError(f"{name}: not an SKMD file")
	bones, at = [], ob
	for _ in range(nb):
		if at + skd.BONE.size > len(data):
			raise skd.SkdError(f"{name}: bones run past the file")
		bname, parent, _t, _obd, _ocn, _obn, oen = skd.BONE.unpack_from(data, at)
		bones.append((skd._cstr(bname), skd._cstr(parent)))
		if oen <= 0:
			raise skd.SkdError(f"{name}: bad bone size")
		at += oen
	return bones


def anim_frames(data: bytes, name: str = ""):
	"""(frame time, [{bone (lowercase): (pos or None, quat or None)} per frame]) from an SKAN file."""
	if len(data) < skd.SKC_HEADER.size:
		raise skd.SkdError(f"{name}: too short for an SKAN header")
	h = skd.SKC_HEADER.unpack_from(data, 0)
	ident, frametime, nchan, ofs_names, nframes = h[0], h[4], h[9], h[10], h[11]
	if ident != skd.SKC_IDENT or nframes < 1 or not 0 < nchan <= 512 or ofs_names + 32 * nchan > len(data):
		raise skd.SkdError(f"{name}: not a readable SKAN file")
	chans = []
	for i in range(nchan):
		cname = skd._cstr(data[ofs_names + 32 * i:ofs_names + 32 * (i + 1)]).lower()
		bone, _, kind = cname.rpartition(" ")
		chans.append((bone, kind))
	frames = []
	for f in range(nframes):
		at = skd.SKC_HEADER.size + skd.SKC_FRAME.size * f
		if at + skd.SKC_FRAME.size > len(data):
			raise skd.SkdError(f"{name}: frame {f} runs past the file")
		oc = skd.SKC_FRAME.unpack_from(data, at)[-1]
		if oc <= 0 or oc + 16 * nchan > len(data):
			raise skd.SkdError(f"{name}: frame {f} channels run past the file")
		pose = {}
		for i, (bone, kind) in enumerate(chans):
			if kind not in ("pos", "rot"):
				continue
			vals = struct.unpack_from("<4f", data, oc + 16 * i)
			pos, q = pose.get(bone, (None, None))
			if kind == "pos":
				pos = vals[:3]
			else:
				q = vals
			pose[bone] = (pos, q)
		frames.append(pose)
	return frametime if frametime > 0 else 0.05, frames


def anim_length(data: bytes) -> float | None:
	"""Seconds an SKAN animation plays (frames x frame time), from its header only; None if unreadable."""
	if len(data) < skd.SKC_HEADER.size or data[:4] != skd.SKC_IDENT:
		return None
	h = skd.SKC_HEADER.unpack_from(data, 0)
	frametime, nframes = h[4], h[11]
	if nframes < 1 or not 0 < frametime < 10:
		return None
	return nframes * frametime


def _mat(q):
	"""3x3 rows of the turn _rotate(q, .) applies: columns are where x, y, z go."""
	cols = [skd._rotate(q, e) for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1))]
	return [[cols[c][r] for c in range(3)] for r in range(3)]


def _mul(a, b):
	return [[sum(a[r][k] * b[k][c] for k in range(3)) for c in range(3)] for r in range(3)]


def _apply(m, v):
	return tuple(sum(m[r][k] * v[k] for k in range(3)) for r in range(3))


def mat_to_quat(m):
	"""Textbook unit quaternion (x, y, z, w) of rotation matrix m (rows), w >= 0."""
	tr = m[0][0] + m[1][1] + m[2][2]
	if tr > 0:
		s = math.sqrt(tr + 1.0) * 2
		q = ((m[2][1] - m[1][2]) / s, (m[0][2] - m[2][0]) / s, (m[1][0] - m[0][1]) / s, 0.25 * s)
	elif m[0][0] > m[1][1] and m[0][0] > m[2][2]:
		s = math.sqrt(1.0 + m[0][0] - m[1][1] - m[2][2]) * 2
		q = (0.25 * s, (m[0][1] + m[1][0]) / s, (m[0][2] + m[2][0]) / s, (m[2][1] - m[1][2]) / s)
	elif m[1][1] > m[2][2]:
		s = math.sqrt(1.0 + m[1][1] - m[0][0] - m[2][2]) * 2
		q = ((m[0][1] + m[1][0]) / s, 0.25 * s, (m[1][2] + m[2][1]) / s, (m[0][2] - m[2][0]) / s)
	else:
		s = math.sqrt(1.0 + m[2][2] - m[0][0] - m[1][1]) * 2
		q = ((m[0][2] + m[2][0]) / s, (m[1][2] + m[2][1]) / s, 0.25 * s, (m[1][0] - m[0][1]) / s)
	n = math.sqrt(sum(c * c for c in q)) or 1.0
	q = tuple(c / n for c in q)
	return q if q[3] >= 0 else tuple(-c for c in q)


def angles_of(m):
	"""MOHAA angles (pitch yaw roll, degrees, pitch positive down) of an axis matrix (columns forward, left, up)."""
	f = (m[0][0], m[1][0], m[2][0])
	left_z, up_z = m[2][1], m[2][2]
	return (math.degrees(math.asin(max(-1.0, min(1.0, -f[2])))), math.degrees(math.atan2(f[1], f[0])),
	        math.degrees(math.atan2(left_z, up_z)))


def pose_tags(bones, pose, want, scale):
	"""{tag (lowercase): (model-space position, axis matrix)} for the bones in want, parents first."""
	world = {}
	ident = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

	def solve(name, depth=0):
		low = name.lower()
		if low in world:
			return world[low]
		parent = parents.get(low, "")
		pos, q = pose.get(low, (None, None))
		local_m = _mat(q) if q else ident
		local_p = pos or (0.0, 0.0, 0.0)
		if parent and parent.lower() != "worldbone" and parent.lower() in parents and depth < 64:
			pp, pm = solve(parent, depth + 1)
			res = (tuple(a + b for a, b in zip(pp, _apply(pm, local_p))), _mul(pm, local_m))
		else:
			res = (tuple(local_p), local_m)
		world[low] = res
		return res

	parents = {b.lower(): p for b, p in bones}
	out = {}
	for b, _ in bones:
		if b.lower() in want:
			p, m = solve(b)
			out[b.lower()] = (tuple(c * scale for c in p), m)
	return out


# ---------------------------------------------------------------- .tik animation lists

def tik_info(text: str, tik_path: str):
	"""(setup path, skelmodel, scale, [(alias, file)]) from a .tik; files resolved against the setup path."""
	tik = skd.parse_tik(text)
	toks = [a if a else b for a, b in re.findall(r'"([^"]*)"|([^\s"]+)', re.sub(r"//[^\n]*", "", text))]
	anims, i = [], 0
	base = tik.path or os.path.dirname(tik_path)
	while i < len(toks):
		if toks[i].lower() == "animations" and i + 1 < len(toks) and toks[i + 1] == "{":
			i += 2
			depth = 1
			while i < len(toks) and depth:
				t = toks[i]
				if t == "{":
					depth += 1
				elif t == "}":
					depth -= 1
				elif depth == 1 and t.lower() == "$path" and i + 1 < len(toks):
					base = skd.norm(toks[i + 1])  # later files in the block are under this folder
					i += 1
				elif depth == 1 and i + 1 < len(toks) and toks[i + 1] not in ("{", "}"):
					f = toks[i + 1]
					if f.lower().endswith((".skc", ".ska", ".tan")):
						anims.append((t.lower(), skd.norm(f if f.lower().startswith("models/") else f"{base}/{f}")))
						i += 1
				i += 1
			continue
		i += 1
	return tik, anims


# ---------------------------------------------------------------- what a level's scripts ask for

def script_words(texts):
	"""(lowercase words and quoted strings, .tik paths relative to models/) the scripts use."""
	words, tiks = set(), set()
	for text in texts:
		text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
		text = re.sub(r"//[^\n]*", "", text)
		for q, w in TOKEN.findall(text):
			t = (q if q else w).strip().lower()
			if not t:
				continue
			words.add(t)
			if t.endswith(".tik"):
				t = skd.norm(t)
				tiks.add(t[len("models/"):] if t.startswith("models/") else t)
	return words, tiks


def build(files, texts, log=print):
	"""The .tags bytes for scripts texts, reading models from files ({game path: entry})."""
	words, tiks = script_words(texts)
	durations, models, clash = {}, [], set()
	# animation lengths: every .tik's animation aliases the scripts mention. A name two .tiks give different
	# lengths ("idle", "stop") is left out: the game then waits a default time, rather than the wrong model's.
	for path in sorted(p for p in files if p.endswith(".tik")):
		try:
			_tik, anims = tik_info(read(files[path]).decode("latin-1"), path)
		except Exception:  # noqa: BLE001 - one bad .tik must not stop the bake
			continue
		for alias, f in anims:
			if alias in words and f in files:
				n = anim_length(read(files[f])[:skd.SKC_HEADER.size])
				if n is None:
					continue
				old = durations.get(alias)
				if old is not None and abs(old - n) > 0.1 * max(old, n):
					clash.add(alias)
				durations[alias] = max(old or 0.0, n)
	for alias in clash:
		del durations[alias]
	# tag tracks: models the scripts name, bones the scripts name
	for rel in sorted(tiks):
		key = "models/" + rel
		if key not in files or key.startswith(SKIP_TREES):
			continue
		try:
			tik, anims = tik_info(read(files[key]).decode("latin-1"), key)
			if tik.mesh not in files:
				continue
			bones = skeleton(read(files[tik.mesh]), tik.mesh)
		except skd.SkdError as err:
			log(f"  {rel}: {err}")
			continue
		want = [b.lower() for b, _ in bones if b.lower() in words]
		if not want or len(want) > 255:
			continue
		baked = []
		for alias, f in anims[:255]:
			# only what the scripts can play: an animation they name, or idle (a model's pose until told otherwise)
			if f not in files or (alias not in words and alias != "idle"):
				continue
			try:
				ft, frames = anim_frames(read(files[f]), f)
			except skd.SkdError as err:
				log(f"  {rel} {alias}: {err}")
				continue
			frames = frames[:MAX_TAG_FRAMES]
			baked.append((alias, ft, [pose_tags(bones, fr, set(want), tik.scale) for fr in frames]))
		if baked:
			models.append((rel, want, baked))
			log(f"  {rel}: tags {', '.join(want)}; {len(baked)} animations")
	return pack(durations, models)


def _name(s: str) -> bytes:
	b = s.lower().encode("latin-1")[:255]
	return struct.pack("<B", len(b)) + b


def pack(durations, models) -> bytes:
	out = bytearray(MAGIC + struct.pack("<I", VERSION))
	out += struct.pack("<I", len(durations))
	for name, secs in sorted(durations.items()):
		out += _name(name) + struct.pack("<f", secs)
	out += struct.pack("<I", len(models))
	for rel, tags, anims in models:
		out += _name(rel) + struct.pack("<B", len(tags))
		for t in tags:
			out += _name(t)
		out += struct.pack("<B", len(anims))
		for alias, ft, frames in anims:
			biggest = max([abs(c) for fr in frames for p, _ in fr.values() for c in p] + [1.0])
			step = biggest / 32000.0
			out += _name(alias) + struct.pack("<fHf", ft, len(frames), step)
			for fr in frames:
				for t in tags:
					p, m = fr.get(t, ((0.0, 0.0, 0.0), [[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
					q = mat_to_quat(m)
					out += struct.pack("<3h", *(int(round(c / step)) for c in p))
					out += struct.pack("<4h", *(int(round(max(-1.0, min(1.0, c)) * 32767)) for c in q))
	return bytes(out)


def write_tags(dst: str, data: bytes) -> int:
	"""Write one MTAG or an MTGC manifest plus 4 KiB pieces; return the piece count."""
	if len(data) <= CHUNK_THRESHOLD:
		with open(dst, "wb") as fh:
			fh.write(data)
		return 0
	count = (len(data) + CHUNK_SIZE - 1) // CHUNK_SIZE
	with open(dst, "wb") as fh:
		fh.write(CHUNK_MAGIC + struct.pack("<IIII", 1, len(data), CHUNK_SIZE, count))
	for i in range(count):
		with open(f"{dst}.{i:03d}", "wb") as fh:
			fh.write(data[i * CHUNK_SIZE:(i + 1) * CHUNK_SIZE])
	return count


def unpack(data: bytes):
	"""(durations, {model: (tags, {anim: (frame time, step, [[(pos, quat) per tag] per frame])})}), for tests."""
	if data[:4] != MAGIC:
		raise ValueError("not a .tags file")
	at = 8

	def name():
		nonlocal at
		n = data[at]
		s = data[at + 1:at + 1 + n].decode("latin-1")
		at += 1 + n
		return s

	(nd,) = struct.unpack_from("<I", data, at)
	at += 4
	durations = {}
	for _ in range(nd):
		k = name()
		durations[k] = struct.unpack_from("<f", data, at)[0]
		at += 4
	(nm,) = struct.unpack_from("<I", data, at)
	at += 4
	models = {}
	for _ in range(nm):
		rel = name()
		nt = data[at]
		at += 1
		tags = [name() for _ in range(nt)]
		na = data[at]
		at += 1
		anims = {}
		for _ in range(na):
			alias = name()
			ft, nf, step = struct.unpack_from("<fHf", data, at)
			at += 10
			frames = []
			for _ in range(nf):
				row = []
				for _ in tags:
					p = struct.unpack_from("<3h", data, at)
					q = struct.unpack_from("<4h", data, at + 6)
					at += 14
					row.append((tuple(c * step for c in p), tuple(c / 32767 for c in q)))
				frames.append(row)
			anims[alias] = (ft, step, frames)
		models[rel] = (tags, anims)
	return durations, models


def main(argv=None):
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument("inputs", nargs="+", help="MOHAA main directory, pk3 files or loose directories")
	ap.add_argument("--out", required=True, help="game root to write maps/<map>.tags into (outside the repository)")
	ap.add_argument("--maps", required=True, help="comma-separated map names")
	args = ap.parse_args(argv)
	import stage_scripts as ss
	files = collect(args.inputs, (".tik", ".skd", ".skc", ".scr"))
	scripts = {p: e for p, e in files.items() if p.endswith(".scr")}
	bad = 0
	for m in args.maps.split(","):
		need, _missing = ss.closure(scripts, m)
		if "maps/%s.scr" % m not in need:
			print("%s: no maps/%s.scr" % (m, m))
			bad += 1
			continue
		print(f"{m}:")
		data = build(files, [read(scripts[p]).decode("latin-1") for p in need])
		dst = os.path.join(args.out, "maps", m + ".tags")
		os.makedirs(os.path.dirname(dst), exist_ok=True)
		pieces = write_tags(dst, data)
		durations, models = unpack(data)
		storage = f"{pieces} x {CHUNK_SIZE}-byte chunks" if pieces else "single file"
		print(f"  wrote maps/{m}.tags: {len(data)} bytes, {len(durations)} animation lengths, {len(models)} models ({storage})")
	return 1 if bad else 0


if __name__ == "__main__":
	sys.exit(main())
