# Probe m1l1-truck-menu-newgame-hudfix — 20261124-193154

- ISO: `/tmp/mohaa-m1l1-menu-newgame-hudfix.iso`
- Route: `m1l1-truck-menu-newgame-hudfix`
- Duration cap: 45s
- Repo: `74b8088bf8`
- Engine: `b84af4eacc`
- Shots: `media/playtests/screenshots/20261124-193154-m1l1-truck-menu-newgame-hudfix/`

MOHAA m1l1 retail menu-to-New-Game route using a local GameCube SDK build with the optional Half-Life suit battery HUD guarded. The map loaded and logged `world DL frame=1 ... bind_miss=0`; no HUD panic or fatal error appears in the captured log. Dolphin evidence only; physical GameCube validation remains open.

## Frame stats
```
final.png: (640, 480) black=9.2% mean=(22, 33, 45)
matched.png: (640, 480) black=9.2% mean=(22, 33, 45)
menu-2.png: (640, 480) black=100.0% mean=(0, 0, 0)
menu.png: (640, 480) black=8.1% mean=(126, 127, 118)
```

## OSReport (key)
```
34:31:56:275 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:31:56:275 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
59:31:56:325 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
109:31:56:928 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: released unused submodels reserve 16 Kb
161:31:56:976 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=client_local_init_ready used=870328 free=3944 unclaimed=114688 avail=118632
192:31:57:012 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=880768 free=1696 unclaimed=106496 avail=108192
198:31:57:053 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: renderer screen map ready
201:31:57:054 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=880768 free=1696 unclaimed=106496 avail=108192
210:31:57:055 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=renderer_images_ready used=880904 free=1560 unclaimed=106496 avail=108056
213:31:57:057 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=renderer_init_ready used=880984 free=1480 unclaimed=106496 avail=107976
226:31:57:064 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=884720 free=5936 unclaimed=98304 avail=104240
235:31:57:067 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=891520 free=3232 unclaimed=94208 avail=97440
254:31:57:081 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:56] Xash3D GameCube: gc_menu_ready set 0
266:31:57:119 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: mainui vidinit backgrounds listed
269:31:57:121 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Rendering Bitmap Font(18, 500) took 0.000065 seconds
272:31:57:121 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Rendering Bitmap Font(6, 500) took 0.000062 seconds
276:31:57:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: mainui vidinit background ready
278:31:57:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: gc_menu_ready set 1
280:31:57:122 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=958392 free=30568 unclaimed=0 avail=30568
282:31:57:123 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: heap mark stage=client_video_init_ready used=958392 free=30568 unclaimed=0 avail=30568
304:31:57:129 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=963288 free=25672 unclaimed=0 avail=25672
323:31:57:141 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: gcmap lookup begin
324:31:57:141 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: no gcmap argument
338:31:57:144 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=967568 free=21392 unclaimed=0 avail=21392
402:31:57:276 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: freed 2 menu/UI textures for map load
403:31:57:276 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: GX HUD/menu slabs released for map load
405:31:57:279 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: menu unloaded for map load
407:31:57:281 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: sound trimmed for map load
408:31:57:281 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: client subsystems trimmed for map load
418:31:57:282 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: renderer trim for map load
420:31:57:282 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: present buf released map load
425:31:57:283 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: play start map buffer ready m1l1
433:31:57:286 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: map load cfg skipped
436:31:57:289 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: pre-spawn mem map set
449:31:57:290 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: present buf released map load
451:31:57:291 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: server string arena spill dropped for map reload
460:31:57:292 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: pre-spawn map buffer prepared for m1l1
463:31:57:292 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: server string arena spill dropped for map reload
474:31:57:989 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:57] Xash3D GameCube: map load compact (no lighting, miptex headers only) 1.87 Mb 竊 1.22 Mb (G154 disc LM)
515:31:58:141 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: world surfedges copied 95.81 Kb to map tail
517:31:58:142 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: world faces copied 100.84 Kb to map tail
529:31:58:145 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: releasing gcmap BSP staging 1.22 Mb before surfaces
626:31:58:378 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: entity overflow reserved 65536 bytes in map arena
1074:31:58:534 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: resource sync skipped for local map route
1076:31:58:537 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: retaining map arena for entity private data
1081:31:58:539 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: renderer restore after map load
1082:31:58:539 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: map loaded m1l1
1083:31:58:539 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=client
1085:31:58:540 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: budget moved entity text to map leftover (20.53 Kb), heap free 54.66 Kb
1086:31:58:545 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: mem stage=map active total=212.65 Kb delta=21 bytes hwm=214.92 Kb map=m1l1 heap_used=911.12 Kb heap_free=54.66 Kb unclaimed=0 bytes
1087:31:58:546 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: mem pools at=map active live=17 slots=17 small=3826 Zone Engine=93829 BaseCmd=42616 Console Commands=12631 Console Variables=23357 FileSystem Pool=28179 maps/m1l1.bsp=13314
1088:31:58:546 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: budget texture region at=map active bytes=0 bytes live=0 bytes arena_usable=3.69 Mb
1089:31:58:547 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: direct-map player prime begin edict=1
1105:31:58:550 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: direct-map player prime ready edict=1 private=0x80b39710 origin=(-1918,-3137,179)
1106:31:58:550 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: direct-map loopback netchan initialized
1107:31:58:551 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: direct-map queued 35 user message regs overflow=0
1108:31:58:551 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: direct-map client ready cs_spawned frames=0x80ae6da0
1113:31:58:552 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: boot phase=map last=map
1118:31:58:553 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: play start retain map buffer for live BSP m1l1
1120:31:58:553 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [19:31:58] Xash3D GameCube: gcmap released 0 precache models for world render
```

- Extracted interior frame: `media/playtests/screenshots/20261124-193154-m1l1-truck-menu-newgame-hudfix/truck-interior-4s.png` (shows the player view inside the landing craft with allied soldiers).
- Local SDK commit: `c66834d` (`Guard optional MOHAA suit HUD sprites`).
- DOL SHA-256: `987c9f8e621f5c7db4d449e96e563a2520d3596bb0d9a5bdb451edc08cd50dd1`.
- ISO SHA-256: `8f2f6287b785de7217a385c47586f9148015c1a6f234af690d0b67d37a23e06d`.
