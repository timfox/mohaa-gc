# MOHAA in-game cutscenes

## m1l1 opening ride

**Tag data and path progression work in Dolphin. Scripted truck models now have animated Studio MDLs, but the new meshes and animation playback still need a runtime capture.**

The runtime log shows the retail m1l1 script loading 5 tagged models and 65 animation lengths, joining as Allies Rifleman, and reading a moving `truck2` tag path through to its endpoint. See [the tag-motion report and capture](../media/2026-11-22-m1l1-tag-arena/README.md).

The first render-binding pass is in the source and has compiled into a GameCube DOL from an isolated copy of the locally available HL1 engine source:

- `script_model` and `script_object` now spawn as `CBaseAnimating` entities; `script_origin` remains an invisible `info_target`.
- `c_model` still selects the baked tag data and now assigns an MDL to renderable script models when its TIKI appears in `maps/<map>.models`.
- The backend reads that manifest and precaches the MDLs in the GameCube `ServerActivate` hook before the first mission frame.
- The exporter keeps single-weight SKD skeletons and writes each TIKI animation alias as a Studio v10 sequence. The `anim` callback selects that sequence on the visible script model while preserving tag sampling and `animdone` timing.

The earlier isolated build produced `/tmp/mohaagc-20261123.dol` (7,454,848 bytes; SHA-256 `4ed97f95e651468ab784d740a5a3c8835987ae8e6a2e55ab0b65be7b2ba5b194`) with the classic libogc stack. Its engine source came from a local HL1 worktree whose shared Git metadata is unavailable, so this is compile/link evidence rather than a build against the canonical shared engine revision; that DOL predates the new sequence exporter and playback callback. The last verified Dolphin run proved tag/path progression only; no runtime capture has confirmed that the new binding renders the trucks.

`tools/mohaa_tiki_model.py` bakes `vehicles/gmctruck_opening.tik` as a Studio v10 model with 52 bones, 2 sequences (`idle`, `open_gate`), 13 surface bodygroups and 5,171 triangles. `vehicles/opeltruck.tik` has 57 bones, 6 sequences (`idle`, `idlelights`, `idlenolights`, `skidding`, `start_wheels`, `stop_wheels`), 11 bodygroups and 4,659 triangles. Fresh models were written under `/tmp/mohaa-animated-stage/xash3d/mohaa/` and parsed by `dod-gc/tools/split_studio_mdl.py info`; they are 296,636 and 243,528 bytes. The `scriptmodels` stage in `tools/mohaa_sd.py` writes both to the user's SD game directory and creates `maps/m1l1.models`. Retail-derived outputs stay on the SD card and are not committed.

The SKC reader decodes every per-bone frame, and both the tag baker and MDL exporter use that shared decoder. Retail data has `opel_opening.skc` at 6 frames / 10 fps and `opel.skc` at 1 frame / 25 fps. The exporter currently omits TIKI per-animation surface visibility changes, so wheel/light toggles and the script's GMC `idlenolights` alias still need a dedicated parity pass.

The conversion supports the truck meshes' single-bone vertex weights; multi-weight models still use the static pose fallback. It does not yet convert the scripted driver actors or apply TIKI surface visibility toggles. The new source binding still needs a GameCube runtime capture to prove it loads and plays these MDL sequences.

## Next implementation

Run a DOL built from the canonical shared engine with the `scriptmodels` stage output. Confirm both models precache, render, follow the script's `.origin`/`.angles`, and play sequences during the opening. Then implement the per-animation surface toggles, resolve GMC `idlenolights`, and convert/render the scripted human actors. The path-follow TIKIs are tag carriers with helper triangles; keep them as tag sources. Do not call the opening cutscene complete until a mid-sequence runtime capture confirms the models and camera visually.

Physical GameCube playback remains a separate validation gate.
