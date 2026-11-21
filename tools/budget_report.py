#!/usr/bin/env python3
"""Per-map budget report: will a MOHAA map fit GoldSrc BSP30 after conversion?

Reads MOHAA .bsp files (loose, inside .pk3 archives, or found under a
directory) and estimates what the planned MOHAA -> .map -> SDHLT -> BSP30
pipeline would produce, then compares that against GoldSrc limits.

The plan it models (see README.md):
  * world and brush-entity brushes become .map brushes, scaled by --scale
  * collidable curved patches get thin clip-brush proxies
  * terrain gets wedge-brush proxies, as coarse as --terrain-tol allows
  * patches, terrain and static models are drawn from a separate render bake,
    so they do not count against BSP30 face/leaf limits

Estimates, not compiler output. The clipnode figure in particular uses an
uncalibrated factor (--clipnodes-per-side); calibrate it against real SDHLT
runs before trusting the verdict on maps near a limit.

Usage:
  budget_report.py PATH [PATH ...] [--json out.json] [--csv out.csv]
  PATH = map .bsp, .pk3 archive, or a directory searched for both.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mohaa_bsp19 as b19  # noqa: E402

# MOHAA player is 94 units tall (OpenMoHAA bg_public.h MAXS_Z); GoldSrc
# standing hull is 72. Uniform scale so MOHAA doorways fit GoldSrc players.
DEFAULT_SCALE = 72.0 / 94.0

# Limits for SDHLT -> BSP30 -> xash3d-gc on GameCube (checked 2026-11-21):
#  * clipnodes: BSP30 stores clipnode children as signed 16-bit, so 32767 is a
#    format limit no matter what the engine allows (xash's 524288 is BSP2 only).
#  * world_coord: SDHLT's hlcsg defaults to a +-32768 extent (-worldextent) and
#    xash computes world size from the map, so stock HL's +-4096 does not apply.
#  * models: SDHLT MAX_MAP_MODELS 512 (xash allows 2048).
#  * edicts: xash3d-gc GC_SP_EDICT_CAP is 900 on GameCube, shared with players,
#    bots and projectiles. Path nodes and lights do not need edicts.
#  * brushes: SDHLT MAX_MAP_BRUSHES. textures/faces: generous, xash allows more.
# Override any of these with --limit name=value.
DEFAULT_LIMITS = {
	"clipnodes": 32767,
	"world_coord": 32768,
	"models": 512,
	"edicts_est": 900,
	"textures": 512,
	"faces_est": 65535,
	"brushes": 32768,
}

# MOHAA entities that never become GoldSrc edicts: AI path nodes turn into
# GOAP waypoints, lights are compile-time only (OpenMoHAA removes them on spawn).
NON_EDICT_CLASSES = {"info_pathnode", "info_grav_pathnode", "light", "worldspawn"}

TIGHT = 0.70  # fraction of a limit at which a value is flagged


def _scaled_bounds(model: b19.Model, scale: float):
	mins = [v * scale for v in model.mins]
	maxs = [v * scale for v in model.maxs]
	return mins, maxs


def classify_brush(contents: int) -> str:
	if contents & b19.CONTENTS_ORIGIN:
		return "origin"
	if contents & (b19.CONTENTS_AREAPORTAL | b19.CONTENTS_FOG) and not contents & b19.CONTENTS_SOLID:
		return "skip"
	if contents & b19.CONTENTS_TRIGGER:
		return "trigger"
	if contents & b19.CONTENTS_FLUID:
		return "water"
	if contents & (b19.CONTENTS_SOLID | b19.CONTENTS_FENCE):
		return "detail" if contents & b19.CONTENTS_DETAIL else "solid"
	if contents & (b19.CONTENTS_PLAYERCLIP | b19.CONTENTS_MONSTERCLIP):
		return "clip"
	if contents & b19.CONTENTS_LADDER:
		return "ladder"
	return "nonsolid"


# Brush classes that produce clipnodes in GoldSrc hulls 1-3.
COLLISION_CLASSES = {"solid", "detail", "clip", "trigger", "ladder"}
# Brush classes whose sides become drawn faces in hull 0.
DRAWN_CLASSES = {"solid", "detail", "water"}


def patch_proxy_brushes(surf: b19.Surface, proxy_subdiv: int) -> int:
	"""Thin clip brushes for one collidable patch: per 3x3 bezier piece,
	proxy_subdiv x proxy_subdiv quads, one slab brush each."""
	w, h = surf.patch_width, surf.patch_height
	if w < 3 or h < 3:
		return 0
	pieces = ((w - 1) // 2) * ((h - 1) // 2)
	return pieces * proxy_subdiv * proxy_subdiv


def terrain_cell_size(heights: list, tol_mohaa: float) -> int:
	"""Coarsest cell size (512/256/128/64) whose two-triangle-per-cell grid
	reproduces every height sample within tol_mohaa (MOHAA units)."""
	n = b19.TERRAIN_SAMPLES

	def h(i, j):
		return heights[j * n + i]

	for cell in (512, 256, 128, 64):
		step = cell // b19.TERRAIN_CELL
		worst = 0.0
		for j in range(n):
			for i in range(n):
				last = (n - 1) // step - 1  # index of the last coarse cell
				ci = min(i // step, last)
				cj = min(j // step, last)
				i0, j0 = ci * step, cj * step
				u = (i - i0) / step
				v = (j - j0) / step
				h00, h10 = h(i0, j0), h(i0 + step, j0)
				h01, h11 = h(i0, j0 + step), h(i0 + step, j0 + step)
				if u + v <= 1.0:
					est = h00 + u * (h10 - h00) + v * (h01 - h00)
				else:
					est = h11 + (1 - u) * (h01 - h11) + (1 - v) * (h10 - h11)
				worst = max(worst, abs(h(i, j) - est))
				if worst > tol_mohaa:
					break
			if worst > tol_mohaa:
				break
		if worst <= tol_mohaa:
			return cell
	return 64


def analyse(bsp: b19.Bsp, scale: float, terrain_tol: float, proxy_subdiv: int,
            clipnodes_per_side: float, limits: dict) -> dict:
	shaders = bsp.shaders

	def shader(i):
		return shaders[i] if 0 <= i < len(shaders) else b19.Shader("", 0, 0, 0)

	# --- brushes, split into world vs brush entities via the model table
	world = bsp.models[0] if bsp.models else None
	world_range = range(world.first_brush, world.first_brush + world.num_brushes) if world else range(0)
	brush_classes = Counter()
	collision_sides = 0
	drawn_faces = 0
	used_textures = set()
	for br in bsp.brushes:
		cls = classify_brush(shader(br.shader).content_flags)
		brush_classes[cls] += 1
		if cls in COLLISION_CLASSES:
			collision_sides += br.num_sides
		if cls in DRAWN_CLASSES:
			for si in range(br.first_side, br.first_side + br.num_sides):
				if si >= len(bsp.brushsides_shader):
					break
				sh = shader(bsp.brushsides_shader[si])
				if sh.surface_flags & b19.SURF_NODRAW or "caulk" in sh.name.lower():
					continue
				drawn_faces += 1
				used_textures.add(sh.name.lower())
	world_brushes = len(world_range)
	gs_brushes = sum(n for c, n in brush_classes.items() if c not in ("origin", "skip", "nonsolid"))

	# --- surfaces
	surf_types = Counter(b19.SURFACE_TYPE_NAMES.get(s.surface_type, "?") for s in bsp.surfaces)
	patch_solid = 0
	patch_proxies = 0
	patch_render_tris = 0
	for s in bsp.surfaces:
		if s.surface_type != b19.MST_PATCH:
			continue
		sh = shader(s.shader)
		used_textures.add(sh.name.lower())
		pieces = max(0, ((s.patch_width - 1) // 2) * ((s.patch_height - 1) // 2))
		patch_render_tris += pieces * 8 * 8 * 2  # 8x8 tessellation per piece for the render bake
		collides = sh.content_flags & (b19.CONTENTS_SOLID | b19.CONTENTS_ANYCLIP) and not sh.surface_flags & b19.SURF_NONSOLID
		if collides:
			patch_solid += 1
			patch_proxies += patch_proxy_brushes(s, proxy_subdiv)

	# --- terrain
	tol_mohaa = terrain_tol / scale if scale > 0 else terrain_tol
	cell_hist = Counter()
	terrain_proxies = 0
	for tp in bsp.terrain:
		used_textures.add(shader(tp.shader).name.lower())
		cell = terrain_cell_size(tp.heights, tol_mohaa)
		cell_hist[cell] += 1
		terrain_proxies += 2 * (b19.TERRAIN_PATCH_SIZE // cell) ** 2
	terrain_render_tris = len(bsp.terrain) * 8 * 8 * 2

	# --- static models
	static_unique = Counter(sm.model.lower() for sm in bsp.static_models)

	# --- entities
	classnames = Counter(e.get("classname", "?") for e in bsp.entities)

	# --- bounds
	bounds = None
	max_coord = 0.0
	if world:
		mins, maxs = _scaled_bounds(world, scale)
		# Union with terrain extents in case the world model bounds leave them out.
		for tp in bsp.terrain:
			x0, y0 = tp.origin
			lo = (x0 * scale, y0 * scale, min(tp.heights) * scale)
			hi = ((x0 + b19.TERRAIN_PATCH_SIZE) * scale, (y0 + b19.TERRAIN_PATCH_SIZE) * scale, max(tp.heights) * scale)
			mins = [min(mins[i], lo[i]) for i in range(3)]
			maxs = [max(maxs[i], hi[i]) for i in range(3)]
		bounds = {"mins": [round(v) for v in mins], "maxs": [round(v) for v in maxs],
		          "size": [round(maxs[i] - mins[i]) for i in range(3)]}
		max_coord = max(abs(v) for v in mins + maxs)

	clip_brush = round(collision_sides * clipnodes_per_side)
	clip_patch = round(patch_proxies * 6 * clipnodes_per_side)
	clip_terrain = round(terrain_proxies * 5 * clipnodes_per_side)
	clipnodes_est = clip_brush + clip_patch + clip_terrain
	pathnodes = sum(n for c, n in classnames.items() if c.lower() in ("info_pathnode", "info_grav_pathnode"))
	edicts_est = sum(n for c, n in classnames.items() if c.lower() not in NON_EDICT_CLASSES)

	estimates = {
		"clipnodes": clipnodes_est,
		"world_coord": round(max_coord),
		"models": len(bsp.models),
		"edicts_est": edicts_est,
		"textures": len(used_textures - {""}),
		"faces_est": drawn_faces,
		"brushes": gs_brushes + patch_proxies + terrain_proxies,
	}
	checks = {}
	worst = "OK"
	order = {"OK": 0, "TIGHT": 1, "OVER": 2}
	for key, value in estimates.items():
		lim = limits.get(key)
		if not lim:
			continue
		frac = value / lim
		status = "OVER" if frac > 1.0 else "TIGHT" if frac >= TIGHT else "OK"
		checks[key] = {"value": value, "limit": lim, "pct": round(frac * 100, 1), "status": status}
		if order[status] > order[worst]:
			worst = status

	return {
		"map": bsp.name,
		"version": bsp.version,
		"file_bytes": bsp.file_size,
		"verdict": worst,
		"scale": round(scale, 4),
		"bounds_scaled": bounds,
		"counts": {
			"shaders": len(shaders),
			"planes": bsp.num_planes,
			"brushes": len(bsp.brushes),
			"world_brushes": world_brushes,
			"brush_classes": dict(brush_classes),
			"surfaces": dict(surf_types),
			"patches_collidable": patch_solid,
			"terrain_patches": len(bsp.terrain),
			"terrain_cell_sizes": {str(k): v for k, v in sorted(cell_hist.items(), reverse=True)},
			"static_models": len(bsp.static_models),
			"static_models_unique": len(static_unique),
			"entities": len(bsp.entities),
			"pathnodes": pathnodes,
			"brush_models": max(0, len(bsp.models) - 1),
			"leafs": bsp.num_leafs,
			"lightmaps": bsp.num_lightmaps,
			"drawverts": bsp.num_drawverts,
		},
		"clipnodes_by_source": {"brushes": clip_brush, "patch_proxies": clip_patch, "terrain_proxies": clip_terrain},
		"proxies": {
			"patch_clip_brushes": patch_proxies,
			"terrain_wedge_brushes": terrain_proxies,
		},
		"render_bake": {
			"patch_tris": patch_render_tris,
			"terrain_tris": terrain_render_tris,
			"static_model_instances": len(bsp.static_models),
		},
		"checks": checks,
		"top_classnames": classnames.most_common(12),
		"top_static_models": static_unique.most_common(8),
	}


def iter_maps(paths):
	"""Yield (display_name, bytes) for every MOHAA .bsp under the given paths.
	For .pk3 archives, later archives (sorted by name) override earlier ones,
	matching how the game layers paks."""
	loose = []
	paks = []
	for p in map(Path, paths):
		if p.is_dir():
			loose += sorted(p.rglob("*.bsp"))
			paks += sorted(p.rglob("*.pk3"))
		elif p.suffix.lower() == ".pk3":
			paks.append(p)
		else:
			loose.append(p)
	for p in loose:
		yield str(p), p.read_bytes()
	merged = {}
	for pak in sorted(paks, key=lambda x: x.name.lower()):
		with zipfile.ZipFile(pak) as z:
			for info in z.infolist():
				n = info.filename
				if n.lower().startswith("maps/") and n.lower().endswith(".bsp"):
					merged[n.lower()] = (pak, n)
	for key in sorted(merged):
		pak, n = merged[key]
		with zipfile.ZipFile(pak) as z:
			yield f"{pak.name}:{n}", z.read(n)


def format_text(r: dict) -> str:
	c = r["counts"]
	out = [f"== {r['map']}  (v{r['version']}, {r['file_bytes'] / 1048576:.2f} MiB)  verdict: {r['verdict']}"]
	if r["bounds_scaled"]:
		b = r["bounds_scaled"]
		out.append(f"   bounds at x{r['scale']}: size {b['size']}  mins {b['mins']}  maxs {b['maxs']}")
	out.append(
		f"   brushes {c['brushes']} {c['brush_classes']}  surfaces {c['surfaces']}")
	out.append(
		f"   patches collidable {c['patches_collidable']}  terrain patches {c['terrain_patches']} "
		f"cells {c['terrain_cell_sizes']}  static models {c['static_models']} ({c['static_models_unique']} unique)")
	out.append(
		f"   proxies: patch clip {r['proxies']['patch_clip_brushes']}  terrain wedges {r['proxies']['terrain_wedge_brushes']}")
	cb = r["clipnodes_by_source"]
	out.append(
		f"   clipnodes est by source: brushes {cb['brushes']}  patches {cb['patch_proxies']}  terrain {cb['terrain_proxies']}"
		f"   entities {c['entities']} (path nodes {c['pathnodes']})")
	for k, v in r["checks"].items():
		out.append(f"   {v['status']:<5} {k:<18} {v['value']:>9} / {v['limit']:<9} ({v['pct']}%)")
	return "\n".join(out)


CSV_FIELDS = ["map", "verdict", "file_bytes", "brushes", "patches_collidable", "terrain_patches",
              "static_models", "entities", "pathnodes", "clip_brushes", "clip_patches", "clip_terrain"]


def main(argv=None) -> int:
	ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
	ap.add_argument("paths", nargs="+")
	ap.add_argument("--scale", type=float, default=DEFAULT_SCALE,
	                help=f"uniform MOHAA->GoldSrc scale (default {DEFAULT_SCALE:.4f} = 72/94)")
	ap.add_argument("--terrain-tol", type=float, default=8.0,
	                help="max terrain height error for collision proxies, GoldSrc units (default 8)")
	ap.add_argument("--patch-subdiv", type=int, default=2,
	                help="clip-proxy quads per bezier piece edge (default 2)")
	ap.add_argument("--clipnodes-per-side", type=float, default=0.5,
	                help="clipnodes (hulls 1-3 total) per collision brush side; UNCALIBRATED (default 0.5)")
	ap.add_argument("--limit", action="append", default=[], metavar="NAME=VALUE",
	                help=f"override a limit; names: {', '.join(DEFAULT_LIMITS)}")
	ap.add_argument("--json", type=Path, help="write all results as JSON")
	ap.add_argument("--csv", type=Path, help="write a one-row-per-map summary CSV")
	ap.add_argument("--quiet", action="store_true", help="only the one-line-per-map summary")
	args = ap.parse_args(argv)

	limits = dict(DEFAULT_LIMITS)
	for item in args.limit:
		k, _, v = item.partition("=")
		if k not in limits:
			ap.error(f"unknown limit {k!r}")
		limits[k] = int(float(v))

	results, failures = [], []
	for name, data in iter_maps(args.paths):
		try:
			bsp = b19.load_bytes(data, name)
		except b19.BspError as e:
			failures.append(str(e))
			continue
		r = analyse(bsp, args.scale, args.terrain_tol, args.patch_subdiv, args.clipnodes_per_side, limits)
		results.append(r)
		if args.quiet:
			over = [k for k, v in r["checks"].items() if v["status"] != "OK"]
			print(f"{r['verdict']:<5} {name}  {' '.join(over)}")
		else:
			print(format_text(r))
			print()

	if results:
		tally = Counter(r["verdict"] for r in results)
		print(f"{len(results)} maps: " + ", ".join(f"{tally[k]} {k}" for k in ("OK", "TIGHT", "OVER")))
	for f in failures:
		print(f"skipped: {f}", file=sys.stderr)

	if args.json:
		args.json.write_text(json.dumps({"limits": limits, "maps": results}, indent=1))
	if args.csv:
		check_keys = list(limits)
		with args.csv.open("w", newline="") as fh:
			w = csv.writer(fh)
			w.writerow(CSV_FIELDS + [f"{k}_pct" for k in check_keys])
			for r in results:
				c = r["counts"]
				row = [r["map"], r["verdict"], r["file_bytes"], c["brushes"], c["patches_collidable"],
				       c["terrain_patches"], c["static_models"], c["entities"], c["pathnodes"]]
				cb = r["clipnodes_by_source"]
				row += [cb["brushes"], cb["patch_proxies"], cb["terrain_proxies"]]
				row += [r["checks"].get(k, {}).get("pct", "") for k in check_keys]
				w.writerow(row)
	return 0 if results or not failures else 1


if __name__ == "__main__":
	sys.exit(main())
