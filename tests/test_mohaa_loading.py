"""Tests for tools/mohaa_loading.py on made-up loading screens (no retail data)."""
import io
import os
import struct
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

try:
    import numpy as np
    from PIL import Image
except ImportError:  # pragma: no cover
    np = Image = None

import mohaa_loading  # noqa: E402
import mohaa_menu  # noqa: E402
import mohaa_sd  # noqa: E402

BAR_TXT = """menu "" 640 480 NONE 1
resource
Label
{
name "loadingflasher"
rect 260 448 120 24
shader "loadingwidget"
}
resource
Button
{
name "continuebutton"
rect 272 448 96 24
shader "continue"
stuffcommand "finishloadingscreen"
}
resource
Label
{
name "loadingbar"
rect 194 456 252 8
linkcvar "loadingbar"
statbar horizontal 0 1
statbar_tileshader textures/mohmenu/loadingbar
}
resource
Label
{
name "loadingbar_border"
rect 192 452 256 16
shader "textures/mohmenu/loadingbar_border"
}
end.
"""

DEFAULT_URC = """menu "loading_default" 640 481 NONE 0
fullscreen 1
postinclude ui/loadingbar.txt
resource
Label
{
name "Default"
rect 0 0 512 512
shader "sepiaload_a"
}
resource
Label
{
name "Default"
rect 384 0 256 512
shader "sepiaload_b"
}
end.
"""

MAP_URC = """menu "m1l1" 640 481 NONE 0
postinclude ui/loadingbar.txt
resource
Label
{
name "Default"
rect 0 0 512 512
shader "m1l1_1"
}
resource
Label
{
rect 0 0 256 256
shader "textures/mohmenu/voodoo/m1l1_a.tga"
enabledcvar "ui_voodoo"
}
end.
"""

DM_URC = """menu "dm/mohdm1" 640 481 NONE 0
postinclude ui/loadingbar.txt
resource
Label
{
rect 0 0 640 480
shader "paper"
}
resource
Label
{
rect 0 0 640 480
shader "shadow"
}
resource
Label
{
rect 96 48 448 336
shader "mohdm1"
}
resource
Label
{
title "AB"
rect 72 408 496 32
fgcolor 1.00 1.00 1.00 1.00
font facfont-20
}
end.
"""

SHADER = """sepiaload_a
{
   {
      clampMap textures/mohmenu/sepiaload_a.tga
   }
}
sepiaload_b
{
   {
      clampMap textures/mohmenu/sepiaload_b.tga
   }
}
m1l1_1
{
   {
      clampMap textures/mohmenu/levelbriefing/m1l1_1.tga
   }
}
paper
{
   {
      clampMap textures/mohmenu/dmloading/paper.tga
   }
}
shadow
{
   {
      clampMap textures/mohmenu/dmloading/shadow.tga
	blendfunc filter
   }
}
mohdm1
{
   {
	map $whiteimage
   }
   {
     clampMap textures/mohmenu/dmloading/mohdm1.tga
	blendfunc gl_one_minus_src_alpha gl_src_alpha
   }
}
"""

FONT = "RitFont\nheight 16.0\naspect 2.0\nindirections {\n" + " ".join(
    "0" if c == 65 else "1" if c == 66 else "-1" for c in range(256)) + "\n}\nlocations {\n" \
    "{ 0.0 0.0 8.0 16.0 } { 8.0 0.0 8.0 16.0 }\n}\n"

RED, BLUE, GREEN, GREY = (200, 0, 0), (0, 0, 200), (0, 200, 0), (100, 100, 100)


def tga(size, color, alpha=None):
    mode = "RGBA" if alpha is not None else "RGB"
    im = Image.new(mode, size, color + ((alpha,) if alpha is not None else ()))
    b = io.BytesIO()
    im.save(b, format="TGA")
    return b.getvalue()


def make_pak(path, with_map=True):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("ui/loadingbar.txt", BAR_TXT)
        z.writestr("ui/loading_default.urc", DEFAULT_URC)
        if with_map:
            z.writestr("ui/loading_m1l1.urc", MAP_URC)
            z.writestr("ui/loading_mohdm1.urc", DM_URC)
        z.writestr("scripts/mohmenu.shader", SHADER)
        z.writestr("textures/mohmenu/sepiaload_a.tga", tga((512, 512), RED))
        z.writestr("textures/mohmenu/sepiaload_b.tga", tga((256, 512), BLUE))
        z.writestr("textures/mohmenu/levelbriefing/m1l1_1.tga", tga((512, 512), GREEN))
        z.writestr("textures/mohmenu/voodoo/m1l1_a.tga", tga((256, 256), (255, 255, 0)))
        z.writestr("textures/mohmenu/loadingwidget.tga", tga((256, 64), (255, 255, 255)))
        z.writestr("textures/mohmenu/loadingbar.tga", tga((256, 8), (220, 10, 10)))
        border = Image.new("RGBA", (256, 16), (0, 0, 0, 0))
        for x in range(256):
            border.putpixel((x, 0), (230, 230, 230, 255))
            border.putpixel((x, 15), (230, 230, 230, 255))
        b = io.BytesIO()
        border.save(b, format="TGA")
        z.writestr("textures/mohmenu/loadingbar_border.tga", b.getvalue())
        z.writestr("textures/mohmenu/dmloading/paper.tga", tga((64, 64), GREY))
        z.writestr("textures/mohmenu/dmloading/shadow.tga", tga((64, 64), (128, 128, 128)))
        z.writestr("textures/mohmenu/dmloading/mohdm1.tga", tga((64, 64), BLUE, alpha=0))
        glyphs = Image.new("RGBA", (16, 16), (255, 255, 255, 255))
        b = io.BytesIO()
        glyphs.save(b, format="TGA")
        z.writestr("gfx/fonts/facfont-20.tga", b.getvalue())
        z.writestr("fonts/facfont-20.ritualfont", FONT)


def near(px, color, tol=12):
    return max(abs(int(a) - b) for a, b in zip(px, color)) <= tol


@unittest.skipIf(np is None, "needs Pillow and numpy")
class LoadingTest(unittest.TestCase):
    def screens(self, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            make_pak(os.path.join(tmp, "pak0.pk3"), **kw)
            return {s[0]: s[1:] for s in mohaa_loading.screens([tmp])}

    def test_header_and_stages(self):
        self.assertEqual(mohaa_loading.parse_menu_header(DEFAULT_URC), ("loading_default", ["ui/loadingbar.txt"]))
        st = mohaa_loading.parse_shader_stages(SHADER)
        self.assertEqual(st["shadow"], [("textures/mohmenu/dmloading/shadow.tga", ("gl_dst_color", "gl_zero"))])
        self.assertEqual(st["mohdm1"][0], ("$whiteimage", None))
        self.assertEqual(mohaa_loading.plate_tiles((194, 456, 252, 8)), (24, 56, 32, 3))

    def test_default_screen(self):
        s = self.screens()
        self.assertEqual(sorted(s), ["default", "m1l1", "mohdm1"])
        rgb, bar, fill = s["default"]
        self.assertEqual(rgb.shape, (480, 640, 3))
        self.assertEqual(bar, (194, 456, 252, 8))
        self.assertTrue(near(rgb[10, 10], RED))        # sepiaload_a
        self.assertTrue(near(rgb[10, 600], BLUE))      # sepiaload_b past a's right edge
        self.assertTrue(near(rgb[452, 300], (230, 230, 230)))  # bar frame drawn
        self.assertTrue(near(rgb[460, 300], RED))      # empty bar: no fill, no flasher, no continue button
        self.assertEqual(fill.shape, (8, 256, 3))
        self.assertTrue(near(fill[4, 100], (220, 10, 10)))

    def test_map_and_dm_screens(self):
        s = self.screens()
        rgb = s["m1l1"][0]
        self.assertTrue(near(rgb[10, 10], GREEN))      # briefing, the voodoo tile skipped
        rgb = s["mohdm1"][0]
        self.assertTrue(near(rgb[10, 10], (50, 50, 50)))     # paper filtered by the shadow
        self.assertTrue(near(rgb[200, 300], BLUE))     # photo over its white stage: (1 - a) src + a dst, a = 0
        self.assertTrue(near(rgb[420, 312], (255, 255, 255)))  # title glyph, centred
        self.assertTrue(near(rgb[420, 100], (50, 50, 50)))

    def test_file_layout(self):
        s = self.screens()
        rgb, bar, fill = s["default"]
        data = mohaa_loading.encode_screen(rgb, bar, fill)
        self.assertEqual(data[:4], b"GCMP")
        self.assertEqual(struct.unpack(">HH", data[4:8]), (640, 488))
        self.assertEqual(struct.unpack(">HHHHBBBB", data[20:32]), (194, 456, 252, 8, 24, 56, 32, 3))
        self.assertEqual(len(data), 32 + 640 * 488 // 2)
        img = mohaa_menu.cmpr_decode(data[32:], 640, 488)
        self.assertTrue(near(img[10, 600], BLUE))
        self.assertTrue(near(img[484, 100], (220, 10, 10)))   # fill rides below the screen

    def test_sd_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            game, sd = os.path.join(tmp, "MOHAA"), os.path.join(tmp, "sd")
            os.makedirs(os.path.join(game, "main"))
            make_pak(os.path.join(game, "main", "pak0.pk3"))
            with redirect_stdout(io.StringIO()) as log:
                rc = mohaa_sd.main(["--mohaa", game, "--sd", sd, "--stages", "loading", "--maps", "m1l1"])
            self.assertEqual(rc, 0, log.getvalue())
            d = os.path.join(sd, "xash3d", "mohaa", "resource", "gc_loading")
            self.assertEqual(sorted(os.listdir(d)), ["default.cmp", "m1l1.cmp"])
            self.assertIn("== loading: 2 files", log.getvalue())


if __name__ == "__main__":
    unittest.main()
