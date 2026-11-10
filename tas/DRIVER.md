# Driver card: producing a verified trace with `kt`

For a coding agent (a Claude Code session or subagent) that has a shell. You turn a task (ordered state
predicates) into an input movie that passes the task check on a replay from power-on. Everything runs locally and
is free; your own turns are the only cost, so work in big strides: one search or one script per sub-goal.

## The loop

1. **Read the task file and the knowledge it points to.** The steps are expressions over named state variables;
   `forbid` lines must never hold. Decide what each step means in state terms before touching the controls.
2. **Create your run:** `kt new <run> --from <start>` (the task's `start:` value; `--force` replaces a run you
   want to start over). Never write into another run.
3. **For each step, search instead of steering.** State the sub-goal as an expression and let the machine find
   inputs: `kt search <run> --goal "<expr>" --avoid "<expr>" --apply`. Chain room-to-room travel with
   `kt go <run> --until "<expr>"` (each step goes to *any* room not seen yet: when you need one particular door,
   use `search` with that room in the goal and the wrong rooms in `--avoid`). Play inputs by hand only to probe a
   mechanic or to wait.
4. **When a search fails, find out why before searching again:** look (`kt look`, `kt play ... --view strip`),
   list objects (`kt ram <run> objects`), print the map (`kt room <run>`), then change the goal, the cell, the
   alphabet or the start point. Never run the same search twice.
5. **Checkpoint before anything you might redo** (`kt ck <run> save NAME`); `kt ck <run> load NAME` goes back.
6. **Finish:** `kt check <run> <task.md>` must print PASS, and `kt verify <run>` must print MATCH. Then look at a
   strip of the key moment (`kt strip <run> --from F --to F`, which changes nothing) and confirm with your own
   eyes that the screen shows what the task is about.

**One command at a time per run.** A run is locked while a command works on it. A search can take up to its
`--time-limit` plus `--refine` (defaults 75 s + 8 s, `go` that much per room): give your shell call a timeout
above that (300 s is safe) so it is not cut off or moved to the background. If you see "run is busy", a previous
command is still working: wait for it. Searches are not reproducible (they are bounded by wall time), so apply
or `--save` the result you got instead of running the same search again.

## Commands

```
kt new R --from power-on | <run>:<checkpoint> | <run>@<frame>
kt play R "<spec>" [--view end|strip|none] [--every N]     # spec: R*40 RA*8 .*30 (B .)x8 ; . = no buttons
kt look R [--scale 3] [--crop x0,y0,x1,y1]                 # pictures are written to runs/R/view/*.png: Read them
kt strip R --from F --to F [--every N]                     # contact sheet of the movie as it is (read-only)
kt rewind R --to FRAME | --frames N                        # truncates the movie: checkpoint first
kt ck R save NAME [note] | load NAME | list
kt ram R status | objects | list | mark | diff | read ADDR [N]
kt ram R define NAME --addr 05E3 [--size 2] [--signed] | --expr "ram[0xDE]*256 + ram[0xDD]" [--event]
kt room R                                                  # collision map, doors, live objects
kt search R --goal EXPR [--avoid EXPR] [--cell TUPLE] [--actions SPEC ...] [--time-limit S] [--refine S] [--apply]
kt go R --until EXPR [--var room] [--avoid EXPR] [--actions SPEC ...]
kt simplify R --from F --task TASK.md --mode smooth|frames # tighten or smooth the finished tail, task-checked
kt lint TASK.md --on RUN ...                               # where does each predicate hold on existing movies?
kt check R TASK.md        kt verify R        kt render R out.mp4 --from F --to F
```

Expressions use the named variables (`kt ram R list`), `ram[addr]`, `frame`, arithmetic, comparisons,
`and/or/not`, `in (a, b)`, `min max abs s8 s16`.

Python does the same in bigger strides (one process, several steps):

```python
import sys; sys.path.insert(0, "/opt/src/kirbys-adventure/tas")
import drive
r = drive.Run("myrun")
r.play("R*40"); print(r.status_line(), r.objects())
res = r.explore("room == 46", avoid="hp != 47", time_limit=90); r.apply(res)     # res["found"], res["frames"]
print(r.ev("x >= 1000 and room == 47"))                                           # any expression
r.close()
```

## Search: how to think

`--mode explore` (the default) needs no score. It keeps one state per **cell** and expands rarely-visited cells
with random macro-actions until the **goal** holds, then spends `--refine` seconds shortening the path.

- **Goal:** the predicate of the task step, or a stepping stone toward it. "Some place I have not been" is a valid
  goal: `room not in (43, 44, 45)` found an unmarked door with no coordinates.
- **Cell:** a tuple expression saying what counts as a different situation. The default is
  `(room, x//16, y//16)`. **Put the mechanic's state into the cell.** If the task depends on an object being
  present or in view, a counter, an ability or a camera position, define a variable for it (`kt ram R define`)
  and add it to the tuple, so the search treats "same place, different mechanic state" as new ground and keeps
  exploring it. Finer position (`x//8`) when a few pixels matter. When position does not change at all
  (cutscenes, minigames, timing presses), put time in the cell: `(room, frame//20)`.
- **Avoid:** every constraint that must survive: `hp != 47` (no damage), `ability != 23` (keep the ability),
  `room != 47` (do not leave). A pruned branch costs nothing; a broken constraint costs a redo.
- **Actions:** macro-actions of ~8 frames. Without `--actions` you get the walking set `R*8  . R*7  R . R*6  L*8
  L . L*6  RA*8  LA*8  UR*8  UL*8  U*8  D*8  DR*8  U*5 .*3  B*2 .*16 U*6  . B*12 .*2  .*8` (no long B hold, so
  no inhaling). Add what the sub-goal needs: holds for an attack (`B*24`), a door
  press (`U*5 .*3`), waits (`.*8`), 1-2 frame steps (`L*2`, `R`) when timing or position must be exact.
- A search keeps nothing unless you pass `--apply` (play the result) or `--save FILE` (then `kt play R --file
  FILE`).
- A search that returns `found: false` lists its newest cells: that is how far it got. Split the goal at that
  point, or add the missing action. One cell only means your actions do not move anything: wrong alphabet.
- **Things that take time after contact** (a ride, a pickup animation, a door that opens): make the goal the
  contact itself (`abs(x - 904) <= 10 and ...`), then wait with `kt play R ".*120"` and read the events.

`--mode beam --score EXPR` (the old tool) is for squeezing frames out of a segment once a route is known.

## Finding state

- **Variables:** `kt ram R mark`, do the thing, `kt ram R diff`. Name what you find (`define`), with `--event`
  for things whose changes you want reported by `play`.
- Trust state, not pictures, for progress; trust pictures, not state, for "does this look like the thing".
- Validate a predicate on a situation where you know its answer before you rely on it.

## Kirby's Adventure facts (this workbench)

- Seeded variables: `x y vx vy hp lives world room trans ability`, and for inhaling `inh` (objects inhaled),
  `mouth` (255 = empty) and `inab` (ability enemies inhaled; 2 or more starts the mix roulette) (+ `stage`, which stays 0 inside world 1's
  stages: do not use it to tell stages apart; use `room`). Full HP is 47, a hit costs 8, `hp` reads 255 while
  dying. `ability` 255 = none, 23 = UFO. `trans` goes 0→1 at a door.
- Objects: 18 slots. A slot is live when its script id `ram[0x6128+slot] < 0x80`. X = `ram[0x6086+s]*256 +
  ram[0x6074+s]`, Y = `ram[0x60AA+s]*256 + ram[0x6098+s]`. Slot 1 is Kirby, enemies and stage objects use 9-17.
  `kt ram R objects` lists them with their script id (the object's type).
  Script ids seen so far: 5 pickup (a 1-Up, a knocked-out ability star), 6 Warp Star, 40 the UFO enemy,
  56 Bronto Burt, 57 Gordo, 65 Shotzo. Short-lived effects also use slots 3-8. A consumed object's x/y keep
  their last values: test liveness on the script id.
- `kt room` lists every door tile of the room, including doors that are not drawn (the collision map marks
  them). For a hidden door, try the listed doors you cannot see in the picture. When a room-goal search stalls,
  search to a door's pixel position (`abs(x - DX) <= 6 and abs(y - DY) <= 8`), then press Up yourself.
- Camera X = `ram[0xDE]*256 + ram[0xDD]` (screen is 256 px wide); scroll limits are 16-bit values at `$05C0`
  (min cam X), `$05C2` (max cam X), `$05C8` (min Kirby X), `$05CA` (max Kirby X).
- Controls: A jump, Up puff up and fly (A flaps), B inhale / spit / exhale, Down swallow (copies the ability),
  Up at a door enters it (not while puffed: exhale with B first). Double-tap a direction to run.
- UFO Kirby: D-pad flies in 8 directions, B shoots, doors need Up held ~6 frames (some need a diagonal: include
  `UL*4`, `UR*4` and a fine cell like `x//4` when a door search fails at the door).
- The goal game (room 42) and the return to the hub play out on their own; a search there needs a time cell.
- A Warp Star carries Kirby only after he has stood on it for ~20 frames, and the ride lasts ~100 more.
- After a room change wait ~45 frames before reading the map.
- The knowledge base is `knowledge/*.md` (walkthrough, mechanics, RAM map, secrets). Do not read
  `knowledge/movies/`, `knowledge/reference-*`, `traces/` or other runs' movies: the trace must be your own.
