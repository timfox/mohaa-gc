# MOHAA in-game cutscenes

## m1l1 opening ride

**Tag data and path progression work in Dolphin. The scene is not yet visually implemented.**

The runtime log shows the retail m1l1 script loading 5 tagged models and 65 animation lengths, joining as Allies Rifleman, and reading a moving `truck2` tag path through to its endpoint. See [the tag-motion report and capture](../media/2026-11-22-m1l1-tag-arena/README.md).

The first render-binding pass is now in the source, but has not been built or run on GameCube yet:

- `script_model` and `script_object` now spawn as `CBaseAnimating` entities; `script_origin` remains an invisible `info_target`.
- `c_model` still selects the baked tag data and now assigns an MDL to renderable script models when its TIKI appears in `maps/<map>.models`.
- The backend reads that manifest and precaches the MDLs in the GameCube `ServerActivate` hook before the first mission frame.
- `anim` still supplies only tag sampling and `animdone` timing; the static MDL does not play the retail SKC sequence.

The last verified Dolphin build proved tag/path progression only; its capture is after the ride and does not show a mid-cutscene view. The new render binding has not yet been built, so visible truck rendering remains unverified.

`tools/mohaa_tiki_model.py` bakes `vehicles/gmctruck_opening.tik` as a 269,724-byte Studio v10 model (13 surface bodygroups, 5,171 triangles) and `vehicles/opeltruck.tik` as a 214,624-byte model (11 bodygroups, 4,659 triangles). The `scriptmodels` stage in `tools/mohaa_sd.py` writes both to the user's SD game directory and creates `maps/m1l1.models`. A staging run produced the two MDLs plus that manifest; `dod-gc/tools/split_studio_mdl.py info` parsed both outputs. Retail-derived outputs stay on the SD card and are not committed.

This conversion is a static idle-pose mesh only. It does not preserve the truck's animated wheels/lights, the scripted driver poses, or other SKC sequences. The new source binding still needs a GameCube runtime capture to prove it loads and displays these MDLs.

## Next implementation

Run the new code on a GameCube build with the `scriptmodels` stage output. Confirm that both models precache, render, follow the script's `.origin`/`.angles`, and remain in the camera view during the opening. Then add SKC playback for sequences such as `idlenolights` and `start_wheels`, and convert/render the scripted human actors. The path-follow TIKIs are tag carriers with helper triangles; keep them as tag sources. Do not call the opening cutscene complete until a mid-sequence runtime capture confirms the models and camera visually.

Physical GameCube playback remains a separate validation gate.
