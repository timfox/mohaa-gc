# m1l2a friendly script runtime proof

Dolphin guest probe, 2026-11-22. The MOHAA script compiler now uses the normal 4 KiB scratch arena block first, then falls back to smaller 2 KiB, 1 KiB, and 512-byte blocks when GameCube heap fragmentation prevents a larger allocation.

Observed in the guest log:
- `MAP_READY m1l2a`
- `FS_LoadFile path=global/friendly.scr`
- `global/friendly.scr read into the idle surface-cache store (71.97 Kb)`
- `mohaa_actor : in from the waiting list (6 left)`
- `WorldDL dumpeye aim`, `world DL frame` (`bind_miss=0`), and `newgame world render ready`
- No `script compile error`, `script error`, or script out-of-memory message in this run.

The 640x480 capture shows the textured m1l2a alley, but the HUD is visibly corrupted in this capture; HUD visual parity remains open. This is emulator evidence, not physical GameCube hardware validation.
