#!/usr/bin/env python3
"""Convert a retail MOHAA weapon's frame-zero pose to a static GoldSrc studio MDL.

Example:
  python3 tools/mohaa_weapon.py retail/main --weapon m1_garand --out /tmp/v_m1_garand.mdl

This first pass preserves the retail mesh, UVs, primary diffuse texture and idle pose. For the M1
Garand it omits `material8`, which the retail TIKI marks nodraw at rest. GoldSrc animation and
weapon behavior are intentionally separate follow-up work; this writer currently requires one
diffuse texture per model.
"""
from __future__ import annotations

import argparse
import math
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mohaa_skd
from ubersound import collect, read


def _name(value: str, size: int) -> bytes:
	b = value.encode("latin-1", "replace")[: size - 1]
	return b + b"\0" * (size - len(b))


def _texture(data: bytes, max_size: int):
	from PIL import Image
	from io import BytesIO

	image = Image.open(BytesIO(data)).convert("RGB")
	width, height = image.size
	if width > max_size or height > max_size:
		scale = max_size / max(width, height)
		width = max(1, int(round(width * scale)))
		height = max(1, int(round(height * scale)))
	if image.size != (width, height):
		image = image.resize((width, height), Image.Resampling.LANCZOS)
	image = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
	palette = (image.getpalette() or [])[:768]
	palette += [0] * (768 - len(palette))
	return image.tobytes(), bytes(palette), width, height


def _static_mdl(name: str, positions, normals, triangles, pixels: bytes, palette: bytes,
				texture_width: int, texture_height: int) -> bytes:
	"""Write a one-bone, one-sequence, one-texture GoldSrc studio v10 model."""
	lo = tuple(min(p[i] for p in positions) for i in range(3))
	hi = tuple(max(p[i] for p in positions) for i in range(3))
	radius = max(math.sqrt(sum(x * x for x in p)) for p in positions)
	out = bytearray(244)

	def align(n=4):
		while len(out) % n:
			out.append(0)

	boneindex = len(out)
	ctl = [-1] * 6
	out += _name("root", 32) + struct.pack("<ii", -1, 0) + struct.pack("<6i", *ctl)
	out += struct.pack("<6f", 0, 0, 0, 0, 0, 0) + struct.pack("<6f", 1, 1, 1, 1, 1, 1)
	ctlindex = len(out)
	hbindex = len(out)
	out += struct.pack("<ii6f", 0, 0, *lo, *hi)
	sgindex = len(out)
	out += _name("default", 32) + _name("", 64) + struct.pack("<ii", 0, 0)
	animindex = len(out)
	out += b"\0" * 12
	seqindex = len(out)
	seq = _name("idle", 32) + struct.pack("<fiiiiiiiiii", 10.0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0)
	seq += struct.pack("<3f", 0, 0, 0) + struct.pack("<ii", 0, 0) + struct.pack("<6f", *lo, *hi)
	seq += struct.pack("<ii", 1, animindex) + struct.pack("<2i", 0, 0) + struct.pack("<2f", 0, 0) + struct.pack("<2f", 1, 1)
	seq += struct.pack("<iiiiii", 0, 0, 0, 0, 0, 0)
	if len(seq) != 176:
		raise ValueError(f"internal sequence layout is {len(seq)} bytes, expected 176")
	out += seq
	bpindex = len(out)
	out += _name("body", 64) + struct.pack("<iii", 1, 1, 0)
	modelindex = len(out)
	out += b"\0" * 112
	meshindex = len(out)
	out += b"\0" * 20
	align()
	triindex = len(out)
	for tri in triangles:
		out += struct.pack("<h", 3)
		for vi, ni, s, t in tri:
			out += struct.pack("<4h", vi, ni, s, t)
	out += struct.pack("<h", 0)
	align()
	vinfo = len(out)
	out += bytes(len(positions))
	align()
	ninfo = len(out)
	out += bytes(len(normals))
	align()
	vertindex = len(out)
	for p in positions:
		out += struct.pack("<3f", *p)
	normindex = len(out)
	for n in normals:
		out += struct.pack("<3f", *n)
	struct.pack_into("<5i", out, meshindex, len(triangles), triindex, 0, len(normals), normindex)
	struct.pack_into("<64sif10i", out, modelindex, _name(name, 64), 0, radius, 1, meshindex,
	                 len(positions), vinfo, vertindex, len(normals), ninfo, normindex, 0, 0)
	struct.pack_into("<i", out, bpindex + 72, modelindex)
	texindex = len(out)
	out += _name(name + ".bmp", 64) + struct.pack("<iiii", 0, texture_width, texture_height, 0)
	skinindex = len(out)
	out += struct.pack("<h", 0)
	align()
	texdata = len(out)
	struct.pack_into("<i", out, texindex + 76, texdata)
	out += pixels + palette
	align()
	hdr = struct.pack("<4si64si", b"IDST", 10, _name(name + ".mdl", 64), len(out))
	hdr += struct.pack("<3f", 0, 0, 0) + struct.pack("<3f", *lo) + struct.pack("<3f", *hi)
	hdr += struct.pack("<3f", *lo) + struct.pack("<3f", *hi) + struct.pack("<i", 0)
	hdr += struct.pack("<26i", 1, boneindex, 0, ctlindex, 1, hbindex, 1, seqindex, 1, sgindex,
	                    1, texindex, texdata, 1, 1, skinindex, 1, bpindex, 0, 0, 0, 0, 0, 0, 0, 0)
	if len(hdr) != 244:
		raise ValueError(f"internal header layout is {len(hdr)} bytes, expected 244")
	out[:244] = hdr
	return bytes(out)


def convert(main_paths, weapon: str, output: Path, skin_size: int = 256, scale: float | None = None):
	files = collect(main_paths, (".tik", ".skd", ".skc", ".shader", ".tga"))
	model = f"models/weapons/{weapon}.tik"
	if model not in files:
		raise ValueError(f"retail model not found: {model}")
	tik = mohaa_skd.parse_tik(read(files[model]).decode("latin-1"))
	if tik.mesh not in files:
		raise ValueError(f"retail mesh not found: {tik.mesh}")
	skd = mohaa_skd.parse_skd(read(files[tik.mesh]), tik.mesh)
	if tik.idle_anim and tik.idle_anim in files:
		mohaa_skd.apply_pose(skd, mohaa_skd.parse_skc(read(files[tik.idle_anim]), tik.idle_anim))
	shaders = {}
	for path, entry in files.items():
		if path.endswith(".shader"):
			shaders.update(mohaa_skd.parse_shaders(read(entry).decode("latin-1", "replace")))
	texture_path = None
	kept = []
	for surface in skd.surfaces:
		material = tik.shaders.get(surface.name.lower(), "").lower()
		if "nodraw" in material or (weapon.lower() == "m1_garand" and surface.name.lower() == "material8"):
			continue
		tex = mohaa_skd.surface_texture(tik, surface.name, shaders)
		if not tex:
			continue
		candidate = tex.lower().lstrip("/")
		if not Path(candidate).suffix:
			candidate += ".tga"
		if candidate not in files and Path(candidate).suffix == ".tga":
			candidate = candidate[:-4] + ".jpg"
		if candidate not in files:
			raise ValueError(f"diffuse texture not found for {surface.name}: {tex}")
		if texture_path is None:
			texture_path = candidate
		if candidate != texture_path:
			raise ValueError("this first-pass writer supports one diffuse texture; weapon surfaces use multiple textures")
		kept.append(surface)
	if not kept or not texture_path:
		raise ValueError("no textured surfaces remain after filtering")
	pixels, palette, texture_width, texture_height = _texture(read(files[texture_path]), skin_size)
	unit_scale = (tik.scale if scale is None else scale) * (72.0 / 94.0)
	positions, normals, triangles = [], [], []
	position_ids, normal_ids = {}, {}
	for surface in kept:
		for tri in surface.triangles:
			corners = []
			for index in tri:
				p = tuple(float(v) * unit_scale for v in surface.positions[index])
				n = tuple(float(v) for v in surface.normals[index])
				pkey = tuple(round(v, 5) for v in p)
				if pkey not in position_ids:
					position_ids[pkey] = len(positions)
					positions.append(p)
				nkey = tuple(round(v, 5) for v in n)
				if nkey not in normal_ids:
					normal_ids[nkey] = len(normals)
					normals.append(n)
				u, v = surface.uvs[index]
				s = min(texture_width - 1, max(0, int(round(u * (texture_width - 1)))))
				t = min(texture_height - 1, max(0, int(round((1.0 - v) * (texture_height - 1)))))
				corners.append((position_ids[pkey], normal_ids[nkey], s, t))
			triangles.append(corners)
	if len(positions) > 2048 or len(normals) > 2048 or len(triangles) > 4096:
		raise ValueError(f"mesh exceeds GoldSrc v10 limits: {len(positions)} verts, {len(normals)} normals, {len(triangles)} tris")
	data = _static_mdl(output.stem, positions, normals, triangles, pixels, palette,
					texture_width, texture_height)
	output.parent.mkdir(parents=True, exist_ok=True)
	output.write_bytes(data)
	return len(positions), len(normals), len(triangles), texture_path, unit_scale


def main(argv=None):
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("main", nargs="+", help="MOHAA main directory or .pk3 files")
	ap.add_argument("--weapon", default="m1_garand", help="weapon TIKI basename")
	ap.add_argument("--out", required=True, type=Path)
	ap.add_argument("--skin-size", type=int, default=256)
	ap.add_argument("--scale", type=float, default=None, help="override TIKI scale; map scale 72/94 is applied")
	a = ap.parse_args(argv)
	nv, nn, nt, tex, scale = convert(a.main, a.weapon, a.out, a.skin_size, a.scale)
	print(f"MOHAA weapon: {a.weapon}, {nt} triangles, {nv} verts, {nn} normals, scale {scale:.5f}")
	print(f"MOHAA texture: {tex}")
	print(f"GoldSrc studio v10: {a.out} ({a.out.stat().st_size} bytes)")
	return 0


if __name__ == "__main__":
	sys.exit(main())
