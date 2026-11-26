# MOHAA on GameCube: remaining retail gaps

This is a running list, updated with each PR. Each entry says what retail does that the port doesn't yet, and where it shows. Newest changes are at the top of each section.

## Missions and scripts
- **m1l2a door hint is unverified in Dolphin.** MOHAA USE now reaches trigger_use/trigger_multiple through the game's PlayerUse (2026-11-26). But the probe's synthetic pad doesn't move the player on the menu New Game route: the TAS buttons arrive, while the stick input leaves the player in place. Needs: a probe input route that moves the player, or a hardware/pad test.
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
- **Damage to the player** (2026-11-26): grunt shots are now scaled by difficulty. Two rifle hits (51 each) used to kill the campaign player; now each hit is about 15 / 23 / 31 on easy / medium / hard. One soldier still hits about once a second at the m1l1 checkpoint, so their accuracy is well above retail's. A per-skill AI accuracy curve is still to do.
- **The campaign player had no side** (fixed 2026-11-26). On the single-player rules the player joins no team, so grunts never treated them as an enemy. They now count as Allies in MOHAA's campaign.
- **Soldiers don't fight each other.** Grunts only target players, so the Allied friendlies and the Germans ignore one another.
- **Attack styles:** `type_attack` turret behaviour, plus `gun`, `startfiring` and `stopfiring`.
- **Alarm and patrol:** `type_idle` alarm and patrol, `alarmnode`, `alarmthread` and `patrolpath`.
- **Disguise:** `type_disguise` and the `disguise_*` settings, used by m1l2a/m1l3.
- **Grenades:** throwing them, and reacting to them.

## Probe tooling
- Menu New Game smoke discs now play `-gctas` replays (buttons). Stick movement doesn't take effect on that route yet.
