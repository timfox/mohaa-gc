# m1l1 cutscene tag loading — 2026-11-22

The original `maps/m1l1.tags` was 50,622 bytes. On the opening map, Xash3D-GC could not allocate the full file from its fragmented general heap, so the cutscene scripts ran without baked model tags.

The tag baker now writes a small MTGC manifest plus thirteen 4 KiB pieces for large files. The MOHAA game code reassembles the original MTAG bytes in the map arena, parses them, and releases the temporary buffer. Small tag files remain in the original single-file format.

The temporary Dolphin disc loaded all thirteen `maps/m1l1.tags.NNN` pieces and logged `mohaa: maps/m1l1.tags: 5 models with tags, 65 animation lengths, 48 KB`. It also reached `MAP_READY m1l1`, `signal prespawn`, and `signal spawn`. The follow-up Dolphin run used the listen-server test auto-join to enter as Allies Rifleman and enabled the retail script’s `origincheck` diagnostic. `truck2 position` changed from `(4105.379 1778.912 1084.307)` to `(3553.976 841.603 999.441)`, then reached `(-2121.583 -3416.317 33.458)` and stayed there after the path ended. This verifies that the retail script reads the baked moving tag frames and advances the truck path through to its endpoint. The screenshot is the first-person in-game frame after that sequence, not a cinematic frame; visual parity of the opening still needs a mid-sequence capture and comparison.

![m1l1 first-person frame after the tag-driven truck path completed](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l1-tag-arena/m1l1-tag-motion-end.png)

Earlier startup capture: [m1l1 class selection frame](m1l1-class-select.png).

Evidence: [initial load log](dolphin.log), [tag-motion Dolphin log](tag-motion-dolphin.log), [post-path screen capture](m1l1-tag-motion-end.png).

- Temporary test ISO: `/tmp/mohaa-m1l1-cutscene/out/m1l1-cutscene-chunked.iso` (SHA-256 `3158e33d8fc31ea7ffc91b61494404a8bb9325978dffc7a29f9ff3c5351a1902`).
- Built DOL: `retail/build-ca7e9b3/out/dodgc.dol` (SHA-256 `41dfa45ce07920055e14059ef47944e9b65eb31732cd545b0f26f5ff2faa076f`).
- The motion probe’s test-only `dod_gc_autojoin` and `set origincheck 1` settings were added to a temporary listen-server config under `/tmp`; no project config changed.
- No retail game assets or binaries are included in this evidence directory.
