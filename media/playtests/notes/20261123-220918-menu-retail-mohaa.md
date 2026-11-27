# MOHAA Probe menu-retail-mohaa — 20261123-220918

- ISO: `/tmp/mohaa-m1l1-retail-play/out/mohaa-retail-menu-play.iso`
- Route: `menu-retail-mohaa`
- Duration cap: 60s
- Repo: `06dfdba066`
- Engine: `db73d0d126`
- Shots: `media/playtests/screenshots/20261123-220918-menu-retail-mohaa/`
- Periodic guest frames: 1 screenshots in `media/playtests/screenshots/20261123-220918-menu-retail-mohaa/frames/`
- Video: `media/playtests/videos/20261123-220918-menu-retail-mohaa-silent.mp4`

MOHAA GameCube playtest. Repo HEAD: 06dfdba066. Engine checkout: /tmp/mohaa-loopback-fix/engine (Git revision db73d0d126). ISO: /tmp/mohaa-m1l1-retail-play/out/mohaa-retail-menu-play.iso (SHA-256 0e6835c301375802e0db7f419432efb221c56b2e3f971523dbe5b1f3ab6a620e). Retail-style boot/menu route with gcplayerinput enabled and m1l1 configured as the MOHAA start map. Isolated Xvfb capture preserves the open interactive session.

## Frame stats
```
final.png: (640, 480) black=8.9% mean=(32, 35, 53)
menu-2.png: (640, 480) black=8.9% mean=(32, 35, 53)
menu.png: (640, 480) black=8.9% mean=(32, 35, 53)
```

## OSReport (key)
```
38:09:20:578 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: linked gamedir=mohaa detected=valve,mohaa
39:09:20:578 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:20] Xash3D GameCube: linked gamedir=mohaa detected=valve,mohaa
64:09:20:681 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:20] FS_Rescan( Medal of Honor: Allied Assault, 0x4000000, english )
143:09:21:482 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: released unused nodes reserve 256 Kb
144:09:21:482 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: released unused submodels reserve 16 Kb
155:09:21:494 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: server game init deferred until map load
160:09:21:500 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=client_local_init_ready used=1169920 free=264256 unclaimed=471040 avail=735296
189:09:21:540 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=renderer_video_init_ready used=1180360 free=253816 unclaimed=471040 avail=724856
197:09:21:593 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: renderer screen map ready
200:09:21:593 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=renderer_screen_alloc_ready used=1180360 free=253816 unclaimed=471040 avail=724856
209:09:21:595 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=renderer_images_ready used=1180496 free=253680 unclaimed=471040 avail=724720
212:09:21:597 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=renderer_init_ready used=1180576 free=253600 unclaimed=471040 avail=724640
226:09:21:631 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=gameui_library_handle_ready used=1184320 free=249856 unclaimed=471040 avail=720896
235:09:21:634 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=gameui_pfninit_ready used=1191120 free=243056 unclaimed=471040 avail=714096
250:09:21:828 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: gc_menu_ready set 0
262:09:21:862 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: mainui vidinit backgrounds listed
265:09:21:863 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Rendering Bitmap Font(18, 500) took 0.000064 seconds
268:09:21:863 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Rendering Bitmap Font(6, 500) took 0.000062 seconds
272:09:21:864 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: mainui vidinit background ready
274:09:21:864 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: gc_menu_ready set 1
276:09:21:864 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=gameui_deferred_vidinit_ready used=1455456 free=105696 unclaimed=344064 avail=449760
278:09:21:865 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=client_video_init_ready used=1455456 free=105696 unclaimed=344064 avail=449760
300:09:21:870 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=engine_subsystems_ready used=1460352 free=100800 unclaimed=344064 avail=444864
319:09:21:881 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: gcmap lookup begin
320:09:21:881 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: no gcmap argument
334:09:21:894 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: heap mark stage=host_main_loop_begin_status used=1464632 free=96520 unclaimed=344064 avail=440584
351:09:22:061 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] LoadBackground: found steam background in game directory
352:09:22:061 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: [22:09:21] Xash3D GameCube: retail menu steam background ready tiles=4
499:09:22:445 Core/HW/EXI/EXI_DeviceIPL.cpp:306 N[OSREPORT]: Xash3D GameCube: G197 CopyDisp ok fb=640 efb=480 xfb=480 stride=640 xfb_k1=1 crt_vf=0
```

- Full Dolphin log: `media/playtests/screenshots/20261123-220918-menu-retail-mohaa/dolphin.log.gz`
