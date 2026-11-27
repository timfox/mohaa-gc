# m1l1 studio-arena runtime probe — 2026-11-23

The actor-spill preference was removed for the German model and a candidate was built with a larger non-network studio model share. The isolated Dolphin run reached `MAP_READY m1l1`, parsed the path graph and loaded the opening truck models. The captured frame is the m1l1 team-selection menu, before a player joins the mission.

The actor still fails to promote. The game’s `waf configure` command uses `--gamedir mohaa`, and its compile flags include `-DXASH_DODGC_NETWORK=1`; `model.c` therefore selects the network studio-share branch (184 KiB), so the 704 KiB non-network branch edit had no effect. On the script retry the German MDL is read from disc, but studio promotion reports `studio malloc failed` for its 173.47 KiB mesh. Next isolate a MOHAA-specific allocation policy without changing DoD’s memory profile, then verify static MEM1 and map headroom.

The probe ran 65 seconds and was stopped by timeout (124), not a guest crash. The compressed OSReport is `dolphin.log.gz`.

Artifacts:

- ISO: `/tmp/mohaa-m1l1-actor-studio-build/out/mohaa-m1l1-actor-studio.iso` (1,165,940,736 bytes; SHA-256 `825a0b0a14e4f0388973441d9a435e99ee75f8511ac1b1311c4965122ccaaecd`).
- DOL: `/tmp/mohaa-m1l1-actor-studio-build/out/mohaa-m1l1-actor-studio.dol` (7,484,448 bytes; SHA-256 `c835b406a5e6c02f1842bf4343706c50fd085a0140a689b824456abc16c0010a`).
- This ISO runs in the desktop Dolphin window with the copied keyboard mapping from `/tmp/mohaa-m1l1-user/Config/`.
