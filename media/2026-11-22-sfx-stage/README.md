# MOHAA campaign SFX staging audit — 2026-11-22

Ran the campaign SFX stage against the installed MOHAA files and both local
retail CDs. The stage extracted InstallShield's separate ambience, mechanics,
vehicle, weapons, and dialogue groups while preserving dialogue subdirectories.

Command:

```sh
python3 tools/mohaa_sd.py --cd retail/cd/disc1 retail/cd/disc2 \
  --sd /tmp/mohaa-sfx-prefix-20261122 \
  --work /tmp/mohaa-sfx-prefix-work-20261122 \
  --stages sounds --list
```

Result: 37 map sound tables scanned; 378 referenced samples converted; 2
skipped because their sources are absent from the local retail install/CDs:
`sound/mechanics/moh_cello3.wav` and `sound/mechanics/moh_cello4.wav`.
Three scripted MP3 samples were decoded by ffmpeg and written as GameCube-friendly
22.05 kHz mono 16-bit PCM WAVs:

- `sound/mohaa/music/medicdance.wav`
- `sound/mohaa/music/mus_aircraftfacility.wav`
- `sound/mohaa/music/mus_berlin.wav`

The generated `.snd` tables reference these WAV paths. The three WAV headers
were inspected; `medicdance.wav` contains the loop cue used by GoldSrc.

The converter's resolver now follows MOHAA's prefix lookup: the exact alias and
non-underscore suffix variants are candidates together, while underscore suffixes
start separate alias families. The local OpenMOHAA reference implementation
(`code/qcommon/alias.c`, `Alias_ListFindRandom`) uses this rule. This restored the
`arty_leadin08` sample to the `arty_leadin` family on `m3l1a`, `m3l1b`, and `m5l3`;
the regenerated tables reference and include its converted WAV. `m3l1a` now lists
103 distinct samples, above the tool's advisory budget of 96.

The audit still reports unresolved script aliases: `sanford_and_son`,
`den_m2l2_258b`, `wave_laps`, `dfr_panic_35c_13`, `flak88_hit`, `temp`,
`dfr_m5l3_add01`, `radio_watchout`, and `gate_large_open`. The repeated
`dfr_panic_35c_13` occurs on two maps. These remain unresolved rather than being
assigned invented sounds. The DoD runtime has a larger 512-sample channel pool,
but this map's runtime behavior still needs validation.

The generated stage was written under `/tmp` and removed after this audit.
Retail assets and converted audio are not committed. No test suite or hardware
playback was run; runtime SFX playback, unresolved aliases, and the two missing
cello sources remain open.
