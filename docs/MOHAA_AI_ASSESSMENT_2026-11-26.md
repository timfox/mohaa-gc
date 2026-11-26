# MOHAA AI: a first assessment (2026-11-26)

This compares how retail Medal of Honor: Allied Assault runs its soldiers with what the GameCube port runs today. It is based on:

- the port's source: `dod-gc/src/dod_grunts.{c,h}`, `dod_grunt.cpp`, `dod_mohaa.c`, `dod_mohaa_ents.cpp`;
- the 53 retail scripts the SD stage writes for m1l1, m1l2a, m1l2b and `global/`;
- the Dolphin runs on 2026-11-26 (`media/2026-11-26-codex-engine/`).

## Retail MOHAA: script-driven actors, not GOAP

MOHAA does not use goal-oriented action planning (that came later, with F.E.A.R.). Each `Actor` in the game DLL runs a think state machine. Level scripts steer it with per-actor settings and handler threads.

- **Idle behaviours (`type_idle`):** idle, patrol along a `patrolpath`, alarm (run to an `alarmnode`, then `alarmthread`), and the disguise states used by the m1l2a/m1l3 papers scenes (`type_disguise` with salute, sentry or officer, plus `disguise_range`, `disguise_period` and `disguise_level`).
- **Perception:** `sight`, `hearing`, `fov`, `noticescale`, and `enemysharerange`, which alerts allies nearby. A curious state sits between idle and attack: the actor looks toward a sound or a glimpse before committing.
- **Attack behaviours (`type_attack`):** cover (moves between path nodes flagged as cover, peeks and fires), turret (mans an MG42), alarm, and run-and-shoot.
  - A soldier stays inside `leash` / `fixedleash`, `tether`, `mindist` and `maxdist`.
  - Its weapon comes from `gun`, its aim from `accuracy`, and `favoriteenemy` / `threatbias` pick its target.
  - It throws grenades and reacts to them (`gren_awareness`), and goes through pain and death animation sets.
- **Script control:** `ai_on`/`ai_off`, `runto`/`walkto`/`crouchto`, `turnto`, `lookat`, `aimat`, `attackplayer`, `startfiring`/`stopfiring`, `say`, `anim`, plus `waittill movedone` / `animdone` / `death`, and handler threads (`painhandler`, `deathhandler`, `attackhandler`).

## The port today: the DoD grunt pool

The mission soldiers are DoD-GC grunts. A grunt is one prop edict wearing a team's player body, plus a row of plain arrays (`dod_grunts.h`). It has no path graph of its own and no weapon entity. There are five states:

- **hold:** stands where the script put it;
- **wander:** walks a heading, turning now and then;
- **advance:** runs at its target;
- **shoot:** stands and fires, with a hit chance that falls off with distance;
- **dead.**

Perception is a line trace roughly every 0.35 s, budgeted at 4 a frame, out to 1800 units. Scripts own their grunts:
- `ai_on`/`ai_off`, `attackplayer`, `runto` and `walkto` map onto it.
  - `runto`/`walkto` follow the converter's path nodes when `maps/<map>.nodes` loaded; otherwise they go in a straight line.
  - As of today, a walk that makes no progress for 4 s arrives anyway, so a blocked actor can't hold a mission.
- `turnto`, `lookat` and `aimat` turn them.
- `waittill movedone` and `animdone` fire.
- The pool holds 48. Extra map soldiers wait in a list and come in near the player as slots free up.

## Coverage of what the staged scripts use

Calls from the 53 staged scripts (m1l1, m1l2a, m1l2b and `global/`), counting `$actor <command>` forms:

| Script command | Calls | Port |
|---|---:|---|
| runto / walkto | 81 / 12 | yes (path nodes, or straight line) |
| turnto / lookat / aimat | 44 / 47 / 1 | yes |
| say | 69 | yes (sound table) |
| useweaponclass, holster / unholster | 37, 11 / 9 | yes |
| accuracy, threatbias | 11, 23 | stored; grunt hit chance is its own |
| setaimtarget, forceactivate | 11, 11 | yes |
| attackplayer | 4 | yes (grunt ADVANCE) |
| **tether** | 16 | **not bound** |
| **type_attack** | 15 | **not bound** (no cover/turret behaviour) |
| **gun** | 13 | **not bound** (grunts carry their side's rifle) |
| **leash / fixedleash** | 9 / 1 | **not bound** |
| **sight / hearing / noticescale** | 7 / 3 / 2 | **not bound** (one fixed sight range, no hearing) |
| **mindist / maxdist** | 5 / 6 | **not bound** |
| **startfiring / stopfiring** | 6 / 6 | **not bound** |
| **alarmthread / alarmnode / patrolpath** | 5 / 2 / 2 | **not bound** |
| **type_idle / type_disguise** | 3 / 1 | **not bound** (m1l2a's papers scene) |

The VM logs each unbound one as "'X' on entity is not bound yet" and goes on, so missions keep running. The soldiers just behave like DoD grunts.

## What this means in play

- **Scripted scenes run.** m1l1's opening ride, the checkpoint guard and the bazooka ambush all play through to the player getting weapons. The 2nd-ranger truck animations ("truck_idle_captain" etc.) can't be applied, because grunts wear DoD player bodies, not the TIKI skeletons. So the passengers stand in their idle pose.
- **Firefights are simple.** Retail soldiers take cover, keep to their leash and tether zones, toss grenades and alert each other. A grunt stands and shoots, or runs straight at you. The difference is largest in m1l1's town fight and m1l2a's courtyard.
- **Stealth and disguise are missing.** m1l2a and m1l3's undercover sections depend on `type_disguise` and perception tuning, which don't exist yet.

## Suggested order of work

1. **Perception and leash fields** (`sight`, `hearing`, `fov`, `leash`, `tether`, `mindist`/`maxdist`): store them per grunt and use them in `DodGrunt_Looked` and the advance step. This is cheap and changes most fights.
2. **Cover from path nodes:** the converter already writes MOHAA's path nodes with their flags. Add an attack sub-state that picks the nearest cover node toward the enemy, moves there, and alternates hide and fire.
3. **gun** (per-grunt weapon and damage table) and **startfiring/stopfiring** for scripted volleys.
4. **Alarm and patrol** (`type_idle alarm|patrol`, `alarmnode`, `alarmthread`, `patrolpath`) on top of the existing walk orders.
5. **Disguise** for m1l2a/m1l3, once perception exists.
6. **TIKI actor bodies** (the German private already has a GCA pack) so scripted animations apply to mission actors, not just the pose set.

All of this has to stay within the grunt's cost budget: one edict per soldier, staggered traces, and a 48-slot pool on MEM1.
