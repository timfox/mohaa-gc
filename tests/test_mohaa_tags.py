#!/usr/bin/env python3
"""mohaa_tags: cutscene tag tracks and animation lengths, from synthetic models and scripts (no retail data)."""
from __future__ import annotations

import math
import os
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import mohaa_skd as skd  # noqa: E402
import mohaa_tags as tags  # noqa: E402


def build_skd(bones):
	"""SKMD with no surfaces: bones [(name, parent)]."""
	body = b""
	for name, parent in bones:
		body += skd.BONE.pack(name.encode(), parent.encode(), 1, 84, 96, 96, 96) + b"\0" * (96 - skd.BONE.size)
	ofs_bones = skd.HEADER.size
	return skd.HEADER.pack(b"SKMD", 5, b"path", 0, len(bones), ofs_bones, ofs_bones + len(body), ofs_bones + len(body)) + body


def build_skc(frames, frametime=0.5):
	"""SKAN: frames [{bone: (pos, quat)}], every frame the same bones in the same order."""
	chans = []
	for bone in frames[0]:
		chans += [bone + " pos", bone + " rot"]
	ofs_frames = skd.SKC_HEADER.size
	ofs_data = ofs_frames + skd.SKC_FRAME.size * len(frames)
	data, fr = b"", b""
	for i, f in enumerate(frames):
		fr += skd.SKC_FRAME.pack(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ofs_data + len(data))
		for bone in frames[0]:
			pos, q = f[bone]
			data += struct.pack("<4f", *pos, 0) + struct.pack("<4f", *q)
	ofs_names = ofs_data + len(data)
	names = b"".join(c.encode().ljust(32, b"\0") for c in chans)
	head = skd.SKC_HEADER.pack(b"SKAN", 13, 0, 0, frametime, 0, 0, 0, 0, len(chans), ofs_names, len(frames))
	return head + fr + data + names


IDENT = (0.0, 0.0, 0.0, 1.0)
# _rotate turns the inverse way: this quaternion turns x onto +y (a quarter turn left) in the skeletor's sense
QUARTER = (0.0, 0.0, -math.sqrt(0.5), math.sqrt(0.5))


class TagsTest(unittest.TestCase):
	def test_child_tags_follow_parent_and_scale(self):
		bones = [("Truck Dummy", "worldbone"), ("Seat Origin", "Truck Dummy"), ("crap", "Truck Dummy")]
		frames = [{"truck dummy": ((100, 0, 0), IDENT), "seat origin": ((10, 0, 0), IDENT), "crap": ((0, 0, 0), IDENT)},
		          {"truck dummy": ((100, 200, 0), QUARTER), "seat origin": ((10, 0, 0), IDENT), "crap": ((0, 0, 0), IDENT)}]
		posed = [tags.pose_tags(bones, f, {"truck dummy", "seat origin"}, 0.5) for f in
		         [{b: (p, q) for b, (p, q) in fr.items()} for fr in frames]]
		self.assertEqual(set(posed[0]), {"truck dummy", "seat origin"})
		p, m = posed[1]["seat origin"]
		# the seat sits 10 along the truck's x, which now points along +y: (100, 210) at half scale
		self.assertAlmostEqual(p[0], 50.0, places=4)
		self.assertAlmostEqual(p[1], 105.0, places=4)
		self.assertAlmostEqual(tags.angles_of(m)[1], 90.0, places=4)

	def test_bake_from_paks(self):
		bones = [("truck dummy", "worldbone"), ("tag_camera", "worldbone"), ("seat", "truck dummy")]
		idle = [{"truck dummy": ((0, 0, 0), IDENT), "tag_camera": ((0, 0, 50), IDENT), "seat": ((20, 0, 0), IDENT)},
		        {"truck dummy": ((0, 100, 0), QUARTER), "tag_camera": ((0, 100, 50), QUARTER), "seat": ((20, 0, 0), IDENT)}]
		with tempfile.TemporaryDirectory() as tmp:
			main, out = os.path.join(tmp, "main"), os.path.join(tmp, "out")
			os.makedirs(main)
			with zipfile.ZipFile(os.path.join(main, "pak0.pk3"), "w") as z:
				z.writestr("models/vehicles/path.tik",
				           "TIKI\nsetup\n{\n\tscale 0.5\n\tpath models/anim/level\n\tskelmodel path.skd\n}\n"
				           "animations\n{\n\tidle path_follow.skc\n\tunused path_unused.skc\n}\n")
				z.writestr("models/anim/level/path.skd", build_skd(bones))
				z.writestr("models/anim/level/path_follow.skc", build_skc(idle))
				z.writestr("models/anim/level/path_unused.skc", build_skc(idle))
				# an actor's animation set, listed under $path, and a name two models disagree on
				z.writestr("models/human/animation/scripted/opel.tik",
				           "animations\n{\n\t$path models/human/animation\n\tdriver_getvisa scripted/opel/getvisa.skc\n"
				           "\t{\n\t\tserver\n\t\t{\n\t\t\t0 sound x\n\t\t}\n\t}\n\tidle scripted/opel/getvisa.skc\n}\n")
				z.writestr("models/human/animation/scripted/opel/getvisa.skc", build_skc(idle * 5, frametime=0.25))
				z.writestr("maps/t1.scr",
				           'main:\n\tlevel.p = spawn script_model\n\tlevel.p model "vehicles/path.tik"\n'
				           '\tlocal.o = level.p gettagposition "tag_camera"\n\tlocal.a = level.p gettagangles "SEAT"\n'
				           '\tlevel.driver anim driver_getvisa\n\texec global/x.scr\nend\n')
				z.writestr("global/x.scr", "main:\n\tself anim idle\nend\n")
			self.assertEqual(tags.main([main, "--out", out, "--maps", "t1"]), 0)
			data = Path(out, "maps", "t1.tags").read_bytes()
			durations, models = tags.unpack(data)
			self.assertAlmostEqual(durations["driver_getvisa"], 2.5, places=5)  # 10 frames x 0.25 s
			self.assertNotIn("idle", durations)  # 1 s on the path, 2.5 s on the actor: left to the model
			self.assertEqual(list(models), ["vehicles/path.tik"])
			names, anims = models["vehicles/path.tik"]
			self.assertEqual(names, ["tag_camera", "seat"])  # "truck dummy" is in no script
			self.assertEqual(list(anims), ["idle"])  # "unused" is in no script
			ft, step, frames = anims["idle"]
			self.assertAlmostEqual(ft, 0.5)
			self.assertEqual(len(frames), 2)
			pos, q = frames[1][1]  # the seat on frame 1: (0 100 0) + 20 along +y, halved
			self.assertAlmostEqual(pos[0], 0.0, delta=step)
			self.assertAlmostEqual(pos[1], 60.0, delta=step)
			# textbook quaternion of a quarter turn left about z
			self.assertAlmostEqual(q[2], math.sqrt(0.5), delta=1e-4)
			self.assertAlmostEqual(q[3], math.sqrt(0.5), delta=1e-4)
			self.assertEqual(tags.main([main, "--out", out, "--maps", "nope"]), 1)

	def test_quaternion_round_trip(self):
		for q in [IDENT, QUARTER, (0.3, -0.5, 0.1, 0.8)]:
			n = math.sqrt(sum(c * c for c in q))
			q = tuple(c / n for c in q)
			m = tags._mat(q)
			x, y, z, w = tags.mat_to_quat(m)
			back = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
			        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
			        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
			for r in range(3):
				for c in range(3):
					self.assertAlmostEqual(back[r][c], m[r][c], places=6)


if __name__ == "__main__":
	unittest.main()
