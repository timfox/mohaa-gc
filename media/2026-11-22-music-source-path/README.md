# MOHAA music staging source audit, 2026-11-22

The earlier full-stage command used `--mohaa ~/Desktop/mohaa-gc/retail`. That selected
`retail/main` for the PK3 mood tables and scripts, but the extracted loose audio lives separately
in `retail/unshield/main/sound/`. The stage therefore wrote 51 mood tables while converting 0 of
79 referenced tracks. The music stage treated that as success, leaving an incomplete stage.

`tools/mohaa_sd.py` now accepts repeatable `--music-source DIR` paths, passed only to the music
stage. They let a split retail extraction supply audio without affecting map, script, or sound
source precedence. The second null track path, `sound/amb_stereo/null.wav`, is also recognized as
an intentional no-stream sentinel.

## Conversion evidence

Ran into a temporary directory, which was removed after inspection:

```sh
python3 tools/mohaa_sd.py --mohaa retail --music-source retail/unshield/main \
  --sd /tmp/mohaa-music-source-check --stages music --list
```

Output: 51 mood tables, 79 references, 75 WAVs converted, 3 references still missing, and 1
intentional no-stream sentinel skipped. The stage produced 126 files / 355.9 MB. The m1l1 mood
table references `amb_m1_townext.wav` and `amb_m1_interior_01.wav`; both inspect as 22,050 Hz,
mono, signed 16-bit PCM. The existing SD staging tree was not modified.

The remaining source gaps are:

- `sound/amb_stereo/amb_teamdm6_trainstation_ext.mp3` — teamdm6 multiplayer mood.
- `sound/mohpc_prototype_music/the_jet_aircraft_facility.mp3` — prototype mood.
- `sound/music/mus_snipertown_01e.mp3` — referenced by campaign script `maps/m5l1b.scr`.

No local copy of these files was found in the retail tree or `/mnt/datasets/mohaa-gc-run`.
The m5l1b cue remains an unresolved campaign audio gap; no replacement audio was synthesized.
