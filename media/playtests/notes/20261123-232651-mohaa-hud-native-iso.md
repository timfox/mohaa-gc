# MOHAA Probe mohaa-hud-native-iso — 20261123-232651

- ISO: `/tmp/mohaa-hud-visual/mohaa-m1l1-hud-native-build.iso`
- Route: `mohaa-hud-native-iso`
- Duration cap: 60s
- Repo: `6be6ce53a9`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-232651-mohaa-hud-native-iso/`
- Periodic guest frames: 7 screenshots in `media/playtests/screenshots/20261123-232651-mohaa-hud-native-iso/frames/`
- Video: `media/playtests/videos/20261123-232651-mohaa-hud-native-iso-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 6be6ce53a9. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-visual/mohaa-m1l1-hud-native-build.iso (SHA-256 1f755cf69186ac6621cf2aa423c228c1d1b1df482478678385edb8b2c6ebaacf). GameCube-aware ISO rebuild with retail MOHAA HUD pack. Capture New Game m1l1 gameplay, sprite-load reports, and m1l1 skybox.

## Frame stats
```
final.png: (640, 480) black=74.5% mean=(15, 13, 14)
intro.png: (640, 480) black=67.4% mean=(4, 4, 3)
```

## OSReport (key)
```
38:26:53:130 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
39:26:53:130 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:52] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
65:26:53:231 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:52] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
139:26:54:076 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: released unused nodes reserve 256 Kb
140:26:54:076 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: released unused submodels reserve 16 Kb
151:26:54:090 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: server game init deferred until map load
156:26:54:096 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=client_local_init_ready used=1149944 free=276936 unclaimed=163840 avail=440776
185:26:54:137 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1160384 free=266496 unclaimed=163840 avail=430336
193:26:54:181 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: renderer screen map ready
196:26:54:182 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1160384 free=266496 unclaimed=163840 avail=430336
205:26:54:183 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=renderer_images_ready used=1160528 free=266352 unclaimed=163840 avail=430192
209:26:54:185 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=renderer_init_ready used=1258928 free=167952 unclaimed=163840 avail=331792
223:26:54:248 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=1262672 free=164208 unclaimed=163840 avail=328048
232:26:54:252 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=1269480 free=157400 unclaimed=163840 avail=321240
250:26:54:366 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=client_video_init_ready used=1434152 free=136088 unclaimed=20480 avail=156568
272:26:54:373 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1439040 free=131200 unclaimed=20480 avail=151680
292:26:54:385 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: gcmap lookup begin
293:26:54:385 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: no gcmap argument
297:26:54:392 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: intro AVI play media/mohaa_intro.avi
298:26:54:392 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=intro_avi_play used=1443336 free=126904 unclaimed=20480 avail=147384
301:26:54:431 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: ARAM map 0x00004000 1,024 Kb sfx (session)
302:26:54:431 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: ARAM map 0x00104000 14.98 Mb FREE
303:26:54:432 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: ARAM map 0x00fffd00 256 bytes waddir (stream)
304:26:54:432 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: ARAM map 0x00fffe00 256 bytes waddir (stream)
305:26:54:432 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: ARAM map 0x00ffff00 256 bytes waddir (stream)
311:26:54:501 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1455832 free=114408 unclaimed=20480 avail=134888
328:26:54:531 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:53] Xash3D GameCube: intro AVI decoded first frame
333:26:54:532 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: G197 CopyDisp ok fb=640 efb=480 xfb=480 stride=640 xfb_k1=1 crt_vf=0
371:26:55:574 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:54] Xash3D GameCube: intro AVI progress frame=15/2503 elapsed=1.06
374:26:56:583 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:55] Xash3D GameCube: intro AVI progress frame=31/2503 elapsed=2.07
407:26:58:524 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:26:57] Xash3D GameCube: intro AVI progress frame=60/2503 elapsed=4.01
421:27:02:527 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:27:01] Xash3D GameCube: intro AVI progress frame=120/2503 elapsed=8.01
```

- Full Dolphin log: `media/playtests/screenshots/20261123-232651-mohaa-hud-native-iso/dolphin.log.gz`
