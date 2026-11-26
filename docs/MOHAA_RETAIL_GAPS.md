# MOHAA on GameCube: remaining retail gaps

This is a running list, updated with each PR. Each entry says what retail does that the port doesn't yet, and where it shows. Newest changes are at the top of each section.

## Missions and scripts
- **The campaign player can walk** (2026-11-26, xash3d-gc claude/mohaa-probe-sticks). The HL1 intro-tram code had pinned the player to m1l2a's *12 brush, and single-slot world-render boots skipped server PM_Move. The player's maxspeed is also set to 220 when nothing else has set it.
- **m1l2a door hint: verified on screen.** In Dolphin, USE reaches `door_locked` (80 units away), the trigger fires, the retail locked-door rattle plays, and the hint thread's `iprintlnbold` draws "Press USE to open doors. If you cannot open the door, you will be able to hear the handle rattle." under the compass for 5 s, wrapped to two lines (`media/2026-11-26-m1l2a-walk-use/m1l2a-hint-1.jpg`, `-2.jpg`).
- **m1l1 2nd-ranger truck animations** (`truck_idle_captain` and the like) can't be applied. Mission actors wear DoD player bodies, not TIKI skeletons, so the passengers stand in their idle pose.
- **Path nodes on large maps.** m1l2a's 1104 path nodes (46 KB) fail to allocate at map load, so its walks go in straight lines.
- **Music** needs the CD-sourced loose music (`--cd`) or `--music-source`. A Paks-only install has none.
- **Dialogue** aliases missing from map sound tables, e.g. m1l1 `dfr_m1l1_add01` and `truck1_run`.
- Bound since the last update: `loc_convert_string`, and `getboundkey1`/`getboundkey2` (pad buttons). The m1l2b hint read "NILNOT BOUNDNIL"; it now prints "NOT BOUND" as retail does for keys the pad has no button for.

## Rendering
- **The GMC** still shows a flat grey panel near the camera on the ride. The Opel is textured. Check the GMC skin binding (only "studio skinned ... opeltruck" is logged).
- **The m1l1 trucks' skins** now upload as CMPR at gc_quality 0 (2026-11-26). They read dark under the night light grid; compare against retail.
- **Tag-driven parts are missing:** the truck canopy and tailgate animations (`open_gate`, wheels).
- **libogc2 builds** run out of MEM1 loading the m1l1 BSP. Classic libogc fits.

## AI (see MOHAA_AI_ASSESSMENT_2026-11-26.md)
- **Perception:** `sight`, `hearing` and `fov` are bound now (2026-11-26): per-grunt sight range, hearing radius and field of view in GruntLook. Still missing: `noticescale`, `enemysharerange` (alerting nearby allies), and a curious state that turns toward a noise before it attacks.
- **Zones:** `leash`, `tether`, `mindist` and `maxdist` are bound (2026-11-26). An actor stops at its leash edge, fights from `maxdist`, and backs off inside `mindist`. `fixedleash` is accepted, since the leash centre is already fixed. Still missing: `tether` only centres the leash where the entity was when the command ran; it doesn't follow a moving entity.
- **Cover** (2026-11-26): a fighting actor runs to the nearest free cover path node (MOHAA flags DUCK, COVER, CRATE or CONCEALMENT) within 520 units and fights from there; `attackplayer` actors charge instead. Seen in Dolphin on m1l1 ("GRUNT 36 takes cover at -2963 -1754").
- **Damage to the player** (2026-11-26): grunt shots are now scaled by difficulty. Two rifle hits (51 each) used to kill the campaign player; now each hit is about 15 / 23 / 31 on easy / medium / hard. Their hit chance in the campaign is now scaled by difficulty too (x0.35 / 0.5 / 0.7 on easy / medium / hard).
- **The campaign player had no side** (fixed 2026-11-26). On the single-player rules the player joins no team, so grunts never treated them as an enemy. They now count as Allies in MOHAA's campaign.
- **Soldiers don't fight each other.** Grunts only target players, so the Allied friendlies and the Germans ignore one another.
- **Weapons and attack styles** (2026-11-26): `gun` and the `.weapon` field pick the DoD weapon a soldier fires, by MOHAA name; `"none"` leaves it unarmed, and an unknown name falls back to its side's rifle. `type_attack runandshoot` charges; `cover`, `turret` and the other styles fight from cover. `startfiring` and `stopfiring` toggle charging on actors and are ignored on turrets. Still missing: turret behaviour itself (manning an MG42), the MG42 entities, and burst-fire settings.
- **Patrol and alarm** (2026-11-26): `type_idle patrol` plus `patrolpath` walks the info_waypoint chain, following each waypoint's target, and also works as spawn keys. An enemy in sight ends the walk. On a soldier's first sight of an enemy, its `alarmthread` runs and it runs to its `alarmnode`. Seen in Dolphin on m1l2b: patroller02 walks patrolpath02, t329, t327 and on, and loops. Still missing: alerting nearby soldiers (`enemysharerange`), and retail's alarm-type idle behaviour (running to an alarm and raising it).
- **More unbound commands seen on m1l2b:** `nottriggerable`, `triggerable`, `setcollisionentity`, `german`, `immune`, `flypath`.
- **Disguise** (2026-11-26): `$player.has_disguise` (set, read back) and `type_disguise` (command or field). Soldiers that heed a disguise (any type but `none`, the default for mission soldiers) let a disguised player pass. Firing a weapon ends the disguise. Seen in Dolphin on m2l2a: "player disguise on", and 48 soldiers loaded with no shots fired. Still missing: soldiers saluting or asking for papers, the `disguise_range`, `disguise_period` and `disguise_level` checks, and the papers sequence (showing papers with USE).
- **The grunt pool is full on m2l2a** (48 of 48 soldiers), so later mission soldiers wait for a free slot.
- **More unbound commands seen on m2l2a:** `resetleash`, `getwalkanim`.
- **Grenades:** throwing them, and reacting to them.

## Probe tooling
- Menu New Game smoke discs now play `-gctas` replays (buttons). Stick movement doesn't take effect on that route yet.
