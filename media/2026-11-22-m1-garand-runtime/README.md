# MOHAA M1 Garand runtime capture

Latest Dolphin capture, recorded Nov. 22 at 3:05 PM PT:

![MOHAA m1l2a with the converted Garand viewmodel](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1-garand-runtime/screenshots/20261122-150547-mohaa-garand-aspect-ratio/final.png)

- [Latest Dolphin log](screenshots/20261122-150547-mohaa-garand-aspect-ratio/dolphin.log)
- [Latest probe note](notes/20261122-150547-mohaa-garand-aspect-ratio.md)

The converter now preserves the retail atlas's 2:1 aspect ratio. The runtime log confirms that the
86,968-byte model was read through `gc_studio/v_garand.mdl` as a 256x128 skin, and m1l2a reached the
world-render-ready state at about 45 FPS in Dolphin. The atlas itself decodes correctly, but its
in-game colors still render as green and magenta bands; that renderer/material issue remains open.
The model is still a single idle pose without retail hands or weapon animation.

The earlier capture below records the initial visible-model pass:

- [Initial visible-model screenshot](screenshots/20261122-145519-mohaa-garand-visible/final.png)
- [Initial Dolphin log](screenshots/20261122-145519-mohaa-garand-visible/dolphin.log)
- [Initial probe note](notes/20261122-145519-mohaa-garand-visible.md)

The first version of `tools/mohaa_weapon.py` converted the retail `models/weapons/m1_garand` SKD and
frame-zero idle pose into a 119,736-byte GoldSrc v10 studio model. The latest version preserves the
atlas aspect ratio (512x256 downscaled to 256x128) and writes an 86,968-byte model. The isolated smoke
disc staged it as
`gc_studio/v_garand.mdl`. Dolphin loaded that model from the MOHAA gamedir (`116.93 KiB`, one
texture) and reached `map loaded m1l2a` / `newgame world render ready`.

The first capture at 2:48 PM loaded the model without drawing it because that ISO had the `gcvst`
and `fullphysics` diagnostic flags. This capture removes those flags. The log now confirms the
viewmodel bind, skin upload, bone setup and first-person draw pass; the Garand is visible in-frame.
Its framing/material appearance still needs tuning. The converter currently supports one diffuse
texture and a single static idle pose; hands, weapon animations, ammo interaction, and gameplay are
not converted here.

The ISO and generated model are temporary files under `/tmp/mohaa-garand-visible-20261122/` and
are not included in the repository.
