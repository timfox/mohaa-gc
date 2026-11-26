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
- **The m1l1 trucks' skins** now upload as CMPR at gc_quality 0 (2026-11-26). They read dark under the night light grid; compare against retail.
- **Tag-driven parts are missing:** the truck canopy and tailgate animations (`open_gate`, wheels).
- **libogc2 builds** run out of MEM1 loading the m1l1 BSP. Classic libogc fits.

## AI (see MOHAA_AI_ASSESSMENT_2026-11-26.md)
- **Perception:** `sight`, `hearing`, `fov`, `noticescale` and `enemysharerange` aren't bound.
- **Zones:** `leash`, `fixedleash`, `tether`, `mindist` and `maxdist` aren't bound.
- **Attack styles:** `type_attack` cover and turret behaviour, plus `gun`, `startfiring` and `stopfiring`.
- **Alarm and patrol:** `type_idle` alarm and patrol, `alarmnode`, `alarmthread` and `patrolpath`.
- **Disguise:** `type_disguise` and the `disguise_*` settings, used by m1l2a/m1l3.
- **Grenades:** throwing them, and reacting to them.

## Probe tooling
- Menu New Game smoke discs now play `-gctas` replays (buttons). Stick movement doesn't take effect on that route yet.
