# m1l2a local.self runtime proof

Dolphin guest runtime probe on a temporary GameCube ISO, 2026-11-22. The GameCube DOL was built with the same `XASH_GC_PM_MAX_PHYSENTS=256` and `XASH_GC_PM_MAX_MOVEENTS=32` caps used by the MOHAA server archive.

Evidence:
- `dolphin.log`: full guest log from a 20 second probe.
- `final.png`: 640x480 Dolphin capture of the textured m1l2a alley.
- `probe.md`: route, capture summary, and key boot lines.

Observed: `MAP_READY m1l2a`, `WorldDL dumpeye aim`, `world DL frame` (`bind_miss=0`), and `newgame world render ready`. The guest log loads `global/door_locked.scr` and contains no `waittill applied to NIL` or `playsound applied to NIL` errors. It does report separate campaign incompleteness: missing `global/friendly.scr` and NIL actor operations in `maps/m1l2a.scr`.

The ISO and DOL were built under `/tmp/mohaa-selfbinding/` and are intentionally not committed. Dolphin is emulator evidence, not physical GameCube hardware validation.
