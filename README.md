# mohaa-gc

Medal of Honor: Allied Assault content brought into **DoD-GC** (GoldSrc on
GameCube). This is an asset port, not an engine port: MOHAA maps, models and
missions are converted into formats the existing dod-gc runtime already plays.

No retail game data lives in this repository. Point the tools at your own
copy of the game's `.pk3` files.

The CDs hold loose music, ambience, vehicle, mechanics, weapons and dialogue
samples outside the PK3 files. Pass the CDs with your installed folder so the
stager can unpack those InstallShield groups, then run both sound stages:

```bash
python3 tools/mohaa_sd.py --cd /path/to/cd1 /path/to/cd2 --mohaa ~/MOHAA --sd /media/SDCARD --stages sounds,music
```

The SFX stage writes map-specific `maps/<map>.snd` tables and native 22.05 kHz-or-lower mono
PCM samples under `sound/mohaa/`. Samples too large for the GameCube's 1 MiB ARAM sound ring
are converted at 11.025 kHz when that fits; looping samples retain a WAV cue point. It keeps
nested retail dialogue paths intact. The music stage
still needs separate loose tracks when the install's `main/` folder does not contain them; see
`--music-source` below.

If effects or dialogue were extracted into a separate folder containing `sound/`, pass it with
`--sound-source`. It is read only by the sounds stage:

```bash
python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sound-source /path/to/extracted/main \
  --sd /media/SDCARD --stages sounds
```

If the loose music files were extracted separately from the `main/` folder,
pass that directory with `--music-source`; it is read only by the music stage:

```bash
python3 tools/mohaa_sd.py --mohaa ~/MOHAA --music-source /path/to/extracted/main --sd /media/SDCARD --stages music
```

## Intro movie

The movie stage converts MOHAA's silent `main/video/intro.RoQ` and its adjacent
`intro.mp3` soundtrack into GameCube streams:

```bash
python3 tools/intro_movie.py ~/MOHAA/main/video/intro.RoQ --sd /media/SDCARD
```

When the loose `Video Files` cabinet was extracted separately from the installed `main/` folder,
pass that directory to the regular stager so it can find both the intro and its soundtrack:

```bash
python3 tools/mohaa_sd.py --mohaa ~/MOHAA --movie-source /path/to/Video_Files \
  --sd /media/SDCARD --stages movie
```

Repeat `--movie-source` for additional extraction folders. The movie stage also searches the
installed folder and CD groups supplied with `--cd`.

It writes `xash3d/mohaa/media/mohaa_intro.gcvid` (GCV2, 320x240 RGB565 frames at 15 fps) and
`mohaa_intro.gcpcm` (GCPA, 48 kHz stereo signed 16-bit big-endian PCM). The stock retail intro is
letterboxed to preserve its 2:1 picture. On the local retail extraction, all 2,503 output frames
were validated against ffmpeg after the converter's documented one-bit RGB565 delta threshold;
the PCM payload matched ffmpeg byte for byte. The stream is 137.9 MB of video at 0.83 MB/s plus
30.9 MB of audio. Existing Dolphin evidence in
[`media/2026-11-22-intro-movie/README.md`](media/2026-11-22-intro-movie/README.md) confirms picture
and sound playback on a test disc; SD-card streaming on physical hardware remains to be checked.
The generated streams contain retail game data and must stay outside the repository.

## Map pipeline (planned)

```
MOHAA .bsp ("2015" v19)
   -> BSP19 reader                     tools/mohaa_bsp19.py
   -> Valve-220 .map (brushes scaled ~0.77, clip proxies for patches/terrain)
   -> SDHLT csg/bsp/vis -> BSP30       dod-gc tools/mapbridge
   -> MOHAA's lightmaps copied in      tools/bsp19_lightmaps.py
   -> GX world bake + detail meshes    dod-gc tools/bake_worlddl_goldsrc.py
```

Curved patches, LOD terrain and static models get a simplified collision
version in the .map and a full-detail mesh in the render bake, so they do not
count against BSP30 limits.

## Budget report

Before converting anything, measure which maps fit GoldSrc limits:

```bash
python3 tools/budget_report.py "/path/to/MOHAA/main" --json budget.json --csv budget.csv
python3 tools/budget_report.py pak0.pk3 pak1.pk3 --quiet        # one line per map
python3 tools/budget_report.py m1l1.bsp --limit world_coord=8192  # override a limit
```

Inputs can be loose `.bsp` files, `.pk3` archives (later paks override
earlier ones, like the game), or directories searched for both.

Per map it reports brush classes (solid, detail, clip, water, trigger),
surface types, collidable patches, terrain patches and the coarsest collision
grid each one needs, static models, entities, world bounds after scaling, and
checks each estimate against a limit:

| Check | Default limit | Note |
| --- | --- | --- |
| `clipnodes` | 32,767 | BSP30 format limit (signed 16-bit). Estimate = collision brush sides x `--clipnodes-per-side` (0.5, **uncalibrated**), split by brushes, patch proxies and terrain proxies |
| `world_coord` | 32,768 | Largest absolute coordinate after `--scale` (default 72/94). SDHLT's default `-worldextent`; xash sizes the world from the map |
| `models` | 512 | World plus brush entities (SDHLT) |
| `edicts_est` | 900 | xash3d-gc `GC_SP_EDICT_CAP` on GameCube, shared with players, bots and projectiles. Path nodes (future GOAP waypoints) and lights are not counted |
| `textures` | 512 | Unique textures on drawn brush faces, patches and terrain |
| `faces_est` | 65,535 | Drawn brush sides before BSP splitting, so a low bound |
| `brushes` | 32,768 | Converted brushes plus patch and terrain proxies (SDHLT) |

Status is `OK` below 70% of a limit, `TIGHT` from 70% to 100%, `OVER` above.
The defaults come from SDHLT and xash3d-gc source (see the comment above
`DEFAULT_LIMITS`); override any of them with `--limit name=value`.

Known gaps: the clipnode factor needs calibrating against real SDHLT runs, and
the report does not yet predict the compiled BSP30 size against the engine's
3 MiB map buffer.

## Brush extraction (BSP19 -> .map)

```bash
python3 tools/bsp19_to_map.py retail/main/Pak5.pk3:maps/m1l1.bsp -o m1l1.map --wad m1l1.wad
sdHLCSG m1l1.map && sdHLBSP m1l1.map      # fast fullbright loop; add sdHLVIS
python3 tools/bsp19_lightmaps.py retail/main/Pak5.pk3:maps/m1l1.bsp m1l1.bsp   # MOHAA's own light
```

`bsp19_lightmaps.py` lights the compiled BSP30 with the light MOHAA shipped, so no sdHLRAD run is needed. Each lit face gets a GoldSrc lightmap (one luxel per 16 texels), and each luxel samples the MOHAA lightmap of the coplanar MOHAA surface under it. Luxels with no MOHAA surface within 24 units take their face's average, and a face with no coplanar MOHAA surface at all (one the conversion made up) samples the nearest MOHAA surface facing its way within 96 units, or failing that gets the map's average light rather than a flat grey that glows at night. MOHAA stores light one overbright bit down, so samples are doubled, and the default `--gain` of 2.5 adds a little more because at 2.0 the night towns of m1l1 read too dark on the GameCube. Without a lighting lump the map draws fullbright, and on the GameCube the models drew black. Like every converter step, it runs on the user's own install.

`bsp19_lightgrid.py` copies MOHAA's light grid (the colours retail lights soldiers and other models with, one per 32 units) to `media/lg_<map>.gcg`, keeping MOHAA's run-length layout so the GameCube engine can sample it from ARAM. Its colours are scaled to match the lightmaps.

The maps stage resolves each BSP's sky shader through the retail `scripts/sky.shader`, reads its six `skyParms` environment images from the paks, and writes 128x128 GameCube CMPR faces as `media/sky_<env><side>.cmp`. It also writes that environment root as the compiled map's `skyname`. For example, m1l2a's `textures/sky/africanight` resolves to `env/mohnight1`, avoiding the renderer's clear-colour fallback when the source BSP has no GoldSrc `skyname` key.

The `hud` stage reads retail `textures/hud/*.tga` art from the paks and writes one-frame Xash3D version-32 RGBA sprites under `sprites/mohaa/`. The low-memory GameCube HUD path draws the retail health gauge, ammo arm pieces, ammo readout, and crosshair from these sprites, keeping the source alpha edges intact for the GX texture path. Select it with `--stages hud` or include it when rebuilding maps with `--stages hud,maps`.

Writes a Valve-220 .map that SDHLT compiles to BSP30. Stage one only covers brushes:

- Every brush is rebuilt from its planes. Bevel and duplicate planes drop out, and the world is scaled by `--scale` (default 72/94).
- MOHAA detail brushes go into one `func_detail`. Caulk/nodraw becomes `NULL`, clip becomes `CLIP`, sky becomes `sky`, water becomes `!water`.
- Doors and script objects are written as brush entities. Rotating doors get an `ORIGIN` brush. MOHAA player starts become DoD spawns, lifted onto GoldSrc's hull.
- Brushes SDHLT would reject are fixed or dropped and counted: slivers under 1.1 units thick are inflated to 1.1 (dropping them opened leaks), flat ones are dropped, runaway brushes past ±32000, and sides that sdHLCSG would read as the same plane as another side. Sky faces on brush entities become `NULL`. `func_rain` volumes become `func_illusionary` with `zhlt_noclip`. Detail brushes with sky stay in the world.
- Inflated detail slivers go into `func_wall` entities, one per 1024-unit cell, instead of `func_detail`. Each one in `func_detail` cost 6 to 13 world leaves (m4l3: +44% world leaves, obj_team3: +62%). As separate brush models they are drawn, stop bullets, and are culled by cell. They carry `zhlt_noclip` (each sliver cost about 40 clipnodes as its own model), and a `CLIP` copy of each sliver in the world blocks players instead (voxelized when `--simplify-collision` is on and it is angled). `--thin-detail-in-world` restores the old behaviour. `--detail-walls` does the same for all detail brushes (walls whose brushes are all `NULL` are not written: nothing to draw, players still collide with the CLIP copy, bullets pass; `--wall-cell` sets the cell size; larger cells mean fewer brush models, SDHLT allows 512, and less tree overhead), to cut world leaves on maps over the 8192 limit (angled ones collide through voxel boxes under `--simplify-collision`). Inflation grows every source plane, so a sliver whose end caps were too small to keep a face stays closed.
- MOHAA terrain is not a brush, so every terrain patch gets a `NULL` column underneath it to stop hull 0 leaking. Turn this off with `--no-terrain-seal`. `--terrain-brushes` also writes the terrain surface as `CLIP` wedges. They only affect the player hulls, but they cost a lot of clipnodes: m3l1a needs about 37k extra raw clipnodes even at `--terrain-tol 32`.
- Terrain and curved patches collide through the same engine mesh. MOHAA LOD terrain is not a brush, and patches are not brushes either, so both used to have no player collision (under terrain you landed on the seal columns). By default every terrain patch goes into `<out>.mcol` as an exact 9 x 9 heightfield (format 3, about 112 bytes per patch), the way MOHAA's cm_terrain stores it; the engine builds each cell's two wedges during the sweep. Every solid world patch goes in as thin prisms, tessellated within about `--mesh-patch-tol` (2 units), the way Quake 3 collides with patches. `--no-mesh-terrain` and `--mesh-patch-tol 0` turn them off. `--terrain-brushes` (clipnode terrain) replaces the mesh terrain.
- Player starts are lifted out of the engine mesh. MOHAA puts a spawn origin at the feet on the terrain, so the corners of GoldSrc's 32 x 32 box can sit inside rising ground, and a stuck spawn never spawns anyone. When the mesh holds a start inside, the converter drops the box from 128 units above and places it where it lands (stats `player_starts_lifted`, and `player_starts_stuck` when that still fails).
- Unnamed static brush models merge. MOHAA maps carry hundreds of `script_object` brush models, and GoldSrc allows 512 models in all (m5l2b had 435 brush models alone). Each one with no targetname, target or angles goes into one `func_wall` per `--wall-cell` cell (stats `static_brush_models_merged`, `static_brush_model_walls`). Scripts can't reach those, so nothing changes in play. `--keep-brush-models` keeps every model. Triggers that share every key (same setthread, wait and so on) and have no targetname become one trigger, since touching any of its brushes fires it the same way; a `trigger_once` stays on its own (stats `triggers_merged`). With `--scripts <MOHAA main or pk3>` the converter reads the level's scripts (maps/<map>.scr and the global scripts it pulls in) and drops each targetname that no script word and no entity target uses, so those entities merge too (stat `targetnames_unused`). A name a script could build from a number, like `"crate_" + local.i`, stays. Brush models that share every key, name included (exploder pieces of one set, say), become one entity too, since scripts move or hide them together through `$name` (stat `same_key_models_merged`). An `exploderchunk`'s own target only aims it, so chunks of one set merge even when each aims elsewhere, and fly as one piece at the first chunk's target (m5l2b had 259 of them). The other chunks' aim points then need no entity, so they are dropped too (m5l2b's ran it out of edicts). A set whose first chunk has no target takes the first one that does. Named points that a script reaches by `$name` are written right after worldspawn (stat `script_points_first`), since the engine keeps only as many `info_target`s as its edict budget allows, in file order.
- `tools/props_models.py MAIN <map>.props -o <map>.mprop` packs those props for the engine: each model's posed LOD 0 mesh (`tools/mohaa_skd.py` reads `.tik`, SKMD `.skd` and the idle `.skc`), its textures at no more than 128 pixels a side in 8-bit palettes (index 255 is transparent for alpha-tested leaves), and every instance. The pack is built from retail data, so keep it out of git.
- Static models (MOHAA's trees, rocks and props in LUMP_STATICMODELDEF) go to a `<out>.props` sidecar, one line each: origin, angles and model scale converted, then the `.tik` path. They take no edict and no model slot; the engine is meant to draw them from that list. Their collision is already in the map, since MOHAA ships clip brushes around them.
- `--simplify-collision`: angled detail and clip brushes stop colliding. Detail brushes are still drawn, from a `zhlt_noclip` `func_detail`. Their volume is voxelized on `--collision-grid` (16 units by default, under GoldSrc's 18-unit step) and greedy-merged into axial `CLIP` boxes. Benchmark with 1,500 randomly angled beams: planes went from 91k to 10k and clipnodes from 135k to 117k. `--collision-aabb FILL` gives an angled brush its own bounding box instead of voxels when it fills at least FILL of that box or is smaller than a cell (exact for small debris and near-axial pieces). `--mesh-collision` (with `--simplify-collision`) writes reachable angled brushes to `<out>.mcol` (`tools/mesh_collision.py`: angled planes, brushes whose bounds serve as their axial planes and bevels, a BVH). xash3d-gc sweeps player and monster boxes against them the way Quake 3/MOHAA collision does, so slopes are exact and cost no clipnodes. `--collision-exact UNITS` keeps exact CLIP collision for angled brushes at least UNITS long (a big slope is a few planes exact but hundreds of voxel steps). `--collision-reach UNITS` skips player collision for angled detail further than UNITS from every path node and player start. That spends the clipnode budget where players can go, so the reachable part can use a finer grid. `--collision-grid-z` sets the vertical cell on its own, so xy can be coarser (fewer boxes) while voxel slopes stay climbable steps under 18 units.
- Leak fallbacks: `--detail-world` writes MOHAA detail brushes into worldspawn, because `func_detail` never seals in SDHLT. `--seal-box` wraps the whole map in a `NULL` box.
- `--wad` writes placeholder textures (a flat checker per name) so SDHLT can compile without the real art.

Not handled yet: texture alignment (Q3-family brush sides store none, so faces are box-projected), curved patches, terrain and static models (render bake plus engine mesh collision), triggers, and point entities other than player starts.

## Compiler: SDHLT with 32-bit clipnodes

Stock BSP30 tops out at 32,767 clipnodes, and 15 MOHAA maps go over it. `third_party/sdhlt-bsp30ext/` holds a GPL-2 patch for SDHLT that writes those maps in Xash3D's BSP30ext layout, which xash3d-gc already loads. Maps under the limit still come out as stock BSP30. `tools/bsp30_check.py` reads either layout, checks the hulls, and samples hull contents at a point.

```bash
third_party/sdhlt-bsp30ext/build.sh /tmp/sdhlt
python3 tools/bsp30_check.py m1l2a.bsp --point 0 0 40 1
```

## In-game cutscenes

MOHAA scripts and baked model tags can advance the m1l1 opening truck path in Dolphin. The scripted GMC and Opel truck models export their SKC sequences and TIKI surface states, and `anim` commands select the matching Studio sequence/bodygroups. The latest isolated DOL has run through the m1l2b listenserver: it reaches map-ready, connects its local client, and draws the first-person weapon and HUD. That frame is very dark, and the isolated engine source has no canonical Git metadata. See the [m1l2b runtime capture](media/2026-11-23-m1l2b-current-runtime/README.md), [cutscene status](docs/MOHAA_CUTSCENE_STATUS.md), and [m1l1 tag-motion evidence](media/2026-11-22-m1l1-tag-arena/README.md).

The current project-history and progress talk is [available as a PDF](output/pdf/mohaa-gamecube-progress-2026-11-23.pdf), with its [full speaker script](output/presentation/mohaa-gdc-narration.txt). The full nine-slide talk is available as a [narrated video](output/presentation/mohaa-gdc-progress-narrated.mp4) and [audio track](output/presentation/mohaa-gdc-narration.mp3), rendered locally with Qwen3-TTS 1.7B CustomVoice.

`tools/mohaa_tiki_model.py` can bake a TIKI mesh, skeleton, named SKC sequences and per-sequence surface visibility into a GoldSrc Studio v10 MDL. For example, write the output into a temporary game tree; generated models contain retail data and must stay out of Git:

```bash
python3 tools/mohaa_tiki_model.py retail/main \
  --model vehicles/gmctruck_opening.tik \
  --out /tmp/mohaa-script-models/models/vehicles/gmctruck_opening.mdl
```

The exporter supports Xash's four-influence Studio v10 skinning format and up to 31 surface bodygroups. It reads animation aliases through included TIKIs; repeat `--animation <alias>` to keep a small mission-specific sequence set. When a vertex has more than four influences, it keeps the four strongest and renormalizes them. Models with an unsupported skeleton fall back to a posed static model. The script-entity sequence binding is in the GameCube DOL; direct visual confirmation still needs an m1l1 runtime capture.

The m1l1 German Afrika private TIKI exports as a composite Studio model: body, covered head, hands, helmet, loadout, and KAR clip share a 72-bone rig. The stage keeps all ten m1l1 actor aliases used by the retail script, from `opel_driver` through the kill, get-visa, and idle-visa animations. It splits the actor into an MDL core, external skin, and hashed GameCube animation pack so all ten retail sequences stay intact while the core fits the engine's lean per-file limit. A direct split of the current model produced a 177,632-byte core, 66,632-byte external skin, and 308,864-byte animation pack. The matched m1l1 Dolphin run loaded the external skin and GCA pack and submitted draw calls for the actor. The class-picker capture does not yet prove correct appearance, animation, or cutscene motion. Evidence: [m1l1 actor runtime capture](media/2026-11-23-m1l1-actor-runtime/README.md).

To stage the visible m1l1 trucks, configured scripted actors, and `maps/m1l1.models` on an SD card, use:

```bash
python3 tools/mohaa_sd.py --mohaa ~/MOHAA --sd /media/SDCARD \
  --maps m1l1 --stages scriptmodels --list
```

The GameCube game code precaches the manifest at `ServerActivate`; matching TIKIs are assigned to script entities and tracked mission actors. Current runtime evidence confirms m1l2b boot, local listenserver connection and first-person HUD/weapon drawing, but does not confirm the m1l1 truck or actor models animating.

## Mission scripts

`script/` holds a clean-room, MIT-licensed VM for MOHAA's `.scr` (Morpheus)
scripting language, written in C99 for the GameCube build. Script commands
are bound to DoD-GC entities by the game code. See [script/README.md](script/README.md).

```bash
make -C script && out/msrun tests/scripts/mission.scr      # mock-world run
python3 tools/check_scripts.py "/path/to/MOHAA/main"      # compile every retail script
python3 tools/ubersound.py "/path/to/MOHAA/main" --out /tmp/mohaa-sound --wav   # per-map sound tables + 22 kHz mono wavs
```

## Tests

```bash
python3 -m unittest discover -s tests
```

The script VM tests build `out/msrun` with the system C compiler.
`tests/make_sample_bsp.py` writes a small synthetic MOHAA BSP (v17 or v19), so
the tests need no game data.

## References

The reader is written from the BSP struct layouts documented in
[OpenMoHAA](https://github.com/openmoh/openmohaa)'s `code/qcommon/qfiles.h`.
No code is copied from GPL projects.

## Per-map flags

`tools/map_flags.txt` lists the converter flags each retail map needs to fit the GameCube limits. Those limits are at most 32767 clipnodes, at most 8192 world leaves, and a BSP of at most 3 MiB without its lighting lump. Compile every map with `sdHLBSP -hull2alias`. Collision uses the finest voxel grid that fits each map. The 64 to 96-unit grids on the m6 maps, m3l3, m4l1, m4l2, m5l2b and m5l3 still need a Dolphin playtest.

## DoD-GC fork

`dod-gc/` is a full copy of the DoD-GC game tree. MOHAA's game-side code (script binding,
soldiers, path nodes, music) is developed there; see `dod-gc/FORK.md`.

Staging a level: `tools/stage_scripts.py <main> --out <disc> --maps m1l1` copies the map script and
every `global/*.scr` it pulls in. `tools/ubersound.py` stages sounds, `tools/music.py` stages
music, and `tools/bsp19_to_map.py` converts the map (`.map`, `.nodes`).
