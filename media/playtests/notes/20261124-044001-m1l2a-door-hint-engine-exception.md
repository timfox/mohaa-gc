# MOHAA Probe m1l2a-door-hint-engine-exception — 20261124-044001

- ISO: `/dev/shm/mohaa-door-hint-engine-out/mohaa-m1l2a-door-hint.iso`
- Route: `m1l2a-door-hint-engine-exception`
- Duration cap: 40s
- Repo: `bd6a4241d7`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-044001-m1l2a-door-hint-engine-exception/`
- Periodic guest frames: 1 screenshots in `media/playtests/screenshots/20261124-044001-m1l2a-door-hint-engine-exception/frames/`
- Video: `media/playtests/videos/20261124-044001-m1l2a-door-hint-engine-exception-silent.mp4`

MOHAA GameCube full-physics probe after enabling the named retail door_locked trigger in the isolated engine build.

## Frame stats
```

```

## OSReport (key)
```
17:40:03:632 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
32:40:03:653 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
33:40:03:653 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:40:03] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
38:40:03:655 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l2a
64:40:03:684 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:40:03] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
81:40:04:084 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:40:03] Program args: xash xash -dev 2 -log -game mohaa -gcnewgame -gcworldrender -gcmap m1l2a -gclistenserver m1l2a -gcfullphysics -gcchangelevel m1l2a -gcplayerinput -width 320 -height 240
115:40:04:107 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [04:40:03] Xash3D GameCube: released unused submodels reserve 16 Kb
```

- Full Dolphin log: `media/playtests/screenshots/20261124-044001-m1l2a-door-hint-engine-exception/dolphin.log.gz`

## Result

Dolphin exited before gameplay at frame 0. The engine and cached MOHAA SDK archives had incompatible `playermove_t` layouts: engine 600/64 versus SDK 256/32. The controller driver attached, but its scheduled inputs came after the fatal status. The 1.9-second MP4 contains no playable map footage. This run does not test the USE exception or hint.
