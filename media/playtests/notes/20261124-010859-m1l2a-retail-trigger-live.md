# MOHAA Probe m1l2a-retail-trigger-live — 20261124-010859

- ISO: `/tmp/mohaa-compass-build/mohaa-m1l2a-retail-trigger-input.iso`
- Route: `m1l2a-retail-trigger-live`
- Duration cap: 65s
- Repo: `be19bf9df1`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-010859-m1l2a-retail-trigger-live/`
- Periodic guest frames: 60 screenshots in `media/playtests/screenshots/20261124-010859-m1l2a-retail-trigger-live/frames/`
- Video: `media/playtests/videos/20261124-010859-m1l2a-retail-trigger-live-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: be19bf9df1. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-compass-build/mohaa-m1l2a-retail-trigger-input.iso (SHA-256 e4142e5ae93ee679b131215a5ff584e0859e0dd13a09b9cce81b9fc40658ea15). Intended to test the retail m1l2a `hint_door` trigger without injected hint calls.

## Result

The controller pipe did not attach. The capture harness used the normal keyboard profile, and the pipe driver reported `Dolphin gamepad FIFO did not become writable`. No deterministic input reached the game, so this run does not verify the natural trigger or its hint. It preserves 60 frames, the final still, video, and Dolphin log for the failed input attempt.

## Frame stats
```
final.png: (640, 480) black=9.0% mean=(59, 48, 32)
```

## OSReport (key)
```
36:09:01:130 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
37:09:01:130 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:00] Xash3D GameCube: linked gamedir=mohaa detected=valve,dod,mohaa
63:09:01:397 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:00] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
152:09:03:033 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Program args: xash xash -dev 2 -log -game mohaa -gclistenserver m1l2a -gcmap m1l2a -gcvideo prog -gcplayerinput -width 320 -height 240
194:09:03:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: released unused nodes reserve 256 Kb
195:09:03:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: released unused submodels reserve 16 Kb
247:09:03:155 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=client_local_init_ready used=941936 free=243792 unclaimed=569344 avail=813136
277:09:03:215 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=952688 free=233040 unclaimed=569344 avail=802384
284:09:03:263 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: renderer screen map ready
287:09:03:264 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=952688 free=233040 unclaimed=569344 avail=802384
296:09:03:265 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=renderer_images_ready used=952824 free=232904 unclaimed=569344 avail=802248
299:09:03:267 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=renderer_init_ready used=952904 free=232824 unclaimed=569344 avail=802168
306:09:03:273 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=client_video_init_ready used=956664 free=229064 unclaimed=569344 avail=798408
329:09:03:279 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=960456 free=225272 unclaimed=569344 avail=794616
337:09:03:290 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: gcmap lookup begin
338:09:03:290 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: queue map m1l2a
339:09:03:290 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: direct map begin
341:09:03:291 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: freed 0 menu/UI textures for map load
342:09:03:291 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: GX HUD/menu slabs released for map load
344:09:03:293 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: sound trimmed for map load
345:09:03:293 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: client subsystems trimmed for map load
354:09:03:296 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: renderer trim for map load
355:09:03:296 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: present buf released map load
371:09:03:300 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: map load cfg skipped
374:09:03:303 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: pre-spawn mem map set
388:09:03:305 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: present buf released map load
390:09:03:306 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: server string arena spill dropped for map reload
399:09:03:307 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: pre-spawn map buffer prepared for m1l2a
403:09:03:307 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:02] Xash3D GameCube: server string arena spill dropped for map reload
412:09:04:166 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:03] Xash3D GameCube: map load compact (no lighting, miptex headers only) 3.14 Mb 竊 1.96 Mb (G154 disc LM) +align
459:09:04:474 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:03] Xash3D GameCube: world surfedges copied 230.03 Kb to map tail
471:09:04:477 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:03] Xash3D GameCube: releasing gcmap BSP staging 1.96 Mb before surfaces
578:09:06:740 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:06] Xash3D GameCube: freed 126 menu/UI textures for map load
579:09:06:740 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:06] Xash3D GameCube: GX HUD/menu slabs released for map load
587:09:06:820 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:06] PM_WorldMesh: maps/m1l2a.mcol, 0 brushes, 146 terrain patches, 7870 patch triangles, 243960 bytes in the map arena
649:09:07:769 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] mohaa: running maps/m1l2a.scr (budget 384 KiB, 384 KiB in the map arena in 1 piece, the rest from the heap)
1062:09:08:238 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: resource sync skipped for local map route
1068:09:08:245 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: renderer restore after map load
1069:09:08:245 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: map loaded m1l2a
1070:09:08:245 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1072:09:08:246 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: budget moved entity text to map leftover (46.10 Kb), entity reserve returned, heap free 284.13 Kb
1077:09:08:256 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1079:09:08:257 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: direct map ready
1082:09:08:257 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: skip startup video scan for gcmap route
1083:09:08:258 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: gcmap smoke frames begin
1084:09:08:258 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: gcmap smoke frames ready
1087:09:08:258 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1464120 free=274568 unclaimed=16384 avail=290952
1088:09:08:258 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: solo listenserver active map=m1l2a (gcmap tip)
1102:09:08:270 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: livemap armed=0 (file absent)
1111:09:08:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: released unused nodes reserve 256 Kb
1112:09:08:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: released unused submodels reserve 16 Kb
1113:09:08:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: freed 126 menu/UI textures for map load
1114:09:08:316 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: GX HUD/menu slabs released for map load
1135:09:08:323 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: titles init skipped for gcmap smoke route
1140:09:08:331 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1230:09:08:384 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: heap mark stage=client_module_ready used=1198368 free=540320 unclaimed=16384 avail=556704
1232:09:08:384 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1198368 free=540320 unclaimed=16384 avail=556704
1260:09:08:435 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
1261:09:08:435 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: client edicts capped for map route max=460 requested=460
1262:09:08:436 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [01:09:07] Xash3D GameCube: serverdata map CRC skipped for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261124-010859-m1l2a-retail-trigger-live/dolphin.log.gz`
