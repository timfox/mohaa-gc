# Morpheus script VM (MOHAA `.scr`)

This folder runs Medal of Honor: Allied Assault mission scripts inside DoD-GC.
It's a small, self-contained C99 library. The game code embeds it and binds
script commands to GoldSrc entities.

```
maps/m1l1.scr ──compile at level load──> bytecode ──> threads (coroutines)
                                                        │
                       ms_register("moveto", MS_ON_ENTITY, ...)   <- DoD-GC binds
                       "$door1 moveto (0 0 96)"  ─────────────────> func_door
```

## Licence

MIT, like the rest of this repository. This is a **clean-room** implementation.
It was written from how the shipped MOHAA scripts behave, with OpenMoHAA
(GPL-2) used only as a behaviour reference. No OpenMoHAA code is copied.
That keeps it safe to link into the DoD-GC game code. If that code comes
from hlsdk-portable, it is under Valve's HL SDK licence, and that licence
can't be combined with GPL code.

## What works

The full language:

- labels with parameters, `thread`, `waitthread`, `exec`, `waitexec`
  (including `file.scr::label` and the method forms `$ent thread label`),
  `goto`, `end <value>`
- `wait`, `waitframe`, and `waittill` on any listener (`level waittill spawn`,
  `$trigger waittill trigger`, `$ent waittill removed`)
- `local.` `level.` `game.` `parm.` `group.` `self.` variables, entity fields
  (`$door.locked = 1`), arrays (`local.a[1][2]`, copy on write), const arrays
  (`a::b::c`), `makearray`/`endarray`, `.size`, vectors `(x y z)`
- `if`/`else`, `while`, `for`, `do`/`while`, `switch`/`case`/`default`,
  `break`, `continue`, `try`/`catch`, `?:`, every operator, including the
  old `ifequal`-style word operators
- `$targetname` lookup. Several matches give a list, and `$guys hide`
  applies to each one.
- MOHAA's quirks: `-` is negation or subtraction depending on whitespace,
  identifiers swallow punctuation (`global/ambient.scr`), and runtime
  errors are reported while the script keeps going
- built-ins: printing, `randomint`/`randomfloat`, math in degrees, vector
  helpers, `isdefined`, `typeof`, `getarraykeys`

Not yet: save/load of running threads, the remaining ~200 thread commands
that touch the game (HUD, camera, music, objectives), and every entity event.
Those are host bindings, added as DoD-GC needs them.

## GameCube budgets

- Every allocation goes through the host allocator and is counted.
  `ms_config.memory_budget` makes allocations past the cap fail cleanly.
  The mission test peaks at about 28 KB.
- The compiler works one top-level statement at a time and frees its syntax
  tree after each, so compiling costs little more than the result: the peak
  is bounded by the largest statement, not the file.
- Compiled scripts are compact. Name ids and string-constant indexes are 16-bit
  operands, small ints one byte, the line table (for error messages) a varint
  stream, and a script's string constants share one block with a pinned
  reference count instead of a heap allocation each.
- `msrun -stats` prints where the memory goes, per script and by kind.
- Threads are coroutines with a small growable value stack (16 slots to
  start). There are no OS threads.
- A thread that loops 10,000 times without waiting is killed and reported,
  so a broken script can't stall a frame.
- Bytecode stays native-endian in RAM and is never shipped, so the
  PowerPC's big-endian byte order doesn't matter.

## Binding DoD-GC

```c
static int sv_moveto(ms_call *c)              /* "$door moveto (0 0 96)" */
{
    edict_t *e = edict_from_id(ms_call_target(c)->u.id);
    float dest[3];
    ms_arg_vector(c, 0, dest);
    mover_start(e, dest);                     /* func_door / func_train logic */
    return 0;
}

static int sv_waitmove(ms_call *c)            /* resumes on "movedone" */
{
    ms_call_wait_signal(c, ms_call_target(c), "movedone");
    return 0;
}

ms_host host = { .load_file = pk3_load, .print = con_print,
                 .find_targetname = find_by_targetname, .entity_valid = edict_alive,
                 .get_field = ent_get_field, .set_field = ent_set_field };
ms_vm *vm = ms_create(&host, &(ms_config){ .memory_budget = 512 * 1024 });
ms_register(vm, "moveto", MS_ON_ENTITY, sv_moveto, NULL);
ms_register(vm, "waitmove", MS_ON_ENTITY, sv_waitmove, NULL);

ms_exec(vm, "maps/m1l1.scr", NULL, NULL, NULL, 0);   /* at level load */
ms_notify(vm, &level, "prespawn");                   /* then "spawn" */
ms_frame(vm, gpGlobals->time);                       /* every server frame */
ms_notify(vm, &door, "movedone");                    /* from game code */
ms_entity_removed(vm, id);                           /* when an edict is freed */
```

Following the project rule of mapping MOHAA features to their GoldSrc
equivalents, the bindings target existing DoD-GC entities:

| MOHAA script use | DoD-GC / GoldSrc equivalent |
| --- | --- |
| `script_object`, `script_model` + `moveto`, `rotateto`, `time`, `waitmove` | brush/model movers (func_door/func_train mover code), `movedone` notify |
| `trigger_multiple`, `trigger_use`, `waittill trigger` | trigger_multiple / trigger_once, notify on touch/use |
| `trigger $name` | `SUB_UseTargets` on the edict |
| `spawn <class> key value...` | `CREATE_NAMED_ENTITY` + keyvalues + `DispatchSpawn` |
| `hide`, `show`, `remove`, `playsound`, `loopsound` | `EF_NODRAW`, `UTIL_Remove`, `EMIT_SOUND` |
| AI: `runto`, `attack`, `turnto`, `ai_on/off`, `waittill death` | goals on the GOAP planner, `death` notify |
| `iprintln`, objectives, `centerprint` | HUD messages |

## Tools

```bash
make -C script                                   # builds out/msrun
out/msrun tests/scripts/mission.scr              # run against the mock world
out/msrun -mem tests/scripts/mission.scr         # with memory stats
python3 tools/check_scripts.py "/path/to/MOHAA/main"   # compile every retail script
```

`msrun` builds its mock world from `//@ent`, `//@at` and `//@run` comment
directives in the script (see `tools/msrun.c`). It logs every entity command
nobody handles, which is how the tests check what a script asked the world
to do.

## Files

| File | Contents |
| --- | --- |
| `include/morpheus.h` | public API: host table, commands, values |
| `src/ms_compile.c` | lexer, recursive-descent parser, bytecode compiler |
| `src/ms_vm.c` | threads, scheduler, interpreter, call interface |
| `src/ms_value.c` | counted allocator, names, strings, arrays, operators |
| `src/ms_builtins.c` | thread commands (flow, printing, math, vectors) |
| `tools/msrun.c` | mock-world runner and compile checker |
