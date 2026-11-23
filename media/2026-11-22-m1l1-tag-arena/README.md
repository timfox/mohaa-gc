# m1l1 cutscene tag loading — 2026-11-22

The original `maps/m1l1.tags` was 50,622 bytes. On the opening map, Xash3D-GC could not allocate the full file from its fragmented general heap, so the cutscene scripts ran without baked model tags.

The tag baker now writes a small MTGC manifest plus thirteen 4 KiB pieces for large files. The MOHAA game code reassembles the original MTAG bytes in the map arena, parses them, and releases the temporary buffer. Small tag files remain in the original single-file format.

The temporary Dolphin disc loaded all thirteen `maps/m1l1.tags.NNN` pieces and logged `mohaa: maps/m1l1.tags: 5 models with tags, 65 animation lengths, 48 KB`. It also reached `MAP_READY m1l1`, `signal prespawn`, and `signal spawn`. The screenshot is at the m1l1 class selection overlay with the map rendered. That proves tag loading and mission startup; it does not yet show the opening truck cinematic after the player joins a class.

![m1l1 map at class selection](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l1-tag-arena/m1l1-class-select.png)

Evidence: [Dolphin log](dolphin.log), [screen capture](m1l1-class-select.png).

- Temporary test ISO: `/tmp/mohaa-m1l1-cutscene/out/m1l1-cutscene-chunked.iso` (SHA-256 `3158e33d8fc31ea7ffc91b61494404a8bb9325978dffc7a29f9ff3c5351a1902`).
- Built DOL: `retail/build-ca7e9b3/out/dodgc.dol` (SHA-256 `41dfa45ce07920055e14059ef47944e9b65eb31732cd545b0f26f5ff2faa076f`).
- No retail game assets or binaries are included in this evidence directory.
