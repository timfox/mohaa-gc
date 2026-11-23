# MOHAA in-game cutscenes

## m1l1 opening ride

**Tag data and path progression work in Dolphin. The scene is not yet visually implemented.**

The runtime log shows the retail m1l1 script loading 5 tagged models and 65 animation lengths, joining as Allies Rifleman, and reading a moving `truck2` tag path through to its endpoint. See [the tag-motion report and capture](../media/2026-11-22-m1l1-tag-arena/README.md).

The current game-side bindings do not render the scene's script models:

- `M_Spawn` in `dod-gc/src/dod_mohaa_ents.cpp` maps `script_model`, `script_origin`, and `script_object` to `info_target`.
- `M_Spawn` skips their `model` key because MOHAA `.tik` models are not converted/precached as GoldSrc models.
- `c_model` in `dod-gc/src/dod_mohaa.c` selects a baked tag model for tag lookup; it does not assign a drawable model.
- `anim` currently supplies animation timing and tag sampling; it does not deform or sequence a rendered mesh.

Consequently the verified moving path is script/runtime behavior only. The opening trucks, path model, and scripted driver meshes are still missing from the visual scene. The existing screenshot is after the ride, not a mid-cutscene visual proof.

## Next implementation

Add a retail-data pipeline and runtime binding for the m1l1 scripted TIKI models. Start with one model each for `vehicles/gmctruck_opening.tik`, `vehicles/opeltruck.tik`, and `vehicles/gmctruckpath_opening.tik`; preserve the script's model, animation, origin, and angles updates. Then capture the ride mid-sequence in Dolphin and compare placement and motion against the retail script/reference. Do not call the opening cutscene complete until the models render and the frame capture confirms the scripted camera/path visually.

Physical GameCube playback remains a separate validation gate.
