# Medal of Honor: Allied Assault GameCube milestones

The order and priority below come from Tim's project direction. Use the probe archive under `media/playtests/` as the evidence trail for implementation and playtest gates. A milestone is not complete until its stated behavior has repeatable runtime evidence on the GameCube target; Dolphin results are emulator evidence, not retail-hardware certification.

| ID | Focus | Priority | Status |
|----|-------|----------|--------|
| M0 | Existing implementation certification | Critical | In progress |
| M1 | Map conversion and collision validation | Critical | In progress |
| M2 | Campaign scripting and event parity | Critical | In progress |
| M3 | GOAP and cooperative campaign AI | Critical | Not yet assessed |
| M4 | Character and weapon animation fidelity | High | In progress |
| M5 | GX rendering and audio fidelity | High | In progress |
| M6 | Memory and native hardware performance | Critical | In progress |
| M7 | Playable campaign vertical slice | Critical | Not yet assessed |
| M8 | Full campaign expansion and release | High | Not yet assessed |

## Evidence and capture policy

Every probe or playtest should retain its guest-window screenshots, periodic gameplay frames, Dolphin log, provenance note, and video when available. The MOHAA playtest wrapper captures extra frames every eight seconds by default (`MOHAA_CAPTURE_INTERVAL` changes the interval). If PulseAudio is unavailable, it records a silent H.264 video so the visual run is still reviewable; set `MOHAA_FORCE_SILENT_VIDEO=1` to select that path explicitly. Use `--skip-video` only when a still-and-log probe is intentional.

Keep raw project captures local for debugging and future work-in-progress edits. Do not publish or schedule a social video without Tim's approval. Any on-screen notes must describe real code or playtest findings; use Tim-provided music only.

## Current evidence snapshot

- M0: isolated Dolphin runs load MOHAA and reach m1l1; current probes retain build/engine/ISO provenance and OSReport.
- M1: m1l1's full maps stage now rebuilds with patched SDHLT, emits the `mohnight1` skyname and six 128×128 CMPR faces, and reaches gameplay in Dolphin with the sky visibly drawn. Its capture is archived; broader map conversion, collision coverage, and physical hardware validation remain open.
- M2: m1l1 scripted `walkto` advances; complete cutscene/event parity is not yet certified.
- M4: the German actor MDL and 10-sequence GCA pack load. Correct visible sequence playback and bodygroup fidelity remain open.
- M5: representative HUD and map captures exist; full GX/material and audio parity remains open.
- M6: MOHAA-specific spill behavior has isolated build/runtime evidence; native GameCube performance remains unverified.

The current detailed cutscene evidence and open checks are in [MOHAA_CUTSCENE_STATUS.md](MOHAA_CUTSCENE_STATUS.md). The capture archive and index are in [media/playtests](../media/playtests/).
