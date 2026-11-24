# MOHAA Probe mohaa-retail-hud-lowmem — 20261124-031504

- ISO: `/tmp/mohaa-hud-refine/out/mohaa-playable-retail-hud.iso`
- Route: `mohaa-retail-hud-lowmem`
- Duration cap: 60s
- Repo: `ebf188540a`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261124-031504-mohaa-retail-hud-lowmem/`
- Periodic guest frames: 2 screenshots in `media/playtests/screenshots/20261124-031504-mohaa-retail-hud-lowmem/frames/`
- Video: `media/playtests/videos/20261124-031504-mohaa-retail-hud-lowmem-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: ebf188540a. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-hud-refine/out/mohaa-playable-retail-hud.iso (SHA-256 1f54e4d5347097d7b7fe8d4382573416c2c5b18958102b1074985d4bcc8a7362). Retail menu route with matched playable low-memory profile and MOHAA lean HUD startup.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(32, 35, 53)
menu-2.png: (640, 480) black=8.9% mean=(32, 35, 53)
menu.png: (640, 480) black=8.9% mean=(32, 35, 53)
```

## OSReport (key)
```
34:15:06:508 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=mohaa
35:15:06:508 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:06] Xash3D GameCube: linked gamedir=mohaa detected=mohaa
61:15:06:556 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:06] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
116:15:07:342 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: released unused nodes reserve 256 Kb
117:15:07:342 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: released unused submodels reserve 16 Kb
128:15:07:352 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: server game init deferred until map load
133:15:07:357 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=client_local_init_ready used=1140984 free=282664 unclaimed=8192 avail=290856
162:15:07:387 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1151424 free=272224 unclaimed=8192 avail=280416
170:15:07:440 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: renderer screen map ready
173:15:07:441 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1151424 free=272224 unclaimed=8192 avail=280416
182:15:07:442 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=renderer_images_ready used=1151560 free=272088 unclaimed=8192 avail=280280
186:15:07:443 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=renderer_init_ready used=1249952 free=173696 unclaimed=8192 avail=181888
198:15:07:592 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=1253704 free=169944 unclaimed=8192 avail=178136
207:15:07:595 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=1260504 free=163144 unclaimed=8192 avail=171336
227:15:07:694 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: gc_menu_ready set 0
239:15:07:728 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: mainui vidinit backgrounds listed
242:15:07:729 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Rendering Bitmap Font(18, 500) took 0.000064 seconds
245:15:07:729 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Rendering Bitmap Font(6, 500) took 0.000061 seconds
249:15:07:730 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: mainui vidinit background ready
251:15:07:730 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: gc_menu_ready set 1
253:15:07:730 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=1360200 free=63448 unclaimed=8192 avail=71640
255:15:07:731 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=client_video_init_ready used=1360200 free=63448 unclaimed=8192 avail=71640
277:15:07:736 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1365096 free=58552 unclaimed=8192 avail=66744
296:15:07:746 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: gcmap lookup begin
297:15:07:746 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: no gcmap argument
306:15:07:748 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1369376 free=54272 unclaimed=8192 avail=62464
323:15:07:894 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] LoadBackground: found steam background in game directory
324:15:07:894 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [03:15:07] Xash3D GameCube: retail menu steam background ready tiles=4
391:15:08:142 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: G197 CopyDisp ok fb=640 efb=480 xfb=480 stride=640 xfb_k1=1 crt_vf=0
```

- Full Dolphin log: `media/playtests/screenshots/20261124-031504-mohaa-retail-hud-lowmem/dolphin.log.gz`
