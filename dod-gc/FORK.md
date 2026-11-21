# DoD-GC fork for MOHAA

This folder is a full copy of the timfox/dod-gc game tree, forked at dod-gc `1a31fd6`
(main `cd8a4fb` plus the grunt spawn build fix from dod-gc #195). From here on, MOHAA work,
including changes to DoD code that MOHAA needs, lands in this folder and not in dod-gc (Tim's
call, 2026-11-21). Left out of the copy: `promo/`, `.github/` and the built `.iso`/`.dol`.

- The script VM in `src/mohaa/` is a copy of `../script/`. Refresh it with
  `scripts/sync-mohaa-vm.sh ..` after a VM change.
- Builds and tests work the same way as in dod-gc: run `scripts/integrate-dod-gameplay.py` against
  hlsdk-portable and `python3 -m pytest tests` from this folder.
- To take a dod-gc fix, copy the changed files over and note the dod-gc commit here.

MOHAA changes since the fork:
- `src/dod_mohaa_paths.h`: path nodes from `maps/<map>.nodes`, used by `dod_mohaa.c`. A
  `runto`/`walkto` order walks node to node, and the grunts only ever get straight-line orders.
- `dod_mohaa_ents.cpp`:
  - `mohaa_actor` map soldiers.
  - A waiting list for soldiers that find the 48-slot pool full. They spawn near players as slots
    free up, and a corpse gives its slot back after 20 s.
  - Music sent to every player.
  - The walk test, `getcvar` and screen fades.
- `dod_mohaa.c`:
  - Music: `soundtrack`, `forcemusic`, and `stufftext` with the tm* commands.
  - `isalive`, `getcvar`, `fadeout`, `fadein`.
  - Path nodes named like entities.
