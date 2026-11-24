# m1l1 retail HUD packaging probe — 2026-11-23

The previous runtime log reported seven missing files under `sprites/mohaa/`. The local retail `retail/main/Pak*.pk3` sources contain `textures/hud/*.tga`; running `python3 tools/mohaa_sd.py --mohaa retail/main --sd /tmp/mohaa-hud-stage --stages hud` generated 80 v32 RGBA sprites (5.8 MiB staged). The required health, ammo-arm, ammo-bar, and crosshair sprites are present.

For this test ISO, those 80 files were added to a temporary copy of the existing `extras.pk3`. The retail source files and existing staged data were not modified. In the 65-second isolated Dolphin probe:

- The actor loaded (173.47 KiB), the 643-node graph loaded, and scripted `walkto` advanced.
- There were no `Could not load HUD sprite` errors; the seven required sprite names are in the test pack.
- One `UserMsg: No pfn HudText 73` error remains. Its callback/display behavior still needs investigation.
- The frame is at the team picker; this run does not prove final in-game HUD drawing or actor animation.

The probe was bounded by a 65-second timeout and was isolated from the desktop Dolphin session. Compressed OSReport: `dolphin.log.gz`.

Artifacts under `/tmp`:

- Test ISO `/tmp/mohaa-m1l1-hud-probe/mohaa-m1l1-hud.iso` — 1,167,302,656 bytes; SHA-256 `c6dd6c650bb31a851c5ceaf9e91cad8c19d9d079fb99ad988703f153c02533e4`.
- Temporary merged HUD pack `/tmp/mohaa-m1l1-hud-probe/mohaa-hud-extras.pk3` — 2,980,851 bytes.
- HUD stage `/tmp/mohaa-hud-stage/xash3d/mohaa/sprites/mohaa/` — 80 `.spr` files.

The desktop Dolphin session was left on the prior actor-loading ISO.
