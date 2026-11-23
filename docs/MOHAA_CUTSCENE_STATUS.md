# MOHAA in-game cutscenes

## m1l1 opening ride

**Tag data and path progression work in Dolphin. The scene is not yet visually implemented.**

The runtime log shows the retail m1l1 script loading 5 tagged models and 65 animation lengths, joining as Allies Rifleman, and reading a moving `truck2` tag path through to its endpoint. See [the tag-motion report and capture](../media/2026-11-22-m1l1-tag-arena/README.md).

The current game-side bindings do not render the scene's script models:

- `M_Spawn` in `dod-gc/src/dod_mohaa_ents.cpp` maps `script_model`, `script_origin`, and `script_object` to `info_target`.
- `M_Spawn` skips their `model` key because MOHAA `.tik` models are not converted/precached as GoldSrc models.
- `c_model` in `dod-gc/src/dod_mohaa.c` selects a baked tag model for tag lookup; it does not assign a drawable model.
- `anim` currently supplies animation timing and tag sampling; it does not deform or sequence a rendered mesh.

Consequently the verified moving path is script/runtime behavior only. The opening trucks and scripted driver meshes are still missing from the visual scene. The existing screenshot is after the ride, not a mid-cutscene visual proof.

An offline static-mesh prototype now exists at `tools/mohaa_tiki_model.py`. Using the retail `main/` data, it baked `vehicles/gmctruck_opening.tik` as a 269,724-byte Studio v10 model (13 surface bodygroups, 5,171 triangles) and `vehicles/opeltruck.tik` as a 214,624-byte model (11 bodygroups, 4,659 triangles). `dod-gc/tools/split_studio_mdl.py info` parsed both outputs and reported one sequence and one texture. The generated MDLs stay in `/tmp/mohaa-script-models/`; retail-derived models are not committed.

This conversion is a static idle-pose mesh only. It does not preserve the truck's animated wheels/lights, the scripted driver poses, or other SKC sequences, and the game does not load or display these MDLs yet.

## Next implementation

Add runtime model preloading and binding for the two converted truck meshes so the script's `.model`, `.origin`, and `.angles` commands affect visible entities. Then add SKC sequence playback for commands such as `idlenolights` and `start_wheels`, and convert/render the scripted human actors. The path-follow TIKIs are tag carriers with a tiny helper triangle, so keep them as tag sources rather than treating them as visible truck models. Capture the ride mid-sequence in Dolphin and compare placement and motion against the retail script/reference. Do not call the opening cutscene complete until the models render and the frame capture confirms the scripted camera/path visually.

Physical GameCube playback remains a separate validation gate.
