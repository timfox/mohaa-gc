# m1l1 path-node build runtime check

- Date: 2026-11-23
- ISO: `/tmp/mohaa-m1l1-pathnodes-build/out/mohaa-m1l1-pathnodes-gca-lean.iso`
- ISO SHA-256: `ff2add4b00f09cdfb5ead2ce5d61d01fe2822f1b8dd76d41d5054c095e1a041d`
- DOL SHA-256: `3fb6837072580a94a8d8e7f2b38bef21784b99e1325841009fe2b470a016c02e`
- Dolphin: local baseline build at `/home/tim/.local/xash3d-gc-baseline/3rdparty/dolphin/build/Binaries/dolphin-emu`
- Result: m1l1 loaded and reached the Allied class picker. The window is left running for interactive play.
- Capture: [current.png](current.png)

This session used an isolated profile in `/tmp/mohaa-m1l1-user`. It did not enable a guest OSReport log, so this frame confirms map presentation and input UI only; it does not verify path-node parsing or the cutscene actor.

## Controls in the isolated profile

The copied Dolphin profile maps the keyboard as the GameCube pad: D-pad `T/G/F/H` (up/down/left/right), A `X`, B `Z`, Start `Enter`; movement uses arrow keys, with `Q/W` for L/R. No input was injected during the check.
