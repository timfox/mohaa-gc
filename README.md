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
| `clipnodes` | 32,767 | Estimate = collision brush sides x `--clipnodes-per-side` (0.5, **uncalibrated**) |
| `world_coord` | 4,096 | Largest absolute coordinate after `--scale` (default 72/94) |
| `models` | 400 | World plus brush entities |
| `entities` | 2,048 | |
| `textures` | 512 | Unique textures on drawn brush faces, patches and terrain |
| `faces_est` | 65,535 | Drawn brush sides before BSP splitting, so a low bound |
| `brushes` | 32,768 | Converted brushes plus patch and terrain proxies |

Status is `OK` below 70% of a limit, `TIGHT` from 70% to 100%, `OVER` above.
The defaults are stock Half-Life / SDHLT values. xash3d-gc may allow more;
override with `--limit name=value` once its real values are confirmed.

Known gaps: the clipnode factor needs calibrating against real SDHLT runs, and
the report does not yet predict the compiled BSP30 size against the engine's
3 MiB map buffer.

## Tests

```bash
python3 -m unittest discover -s tests
```

`tests/make_sample_bsp.py` writes a small synthetic MOHAA BSP (v17 or v19), so
the tests need no game data.

## References

The reader is written from the BSP struct layouts documented in
[OpenMoHAA](https://github.com/openmoh/openmohaa)'s `code/qcommon/qfiles.h`.
No code is copied from GPL projects.
