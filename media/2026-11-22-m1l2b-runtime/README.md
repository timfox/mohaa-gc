# MOHAA m1l2b GameCube runtime capture — 2026-11-22

Fresh 45-second Dolphin smoke run of the m1l2b map using the local MOHAA SD stage plus the shared DoD/Valve smoke assets. The ISO was assembled from the MOHAA gamedir and booted with `--smoke-map m1l2b --world-render`.

## Result

The engine reached `MAP_READY m1l2b` and `newgame world render ready`; the screenshot shows the first-person view in the night airfield map. This is an automated local map/world-render smoke route, not a complete MOHAA retail gameplay port.

![m1l2b in Dolphin](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/m1l2b-dolphin-final.png)

## Run identity

- Engine source: Xash3D-GC commit `52f7ae8bbb`.
- DOL SHA-256: `00058c7af6468840062e39d0ef5536af6ce2d5537f188e7051b1cdda29bcd17e`.
- ISO SHA-256: `80a8f55f8573b7f3acb5665ead9a0181a76ee09f682cdcd2a774f59ca310fc55` (built under `/tmp/mohaa-m1l2b-runtime-20261122/`).
- m1l2b BSP SHA-256: `ef71b1bd3f121d74560ba47bac1304e3c62d8c371d069dba5a7579e4d92b8a74`.
- Dolphin build revision: `7c9d49d63d` (`/home/tim/.local/xash3d-gc-baseline/3rdparty/dolphin`).
- Probe: 45 seconds, 640x480 screenshot; MMU and Accurate CPU Cache enabled. No physical GameCube result is claimed.

## Open issues from this run

- The runtime reported `newgame world render ready`, then a measured frame split of about 198 ms (`5.0 fps`) in this probe; map performance needs optimization and a follow-up capture.
- The MOHAA gamedir has no `media/gp_m1l2b.gcp` prop pack or `media/ss_m1l2b.gcs` soundscape pack yet. The shown first-person object is a fallback melee model.
- A filesystem pool allocation failed once during map load (225.04 KiB request); the map still reached the render-ready marker.

Full Dolphin/OSReport log: [dolphin.log](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/dolphin.log).
