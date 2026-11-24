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

- M0: an isolated direct m1l1 run now loads all seven MOHAA HUD sprites, completes client redraws, and visibly draws the health/ammo HUD while loading and drawing all six `mohnight1` sky faces. The screenshot also shows the m1l1 class picker over the running map. Evidence: [HUD and sky direct-map probe](../media/playtests/notes/20261123-232953-mohaa-hud-direct-map.md). Full existing-implementation certification and physical hardware validation remain open.
- M1: the stage resolves all 37 retail maps; 19 maps map to eight real cubemaps (48 CMPR faces), and 18 previously staged BSPs now have their skyname. The latest retail New Game capture visibly draws the m1l1 `mohnight1` sky and logs all six CMPR faces loaded. m1l3a and training load all six faces for their distinct environments, though their current captures do not show a clear sky draw. Fourteen maps reference the missing retail root `idontexist` and are left without a skyname. Broader map conversion, collision coverage, per-root visual checks, and physical hardware validation remain open.
- M2: m1l1 scripted `walkto` advances; complete cutscene/event parity is not yet certified.
- M4: the German actor MDL and 10-sequence GCA pack load. Correct visible sequence playback and bodygroup fidelity remain open.
- M5: latest m1l1 runtime evidence covers the retail cubemap draw and visible HUD art; full GX/material and audio parity remains open.
- M6: MOHAA-specific spill behavior has isolated build/runtime evidence; native GameCube performance remains unverified.

The current detailed cutscene evidence and open checks are in [MOHAA_CUTSCENE_STATUS.md](MOHAA_CUTSCENE_STATUS.md). The capture archive and index are in [media/playtests](../media/playtests/).
