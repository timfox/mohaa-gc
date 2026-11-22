# MOHAA M1 Garand runtime capture

Fresh Dolphin capture, recorded Nov. 22 at 2:55 PM PT:

![Retail M1 Garand model drawn in MOHAA m1l2a](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1-garand-runtime/screenshots/20261122-145519-mohaa-garand-visible/final.png)

- [Full Dolphin log](screenshots/20261122-145519-mohaa-garand-visible/dolphin.log)
- [Probe note](notes/20261122-145519-mohaa-garand-visible.md)

`tools/mohaa_weapon.py` converted the retail `models/weapons/m1_garand` SKD and frame-zero idle
pose into a 119,736-byte GoldSrc v10 studio model. The isolated smoke disc staged it as
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
