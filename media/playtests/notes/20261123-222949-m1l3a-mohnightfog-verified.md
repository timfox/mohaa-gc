# MOHAA Probe m1l3a-mohnightfog-verified — 20261123-222949

- ISO: `/tmp/mohaa-skies-stage-update/out/m1l3a-mohnightfog-smoke.iso`
- Route: `m1l3a-mohnightfog-verified`
- Duration cap: 30s
- Repo: `06dfdba066`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-222949-m1l3a-mohnightfog-verified/`
- Periodic guest frames: 3 screenshots in `media/playtests/screenshots/20261123-222949-m1l3a-mohnightfog-verified/frames/`
- Video: `media/playtests/videos/20261123-222949-m1l3a-mohnightfog-verified-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 06dfdba066. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-skies-stage-update/out/m1l3a-mohnightfog-smoke.iso (SHA-256 6dd232bd0b8773361173b02f9f0a5f7aea7a39faa893ac569b57033431e25373). Direct world-render probe for updated retail mohnightfog cubemap. Smoke builder stages six CMPR faces; runtime evidence archived.

## Frame stats
```
final.png: (640, 480) black=9.0% mean=(10, 14, 23)
```

## OSReport (key)
```
27:29:51:560 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l3a
38:29:51:612 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,mohaa
39:29:51:612 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: linked gamedir=mohaa detected=valve,mohaa
43:29:51:616 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: smoke map override m1l3a
65:29:51:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
80:29:52:185 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Program args: xash xash -dev 2 -log -game mohaa -gcworldrender -gcmap m1l3a -width 320 -height 240
115:29:52:224 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: released unused nodes reserve 256 Kb
116:29:52:224 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: released unused submodels reserve 16 Kb
168:29:52:292 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=client_local_init_ready used=1186976 free=226720 unclaimed=491520 avail=718240
198:29:52:359 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1197424 free=216272 unclaimed=491520 avail=707792
205:29:52:432 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: renderer screen map ready
208:29:52:434 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1197424 free=216272 unclaimed=491520 avail=707792
217:29:52:436 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=renderer_images_ready used=1197560 free=216136 unclaimed=491520 avail=707656
221:29:52:440 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=renderer_init_ready used=1295952 free=117744 unclaimed=491520 avail=609264
226:29:52:449 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: screen init minimal for gcmap smoke route
228:29:52:449 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=client_video_init_ready used=1299704 free=113992 unclaimed=491520 avail=605512
251:29:52:461 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1303496 free=110200 unclaimed=491520 avail=601720
259:29:52:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: gcmap lookup begin
260:29:52:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: queue map m1l3a
261:29:52:472 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: direct map begin
263:29:52:473 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: freed 0 menu/UI textures for map load
264:29:52:473 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: GX HUD/menu slabs released for map load
266:29:52:476 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: sound trimmed for map load
267:29:52:476 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: client subsystems trimmed for map load
276:29:52:478 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: renderer trim for map load
277:29:52:478 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: present buf released map load
287:29:52:482 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: map load cfg skipped
290:29:52:486 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: pre-spawn mem map set
304:29:52:489 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: present buf released map load
306:29:52:489 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: server string arena spill dropped for map reload
315:29:52:491 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: pre-spawn map buffer prepared for m1l3a
319:29:52:492 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:51] Xash3D GameCube: server string arena spill dropped for map reload
330:29:52:971 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.47 Mb 竊 1.03 Mb (G154 disc LM) +align
369:29:53:094 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: world surfedges copied 75.40 Kb to map tail
371:29:53:096 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: world faces copied 79.79 Kb to map tail
383:29:53:103 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: releasing gcmap BSP staging 1.03 Mb before surfaces
429:29:53:180 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: map skyname early mohnightfog (before CapFaces)
474:29:53:304 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: freed 47 menu/UI textures for map load
475:29:53:304 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:52] Xash3D GameCube: GX HUD/menu slabs released for map load
1009:29:53:509 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: resource sync skipped for local map route
1015:29:53:516 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: renderer restore after map load
1016:29:53:516 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: map loaded m1l3a
1017:29:53:516 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1019:29:53:517 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: budget moved entity text to map leftover (24.13 Kb), entity reserve returned, heap free 203.09 Kb
1024:29:53:527 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1026:29:53:528 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: direct map ready
1029:29:53:528 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: skip startup video scan for gcmap route
1030:29:53:529 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: gcmap smoke frames begin
1037:29:53:533 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: gcmap smoke frames ready
1040:29:53:533 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1697256 free=203864 unclaimed=4096 avail=207960
1046:29:53:544 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: livemap armed=0 (file absent)
1048:29:53:606 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: released unused nodes reserve 256 Kb
1049:29:53:606 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: released unused submodels reserve 16 Kb
1051:29:53:607 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: freed 47 menu/UI textures for map load
1052:29:53:607 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: GX HUD/menu slabs released for map load
1073:29:53:615 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: titles init skipped for gcmap smoke route
1078:29:53:621 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: client edicts using static gcmap bootstrap tables
1206:29:53:637 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: heap mark stage=client_module_ready used=1438680 free=462440 unclaimed=4096 avail=466536
1208:29:53:637 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: heap mark stage=deferred_client_init_ready used=1438680 free=462440 unclaimed=4096 avail=466536
1233:29:53:679 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:29:53] Xash3D GameCube: serverdata HUD vidinit deferred for local map route
```

- Full Dolphin log: `media/playtests/screenshots/20261123-222949-m1l3a-mohnightfog-verified/dolphin.log.gz`
