# The workbench

- Emulator: FCEUmm libretro core (FCEUX lineage, ~2,000 frames/s per process; search runs 16 of them), NTSC,
  60.0988 fps, headless and fully deterministic. The movie always starts
  at power-on with a blank battery save. Everything you do is replayable; `movie.txt` is the result.
- `play` appends inputs and runs them; `rewind` and `checkpoint load` go back (the movie is truncated or
  replaced — nothing else changes). Checkpoints are cheap: save one at the start of every segment you might
  want to redo, and before anything risky.
- Input spec: tokens `<buttons>*<frames>` separated by spaces; buttons are letters from `A B U D L R T S`
  (T = Start, S = Select) or `.` for no buttons; `(… )xN` repeats a group. Examples: `R*40` (hold right 40
  frames), `RA*6 R*10` (jump right then keep running), `(B .)x8` (mash B), `.*60` (wait one second),
  `T .*20 T` (Start, wait, Start). Newly pressed buttons need a frame without them in between (`A A` is one
  long press; `A . A` is two presses).
- Pictures: `play` view `end` (default) shows the last frame at 2x; `strip` shows up to 16 frames in a grid
  labelled with frame numbers — use it to see motion through a long input. `look` re-shows the screen, with
  optional zoom/crop. NES screen is 256x240.
- RAM: `ram` reads/finds/names addresses. Named vars appear in every status line; flag key ones (room, stage,
  game mode, HP, lives, ability) with event=true so `play` reports when they change. Find addresses with
  mark → play → diff. Pre-seeded and verified by the owner's setup: x, y (world px), vx, vy (1/256 px per
  frame; vy < 0 = rising), hp (47 = full, -8 per hit), lives, world, stage, room, trans, ability. Objects live in
  WRAM tables of 18 slots (Kirby = slot 1; enemies/bosses in other slots: class at $6200+slot, X at
  $6074/$6086+slot, Y at $6098/$60AA+slot) — see the RAM map in the knowledge base; verify the rest yourself.
- `search` is a free, parallel beam search over macro-actions with your RAM expressions as goal/score/avoid.
  It is how a TAS gets frame-tight: once you know what a segment must achieve ("room changes", "boss HP 0",
  "x reaches 1800 without taking damage"), let search find the fastest inputs. Keep the action alphabet small
  and meaningful (e.g. `R*4`, `RA*4`, `RB*4`, `.*4`, `L*4`) and the goal precise; read its result and apply it.
  Score-only results are trimmed to the first frame where the best score was reached (`trimmed_frames`).
- `jev`: TypeSafe's Jev (on OpenRouter) picks among options you define, each decision ~0.4 s and ~$0.00002, from
  the status line and (optionally) the screen. Its vision is weak and it has no memory beyond your
  instructions and its last few choices. Good for cheap reflexive play over long stretches; bad at precision.
- `knowledge` holds the walkthrough, speedrun/TAS notes, mechanics and RAM map (some is inlined below).
- `notes` holds your persistent documents. Episodes end (milestones, handoffs, context limits); the next episode
  starts from your notes, recipe, splits and checkpoints only. doc='notes' is the **current state**, shown in
  full at every episode start: verified RAM, route and door coordinates, which checkpoint is what, open problems,
  the next step. Rewrite it (action=write) rather than appending diaries; keep it under ~16 KB. Episode history
  goes to doc='journal' (append-only, not shown at episode start; read it when you need it).
- `finish` ends the whole run (task done, or nothing useful left to do). Idle episodes cost money: if the work
  is done, call finish instead of handing off.

# The python lab

`python` runs your script in a sandbox here: no network, no access outside the run, but full emulator access
through `lab` (cores at any checkpoint, ~2,000 frames/s per core with ~16 cores, RAM vars, savestates) plus
numpy, torch (CPU) and scikit-learn. Your cwd persists across calls: keep scripts, datasets and models there, and note
in your notebook what is where. Results come back via `lab.save_spec(name, masks)` → `play` with
`inputs_file=name`. Long jobs: `background=true`, then `jobs`. Print summaries, not big dumps.

`labkit/` (read-only, importable: `import roominfo, flowsearch, flow2, goalscan`) holds the previous run's
proven helpers: `roominfo.info(c)` prints the room's collision map with a legend of every attribute value and
the door pixel coordinates; `flow2.flow(ck, (door_x, door_y), actions, solids=…, goal=…, avoid=…)` is a
parallel beam search scored by a distance field from the door over the collision map, recomputed when blocks
break (it carried maze rooms the built-in search could not); `runflow2.py` is its command-line wrapper;
`goalscan.scan(ck, room)` finds the best press frame for the goal game / a cutscene. Read their source first
(`print(open(roominfo.__file__).read())`); they assume Kirby's object slot 1 and the seeded var names.
