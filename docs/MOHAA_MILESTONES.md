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

- 2026-11-25 continuation: the latest `dontdropweapons` implementation produced an isolated 7.54 MB DOL and 123 MiB m1l1 smoke ISO. A bounded 25-second Flatpak Dolphin attempt returned an empty OSReport and no guest render window; this build has no gameplay validation yet. Probe note: [m1l1 dontdrop probe](../media/playtests/notes/20261125-105727-m1l1-dontdrop.md).

- M0: an isolated direct m1l1 run now loads all seven MOHAA HUD sprites, completes client redraws, and visibly draws the health/ammo HUD while loading and drawing all six `mohnight1` sky faces. The screenshot also shows the m1l1 class picker over the running map. Evidence: [HUD and sky direct-map probe](../media/playtests/notes/20261123-232953-mohaa-hud-direct-map.md). Full existing-implementation certification and physical hardware validation remain open.
- M1: the stage resolves all 37 retail maps; 19 maps map to eight real cubemaps (48 CMPR faces), and 18 previously staged BSPs now have their skyname. The 2026-11-24 far-plane fix and smoke-ISO sky-face staging now produce visible cubemap draws on m1l1 (`mohnight1`), m1l3a (`mohnightfog`), and Training (`mohday2`). Fourteen maps reference the missing retail root `idontexist` and are left without a skyname. Broader map conversion, collision coverage, five remaining real sky roots, and physical hardware validation remain open.
- M2: m1l1 scripted `walkto` advances; complete cutscene/event parity is not yet certified. On m1l2a, the script-inclusive smoke ISO runs the retail `hint_door` trigger, executes `iprintlnbold`, and displays the expected single-line instruction beneath the compass. Evidence: [probe note](../dod-gc/playtests/notes/20261124-181420-mohaa-retail-tip-proof.md) and [matched screenshot](../dod-gc/playtests/screenshots/20261124-181420-mohaa-retail-tip-proof/matched.png). An isolated Xash3D-GC build now loads the 263.86 KiB m3l1a and 259.87 KiB m3l3 scripts through map-arena scratch and reaches world-render-ready on both maps. Retail `prespawn` execution and farplane appearance still need a GUI capture. See [script VM validation](MOHAA_SCRIPT_VM_VALIDATION_2026-11-25.md). Full campaign scripting and cutscene/event parity remain open.
- M4: the German actor MDL and 10-sequence GCA pack load. Correct visible sequence playback and bodygroup fidelity remain open.
- M5: m1l1, m1l3a, and Training now show three retail GX cubemaps at runtime, including maps with MOHAA fog far planes. The same probes visibly retain other world-rendering gaps; full GX/material and audio parity remains open.
- M6: MOHAA-specific spill behavior has isolated build/runtime evidence; native GameCube performance remains unverified.

The current detailed cutscene evidence and open checks are in [MOHAA_CUTSCENE_STATUS.md](MOHAA_CUTSCENE_STATUS.md). The capture archive and index are in [media/playtests](../media/playtests/).


## Progress estimate (2026-11-25)

The port is **about 39% complete by weighted milestone evidence**. This is a planning estimate, not a measured code-completion statistic. Critical milestones count twice; High milestones count once. Fractions reflect stated scope and give runtime evidence more weight than build-only evidence.

| ID | Weight | Evidence fraction | Current basis |
|----|--------|-------------------|---------------|
| M0 | 2 | 0.60 | HUD, sky, retail door-tip, and selected runtime paths are evidenced; full existing-implementation and hardware certification remain open. |
| M1 | 2 | 0.60 | All 34 campaign maps have staged BSP, mesh-collision, and path-node files; map-wide structural, collision, and gameplay validation is incomplete. |
| M2 | 2 | 0.45 | Selected retail script commands and m1l1/m1l2a events work; campaign-wide event and cutscene parity is incomplete. |
| M3 | 2 | 0.12 | Scripted grunts honor integer threat priority and `ignoreme` when choosing between co-op players; campaign AI and actor-vs-actor behavior remain unassessed. |
| M4 | 1 | 0.40 | Actor/model assets load; visible animation, bodygroups, and weapon fidelity need broader validation. |
| M5 | 1 | 0.50 | Three sky roots and core HUD render; broad GX materials, effects, and audio remain incomplete. |
| M6 | 2 | 0.30 | Isolated memory/spill improvements have runtime evidence; stable campaign budgets and physical hardware performance remain open. |
| M7 | 2 | 0.35 | Individual maps and scripted interactions are playable in probes; a verified campaign vertical slice is not demonstrated. |
| M8 | 1 | 0.15 | Full campaign expansion/release is not assessed; broad parity and hardware gates remain open. |

Calculation: `(2×.60 + 2×.60 + 2×.45 + 2×.12 + .40 + .50 + 2×.30 + 2×.35 + .15) / 15 = 0.393`, rounded to **39%**. Keep this estimate until campaign-wide evidence changes the milestone fractions.

### Campaign map artifact coverage audit (2026-11-25)

The retail stage contains 37 map-list entries: 34 campaign maps plus `training`, `credits`, and `void`. Every campaign map has a converted BSP, `.mcol` mesh-collision sidecar, and `.nodes` path graph. Across all 37 entries, BSP coverage is 37/37, `.mcol` is 35/37, and `.nodes` is 34/37. Structural checks passed for all 34 campaign BSPs and collision sidecars. These checks establish file structure and references, not in-game collision fidelity. Retained runtime map evidence is concentrated on m1l1 and m1l2a, with startup/sky probes on m1l3a and Training; per-map traversal, collision, campaign flow, frame pacing, and retail hardware remain open.

### Script-model coverage audit (2026-11-25)

The staging tool reads each selected retail BSP and recursive map/global script closure, normalizes actor keys, and collects TIKIs named by BSP placements and explicit script model/spawn commands before building a map-local precache manifest. A full retail-PK3 staging audit resolved 163 distinct drawable TIKIs across 37 maps (414 map/model pairs). Before the latest recipe pass, only six map/model pairs on two maps were configured. The most reused unresolved TIKIs include `human/german_wehrmact_soldier.tik` (25 maps) and `human/1st-ranger_captain.tik` (16). The `m3l1a` script closure also reports a missing `global/ai_off.scr`, so its discovered model list may be incomplete until that dependency is available.

The latest pass adds the German shepherd as a shared map recipe, correcting its retail animation path and staging all 29 aliases into a 100,832-byte GCA pack. One model/skin set is baked once and referenced from all 17 maps that use the dog. The m1l1 and m1l2a scripts also share the same retail German Afrika private MDL path; the stage now bakes their union of 20 bounded aliases once instead of overwriting that path with incompatible per-map variants. The captain/private cores remain 213,380 and 202,188 bytes with 66,632-byte skins and separate 343,712-byte GCA packs. The full pass emitted manifests for 17 maps and 23 map/model pairs across six unique TIKIs; all referenced models and GCA sidecars were copied into `retail/mohaa-full-stage-20261122/xash3d/mohaa/` and a coverage check found no missing model/GCA files. A new [1.1 GB m1l1 test ISO](../media/playtests/notes/20261125-095000-m1l1-dog-full-stage-iso-build.md) contains the updated six-model manifest and sidecars. Dolphin still could not initialize a guest render in the current desktop session, so actor appearance and sequence playback remain unverified. The other 157 unique TIKIs and campaign-wide runtime validation remain open.
