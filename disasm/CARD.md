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
./kd when AT|NAME                    which corpus movies run it, how often, first frame
./kd io AT|NAME --on WINDOW [--calls 200] [--rows 12] [--addrs 40]
./kd trace AT|NAME --on WINDOW [--call K] [--max 400]
./kd watch 07AD 07AE --on attract@560+600   values of RAM addresses over a window, one line per change
./kd look movie@frame                picture -> out/view/<movie>-<frame>.png (Read it)
./kd try --on movie@frame --frames N [--poke ADDR=V ...] [--hold] [--patch BB:AAAA=V ...] [--input "R*30 A"]
./kd vm                              the script opcode table: layout, flow, where and how often each opcode ran
./kd script AT|NAME [--len N]        a script (bytecode) listing with run counts; `kd next --kind script` queues them
./kd sprites [--toml]                pose tables and sprite groups that are not in the database yet
./kd packed [--toml]                 packed streams (what `unpack` expands) that are not in the database yet
./kd corpus list | add FILE --id ID --note TEXT
./kd check --unit U [-v] [--no-build]
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

## Claim kinds (every expression is Python)

| kind | fields | names you can use |
|---|---|---|
| `call` | `fn`, `on` (list of windows), `expect`, optional `where` (use only the calls for which it is true), `min_calls` (default 5), `max_calls`, `model` (Python source: helper functions) | per call: `a x y p s` at entry, `ra rx ry rp rs` at return, `rd[addr]` first value read from an address the call had not written, `wr[addr]` last value written, `mem(addr)` value at return, `reads`, `writes`, `romrd` (PRG offset → byte), `calls` (routine names called, in order), `n` instructions, `frame` |
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
- A held poke (`hold = true`) of a byte the game recomputes every frame changes nothing; poke what it is
  computed from.

What makes a claim worth having:

- **A model beats a property.** `expect = "(rx << 8 | ra) == a * x"` says everything about `mul8`; "A changes"
  says nothing. For a routine with a computable result, write the computation in `model` and compare.
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
