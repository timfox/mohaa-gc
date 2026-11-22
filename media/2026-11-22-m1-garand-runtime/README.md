# MOHAA M1 Garand runtime capture

Fresh Dolphin capture, recorded Nov. 22 at 2:48 PM PT:

![MOHAA m1l2a map and HUD in Dolphin](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1-garand-runtime/screenshots/20261122-144852-mohaa-retail-garand/final.png)

- [Full Dolphin log](screenshots/20261122-144852-mohaa-retail-garand/dolphin.log)
- [Probe note](notes/20261122-144852-mohaa-retail-garand.md)

`tools/mohaa_weapon.py` converted the retail `models/weapons/m1_garand` SKD and frame-zero idle
pose into a 119,736-byte GoldSrc v10 studio model. The isolated smoke disc staged it as
`gc_studio/v_garand.mdl`. Dolphin loaded that model from the MOHAA gamedir (`116.93 KiB`, one
texture) and reached `map loaded m1l2a` / `newgame world render ready`.

This confirms the static mesh and texture container load. The captured listen-server view does not
show the viewmodel yet, so orientation/placement and first-person draw behavior remain open. The
converter currently supports one diffuse texture and a single static idle pose; weapon animations,
hands, ammo interaction, and gameplay are not converted here.

The ISO and generated model are temporary files under `/tmp/mohaa-garand-runtime-20261122/` and are
not included in the repository.
