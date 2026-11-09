# Recipe v1: autonomous TAS discovery with an LLM driver

Distilled on 2026-11-09 from `runs/main`: Claude Opus 5.5 drove a deterministic NES emulator through Kirby's
Adventure (USA Rev A, FCEUmm) from power-on to the ending. Every number below is a measurement from that run
(its own recipe is `runs/main/recipe.md`, its splits are in `harness.json`). Sections are in the order a new run
should apply them. Kirby-specific facts are marked **[Kirby]**; the rest should carry over to other games.

## 0. What the run achieved, honestly

| part | frames | cost | frames/$ |
|---|---|---|---|
| Worlds 1-4 and the first half of 5: the reference TAS 3226M replayed verbatim (it syncs on this core up to f78090) | 78,090 | ~$0.20 | ~400,000 |
| The agent's own play from 5-6 to the ending (Heavy Mole, all of World 6 and 7, Meta Knight, Dedede, Nightmare) | 59,622 | ~$65.5 | ~910 |
| ...of which routine stages in a fresh episode (6-1, 6-5, 7-3, 7-5) | 2.4-3.6k each | $0.75-1.0 each | 2,400-3,600 |
| ...of which bosses and diagnosis (Meta Knights gauntlet, Orb, Nightmare Wizard) | 0.4-2k each | $0.3-3.5 each | 300-1,000 |
| Idle after the game was complete (no stop tool; fixed in the harness) | 0 | ~$22 | 0 |
| **Validation, w12-opus**: a fresh Opus agent with this recipe and no reference inputs, power-on to the W3 hub; task check passed | 51,207 | $23.84 | ~2,150 |
| **Validation, w12-sonnet**: the same task driven by Sonnet 5.5; task check passed | 69,751 | $14.44 | ~4,840 |
| **Sequence task, w2-seq** (§6): from a library prefix at the W2 hub, enter 2-1, copy Tornado, clear 2-1, hub holding it, enter 2-2, no life lost; one episode, task check passed | 4,347 | $1.50 | ~3,100 |

The final movie (137,712 frames, 38.2 min) replays from power-on and matches its savestate. Over the span the
agent played itself, it is **30% slower than the human-made reference TAS** for the same span (59,622 vs 45,847
frames from f78090 to the end): a first-pass search TAS, not a polished one. Its own world 1, played before
any of this recipe existed, was 1-1..1-3 in 13,305 frames. That cost $6.4 on FCEUmm plus $4 for an earlier
Mesen attempt at 1-1, about 1,280 f/$ in all. It was 5,459 frames (70%) behind the reference at the same hub.

**Driver models, same task (power-on to the W3 hub, recipe v1, no reference), measured 2026-11-09:**

| | Opus 5.5 | Sonnet 5.5 |
|---|---|---|
| trace length | 51,207 f (1.85x the reference's 27,650) | 69,751 f (2.5x the reference) |
| cost | $23.84 | $14.44 |
| frames per dollar | ~2,150 | ~4,840 |
| turns / episodes | 606 / 20 | 837 / 22 |
| wall time | ~8 h | ~8.8 h |
| mean $/turn | ~$0.039 | ~$0.017 |

- **Sonnet is the cheaper way to get a complete trace.** Opus produces a 26% shorter one.
- **Both needed steering at one fight each.** Sonnet read the boss HP bar off screenshots; Opus spent its
  first episodes building lab tools.
- **Mixed strategy:** produce traces with Sonnet, then spend Opus on the segments worth optimising.

## 1. Before playing anything

1. **Test every existing movie against your core first.** Replay it in the lab from power-on and log
   (frame, room, hp, lives) on every change. The desync point is the first room that lasts implausibly long,
   where lives drop or x freezes. A verified prefix costs ~$0.2 for 78k frames; redoing it by hand cost $8-15
   and came out 6,000 frames slower. After the desync, repair with one door search; re-attaching the
   reference at ~100 later offsets never re-synced (RNG and positions had diverged).
2. **Read every knowledge-base file's header paragraph completely.** The agent skipped the line saying the
   reference syncs and lost four episodes.
3. **Find the RAM once, verify, and name it.** Position, velocity, room/stage/world, transition code, HP,
   lives, ability, boss HP. **[Kirby]** seeded vars are verified. Extra facts:
   - `trans` goes 0→1 at a door, 0→4 on a hub return, 0→5 on a stage clear.
   - `hp` reads 255 while dying, so death-safe guards are `hp > 47 or hp < N`.
   - The goal-game room is 42. The W1 hub is world 0 room 0; the W2 hub is world 1 room 1.
   - Boss / mid-boss HP lives in the `$61CA+slot` table. Find it by **mark → one confirmed hit → diff**:
     the HP byte drops by the attack's damage (a spat star does -10). The table also holds projectile values,
     and in w12-sonnet a neighbouring entry held the HUD bar in ticks: Mr. Frosty's HP was `$61D5`, while
     `$61DB` (5) was the bar, and a search on the bar byte failed. "The entry equal to the known HP" only
     works at the very start of a fight. The HUD bar lags RAM by ~20 frames.
   - Measured on Mr. Frosty in 2-4: screenshot bar-reading plus manual hits cost ~$2.9 without a kill. After
     the HP byte was found, one random-search call (113 frames, 96 s) killed him for about $0.85 in turns.
   - Collision map: W/H at `$67EE/$67EF`, tiles at `$68C8+screen*192`, attributes at `$7F00`.
     **Solid attribute values differ per tileset**: print a legend per room (labkit `roominfo`) and decide
     solids from it.
4. **Build (or load) the room helpers before the first hard room**: a collision-map dump with door
   coordinates, and a press-frame scanner for cutscenes and the goal game. Both are in `labkit/`.

## 2. The per-room routine (traversal): about 3 turns per room

1. `play .*45`, checkpoint, `roominfo`: one turn. Wait at least 45 frames after a room change: the
   collision-map buffer lags the room var, and a map read too early is the previous room's. In w12-opus a
   stale map aimed both searches at a door behind a camera lock, wasting 720 frames.
2. One search to the door: one turn.
   - **Open, horizontal or slope rooms: the built-in beam.** Beam 256-512, 8-frame actions. Alphabet:
     `R*8` `UR*8` `DR*8` `U*8` `D*8` `L*8` `U*5 .*3` (door) `B*2 .*16 U*6` (door while puffed: a floating
     Kirby can't enter a door until it exhales) `. B*12 .*2` (shot); one action per code span. Settings:
     - score `-2*abs(x-door_x) - abs(y-door_y)`
     - goal: room changed and not the entry room
     - avoid `hp > 47 or hp < N or room == <entry room>`

     - Depth must cover the room: about `room_width_px / 12` 8-frame actions, since normal Kirby makes
       ~1.5 px/frame. Three of three ~1,000 px rooms in 2-1 failed at depth 70. Alternatively, chain a
       score-only partial and then a short goal search.
     - Add `RA*8` (it climbs steps while floating) and `B .*3` (it deflates Kirby after a fight or ambush).

     Yield: 200-600 frames per call in 40-120 s.
   - **Vertical, maze or blocked rooms, and anything at 1 HP bar: the distance-field beam** (labkit `flow2`).
     Pass the tileset's solids and shot macros.
     - Measured results:
       - 6-4 room 87: 1,184 frames in one call after three built-in calls had stalled.
       - w12-opus 2-5: 3 of 3 long rooms first try at 1 HP bar, where the built-in beam stalled behind
         enemies.
     - It floats (~1 px/frame against the beam's ~1.7 in open rooms) and a call takes 6-10 minutes of wall
       time.
   - **Water rooms:** flow2 stalled; beams through hand-placed waypoints worked (w12-sonnet).
   - **Breakable and bomb blocks** (normal Kirby can also break them by inhaling): random-mode search with the
     goal "this tile byte changed",
     `ram[0x68C8 + idx] != v`, with attack macros including the slide `D*4 A*4`. This found the 2-2 bomb
     blocks in 11-37 s, after six turns of manual tests.
   - **Warp Stars are objects, not doors.** `roominfo` doesn't list them: read their position from the object
     slots and target that. Riding one isn't a room change for ~300 frames, so use the goal `trans != 0` or
     `play .*N` after contact.
3. `play` the result with `view: none` once the routine is trusted, then go on to the next room.

Measured on 6-5 (4 rooms, 12 turns): 2,707 frames for $0.75, about 3,600 f/$.

**Score design: each of these mistakes cost 1-3 stalled two-minute searches.**
- A piecewise score must be continuous and monotone along the path, with each phase's base above the
  previous phase's maximum. A zigzag shaft works with `band*1000 + progress_within_band`.
- A pure `x` score takes whichever branch goes furthest right (it took a wrong corridor in 1-2 room 50).
  Constrain y, or use the distance field.
- In hilly rooms, the y term of `-2|dx| - |dy|` crowds the floating branches out of the beam (4 stalls in
  2-1, w2-seq). Score `x`, plus a pit penalty, until near the door, then add y. Chained score-only partials
  worked.
- Always give a goal. Score-only results end in a long held input once progress saturates.
- If the best x stops moving, Kirby may be physically pinned. Look at a `strip` before searching again; in
  6-3 and 7-3 a two-call manual nudge fixed it.
- **[Kirby]** Door entry depends on Kirby's state:
  - The UFO needs Up held ~5 frames, and `U .*2` never triggers it. When a door search fails at the right
    coordinates, read how long Up is held in a known-good door entry.
  - Rooms with the entry door at Kirby's feet: any U action re-enters it, so put `room == <prev>` in avoid
    as well as excluding it from the goal.
  - Door coordinates from a screenshot: `door_world = kirby_world + (door_screen - kirby_screen)`.
    The first guess was ~60 px off; this formula was right.
- Rooms with two doors: read the walkthrough's room order first. A door search enters whichever door you
  name.
- **[Kirby] Hubs:**
  - `roominfo` lists minigame, arena and warp-star tiles as doors. Confirm a door by its number in a
    screenshot, and check `stage` right after entering. In w12-opus, Crane Fever cost 2,650 frames and $0.7,
    and the Arena star door cost 330 frames.
  - A stage clear that unlocks something plays a ~240-frame cutscene that ignores input and extends the hub
    map. Wait it out, then run `roominfo` again. Without an unlock, input is accepted right after the fade.
  - HP does not refill on entering a hub or a stage.
- **Stage clears count only by RAM** (goal-game room, then `trans` 0→4), never by a screenshot. A wrong
  last door in 7-6 produced a fake "hub", which cost ~$1 and two episodes.

## 3. Fights

- **Normal Kirby (no UFO): one hit per random-search call.**
  - How: inhale an enemy or a projectile and spit the star (10 damage). Depth 25-40, goal `bhp < <current>`
    (the boss's HP var), avoid `hp > 47 or hp < N`.
  - In w12-opus this worked on every fight:
    - Poppy Bros Sr., Mr. Frosty, Mr. Tick-Tock and Grand Wheelie: 3 calls each;
    - Whispy Woods: 6 of 6 calls at 52-259 frames each;
    - Paint Roller: 8 hits;
    - the 2-3 Meta-Knights: one bar step per call, 11 calls of 62-244 frames.
  - If two calls fail, look at a `strip`. Knights on platforms that are solid from below need a short
    reposition beam first.
  - A death resets the boss HP var to 0, so the last goal must be `bhp == 0 and hp < 48`.
  - **After a boss dies the stage does not end by waiting.** Kirby must collect the Star Rod piece or the
    item: float above it and press Down. `trans` goes 0→5 about 400 frames later, and the hub follows about
    400 frames after that. w12-sonnet waited 2,000+ frames at Paint Roller, about $1. Find the piece with
    `ram` action `objects`.
  - Protect HP before ambush rooms (2-3's Meta-Knights at one HP bar were slow in both runs); pick up the
    Maxim Tomato when it's on the way.
  - Mid-boss arenas lock the camera until the boss dies.
  - At one HP bar, a state where the next hit can't be survived needs a survival rollout in the lab first.
- **Mid-boss template with the UFO** (worked first try on four mid-bosses in 7-2, 109-131 frames each, one
  call of ~60 s):
  - random-mode search, samples 4000, depth 12
  - actions `B*68 .*2` `B*36 .*2` `. B*12 .*2` `R*8` `L*8` `U*8` `D*8` `.*8` `R B*67 .*2` `R B*11 .*2`
  - goal `<boss hp var> == 0`

  Then a door search (93-117 frames).
- **Several moving enemies** (the 6-6 Meta Knights gauntlet):
  - Use **random mode, one kill per call**: 65-103 frames per kill, 10-80 s per call.
  - Beam with score `-bar` stalled after 2 kills (3 calls of 100-230 s each); a shaped score reached 5 kills,
    then also stalled.
  - Beam dedupes onto a cluster near the last kill; random sampling keeps whole plans diverse.
  - Switch after the first stall.
- **Bosses with phases** (Nightmare Orb, then Nightmare Wizard):
  - First log long enough in the lab to see every phase. The Wizard's HP fills 1,330 frames into the room,
    and 1,600-frame lab runs had missed it, which cost ~6 episodes.
  - Checkpoint the frame the fight really starts.
  - A hand-written greedy controller in the lab can beat search on a grind. Orb: hold an x target and mash B,
    with a 24-frame savestate shield that vetoes any HP loss. A 6-run sweep of the x target took the Orb from
    3,312 to 1,952 frames in 2 minutes.
- Re-seeding a random search on a hit it already found gains ~0 frames (the Wizard's hit 5: 554 vs 555).
  Spend optimisation on structure instead: alphabet, strategy, route.

## 4. Which controller, measured (same checkpoints: 7-3 rooms 145 and 144, 7-4 room 148)

Search wins.

| controller | room 145 | room 144 | room 148 | cost |
|---|---|---|---|---|
| built-in beam search | 561 | 715 | 555 | 2-4 turns |
| tiny random-forest clone of search (650 samples, flow hint; trains in 2 s) | 624 | 672 | died | $0 |
| Jev with RAM features + flow hint | died | timeout | died | $0.003 |
| shield + RF clone | timeout | 672 | 784 | $0 |
| shield + Jev | 1448 | timeout | 880 | $0.03 |

- **Agreement with search labels, offline (160 states):**
  - Jev with RAM features only: 0.56. Jev given a distance-field "hint" feature: 0.73.
  - The hint alone: 0.74. Always pressing right: 0.51.
- **Verdict:**
  - Reactive policies die without lookahead, and even shielded they are 1.2-2.6x slower than search.
  - Jev adds nothing beyond the best feature you feed it, and its vision cannot read the game screen (it
    called the title screen "gameplay").
  - The tiny clone beats Jev at zero cost, but not search.
  - Controllers pay only as hand-written greedy controllers for grinds, or as rollout priors inside search.
- **Where the LLM is worth its cost:** route decisions, objective design (goal/score/avoid), diagnosis when
  a search stalls, and reading the map. Not frame-by-frame control.

## 5. Cost control: the harness lessons

- **A turn's cost grows with context.** Mean cost per turn:

  | context | 20-40K | 40-60K | 60-80K | 80-100K |
  |---|---|---|---|---|
  | cost per turn | $0.04 | $0.05 | $0.09 | $0.17 |

  Past the tool-result clearing trigger, every clear rewrites the prompt cache. The same routine cost $0.95
  for 7-3 in a fresh episode and $5.9 for 7-2 at the end of a long one. **Milestone at every stage clear, so
  that each stage starts a fresh, small episode.**
- **Notes are state, not a diary.** The notebook grew to 73 KB of per-episode logs, so each new episode
  started at 67K tokens (~$0.33 just to begin). With an early handoff threshold, every episode was then
  asked to hand off immediately (episodes 46-62: 3 turns each). Keep `notes` as a rewritten current-state
  document under ~16 KB and put history in `journal`.
- **Stop when done.** After the game was complete, the run burned ~$22 in 62 empty episodes because nothing
  could end it. Use `finish`. The harness also stops after 3 episodes in a row with no work done.
- **Lab work is free in dollars but not in wall time.** Prefer one long lab script (scan, sweep, train)
  over many turns of `play`. Read `strip` views instead of 10-frame plays.
- **Give each episode room to finish one diagnosis-then-act loop.** Two-to-three-turn episodes ending in
  "NEXT: …" made the endgame crawl (19 episodes for 2 bosses).

## 6. Goal-directed traces ("get to level X", "do A then B")

A task is a header of ordered RAM predicates plus free text (`tasks/*.md`, checked by `task.py`):

```
---
name: w1-from-scratch
start: power-on              # or <run>:<checkpoint>: begin from that verified movie prefix
reference: forbidden         # hide reference movies and their splits from the agent
steps:                       # must become true in this order on a replay from power-on
  - 1-1 entered: world == 0 and room == 43
  - Whispy arena: world == 0 and stage == 7 and room == 8
  - World 2 hub: world == 1 and room == 1
forbid:                      # optional: must never hold on any frame (e.g. no deaths)
  - lost a life: lives < 4
---
```

How to produce one:
1. **Write the goal in RAM terms first.** Express every requirement as a predicate over verified vars:
   - room ids, from the reference splits or your own logs;
   - world/stage, `trans` codes, ability ids, HP or lives floors.

   Prose goals ("beat the boss") get milestoned wrongly; predicates don't.
2. **Start from the longest verified prefix in the trace library** when the task allows it:
   - movies already verified on this core: `runs/*/movie.txt` and their `ms-*` checkpoints, plus reference
     movies up to their desync point.
   - "reach any room the library has" is then a truncation, costing $0. Example: anything up to 5-6 is
     already a prefix of `runs/main`.
   - The agent works only on the missing steps.
3. **Plan the route per step** from the walkthrough (rooms, doors, abilities needed). Then run the per-room
   routine (§2) and the fight templates (§3). `milestone` at every stage clear.
4. **Guard every later step's constraint in search.** After a required pickup, put the loss condition in
   every search's `avoid`, e.g. `ability != 18` after Tornado was copied. Find the pickup itself with a
   goal search: `ability == 18` with B/D actions took 181 frames and 12 s. (Measured in w2-seq.)
5. **Order and constraints are checked, not trusted.** `finish` replays from power-on and checks the steps
   in order plus the `forbid` invariants. It ends the run only when they pass; otherwise it returns the first
   failing step.
6. **Budget.** Estimate at the start from §0's rates, and write the actual cost per segment into the report:
   - ~$0.25-0.35 per routine room;
   - ~$0.5-1 per mid-boss;
   - $1-4 per boss, more if it has phases you haven't logged.

## 7. Harness wishes: status

| wish | status |
|---|---|
| a stop/finish tool, stop on idle episodes | done (`finish`; 3 idle episodes stop the run) |
| notes kept small; handoff relative to the episode's start size | done (journal doc, 16 KB notes guard) |
| goal predicates for milestones and tasks | done (`task.py`, `finish`) |
| distance-field search for maze rooms | in the lab (`labkit/flow2.py`), not yet built into `search` |
| object-slot viewer (per-frame class/x/y/hp table for all 18 slots) | done for the current frame (`ram` action `objects`); over a frame range: open |
| RAM addresses parse as hex everywhere (`61CA` used to be read as decimal) | done |
| `rollout(policy, shield)` primitive; search seeded by a policy prior | open |
| a `play` limit above 3,600 frames, or "replay file a..b" | open (the lab plus `inputs_file` covers it) |
| `roominfo` lists Warp Star objects and marks minigame/arena doors | open (w12-opus) |
| the distance-field search built into `search` (saves 6-10 min of lab wall time per call) | open (w12-opus) |
| `apply` trims a found result to the goal frame (it appends the rest of the last action, e.g. `R*27`) | open (w12-opus) |
| lab scripts can import helpers saved in the lab dir; spawn pools need `if __name__ == "__main__":` | done (lab dir on `PYTHONPATH`); the guard is the script's job |

## 8. Open optimisation leads (not done)

- **Hub waits:** input seems to be accepted from ~205-210 frames after arriving in a hub, not 240. That
  would save ~30 frames per stage start (~400 frames per game). Unverified: scan k from 200 to 240 with the
  real door inputs before using it.
- Bonkers in 6-3 took 453 frames, against ~110 with the mid-boss template.
- Orb: lead the shots, or seed a beam search with the greedy controller.
