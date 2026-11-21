# mohaa-gc

Medal of Honor: Allied Assault content brought into **DoD-GC** (GoldSrc on
GameCube). This is an asset port, not an engine port: MOHAA maps, models and
missions are converted into formats the existing dod-gc runtime already plays.

No retail game data lives in this repository. Point the tools at your own
copy of the game's `.pk3` files.

## Map pipeline (planned)

```
MOHAA .bsp ("2015" v19)
   -> BSP19 reader                     tools/mohaa_bsp19.py
   -> Valve-220 .map (brushes scaled ~0.77, clip proxies for patches/terrain)
   -> SDHLT csg/bsp/vis/rad -> BSP30   dod-gc tools/mapbridge
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
sdHLCSG m1l1.map && sdHLBSP m1l1.map      # fast fullbright loop; add sdHLVIS / sdHLRAD later
```

Writes a Valve-220 .map that SDHLT compiles to BSP30. Stage one only covers brushes:

- Every brush is rebuilt from its planes. Bevel and duplicate planes drop out, and the world is scaled by `--scale` (default 72/94).
- MOHAA detail brushes go into one `func_detail`. Caulk/nodraw becomes `NULL`, clip becomes `CLIP`, sky becomes `sky`, water becomes `!water`.
- Doors and script objects are written as brush entities. Rotating doors get an `ORIGIN` brush. MOHAA player starts become DoD spawns, lifted onto GoldSrc's hull.
- Brushes SDHLT would reject are fixed or dropped and counted: slivers under 1.1 units thick are inflated to 1.1 (dropping them opened leaks), flat ones are dropped, runaway brushes past ±32000, and sides that sdHLCSG would read as the same plane as another side. Sky faces on brush entities become `NULL`. `func_rain` volumes become `func_illusionary` with `zhlt_noclip`. Detail brushes with sky stay in the world.
- Inflated detail slivers go into `func_wall` entities, one per 1024-unit cell, instead of `func_detail`. Each one in `func_detail` cost 6 to 13 world leaves (m4l3: +44% world leaves, obj_team3: +62%). As separate brush models they are drawn, stop bullets, and are culled by cell. They carry `zhlt_noclip` (each sliver cost about 40 clipnodes as its own model), and a `CLIP` copy of each sliver in the world blocks players instead (voxelized when `--simplify-collision` is on and it is angled). `--thin-detail-in-world` restores the old behaviour. `--detail-walls` does the same for all detail brushes (walls whose brushes are all `NULL` are not written: nothing to draw, players still collide with the CLIP copy, bullets pass; `--wall-cell` sets the cell size; larger cells mean fewer brush models, SDHLT allows 512, and less tree overhead), to cut world leaves on maps over the 8192 limit (angled ones collide through voxel boxes under `--simplify-collision`). Inflation grows every source plane, so a sliver whose end caps were too small to keep a face stays closed.
- MOHAA terrain is not a brush, so every terrain patch gets a `NULL` column underneath it to stop hull 0 leaking. Turn this off with `--no-terrain-seal`. `--terrain-brushes` also writes the terrain surface as `CLIP` wedges. They only affect the player hulls, but they cost a lot of clipnodes: m3l1a needs about 37k extra raw clipnodes even at `--terrain-tol 32`.
- `--simplify-collision`: angled detail and clip brushes stop colliding. Detail brushes are still drawn, from a `zhlt_noclip` `func_detail`. Their volume is voxelized on `--collision-grid` (16 units by default, under GoldSrc's 18-unit step) and greedy-merged into axial `CLIP` boxes. Benchmark with 1,500 randomly angled beams: planes went from 91k to 10k and clipnodes from 135k to 117k. `--collision-aabb FILL` gives an angled brush its own bounding box instead of voxels when it fills at least FILL of that box or is smaller than a cell (exact for small debris and near-axial pieces). `--collision-exact UNITS` keeps exact CLIP collision for angled brushes at least UNITS long (a big slope is a few planes exact but hundreds of voxel steps). `--collision-reach UNITS` skips player collision for angled detail further than UNITS from every path node and player start. That spends the clipnode budget where players can go, so the reachable part can use a finer grid. `--collision-grid-z` sets the vertical cell on its own, so xy can be coarser (fewer boxes) while voxel slopes stay climbable steps under 18 units.
- Leak fallbacks: `--detail-world` writes MOHAA detail brushes into worldspawn, because `func_detail` never seals in SDHLT. `--seal-box` wraps the whole map in a `NULL` box.
- `--wad` writes placeholder textures (a flat checker per name) so SDHLT can compile without the real art.

Not handled yet: texture alignment (Q3-family brush sides store none, so faces are box-projected), curved patches, terrain and static models (render bake plus engine mesh collision), triggers, and point entities other than player starts.

## Compiler: SDHLT with 32-bit clipnodes

Stock BSP30 tops out at 32,767 clipnodes, and 15 MOHAA maps go over it. `third_party/sdhlt-bsp30ext/` holds a GPL-2 patch for SDHLT that writes those maps in Xash3D's BSP30ext layout, which xash3d-gc already loads. Maps under the limit still come out as stock BSP30. `tools/bsp30_check.py` reads either layout, checks the hulls, and samples hull contents at a point.

```bash
third_party/sdhlt-bsp30ext/build.sh /tmp/sdhlt
python3 tools/bsp30_check.py m1l2a.bsp --point 0 0 40 1
```

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
