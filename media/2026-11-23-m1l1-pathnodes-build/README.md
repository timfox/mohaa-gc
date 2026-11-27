# m1l1 path-node allocator build

## Artifacts

- ISO: `/tmp/mohaa-m1l1-pathnodes-build/out/mohaa-m1l1-pathnodes-gca-lean.iso`
- ISO size: 1,209,163,776 bytes
- ISO SHA-256: `ff2add4b00f09cdfb5ead2ce5d61d01fe2822f1b8dd76d41d5054c095e1a041d`
- DOL: `/tmp/mohaa-m1l1-pathnodes-build/out/mohaagc.dol`
- DOL size: 7,489,440 bytes
- DOL SHA-256: `3fb6837072580a94a8d8e7f2b38bef21784b99e1325841009fe2b470a016c02e`

## Build provenance

The game code is from `/home/tim/Desktop/mohaa-gc` at commit `e1db9c9ea199fe0aa5481fa1de5bca3718bcc69e`. The engine source was the isolated scratch tree `/tmp/mohaa-loopback-fix/engine`, commit `db73d0d12668`; it contains the local MOHAA studio-memory spill adjustment and does not represent a clean canonical engine checkout. `git status` on this scratch tree could not complete because its `3rdparty/MultiEmulator` git metadata path is missing.

The build used a temporary SDK copy at `/tmp/mohaa-m1l1-pathnodes-build/hlsdk-portable`, copied from the local `claude/dod-hlsdk-integration` source at `238827b83d38be13ffcd282bdb5330b6c94a4863`. The original copy under `cutscene-20261122/` was not modified. DevkitPPC reports version 16.1.0; the engine DOL uses libogc. The SDK/game archive and full engine compiled, linked, and installed successfully after setting `DEVKITPRO=/opt/devkitpro`.

The disc used the staged MOHAA m1l1 data, including the split German actor and truck models, plus the existing lean DoD/Valve support trees. The builder's own integrity check and an independent header-offset read both confirmed that the DOL embedded in the ISO byte-matches the input DOL.

## Offline checks

- Extracted `/xash3d/mohaa/maps/m1l1.nodes` from the ISO; it is 23,835 bytes and byte-matches the staged 643-record file.
- Extracted the German actor's hashed `.gca`; it byte-matches the staged 308,864-byte animation pack.
- Extracted `gamecube.cfg`; it selects `listenserver m1l1`, `gcworldrender`, and `gcplayerinput`.
- The DOL contains the new `could not load path nodes`, `path node allocation failed`, and `0 path nodes parsed` diagnostic strings.
- `powerpc-eabi-gcc -fsyntax-only` passed for the modified MOHAA C source, and `git diff --check` passed at commit time.

No Dolphin or physical GameCube run has verified the new path-pool allocation yet. Four Dolphin Flatpak sessions were still reported running with unknown disc selections; they were left untouched.
