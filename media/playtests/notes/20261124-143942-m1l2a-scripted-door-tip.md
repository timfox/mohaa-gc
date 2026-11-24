# MOHAA Probe m1l2a-scripted-door-tip — 20261124-143942

- ISO: `/tmp/mohaa-m1l2a-script-stage.iso`
- Route: `m1l2a-scripted-door-tip`
- Duration cap: 100s
- Repo: `2f2c0c49c2`
- Engine: `1f16d40c3f`
- Shots: `media/playtests/screenshots/20261124-143942-m1l2a-scripted-door-tip/`

MOHAA probe attempt. Repo HEAD: e2b7286310. Engine checkout: /home/tim/Desktop/mohaa-gc/retail/xash3d-gc-latest (Git revision 1f16d40c3f). ISO: /home/tim/Desktop/mohaa-gc/retail/mohaa-m1l2a-scripted-door-tip-20261124/mohaa-m1l2a-scripted-door-tip.iso (SHA-256 7f33e5727fe3e4800b3502b0b878811fb5763c1e50e872da20c6892a94ef0f81). The disc now contains both retail mission scripts and a scripted New Game/changelevel route, but Dolphin aborted before boot: Qt could not connect to display `:110` under Xvfb, and no host X server is currently reachable. No game frames or script runtime evidence were produced. Runtime initialization and the onscreen tip remain open.

## Launch log

The captured launcher log is `media/playtests/screenshots/20261124-143942-m1l2a-scripted-door-tip/dolphin.log.gz`. It contains the Qt xcb connection failure; Dolphin never opened a guest window. The host has no reachable X server (`xdpyinfo` fails on `:0`, `:1`, and available stale socket displays), and Xvfb cannot create its socket because the managed `/tmp/.X11-unix` directory is owned by `nobody` rather than root. A separate `-b -v Null` headless attempt ran until its 90-second timeout but produced no Dolphin OSReport log, so it does not verify the game VM.

## Static path verification

The ISO contains both `xash3d/mohaa/maps/m1l2a.scr` and `xash3d/mohaa/global/door_locked.scr`. The MOHAA GameCube module ELF `/tmp/mohaa-matching-layout-build/out/bin/xash-mohaa` exports `Dod_MohaaLevelInit`, `Dod_MohaaNotify`, and `DodGC_MohaaTrigger`. In `/tmp/mohaa-current-clean-build/hlsdk-gamecube/mohaa/dlls/libhl_gamecube_ppc.a`, `triggers.cpp.1.o` references `DodGC_MohaaTrigger`, while `dod_mohaa_ents.cpp.1.o` defines it. This verifies the script and trigger bridge are linked into the probe build; it does not prove they execute in-game or that the HUD tip is visible.
