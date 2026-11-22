# MOHAA m1l2a HUD ownership fix — 2026-11-22

Dolphin visual probe of a temporary MOHAA GameCube ISO built from Xash3D-GC commit `cd5e31a68` plus the local changes in this worktree. The DOL and ISO were isolated under `/tmp`; no retail data or release artifact was overwritten.

- Route: local listen server on `m1l2a`, 60-second cap, world render enabled.
- Result: `newgame world render ready`; no fatal/error path in the guest log.
- HUD allocator: 128 KiB borrowed decode-buffer arena; the log records evictions 0 through 3 as later decodes safely evicted and reacquired the cells.
- Screenshot: `final.png` (640×480, captured in gameplay).
- Selected guest log lines: `guest-key-lines.txt`; full Dolphin log remains in the temporary probe directory.
- Toolchain: devkitPPC 16.1.0, libogc at `/opt/devkitpro/libogc`; Dolphin binary `/home/tim/.local/xash3d-gc-baseline/3rdparty/dolphin/build/Binaries/dolphin-emu`.
- Physics caps: 256 physents / 32 moveents, matching the staged MOHAA game DLL.

Temporary artifact SHA-256:

- DOL: `fad23ab89d2a952b452819dae22029617d02bd84aae70eb055ca3ba2045a7366`
- ISO: `0cb0dff6de789eade27631cd6bd8850ebe4e9769fed9d02d3d3dda7accb4613a`
- Screenshot: `b2589256b260b2472378b10f6a892d7f56aa846e6f6794accb4274aa64114709`
