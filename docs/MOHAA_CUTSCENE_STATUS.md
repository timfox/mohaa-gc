# MOHAA in-game cutscenes

## m1l1 opening ride

**Tag data and path progression work in Dolphin. Scripted truck models now have animated Studio MDLs, but the new meshes and animation playback still need a runtime capture.**

The runtime log shows the retail m1l1 script loading 5 tagged models and 65 animation lengths, joining as Allies Rifleman, and reading a moving `truck2` tag path through to its endpoint. See [the tag-motion report and capture](../media/2026-11-22-m1l1-tag-arena/README.md).

The first render-binding pass is in the source and has compiled into a GameCube DOL from an isolated copy of the locally available HL1 engine source:

- `script_model` and `script_object` now spawn as `CBaseAnimating` entities; `script_origin` remains an invisible `info_target`.
- `c_model` still selects the baked tag data and now assigns an MDL to renderable script models when its TIKI appears in `maps/<map>.models`.
- The backend reads that manifest and precaches the MDLs in the GameCube `ServerActivate` hook before the first mission frame.
- The exporter keeps single-weight SKD skeletons and writes each TIKI animation alias as a Studio v10 sequence. Two body choices per surface let the runtime match TIKI init and per-alias `+nodraw`/`-nodraw` entry actions; the visible-surface bitmask is stored in the scripted model's sequence metadata. The `anim` callback selects the sequence and applies its bodygroups while preserving tag sampling and `animdone` timing.

The earlier isolated build produced `/tmp/mohaagc-20261123.dol` (7,454,848 bytes; SHA-256 `4ed97f95e651468ab784d740a5a3c8835987ae8e6a2e55ab0b65be7b2ba5b194`) with the classic libogc stack. Its engine source came from a local HL1 worktree whose shared Git metadata is unavailable, so this is compile/link evidence rather than a build against the canonical shared engine revision; that DOL predates the new sequence exporter and playback callback. The last verified Dolphin run proved tag/path progression only; no runtime capture has confirmed that the new binding renders the trucks.

On 2026-11-23, the changed MOHAA server/client sources (`dod_mohaa.c`, `dod_mohaa.h`, and `dod_mohaa_ents.cpp`) compiled into scratch GameCube archives, and the engine linked a fresh 7,752,096-byte DOL with the classic libogc stack. Its SHA-256 is `d42b8d78675fad19cd86d120f5a7b6db4b59d56b6a9290c6c25ce17ec823070e`. The engine source was copied from the local HL1 worktree without canonical Git metadata; the missing MultiEmulator and `library_suffix` dependencies came from other local snapshots. A clean local mainui snapshot replaced the stale source in the scratch copy, and `check-menu-provenance.sh --dol` now passes. Treat this as compile/link evidence for the updated game code, not a canonical engine build: the exact engine and mainui revisions are not recorded from their original Git metadata, and the DOL has not been run in-game. The artifact and logs are under `/tmp/mohaa-current-build-20261123/`.

`tools/mohaa_tiki_model.py` bakes `vehicles/gmctruck_opening.tik` as a Studio v10 model with 52 bones, 3 sequences (`idle`, synthetic `idlenolights`, `open_gate`), 13 surface bodygroups and 5,171 triangles. The synthetic alias reuses the retail idle SKC and TIKI init visibility because the m1l1 script calls `idlenolights`, which this retail TIKI does not declare. `vehicles/opeltruck.tik` has 57 bones, 6 sequences (`idle`, `idlelights`, `idlenolights`, `skidding`, `start_wheels`, `stop_wheels`), 11 bodygroups and 4,659 triangles. Fresh models were written under `/tmp/mohaa-tiki-visibility-stage/xash3d/mohaa/` and parsed by `dod-gc/tools/split_studio_mdl.py info`; they are 302,860 and 244,760 bytes. The `scriptmodels` stage in `tools/mohaa_sd.py` writes both to the user's SD game directory and creates `maps/m1l1.models`. Retail-derived outputs stay on the SD card and are not committed.

The SKC reader decodes every per-bone frame, and both the tag baker and MDL exporter use that shared decoder. Retail data has `opel_opening.skc` at 6 frames / 10 fps and `opel.skc` at 1 frame / 25 fps. The converted TIKI visibility states now match the retail init and sequence entries: GMC `open_gate` reveals the scripted panels, Opel `idle`/`idlelights`/`idlenolights` switch the light surface, and wheel aliases switch between moving and still wheel meshes.

The conversion supports the truck meshes' single-bone vertex weights; multi-weight models still use the static pose fallback. It does not yet convert the scripted driver actors. The new source binding still needs a GameCube runtime capture to prove it loads, animates, and switches bodygroups correctly.

## Next implementation

Run a DOL built from the canonical shared engine with the `scriptmodels` stage output. Confirm both models precache, render, follow the script's `.origin`/`.angles`, play sequences, and switch surfaces during the opening. Then convert/render the scripted human actors. The path-follow TIKIs are tag carriers with helper triangles; keep them as tag sources. Do not call the opening cutscene complete until a mid-sequence runtime capture confirms the models and camera visually.

Physical GameCube playback remains a separate validation gate.
