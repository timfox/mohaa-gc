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

## Isolated GameCube build probe

On 2026-11-22, the staged m1l1 gameplay data was copied to
`/tmp/mohaa-audio-runtime-20261122-0945/mohaa`, then the four converted m1l1 WAVs above were
added to that temporary copy. The retail SD stage and ISO caches were not changed. A current
MOHAA DOL and 138 MB intro-only test ISO were built under that temporary directory using the
MOHAA source checkout, Xash3D-GC revision `bb5b942577`, the DoD GameCube build scripts, and the
HLSDK integration checkout. The ISO was assembled as a test disc, not a release image.

- DOL SHA-256: `e507c3f1c2377ec06dc2edbe53cb0bcb885fa2d991392f08b533fa4e032766c1`
- ISO SHA-256: `0173c74c989186f3c750f7ac88f58058a8440d8ecc0e7eecf2d917482ab4fa75`
- The ISO staging cache contains all four WAVs under `sound/mohaa/music/`.
- Dolphin could not provide runtime evidence in this environment. Direct and Xvfb launches
  could not connect to X11; an offscreen launch opened the emulator UI but produced no guest
  window or OSReport. PulseAudio capture was denied by the sandbox. Music playback therefore
  remains unverified; the build and disc content are verified only.

The first build retry also found that the temporary mainui checkout lacked its tracked `miniutl`
source directory. That directory was copied into the isolated build tree, after which the DOL
build succeeded. No submodule initialization was run, and the original `MultiEmulator` symlink was
left untouched.
