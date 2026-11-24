# m1l1 spill-capacity runtime probe — 2026-11-23

This candidate configures a MOHAA-only 1 MiB world-array spill; other GameCube game directories retain the engine's existing 900 KiB spill. The isolated Dolphin run reached `MAP_READY m1l1`.

Verified in OSReport:

- `maps/m1l1.nodes`: 643 nodes, 2,067 links, 4,447 walk tests; scripted `walkto` calls advance over path nodes.
- `gmctruck_opening.mdl`: loaded from spill, 231.01 KiB resident.
- `opeltruck.mdl`: loaded from spill, 206.27 KiB resident.
- `german_afrika_private.mdl`: loaded, 173.47 KiB; studio budget 772.24 KiB / 1.50 MiB; world spill pinned through 973.28 KiB.

This proves successful model loading and path progression, not that the actor is visually correct, animates properly, or completes the opening. The captured frame is the m1l1 team picker. The 65-second isolated run was stopped by timeout (124), not a guest crash. OSReport is in `dolphin.log.gz`.

Build artifacts (outside the repo):

- ISO: `/tmp/mohaa-m1l1-spill1024-build/out/mohaa-m1l1-spill1024.iso` — 1,165,938,688 bytes; SHA-256 `75da18d5516278dc8b5d04ba5f1b19c91f102e721f0e95f02acd20debb6995c9`.
- DOL: `/tmp/mohaa-m1l1-spill1024-build/out/mohaa-m1l1-spill1024.dol` — 7,484,192 bytes; SHA-256 `31e78bb43a43ce6aac5886a9a0717b77776277cf88b7b03f8908debe3a56a7b5`.

The engine changes are isolated in `/tmp/mohaa-loopback-fix/engine`: `wscript` defines `XASH_MOHAA_GAMECUBE` for `--gamedir mohaa`, and `mod_bmodel.c` uses the larger spill only under that define. The shared engine checkout was not edited. Desktop Dolphin is running this ISO in `/tmp/mohaa-m1l1-playable` with Tim's saved keyboard bindings.
