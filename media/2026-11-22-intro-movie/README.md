# MOHAA intro movie on DoD-GC: Dolphin runs, 2026-11-22

The engine is xash3d-gc 0f8fd6a (the A/B/Start cinematic skip). Discs are menu discs built from mohaa-gc 94b04a3 (gamedir dod), with the hlsdk at its pin 0e324da.
The Dolphin build is ~/xash3d-gc-hl1/3rdparty/dolphin/build/Binaries/dolphin-emu (7c9d49d63d). Each run used its own user dir. Pad 1 is a Dolphin input pipe.

Neither Dolphin on ceres emulates a GameCube SD adapter. For the A runs, the converted movie
(tools/mohaa_sd.py movie stage) went onto a test-only disc through DODGC_CONTENT_EXTRA.
The release layout, read from sd:/, is not tested here.

| Files | Run | Result |
| --- | --- | --- |
| 01-* | B: no movie on the disc | The log reads "startup video payload missing media/mohaa_intro.avi", then "activating menu without startup cinematic". The menu is up about 1 s after boot. |
| 02-* | A: movie at 320x160 (the converter's default) | The GCVID opens (320x160, 2503 frames) and the native intro audio plays. **The picture is black for the whole intro**, in both the window capture and Dolphin's own frame dump. This is an engine bug in the non-240 upload path. No A press reached the engine in this run (harness bug: the pipe device name was wrong). |
| 03-* | A: the same movie re-encoded at 320x240, A pressed at 20 s | The intro plays with picture and sound at 15 fps on schedule (frame 123 at 8.26 s). The log reads "cinematic skipped by A_BUTTON", then "activating menu after cinematic", then "gc_menu_ready set 1", all within the same second. |

Timing for run 03 is in 03-run-timing.txt: recording started 2.0 s after Dolphin launched, and A was sent at 20.26 s into the recording.

## Final runs on the mohaa game folder (04–06)

Engine: xash3d-gc 4f74253. Repo: mohaa-gc da3512e (DODGC_GAME=mohaa). The disc's game folder is mohaa/ over dod/.
The log shows `linked gamedir=mohaa detected=valve,dod,mohaa` and `GCFS_LoadGameInfo( mohaa ... )`.
The movie comes from tools/mohaa_sd.py (movie stage): a letterboxed 320x240 frame, 2503 frames, 137.9 MB, 0.83 MB/s.
Test discs carry it through DODGC_MOHAA_TEST_DIR, because Dolphin has no SD adapter.

| Files | Run | Result |
| --- | --- | --- |
| 04-* | B: no movie | The log reads "startup video payload missing media/mohaa_intro.avi", then "activating menu without startup cinematic". The menu is up about 1 s after boot. **No sound:** the recording and Dolphin's DSP dump are both at -91 dB, although the log says "DoD music stream open=1". Run 01 (the dod build without the intro) is silent the same way, so this isn't new with mohaa. |
| 05-* | A: test movie, A pressed at 20.26 s | The intro plays with picture (letterboxed) and sound. The log reads "cinematic skipped by A_BUTTON", then "activating menu after cinematic", then "gc_menu_ready set 1". The menu music starts right after the skip; gamestartup.wav matches the recording at 20.5 s. |
| 06-* | A: test movie, 65 s, no press | The intro keeps playing on schedule (frame 120 at 8.00 s). **No overlap:** gamestartup.wav does not match anywhere in the 65 s recording (best ncc 0.085), while it matches clearly after the skip in run 05 (ncc 0.87–0.98). |

**Menu looks different under mohaa (04, 05):** it isn't the DoD menu anymore. A white block sits where the logo goes. The items are the Half-Life single-player list (New game, Load game, Configuration, Quit) instead of DoD's (New game, Find servers, Options), on a plain blue background. Compare 04-menu-10s.png with 01-runB-menu.png.

## Menu fix runs (07–08)

Built from mohaa-gc 005e15b with engine 4f74253. The mohaa/ disc now gets DoD's menu sources.

| Files | Run | Result |
| --- | --- | --- |
| 07-* | A: test movie, A at 20.26 s, then about 15 s on the menu | Log: "cinematic skipped by A_BUTTON", then "activating menu after cinematic", then "gc_menu_ready set 1", "retail menu steam background ready tiles=4" and "ImageLib TGA resource/gc_menu/logo.tga src=512x32". The menu music plays after the skip (peak -0.1 dB). |
| 08-* | B: no movie, about 20 s | "startup video payload missing media/mohaa_intro.avi", then "activating menu without startup cinematic". Same DoD menu. Still silent (-91 dB), even though the log now shows "DoD music mixed bytes=8192". This is the older issue from before this work. |

**Menu now matches the dod build** (07-08-menu-compare-01dod-04old-07-08new.png: 01 dod, 04 mohaa before the fix, 07 and 08 mohaa after the fix):
- Same DoD soldier background.
- Same "New game / Find servers / Options" list.
- Same DAY of DEFEAT logo.

Small differences remain:
- The item text has slightly wider letter spacing ("Find ser vers").
- The version line reads "UI 5d37ca0b10+ !" instead of "UI 5d37ca0b10". The "+" marks the integration-patched mainui; the "!" was already there in 04.

`share/` holds smaller copies of runs 04–08 (H.264 + AAC, 640x480 or less), plus the stills and logs.
