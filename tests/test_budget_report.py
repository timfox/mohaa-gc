#!/usr/bin/env python3
"""python3 -m unittest discover -s tests"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

import budget_report as br  # noqa: E402
import make_sample_bsp  # noqa: E402
import mohaa_bsp19 as b19  # noqa: E402


class ReaderTest(unittest.TestCase):
	def test_v19_counts(self):
		bsp = b19.load_bytes(make_sample_bsp.build(19), "sample")
		self.assertEqual(bsp.version, 19)
		self.assertEqual(len(bsp.shaders), 7)
		self.assertEqual(len(bsp.brushes), 5)
		self.assertEqual(len(bsp.models), 2)
		self.assertEqual(bsp.models[0].num_brushes, 4)
		self.assertEqual(len(bsp.terrain), 3)
		self.assertEqual(len(bsp.static_models), 2)
		self.assertEqual(bsp.static_models[0].model, "static/barrel.tik")
		self.assertEqual(bsp.num_lightmaps, 2)
		self.assertEqual(bsp.num_leafs, 3)
		self.assertEqual([e["classname"] for e in bsp.entities],
		                 ["worldspawn", "info_player_allied", "func_door", "actor",
		                  "info_pathnode", "info_pathnode", "light"])
		self.assertEqual(bsp.terrain[1].heights[8], 2 * 32)  # base 0 + 2 * (8 * 4)

	def test_v17_lump_shift(self):
		bsp = b19.load_bytes(make_sample_bsp.build(17), "beta")
		self.assertEqual(len(bsp.models), 2)
		self.assertEqual(len(bsp.terrain), 3)
		self.assertEqual(len(bsp.entities), 7)
		self.assertEqual(bsp.static_models, [])

	def test_rejects_other_formats(self):
		with self.assertRaises(b19.BspError):
			b19.load_bytes(b"IBSP" + bytes(400), "q3")
		data = bytearray(make_sample_bsp.build(19))
		data[4] = 30
		with self.assertRaises(b19.BspError):
			b19.load_bytes(bytes(data), "v30")


class TerrainTest(unittest.TestCase):
	def test_cell_sizes(self):
		flat = [0] * 81
		slope = [i * 8 for j in range(9) for i in range(9)]
		self.assertEqual(br.terrain_cell_size(flat, 8), 512)
		self.assertEqual(br.terrain_cell_size(slope, 8), 512)
		bump = [0] * 81
		bump[4 * 9 + 4] = 100  # one spike in the middle
		self.assertEqual(br.terrain_cell_size(bump, 8), 64)
		ridge = [0 if i <= 4 else (i - 4) * 32 for j in range(9) for i in range(9)]
		self.assertEqual(br.terrain_cell_size(ridge, 8), 256)


class ReportTest(unittest.TestCase):
	def analyse(self, **kw):
		bsp = b19.load_bytes(make_sample_bsp.build(19), "sample")
		args = dict(scale=br.DEFAULT_SCALE, terrain_tol=8.0, proxy_subdiv=2,
		            clipnodes_per_side=0.5, limits=dict(br.DEFAULT_LIMITS))
		args.update(kw)
		return br.analyse(bsp, **args)

	def test_classification_and_proxies(self):
		r = self.analyse()
		self.assertEqual(r["counts"]["brush_classes"], {"solid": 3, "clip": 1, "water": 1})
		self.assertEqual(r["counts"]["patches_collidable"], 1)
		self.assertEqual(r["proxies"]["patch_clip_brushes"], 2 * 4)  # 2 pieces x 2x2
		cells = r["counts"]["terrain_cell_sizes"]
		self.assertEqual(cells.get("512"), 2)
		self.assertEqual(r["proxies"]["terrain_wedge_brushes"],
		                 2 * 2 + sum(2 * (512 // int(c)) ** 2 * n for c, n in cells.items() if c != "512"))
		# floor top + 6 crate faces + 6 door faces + 6 water faces; caulk skipped
		self.assertEqual(r["checks"]["faces_est"]["value"], 1 + 6 + 6 + 6)
		self.assertEqual(r["verdict"], "OK")

	def test_edicts_skip_pathnodes_and_lights(self):
		r = self.analyse()
		self.assertEqual(r["counts"]["pathnodes"], 2)
		self.assertEqual(r["checks"]["edicts_est"]["value"], 3)  # player start, door, actor
		cb = r["clipnodes_by_source"]
		self.assertEqual(cb["brushes"] + cb["patch_proxies"] + cb["terrain_proxies"], r["checks"]["clipnodes"]["value"])
		self.assertEqual(cb["terrain_proxies"], round(r["proxies"]["terrain_wedge_brushes"] * 5 * 0.5))

	def test_bounds_scaled(self):
		r = self.analyse(scale=0.5)
		self.assertEqual(r["bounds_scaled"]["size"], [1024, 1024, 160])
		self.assertEqual(r["checks"]["world_coord"]["value"], 512)

	def test_limit_breach_flags_over(self):
		limits = dict(br.DEFAULT_LIMITS, world_coord=600)
		r = self.analyse(limits=limits)
		self.assertEqual(r["checks"]["world_coord"]["status"], "OVER")
		self.assertEqual(r["verdict"], "OVER")

	def test_cli_pk3_json_csv(self):
		with tempfile.TemporaryDirectory() as td:
			td = Path(td)
			(td / "loose.bsp").write_bytes(make_sample_bsp.build(19))
			with zipfile.ZipFile(td / "pak0.pk3", "w") as z:
				z.writestr("maps/m1l1.bsp", make_sample_bsp.build(19))
				z.writestr("maps/readme.txt", "x")
			with zipfile.ZipFile(td / "pak1.pk3", "w") as z:
				z.writestr("maps/m1l1.bsp", make_sample_bsp.build(18))  # overrides pak0
			buf = io.StringIO()
			with redirect_stdout(buf):
				rc = br.main([str(td), "--json", str(td / "out.json"), "--csv", str(td / "out.csv"), "--quiet"])
			self.assertEqual(rc, 0)
			data = json.loads((td / "out.json").read_text())
			names = sorted(m["map"] for m in data["maps"])
			self.assertEqual(len(names), 2)
			self.assertTrue(any(n.endswith("pak1.pk3:maps/m1l1.bsp") for n in names))
			self.assertIn("2 maps:", buf.getvalue())
			self.assertEqual(len((td / "out.csv").read_text().strip().splitlines()), 3)


if __name__ == "__main__":
	unittest.main()
