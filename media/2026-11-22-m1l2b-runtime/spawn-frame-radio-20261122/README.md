# m1l2b mission frame and radio SFX — 2026-11-22

Three local Dolphin listenserver runs isolated the script and audio issue. The earlier full-content capture opened `maps/m1l2b.scr` and `.snd` but did not execute the startup radio sounds. An event-instrumented baseline DOL confirmed `mohaa: signal prespawn` with no `signal spawn` during 50 seconds of gameplay. Xash3D-GC's lean WorldDL listen path skipped `pfnStartFrame` after the player spawned unless a film was active. That prevented the DoD game rules from calling `DodGC_MohaaThink` again.

The tracked `dod-gc/scripts/integrate-dod-gameplay.py` now enables `StartFrame` on that listen path for the `mohaa` game profile. The rebuilt DOL emitted `signal spawn`, loaded `global/items.scr` and `global/objectives.scr`, and requested the two scripted radio aliases. The first fixed disc lacked the radio WAVs and logged file misses; the next disc carried both native WAVs but `static1.wav` exceeded the 512 KiB per-sound ARAM limit. The sound converter now uses 11.025 kHz for oversized samples and preserves the loop cue. The final isolated disc contained both converted radio sounds; [the ISO audit](iso-sfx-audit.txt) records their formats and paths.

The [final OSReport](radio-native-dolphin.log) records `MAP_READY m1l2b`, `newgame world render ready`, `signal prespawn`, `signal spawn`, two `G278 sound chan=6` calls for `shortwave2.wav` and `static1.wav`, and both sounds streaming to ARAM (344.03 KiB and 301.90 KiB). The screenshot shows the first-person game still running after the sound requests:

![m1l2b first-person gameplay](/home/tim/Desktop/mohaa-gc/media/2026-11-22-m1l2b-runtime/spawn-frame-radio-20261122/m1l2b-radio-native.png)

Evidence: [baseline log](baseline-dolphin.log), [frame-fixed log](frame-fixed-dolphin.log), [final log](radio-native-dolphin.log), [DOL build](game-dol-build.log), [frame-fix build](frame-fix-build.log), and [disc build](radio-disc-build.log). The final DOL SHA-256 is `687da2aafd2e6b356ba65e8a93adc7ce4b798cc34ee3c2712f369e67f8f37a96`; the final test ISO SHA-256 is `a5ad3a3cb98e75d05716f4b4aec05daa68238c111d30be691f753bd431ed1670`. The ISO was scratch output and is not committed. Two retail WAVs were extracted and converted only in scratch, then removed. No retail audio or game data is in the commit.

Host checks: 49 integration tests, 4 ubersound tests, 14 MOHAA VM/backend tests, and `git diff --check` passed. The existing ubersound test accepts both 220 and 221 output frames for a 441-frame resampler edge; this environment's baseline FFmpeg produced 220.

The log proves script dispatch and ARAM loading, but the probe did not capture the audio output itself. Audible loop behavior, other missing DoD fallback sounds, retail visual parity, and physical GameCube validation remain open.
