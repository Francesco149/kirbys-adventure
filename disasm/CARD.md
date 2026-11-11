# Documenter card: one unit, from evidence to gates, with `kd`

For a coding agent with a shell. You document one **unit** of Kirby's Adventure (USA, Rev A): a family of routines,
their tables and their RAM variables, or a script. The output is one file, `db/<unit>.toml`: names, descriptions
and **claims that a replay checks**. You are done when `./kd check --unit <unit>` prints `PASS` and no `WEAK`
line. Everything runs locally and is free; your turns are the only cost, so prefer one informative command to
ten small ones.

Work in `/opt/src/kirbys-adventure/disasm`. Write only `db/<your unit>.toml` (and, when you add a trace,
`corpus/` through `kd corpus add`). Never edit `out/`, `evidence/`, other units' files or the tools.

## The loop

1. **Find the unit's code and state.** Start from what you were given (an address, a RAM variable, a behaviour).
   `./kd xref 0599` lists the routines that read and write an address; `./kd fn 3E:C8DD` shows a routine.
2. **Look at the evidence before you read the code.** `kd fn` prints how often every instruction ran, which
   branches went one way only, the callers, the callees, the RAM it touches and the ROM tables it reads.
   `kd when` says in which movies and from which frame it runs; `kd look movie@frame` shows that frame.
3. **Watch it work.** `./kd io NAME --on main@3000+300` tabulates real calls: registers in and out, every
   address read (with the values seen) and written. `./kd trace` prints one call instruction by instruction.
   `./kd try` changes RAM or ROM at a frame and shows what differs from an unchanged run.
4. **Say what it does, in state terms.** Inputs, outputs, side effects, and what the values mean in the game
   when you know. If you do not know what something means, say what it does and stop there.
5. **Write the entries and the claims** (formats below). Every routine, data region and RAM variable you
   describe needs at least one claim about it, and the claim must be able to fail.
6. **`./kd check --unit <unit>`** until it passes. When a claim fails, your understanding is wrong: fix the
   description (and the claim to match the truth), never loosen a claim just to make it pass.
7. **Code that never ran is missing evidence, not a licence to guess.** `never ran` and `NEVER TAKEN` /
   `ALWAYS TAKEN` in a listing mean no movie exercises that path. Either leave it out and list it under
   "Open" in the unit's `summary`, or author a trace that reaches it (`../tas/kt`, card in `../tas/DRIVER.md`),
   add it with `./kd corpus add ../tas/runs/<run>/movie.txt --id <id> --note "<what it exercises>"`, and
   document what the new evidence shows.
8. **Report** what you documented, how many claims pass, and what stays open.

## Commands

```
./kd status                          coverage and documentation levels
./kd next [--bank 3E] [--kind code|data] [-n 20]     undocumented chunks, most used first
./kd fn AT|NAME                      routine: listing with run counts, callers, callees, RAM, tables
./kd dis AT [--len 64]               any range (code, data, untouched bytes)
./kd xref X [--len N]                X = RAM address or name: readers and writers; X = BB:AAAA: who reads / calls it
./kd when AT|NAME [AT ...]           which corpus movies run it, how often, first frame (several addresses at once:
                                     all the exits of a routine in one call)
./kd io AT|NAME --on WINDOW [--calls 200] [--rows 12] [--addrs 40]
./kd find AT|NAME --on WINDOW [--on WINDOW ...] --where "EXPR" [--rows 12]   calls for which EXPR is true (what a
                                     call claim's `where` sees: a x y, ra, rd, wr, ran(...), calls ...): how many per
                                     window, and their frames. For paths that `kd when` cannot find.
./kd trace AT|NAME --on WINDOW [--call K] [--max 400]
./kd watch 07AD 07AE --on attract@560+600   values of RAM addresses over a window, one line per change
./kd look movie@frame                picture -> out/view/<movie>-<frame>.png (Read it)
./kd try --on movie@frame --frames N [--poke ADDR=V ...] [--hold] [--patch BB:AAAA=V ...] [--input "R*30 A"]
./kd types                           the object types: first script, how often and where it first started
./kd vm                              the script opcode table: layout, flow, where and how often each opcode ran
./kd script AT|NAME [--len N]        a script (bytecode) listing with run counts, and the 6502 code and data between
                                     the scripts; `kd next --kind script` queues them
./kd sprites [--toml]                pose tables and sprite groups that are not in the database yet
./kd packed [--toml]                 packed streams (what `unpack` expands) that are not in the database yet
./kd corpus list | add FILE --id ID --note TEXT
./kd check --unit U [-v] [--no-build] [--no-status]
```

Input specs (`--input`, the `input` field) use the workbench's letters: `A B` buttons, `S` Select, `T` Start,
`U D L R` directions, `.` nothing; `R*30` repeats, `RA*8 .*4` is a sequence, `(B .)x8` a loop.

`AT` is `BB:AAAA`: bank (00-3F) and CPU address, hex. Banks 3E and 3F are fixed at `$C000` and `$E000`; every
other bank appears at `$8000` or at `$A000` (the listing shows which). `WINDOW` is `movie@start+length` or
`movie@start-end` in frames of a corpus movie (`kd corpus list`; `main` is the whole game from power-on to the
credits, 137,712 frames). A window costs under a second to reach, so sample several far apart.

## The unit file

```toml
unit = "rng"
title = "Random numbers and the 8x8 multiply"
summary = """What the unit is and how its parts fit, in a paragraph. Then 'Open:' with what is not known."""

[[sym]]                       # a routine (kind = "sub", the default), a code run reached only by jumps
at = "3E:C8DD"                # (kind = "part"), or just a named place inside a routine (kind = "label")
name = "random"
desc = """What it does. Inputs, outputs and side effects in sentences."""
in = "A = exclusive upper bound, or 0"          # optional
out = "A = random number; X, Y unchanged"       # optional
comments = { "C8E6" = "11 rounds" }             # optional inline comments, by address inside the routine

[[data]]
at = "3E:C6DD"
len = 256
name = "half_square_lo"
format = "rows:16"            # bytes | rows:N | ptr16 | ptr16:BB (targets in bank BB) | ptr16m1 (address - 1) | fill
                              # sprites | poses | poseptr:BB (sprite data, see db/sprites.toml)
                              # packed | packlo:HI[:BANK] | packhi:LO | packbank:LO (see db/unpack.toml)
desc = "..."

[[ram]]
at = "003E"
len = 2
name = "rng_state"
desc = "..."

[[claim]]
id = "rng.mul8.model"         # unique; start it with the unit name
about = ["mul8"]              # the names this claim verifies
text = "mul8 returns the 16-bit product of A and X: low byte in A, high byte in X."
kind = "call"
fn = "mul8"
on = ["main@3000+120", "w12-opus@30000+120"]
expect = "(rx << 8 | ra) == a * x"
```

`db/rng.toml` is a complete, passing example with every claim kind. Names are lower_snake_case and global: check
with `grep -rn name db/` before choosing one.

A model that several claims need is written once and shared, also across units:

```toml
[[model]]
name = "probe_geometry"       # global, like every name
code = '''
def down(rd, romrd, xlo, ylo, pt=None): ...
'''

[[claim]]
...
use = ["probe_geometry"]      # these come first, the claim's own `model` (optional) after them
```

`db/probes.toml` defines `probe_geometry` (the four probes as functions of the room's bytes) and `db/kcoll.toml`
uses it together with its own `kirby_feet`: a routine that calls a documented routine is modelled by calling that
routine's model.

## Claim kinds (every expression is Python)

| kind | fields | names you can use |
|---|---|---|
| `call` | `fn`, `on` (list of windows), `expect`, optional `where` (use only the calls for which it is true), `min_calls` (default 5), `max_calls`, `model` (Python source: helper functions), `cases = { "ra in (3, 4)" = 100, "rp & 1" = 20 }` (each expression must be true on at least that many of the calls: the paths the windows must hold) | per call: `a x y p s` at entry, `ra rx ry rp rs` at return, `rd[addr]` first value read from an address the call had not written, `wr[addr]` last value written, `mem(addr)` value at return, `reads`, `writes`, `romrd` (PRG offset → byte, in the order of the first read), `calls` (routine names called, in order), `ran("BB:AAAA")` (how often this call executed the instruction there: the way to say which path a call took, in `expect`, `where` and `cases`), `n` instructions, `frame` |
| `frames` | `on`, any of `always` / `never` / `sometimes` (expression or list) | per frame: `ram[addr]`, `prev[addr]`, `r("name")` / `pr("name")` (a RAM variable now / one frame ago, 16-bit when `len = 2`), `n("routine")` times it started this frame, `pad` (joypad mask: A=1 B=2 Select=4 Start=8 Up=16 Down=32 Left=64 Right=128), `frame` |
| `effect` | `on = "movie@frame"`, `frames`, `poke = { "0599" = 9 }` and/or `patch = { "3E:C6DD" = 0 }`, optional `hold = true` (re-poke every frame), `input = "R*60"` (the treated run gets these inputs instead of the movie's), `expect` | `ram` / `ctl` (after the treated run / the control run, which is the movie untouched), `diff` (set of RAM addresses that differ), `n("routine")` / `cn("routine")` executions in each run, `r("name")` / `cr("name")` |
| `xref` | `expect` | over the whole corpus: `writers(x)`, `readers(x)` (sets of routine names; `x` = RAM name, address, or `(address, length)`), `callers("routine")`, `callees("routine")`, `datareaders("data name")`, `touched(x)` |
| `static` | `expect` | `rom[off]`, `u8(at)`, `u16(at)`, `O("name")` PRG offset, `kind(off)`, `executed(off)`, `dataread(off)` |
| `format` | `about` or `about_formats = ["sprites", "poses", "poseptr"]` (every region of the unit in these formats; the packed formats work the same way), optional `complete = true` | none: the regions must parse, and every byte the corpus read must have been read by the instruction that reads that kind of byte |

Everywhere: `A("name")` is a name's CPU address, `O("name")` its PRG offset. A routine that has no name in
the database is written by its address in a claim: the listing's `sub_3F_E45D` or `loc_3F_E45D` is
`"3F:E45D"` (the automatic names are not stable, the address is).

The `pad` mask of a `frames` claim is the workbench's layout (A = 1 ... Right = 128), which is the reverse of
the bit order the game keeps in RAM (A = $80 ... Right = $01).

Scripts (the bytecode that drives every object; `db/vm.toml` is the worked example) have two more kinds:

| kind | fields | names you can use |
|---|---|---|
| `vmop` | `op` (opcode name from `kd vm`), `on`, `expect`, optional `at = "24:A916"` (only the instruction at that script address), `min` (default 5) | per execution: `args` (operand values in order), `banks`, `op`, `low` (low four bits of a $5x-$Dx opcode: its wait), `addr`, `length`, `next` (where the thread went next, or None), `thread`, `rd` / `wr` / `reads` / `writes` (what the opcode's handler read and wrote), `calls`, `rom` |
| `vmlen` | `ops` (opcode names), `on`, optional `min` | none: checks that every execution continues at start + declared length or at a decoded target |

A script is documented with `[[script]] at name desc` (it runs to the next script label), an opcode with
`[[opcode]] op name args flow desc`. `kd script` shows which instructions of a script never ran.

Details that matter when you write expressions:

- `rd`, `wr` and `romrd` are dicts (`wr[0x3E]`, `0x3E in wr`, `wr.get(0x3E)`); `romrd` is keyed by PRG offset.
  `reads` and `writes` are the sets of their keys.
- `writers()`, `readers()`, `callers()`, `callees()` and `datareaders()` return a set of routines that compares
  by address, so `'random'` and `'3E:C8DD'` are the same member whichever unit named the routine.
- Elements of `calls` equal both the routine's name and its address: `calls[0] == '3E:D655'` and
  `calls[0] == 'obj_free'` are the same test.
- A frame can end while the game is in the middle of its object pass. An invariant about lists the pass edits
  holds only on frames where the pass began and finished (`db/objects.toml`, `objects.run_all.frames`).
- `n("routine")` counts per emulated frame. On a lag frame the main loop does not finish and a "once per frame"
  routine runs zero times; relate it to a state change, or allow 0.
- A routine that runs a handful of times in the whole corpus needs `min_calls` set to what exists (`kd when`).
- Some calls go through a far-call helper that takes the target address and bank from the bytes after the
  `jsr` (3E:D805 is one). `kd xref` on such a target shows the helper, not the real call site, and the code
  after the inline bytes starts a new code run: name it with `kind = "part"`.
- A `part` takes over everything after it up to the next name: `readers()` / `writers()` report the part, not
  the routine it sits in. `callers()` of a part that is reached by a branch is empty (a branch is not an edge).
- `kd when BB:AAAA` works for any instruction, not only for a routine's entry: it gives the first frame of a
  rare path, which is where its window belongs.
- A model's helper functions share the namespace of the claim: `a x y p s`, `ra rx ry rp rs`, `rd wr mem n`
  are taken (a helper named `p` is the status register by the time `expect` runs).
- A call's `rd` / `wr` do not contain what an interrupt did while the call ran, and the PPU is not in the log:
  writes to $2000-$2007 show their last value only.
- `datareaders()` knows at most two readers per byte; do not write "only" about a table three routines read.
- `max_calls` is per window (default 400) and `min_calls` counts over all windows: a claim on a routine that runs
  once per frame sees at most one call per frame of window.
- A tail call (`jmp` to another routine at the end) is not in `calls`; check what the jumped-to routine wrote.
- `rd` has only what the call read before writing it: `$4B` / `$4C` set by `obj_point_off` inside the call are
  not in `rd` of the caller. Compute the point from the object's position instead (`point()` in `kirby_feet`).
- `mem(addr)` works only for an address the call read or wrote.
- Functions in `model` do not see `rd`, `wr`, `romrd`, `mem` or the registers: pass them in. They do see `A`, `O`
  and (in `static` claims) `rom`, `u8`, `u16`. Module-level variables of a model persist across the calls of one
  claim.
- `NEVER TAKEN` / `ALWAYS TAKEN` in a listing mean the target (or the instruction after the branch) never ran at
  all. A branch to code that other paths reach has no marker: compare the run count of the branch with the
  count of the instruction after it.
- Falling or branching into a routine is not an edge: `callers()` has calls and jumps only. But a `call` claim
  on a routine also sees the entries that fall into it, and `calls` holds nested calls too.
- `rp` differs from `p` in bits 4 and 5 after `php` / `plp`, and in bit 2 when an interrupt lands inside the
  call: compare flags with `& 0xC3`. Stack writes (`pha`) are in `writes`.
- `wr` has only the bytes the call wrote: the high byte of a 16-bit value that an `inc` did not touch is not
  there; `mem()` is.
- `--poke` and `--patch` values are decimal, `0x0F` or `$0F`; the address side is hex.
- `calls` has what was reached by `jsr`. A routine reached through `call_vector` / `call_ay` (an indirect jump) or
  by a `jmp` at the end is not in it: use `ran("BB:AAAA")` on its first instruction.
- A routine that takes parameter bytes from behind its `jsr` (`far_call`: address and bank of the routine to call;
  `ppu_record_inline`: the address of a record) is declared with `inline = N` in its `[[sym]]`; the listing shows
  the bytes as "parameter bytes of the call" and the code after them belongs to the same routine. `callers()` of
  a far-called routine is `call_vector`.
- `kd fn` prints `falls into: NAME` when a routine has no `rts` or `jmp` at its end. A `call` claim on the routine
  fallen into also sees the calls that fall in.
- In an `effect` claim the bytes $01B0-$01FF (the CPU stack) differ by timing: leave them out of "nothing else
  differs". `u8` / `rom` are not available in `effect` claims: put table bytes into the model as literals.
- In `cases`, use `rd.get(addr)` for an address that a call which left early did not read.
- Iterating a routine set (`writers(x)`) gives 'BB:AAAA' strings.
- `n("routine")` (frames and effect claims) also counts the times a routine is fallen into. To read counts while
  exploring, put them where the error shows them: `expect = "{}[(n('a'), n('b'))]"` fails with the tuple.
- A script instruction runs before the object's tick routine in the same frame: after a state routine changes the
  script, the new script's first instructions (and its `on_tick`) run in the next frame, before that frame's tick.
  A waiting thread's pc is the address of its next instruction. An object's thread is `obj_first_thread + slot`
  (Kirby's is not always thread 0).
- Some movies advance the game only every second frame in places (w12-sonnet around 48850): count calls, not frames.
- A `[[model]]` name cannot go into `about`; `u16` is not available in `vmop` claims.
- Another agent may add or rename a name while you work. For RAM of another unit use the address in expressions
  (`rd[0x597]`), and its name only in your descriptions.
- A held poke (`hold = true`) of a byte the game recomputes every frame changes nothing; poke what it is
  computed from.

What makes a claim worth having:

- **A model beats a property.** `expect = "(rx << 8 | ra) == a * x"` says everything about `mul8`; "A changes"
  says nothing. For a routine with a computable result, write the computation in `model` and compare.
- **Say which paths the windows hold.** A model that is compared on 3,000 calls of the common path says nothing
  about the rare one. Put the rare paths into `cases` of the model claim (or a second claim with `where`), find
  their frames with `kd when` on an instruction of the path, and add those windows.
- **Two situations, not one.** Give `call` and `frames` claims windows from different places (another world,
  another movie, a boss, a menu). `kd when` finds them. One window is reported as `WEAK`.
- **Say when it must be true and show that it happens.** A `frames` claim needs a `sometimes` so that it cannot
  pass on frames where nothing happens.
- **Completeness comes from `xref`.** "Only `random` writes `rng_state`" is checked against every instruction
  that ran in the whole corpus.
- **Causality comes from `effect`.** If a variable is "lives", poking it must change what the game does with
  lives; if bytes are scratch, poking them must change nothing.
- **Tables are checked by content or by mutation.** A `static` claim for a formula; an `effect` with `patch`
  for "entry N controls X".

## Finding things

- `tas/knowledge/ram-map.md` (RAM addresses collected from many sources, with a status column) and the old
  static notes in `/opt/src/nes-disasm-tool/docs/findings/` are **leads**. Several are wrong. A lead becomes a
  name only after your own evidence agrees.
- Objects: 18 slots, tables indexed by slot in `$6074..$63FF`; slot 1 is Kirby. Script state per thread lives
  in `$6360..`. The frame loop is `3F:E45D` → `obj_run_all` (objects and scripts); `db/objects.toml` has the
  pass, the slot lists, `obj_spawn` and the per-object routine pointers (`obj_tick_*`, `obj_move_*`,
  `obj_position_*`, `obj_draw_*`), and the type tables that give every object type its first script.
  `db/motion.toml` has the coordinates, velocities and the camera; `db/draw.toml` the draw routines, the
  sprite group format (count, then X offset, Y offset, tile ^ 1, attribute) and the two sprite buffers.
  `db/sprites.toml` has every pose table (`pose_tab_BB_AAAA`, what a `sprite_map` instruction names) and
  every sprite group, under address names: when you document an object, rename its tables after it.
- Packed data: `unpack` (3E:C43A) expands a stream at ($16) to ($18); `db/unpack.toml` has the routine, every
  stream (`packed_BB_AAAA`, with the number of bytes it expands to) and the tables that address them
  (`room_data_*` by room number, `tileset_*`). A room's stream is expanded at `$67EE`. When your unit uses a
  stream, rename it there and say what the expanded bytes are.
- Rooms: `db/rooms.toml`. `room` ($055E, 16 bits) is the room number, `room_load` (3F:E638) loads it; the
  header is at `$67EE` (`room_width`, `room_height` in screens of 256 x 192 pixels), `room_map` at `$68C8` holds
  one block number per 16x16 block, `room_cell` (3F:ECF1) turns a position into a cell. A door is a 5-byte record
  in `room_doors`; a room's enemies are its object list (`room_objs_*`, `objs_spawn`), whose kind byte gives the
  object type through `objs_kind_type`. A `call` claim on `room_load` needs windows of 40 frames or more around
  the load (it runs for about 9 frames); `../tas/traces/main/rooms.csv` has the frames. Bank helpers:
  `bank8_set` / `banka_set` (A = bank at `$8000` / `$A000`), with `_push` / `_pop` pairs.
- Tiles: `db/tiles.toml`. `tiles_row` / `tiles_col` / `block_draw` draw a row of 32 tiles, a column of 24, one
  block; a block is `block_tile_0-3` (top left, top right, bottom left, bottom right) and a palette in
  `block_attr`; `nt_attr` is the copy of the attribute tables. Nothing writes the PPU directly: `ppu_write`
  ($00 fill, $01 length, $02/$03 address, $16/$17 source) appends a record to `ppu_queue`, `ppu_flush` sends it
  from the interrupt. `scroll_update` follows the camera (`drawn_x`, `drawn_y`, `scroll_x`, `scroll_y`).
- What is at a point: `block_prop_at` (3F:EF90; $4B:X = X position, $4C:Y = Y position) returns the block's
  `block_prop` and leaves bank 12 mapped for the caller to restore; `door_find` (3F:EDA2) is the door at a point;
  `objs_spawn_col` / `objs_spawn_row` create the objects of the room's list. `db/inroom.toml`.
  The property indexes `prop_shape` and `prop_extra` (bank 12); `prop_shape_at`, `prop_bit5_at`, `prop_bit7_at`,
  `prop_pair_at` return parts of them for the block at a point, `block_break_at` / `block_put_at` change a block
  of `room_map` and redraw it. `db/props.toml`. What the numbers mean is partly open: it is in your unit's code
  if it calls these.
- Kirby and the blocks: `db/kblocks.toml`. `obj_point` / `obj_point_off` (21:9CED / 21:9D01; X, Y = signed
  offsets) put the current object's position where the tests want it. Bit 7 of `prop_shape` is water
  (`kirby_in_water`, `water_entered`, `water_left`), the pair of `prop_extra` a current (`current_push`,
  `room_current`), shapes 9, $A, $B blocks that break (`break_test_0` / `_1` at a point, `break_rect_0` / `_1`
  over `kirby_rect`). 21:9955 creates the object numbered in `spawn_vars+3` at $4B:X, $4C:Y; 3F:F826 requests
  a sound.
- Collision: `db/probes.toml`. `probe_down` / `probe_up` / `probe_left` / `probe_right` (3F:F241, F14D, F39E, F4E2;
  the point as for `block_prop_at`) answer carry clear when a surface is in reach, the signed distance in
  `probe_dist` ($0579, 16 bits) and the kind of surface in A (2 flat, 3-6 sloped floors, 7-8 sloped ceilings).
  A block's class (0 empty, 1 solid, 2-3 floor only, 4-9 sloped floors, 10-11 sloped ceilings) is
  `prop_class[block_prop] >> 1`. Kirby's use of them is `db/kcoll.toml`: `kirby_floor`, `kirby_ceiling`,
  `kirby_walls` (and the `_stop` variants that clear the velocity), `floor_kind` / `floor_dist`, bit 2 of
  `kirby_flags` ($05FB) = a foot landed. The objects' own versions are `db/ocoll.toml` (bank 22: `obj_walk`, `obj_collide`, the point sets `obj_pts`); they use the position, not the world position.
- The top level: `db/frame.toml`. `room_enter` (3F:E45D) loads the room and runs the frame loop (frame_wait,
  joypad_edges, obj_run_all, scroll_update) until `leave_code` ($056A) is not 0: 1 next room, 3 a life lost, 4 the
  stage's end, 5 a stage cleared. `lives` ($0599), `hp` ($0597, $2F full, 8 per bar), `hp_max`, `score` ($0593, 24
  bits, in tens), `world` ($0558), `stage_door` ($0559), `stage_kind` ($0520), `stages_done` / `stages_clear`;
  `scene_run` (A = object type) runs a scene (title, story); `far_call` (3E:D805).
- The status bar: `db/hud.toml` (`hud_update` once per frame from scroll_update; `hud_boss_slot` $059A names the
  object whose variable 0 is shown as the enemy's bar; `hud_card` $05A0). Interrupts, the screen split, PPU
  records, palette and fades: `db/video.toml` (`nmi`, `irq_hud`, `split_mode` $0180, `ppu_record`, `palette_load`,
  `fade_level` $01A2, `bit_mask`).
- What a room does besides blocks and objects: `db/roomtick.toml` (`room_tick`, 38:A000: the hub's door marks and
  reveal, the goal game's marks, wind streaks, the camera locks of `arena_lock`, the per-room `room_extras`).
- Hits: `db/hit.toml`. An object that can be hit calls 3F:E31D with A/X = the address of its 24-byte record
  (`hit_recs`: box, flags, hurt byte, score index, six reactions); `hit_test` (39:8000) tests the current object
  against `kirby_rect` (the rectangle of Kirby's action, kind in its first byte: 0 = inhale), against the shots in
  slots 6-8 (damage = the shot's variable 0) and against Kirby's body ($0509-$050B). An object's hit points are its
  variable 0 ($61CA + slot); a reaction sets a variable or starts a script.
- Kirby's states: `db/khelp.toml`. There is no state number: Kirby's state is the script his object (slot 1) runs.
  The scripts of banks 14-19 call a 6502 routine of their bank once per frame through `call_vector`; it ends with
  `jmp kirby_upkeep` (21:805B: hurt timer and blink, the hook, spikes, his body box, death at negative hp) or
  `ldx #n` / `jmp kirby_script_upkeep` (21:8CE8: change to script n of `kirby_script_lo/hi/bank`, 239 entries).
  The families of states: `kirby_form` ($05E0) picks the set in Kirby's start script (14:A000): the ordinary
  states are scripts $00-$1D in bank 14 (`db/kst14.toml`: `kirby_s_stand` / `kirby_st_stand` and so on; script $02
  `kirby_s_resume` picks the fitting state), $1E-$39 the same with a copy ability held; Sword $60-$7B and Parasol
  $B3-$CF in bank 15 (`db/kst15.toml`); the UFO $DA-$DD and the Star Rod $7C-$B2 in bank 17 (`db/kst17.toml`).
  Each state routine is a fixed chain of tests; the first that answers yes names the next script.
  `kirby_action` ($05E1), `kirby_ability` ($05E3, $FF none), `kirby_hurt_timer` ($05F9), `bump_kind` ($05E4), the
  pad tests (`pad_*`), pose setters, `kirby_hp_sub`.
- Kirby's speeds: `db/kvel.toml`. `kirby_speed` ($05BB) along `kirby_facing` ($61DD) becomes `kirby_vx` ($05B9); `kirby_speed_step` (A = pressed, Y = profile) and `kirby_gravity` (Y = profile) are what his states call.
- Kirby's move step: `db/kmove.toml`. `kirby_step` (21:95D3, once per frame) → `kirby_move`: velocity, the limits
  `kirby_min_x` / `kirby_max_x` / `kirby_min_y`, the camera that follows him; `cam_locked` ($05FA) for rooms that
  scroll by themselves; `kirby_vy` ($05BD) is his own copy of the Y velocity.
- Where things happen in `main`: `../tas/traces/main/rooms.csv` (frame, world, stage, room, hp, lives, ability
  at every room change). 1-1 starts at frame 452, the first boss (Whispy Woods) at 10,401, World 2 at 11,531,
  the last fights from 133,557. `kd when` on your routine is quicker than guessing.
- To see a moment: `./kd look main@4012`, then Read the PNG.

## Rules

- A name states what the evidence shows. No evidence, no name.
- Do not describe how you found something; describe what it is.
- Do not weaken a failing claim; do not write a claim that cannot fail.
- A claim's `text` says exactly what its expression checks, no more. What you believe but did not check goes
  under "Open".
- Keep to your unit. If you need a neighbour's routine named, describe your own and mention the neighbour by
  address.
- Zero-page bytes are reused: before you name one, `kd xref` it. If unrelated routines write it, it is scratch
  for your routine, not a variable.
- The corpus grows while you work. An `xref` claim that passed can fail after someone adds a movie: that is the
  gate doing its job, and the new reader or writer belongs in your description.
- One `kd` at a time per shell call; `kd check` waits when another agent is rebuilding.
