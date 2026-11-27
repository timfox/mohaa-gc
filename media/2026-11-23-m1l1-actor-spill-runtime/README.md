# m1l1 actor spill runtime probe — 2026-11-23

The isolated Dolphin run booted the actor-spill ISO and reached `MAP_READY m1l1`. The probe ran for 55 seconds and was stopped by its timeout (exit 124); this is not a guest crash. OSReport is captured in `dolphin.log.gz`.

Verified in the guest log:

- The retail path graph loads: 643 nodes, 2,067 links, 4,447 walk tests. Scripted `walkto` calls advance over path nodes.
- `gmctruck_opening.mdl` loads from studio spill at 231.01 KiB; `opeltruck.mdl` loads at 206.27 KiB.
- The German actor model does not load. Its 173.47 KiB core misses a spill allocation with 156.59 KiB free at initial spawn, then 68.28 KiB free when the script retries. Deferred loading falls back to the studio arena and fails. Therefore the actor and opening cutscene are not verified visually.

Build artifacts (kept outside the repository):

- ISO: `/tmp/mohaa-m1l1-actor-spill-build/out/mohaa-m1l1-actor-spill.iso` — 1,165,938,688 bytes; SHA-256 `fd0175ce8a8174acb65c80a2b7060a765b9b7427250a95c6dec1b088a6bdf8ad`.
- DOL: `/tmp/mohaa-m1l1-actor-spill-build/out/mohaagc-actor-spill.dol` — 7,484,384 bytes; SHA-256 `d638996ef579be9b6abb67094999edd3f00d7435c86d590e67df05ecd44fae06`.
- The ISO includes the game-side path-node and damage-toggle changes plus an isolated scratch-engine model-routing change. Engine source is `/tmp/mohaa-loopback-fix/engine`; the shared engine checkout was not changed.

The next engine investigation should preserve actors needed by the active mission while managing the shared 800 KiB world-array spill budget. Increasing the arena without checking BSP, WorldDL, animation and client allocations could regress map loading.
