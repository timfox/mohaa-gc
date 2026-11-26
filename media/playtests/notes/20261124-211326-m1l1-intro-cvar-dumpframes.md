# MOHAA Probe m1l1 intro cvar — 2026-11-24 21:13 PT

- Route: `m1l1-intro-cvar-dumpframes`
- ISO: `/home/tim/Desktop/mohaa-gc/.tmp-mohaa-m1l1-intro-cvar-dumpframes.iso`
- ISO SHA-256: `a960f5ed86d5b27de4b85a01d35784b978352508c6b21c134ab0fedbad3c5fe2`
- Route: retail menu New Game with early boot `cvar intro 1` and Xash `dumpframes`
- Dolphin: `/tmp/dolphin-nogui-build-fresh/Binaries/dolphin-emu-nogui`, isolated profile `/tmp/mohaa-intro-cvar-dumpframes-user`
- Duration cap: 45s (timeout exit 124 after the probe interval)
- Full Dolphin log: `/home/tim/Desktop/mohaa-gc/media/playtests/notes/20261124-211326-m1l1-intro-cvar-dumpframes-dolphin.log.gz`

The disc builder wrote `menunewgame`, `cvar intro 1`, and `dumpframes` to the boot config. Dolphin OSReport confirms `disc cfg cvar set`, then `map loaded m1l1`, `MAP_READY m1l1`, and `world DL frame=1`. This establishes that the cvar override was applied before the New Game map load.

The player still remains at `(-1918,-3136,85)` in the outdoor spawn during repeated `ride` samples. Twelve logged `mohaa_actor` entity spawn callbacks return `-1`, but this is expected for the map placeholder: `CMohaaActor::Spawn` replaces or queues the actor, then calls `UTIL_Remove(this)`. The engine only counts a `-1` result as an inhibited/rejected entity when `FL_KILLME` is not set (`engine/server/sv_game.c`, map-entity spawn handling); therefore these lines do not prove actor rejection. Actor presence/queueing and visible truck placement are still unverified. The run did not create a PNG in Dolphin's Dump/Frames directory despite the dumpframes option, so it does not visually verify the truck or prove the mission script's intro branch executed. Next investigate why the player remains at the outdoor spawn and verify the ride/cast in a guest capture.
