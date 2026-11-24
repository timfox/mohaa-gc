# MOHAA Probe m1l1-hud-fix-confirmed — 20261123-230319

- ISO: `/tmp/mohaa-hud-fix/mohaa-hud-m1l1.iso`
- Route: `m1l1-hud-fix-confirmed`
- Duration cap: 80s
- Repo: `f8b4c7ecc9`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-230319-m1l1-hud-fix-confirmed/`
- Periodic guest frames: 2 screenshots in `media/playtests/screenshots/20261123-230319-m1l1-hud-fix-confirmed/frames/`
- Video: `media/playtests/videos/20261123-230319-m1l1-hud-fix-confirmed-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: f8b4c7ecc9. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-fix/mohaa-hud-m1l1.iso (SHA-256 e56129565c5c4c2eef6e42bb56d8dabd6f0ce6f9ce21d4f866387ab81ba33db4). Retail New Game regression after low-memory HUD latch and matched 256/32 engine build; capture m1l1 opening route.

## Frame stats
```
final.png: (640, 480) black=8.0% mean=(62, 57, 30)
menu-2.png: (640, 480) black=8.0% mean=(62, 57, 30)
menu.png: (640, 480) black=8.0% mean=(62, 57, 30)
```

## OSReport (key)
```
39:03:21:789 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,mohaa
40:03:21:789 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:21] Xash3D GameCube: linked gamedir=mohaa detected=valve,mohaa
65:03:21:894 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:21] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
137:03:22:708 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: released unused submodels reserve 16 Kb
189:03:22:770 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=client_local_init_ready used=872792 free=136 unclaimed=0 avail=136
220:03:22:828 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=871568 free=1360 unclaimed=0 avail=1360
226:03:22:869 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: renderer screen map ready
229:03:22:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=871568 free=1360 unclaimed=0 avail=1360
238:03:22:872 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=renderer_images_ready used=871704 free=1224 unclaimed=0 avail=1224
241:03:22:873 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=renderer_init_ready used=871784 free=1144 unclaimed=0 avail=1144
253:03:22:885 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=872744 free=184 unclaimed=0 avail=184
262:03:22:891 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=872744 free=184 unclaimed=0 avail=184
284:03:22:905 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: gc_menu_ready set 0
296:03:22:927 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: mainui vidinit backgrounds listed
299:03:22:929 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Rendering Bitmap Font(18, 500) took 0.000093 seconds
302:03:22:931 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Rendering Bitmap Font(6, 500) took 0.000091 seconds
306:03:22:932 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: mainui vidinit background ready
308:03:22:932 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: gc_menu_ready set 1
310:03:22:932 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=872760 free=168 unclaimed=0 avail=168
312:03:22:933 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=client_video_init_ready used=872760 free=168 unclaimed=0 avail=168
334:03:22:943 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=872760 free=168 unclaimed=0 avail=168
354:03:22:956 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: gcmap lookup begin
355:03:22:957 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: no gcmap argument
364:03:22:959 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=872760 free=168 unclaimed=0 avail=168
428:03:23:117 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: freed 2 menu/UI textures for map load
429:03:23:117 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: GX HUD/menu slabs released for map load
431:03:23:123 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: menu unloaded for map load
433:03:23:124 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: sound trimmed for map load
434:03:23:124 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: client subsystems trimmed for map load
441:03:23:125 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: freed 0 menu/UI textures for map load
442:03:23:125 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: GX HUD/menu slabs released for map load
447:03:23:126 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: renderer trim for map load
449:03:23:126 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: present buf released map load
454:03:23:127 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: play start map buffer ready m1l1
462:03:23:131 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: map load cfg skipped
465:03:23:134 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: pre-spawn mem map set
479:03:23:136 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: present buf released map load
481:03:23:137 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: server string arena spill dropped for map reload
490:03:23:138 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
493:03:23:138 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:22] Xash3D GameCube: server string arena spill dropped for map reload
502:03:23:639 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.79 Mb 竊 1.14 Mb (G154 disc LM)
532:03:23:731 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
534:03:23:733 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: world faces copied 100.84 Kb to map tail
542:03:23:737 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: world texinfo copied to map tail 12.59 Kb
549:03:23:743 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: releasing gcmap BSP staging 1.14 Mb before surfaces
643:03:23:986 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: entity overflow reserved 65536 bytes in map arena
648:03:24:110 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] PM_WorldMesh: maps/m1l1.mcol, 0 brushes, 18 terrain patches, 13212 patch triangles, 388920 bytes in the map arena
1077:03:24:291 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: resource sync skipped for local map route
1079:03:24:295 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: retaining map arena for entity private data
1084:03:24:298 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: renderer restore after map load
1085:03:24:298 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: map loaded m1l1
1086:03:24:298 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1088:03:24:299 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: mem stage=map active total=229.12 Kb delta=18 bytes hwm=231.39 Kb map=m1l1 heap_used=849.68 Kb heap_free=2.79 Kb unclaimed=0 bytes
1089:03:24:299 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: mem pools at=map active live=25 slots=25 small=8176 Zone Engine=93829 BaseCmd=42616 Console Commands=12631 Console Variables=23315 FileSystem Pool=47366 wad:halflife.wad=6682
1091:03:24:300 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: budget texture region at=map active bytes=0 bytes live=0 bytes arena_usable=3.56 Mb
1092:03:24:301 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: direct-map player prime begin edict=1
1108:03:24:305 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: direct-map player prime ready edict=1 private=0x80b51610 origin=(-1918,-3137,179)
1109:03:24:306 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: direct-map loopback netchan initialized
1110:03:24:307 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: direct-map queued 35 user message regs overflow=0
1111:03:24:307 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [23:03:23] Xash3D GameCube: direct-map client ready cs_spawned frames=0x80b04400
```

- Full Dolphin log: `media/playtests/screenshots/20261123-230319-m1l1-hud-fix-confirmed/dolphin.log.gz`
