# MOHAA campaign SFX staging audit — 2026-11-22

Ran the campaign SFX stage against the installed MOHAA files and both local
retail CDs. The stage extracted InstallShield's separate ambience, mechanics,
vehicle, weapons, and dialogue groups while preserving dialogue subdirectories.

Command:

```sh
python3 tools/mohaa_sd.py --cd retail/cd/disc1 retail/cd/disc2 \
  --sd /tmp/mohaa-sfx-resample-20261122 \
  --work /tmp/mohaa-sfx-resample-work-20261122 \
  --stages sounds --list
```

Result: 37 map sound tables scanned; 379 referenced samples converted; 2
skipped because their sources are absent from the local retail install/CDs:
`sound/mechanics/moh_cello3.wav` and `sound/mechanics/moh_cello4.wav`.
Three scripted MP3 samples were decoded by ffmpeg and written as GameCube-friendly
22.05 kHz mono 16-bit PCM WAVs:

- `sound/mohaa/music/medicdance.wav`
- `sound/mohaa/music/mus_aircraftfacility.wav`
- `sound/mohaa/music/mus_berlin.wav`

The generated `.snd` tables reference these WAV paths. The three WAV headers
were inspected; `medicdance.wav` contains the loop cue used by GoldSrc.

WAV and MP3 sources now pass through FFmpeg's SWR band-limited resampler before
being written as little-endian mono 16-bit PCM. The full stage produced 378
samples at 22,050 Hz and one source-preserving 18,100 Hz sample; all 379 outputs
are mono 16-bit WAVs at or below the GameCube target rate. The gate source
`GateWoodOpen_01.wav` kept its duration across conversion: 173,573 frames at
44,100 Hz became 86,786 frames at 22,050 Hz.

The converter's resolver now follows MOHAA's prefix lookup: the exact alias and
non-underscore suffix variants are candidates together, while underscore suffixes
start separate alias families. The local OpenMOHAA reference implementation
(`code/qcommon/alias.c`, `Alias_ListFindRandom`) uses this rule. This restored the
`arty_leadin08` sample to the `arty_leadin` family on `m3l1a`, `m3l1b`, and `m5l3`;
the regenerated tables reference and include its converted WAV. `m3l1a` now lists
103 distinct samples, above the tool's advisory budget of 96.

The script scanner removes `//` and `/* ... */` comments outside quoted strings
before finding calls, includes, and alias definitions. A full campaign rerun
after this change retained the same 378 conversions and two unavailable cello
sources, confirming that current live calls were preserved.

The active `gate_large_open` call on m6l3a had no active alias definition, but
the map's block-commented legacy metadata names
`sound/mechanics/GateWoodOpen_01.wav` and its `0.8 / 160 / item` parameters.
That exact WAV exists in Pak3. The converter now applies a map-scoped fallback
only when the call is live and no global alias resolves. The regenerated
`m6l3a.snd` references `mohaa/mechanics/gatewoodopen_01.wav`; the converted file
is 22.05 kHz mono 16-bit PCM.

The audit still reports unresolved script aliases: `sanford_and_son`,
`den_m2l2_258b`, `wave_laps`, `dfr_panic_35c_13`, `flak88_hit`, `temp`,
and `dfr_m5l3_add01`. The repeated `dfr_panic_35c_13` occurs on two maps. The
earlier `radio_watchout` warning came from a call inside a block comment and is
no longer reported. `wave_laps` has a same-named WAV in Pak3, but only the
underscore-delimited `wave_laps_low`, `_med`, and `_high` aliases are active, so
the converter leaves the base call unresolved. These seven aliases remain
unresolved rather than being assigned invented sounds. The DoD runtime has a
larger 512-sample channel pool, but runtime behavior still needs validation.

The generated stage was written under `/tmp` and removed after this audit.
Retail assets and converted audio are not committed. No test suite or hardware
playback was run; runtime SFX playback, unresolved aliases, and the two missing
cello sources remain open.
