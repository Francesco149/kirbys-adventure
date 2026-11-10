# Playbook v2: an agent drives a deterministic game to a stated behaviour

The method for having an agent author a **verified input trace** autonomously: a speedrun segment, a test trace
that exercises one behaviour, or a demo clip. It was distilled from the Kirby's Adventure work in this repo
(`RECIPE.md` v1.2 is the per-game recipe from the first session; this file is the game-independent method that
replaced its core loop on 2026-11-10) and then applied to a non-emulator target. Every number is a measurement;
`V2-LEDGER.md` has the raw rows.

## 1. The idea in five lines

1. **A trace is a list of inputs from a fixed start.** Determinism makes it a program: replay it and you get the
   same state, so it can be verified, extended, cut and searched.
2. **A goal is an ordered list of state predicates** plus things that must never happen. Prose goals are
   translated into predicates before anything is played.
3. **The model never steers.** It names state, writes predicates and designs the search (what counts as a new
   situation, which inputs exist, what must not break). A local search finds the inputs.
4. **The search needs no score.** It explores toward situations it has not seen until the predicate holds.
   Scores, distance fields and beams are a later, optional speed pass.
5. **Done means checked:** the predicates hold in order on a replay in a fresh process, the replay matches, and
   someone (the driver, or a cheap vision model) looked at the frames the trace is about.

## 2. What the target must provide

| level | the target can… | what you get |
|---|---|---|
| L0 replay | run an input file from a fixed start, deterministically; report a state hash; dump state and a picture at chosen frames | verified traces, parameter sweeps, the whole loop below at seconds per probe |
| L1 step | be stepped frame by frame in-process with state readable every frame | per-frame predicates, events, `mark → act → diff` in one call |
| L2 snapshot | save and restore state in memory (emulator savestate, process fork, a serialisable game state) | search at 10^4-10^5 frames/s: exploration, beams, simplification |

- Kirby on FCEUmm is L2: ~2,000 frames/s per core, 14 KB savestates, 16 workers.
- Fortune Summoners under `rhost` (OpenSummoners) is L0: a replay from boot per probe, ~200 frames/s under
  wine, batches of parallel replays. See §8 for what that changes.
- Determinism is checked first, not assumed: the same trace twice must give the same hash, in two processes.
- State access is by name: a table of named variables (address or expression) that the driver extends as it
  learns. For a source port these are symbols; for an emulator, RAM addresses found by diffing.

## 3. Who does what

| actor | does | does not |
|---|---|---|
| orchestrator (a strong model in a coding-agent session) | reads the guide; writes predicates; finds and names state; chooses cell, alphabet and constraints; diagnoses failed searches; judges the result | choose inputs frame by frame |
| search (local, free) | finds inputs that reach a predicate; shortens and smooths them | know what the goal means |
| checker (local, free) | replays in a fresh process; evaluates the ordered steps and the forbids | — |
| cheap vision model (optional) | answers a yes/no question about a frame for acceptance ("do the blocks spell HAL?") | drive, plan, or read state |

Measured on Kirby (first session): reactive controllers lose. Jev fed RAM features died or timed out on 3 of 3
rooms, a tiny behaviour-cloned model beat it at zero cost, and neither beat search. As a visual judge Jev scored
2 of 4 (it answered "no" to everything); a general cheap VLM (Gemma 4 26B on OpenRouter) scored 4 of 4 at
$0.000025 and under a second per frame.

## 4. The loop

1. **Orient.** Check determinism. List what exists: verified traces to start from (the library), a knowledge
   base, named state. Test any reference movie against your runtime before using or hiding it.
2. **Write the task.** Ordered steps and `forbid` lines as expressions over named state (`tasks/*.md`). Start
   from the longest verified library prefix that the task allows.
3. **Lint the predicates** on traces whose behaviour you know (`kt lint`): a step that never holds on a trace
   that does the thing is a wrong predicate. (`stage == 1` never held in stage 1-2: the variable was not a
   stage index.)
4. **Find the state the mechanic lives in.** Object tables, counters, camera, flags: `mark → act → diff`, the
   knowledge base, or the source. Name it. This is where prose becomes searchable: "the Warp Star disappears
   from view" became `nstar` = number of live objects with the star's script id.
5. **Search each step** (§5). One call per sub-goal; a chain command for "next room until X".
6. **Check and verify.** `check` (ordered steps + forbids on a replay from the start, fresh process) and
   `verify` (the replay's state hash equals the live one).
7. **Look.** A contact sheet of the moment the trace is about. For unattended runs, ask a cheap vision model a
   yes/no question per key frame.
8. **Finish for the purpose** (§6): leave it, smooth it, or squeeze it. Then file the trace and its checkpoints
   in the library, and write what you learned as current state, not a diary.

## 5. Search without scores

`explore(goal, cell, avoid, actions)`: keep one state per **cell**; pick cells that were rarely expanded or
just discovered; run short random sequences of macro-actions from them in parallel; file every state passed
through under its cell if the cell is new or was reached in fewer frames; stop when the goal holds, then keep
going for a few seconds expanding only cells reached earlier than the best goal time (the path only gets
shorter).

The four knobs are the model's whole job:

- **Goal.** A predicate. "Somewhere I have not been" is a valid one: `room not in (0, 42, 43, 44, 45)` found
  1-1's invisible door in 16 s with no coordinates and no map.
- **Cell.** A tuple that says what counts as a different situation; default `(room, x//16, y//16)`.
  **Put the mechanic's state in the cell.** With `(x//8, y//16, nstar)` the search found the HAL-room trick
  (walk away until the star unloads, come back) in 3.8 s, because "past the pillar with no star" was new
  ground. Put time in the cell (`frame//20`) when nothing moves: cutscenes, minigames, timing presses.
- **Avoid.** Every constraint that must survive: no damage, keep the ability, do not leave the room.
- **Actions.** ~8-frame macro-actions, plus what the sub-goal needs: a long hold to inhale, a door press, a
  wait, 1-2 frame steps when position or timing must be exact.

Chaining: `go(until)` repeats "reach a value of `room` not seen yet" until a predicate holds. It carried UFO
Kirby through three rooms to the goal game in one call (66 s of search).

What it replaced: in recipe v1.2 every room cost about three model turns (map dump, a search with a
hand-written score, apply), and a wrong score cost one to three stalled two-minute searches.

Fights: one hit per call. With the boss HP variable and the mouth state in the cell, one hit on Poppy Bros. Sr.
at one HP bar took 2.9 s to find; asking for the whole kill in one 120 s call found nothing.

Speed passes, when frames matter:
- longer `refine` (the exploration is anytime: first path 1,266 f, 1,087 f fifteen seconds later on 1-1's
  first room; the hand-scored beam of the first session took 1,063 f and its speed run 844 f);
- a beam with a score on the segments worth it (v1.2's technique; run macros, phased scores);
- route changes, which no search finds for you: they come from the knowledge base.

## 6. Three kinds of trace

| | speedrun / TAS | test trace | demo clip |
|---|---|---|---|
| objective | fewest frames | reaches the behaviour, stays valid | shows the behaviour legibly |
| predicates | milestones | one per stage of the behaviour, tight forbids | the thing shown, plus "nothing ugly" (no damage, no death) |
| after the search | beam / refine per segment, route work | `simplify --mode smooth`: fewest input changes | smooth, add holds on the money shot, render |
| acceptance | replay + frame count vs a reference | replay + ordered steps | replay + steps + a look at the frames |

`simplify` is delta debugging on inputs: delete a hold, shorten it or merge it into its neighbour, keep the edit
if the rest of the trace still passes the task's remaining steps and forbids. On the whole HAL trace it removed
40% of the input changes and 6% of the frames and the trace still passed: it makes traces readable, not fast.
It also removes anything the task does not demand, including a deliberate pause, so state the pause as a step
or add it after.

## 7. Which driver

Same two secret tasks, same guide text, five drivers (`V2-LEDGER.md`):

| driver | tools | UFO room | HAL room |
|---|---|---|---|
| Sonnet 5.5 on the API harness | v1.2 (beam, lab) | pass, 37 turns, $0.58 | pass, 117 turns, $2.00, 39 min |
| Opus 5.5 on the API harness | v1.2 | pass, 36 turns, $1.15 | pass, 75 turns, $2.84, 39 min |
| Sonnet subagent in Claude Code | `kt` + `DRIVER.md` | pass, 26 tool calls, 66k tokens | pass, 44 tool calls, 88k tokens |
| Fable in Claude Code, direct | `kt` | pass, 5 tool calls | pass, 19 tool calls |

Two held-out tasks with the final card, fresh subagents: the hidden 1-Up room (Sonnet 25 tool calls, Fable 16)
and an ability-lifecycle test trace (Sonnet 10, Fable 16). All passed.

Long task, same harness and models, only the search tools changed (World 1 from power-on, with its fights):
Opus 241 turns / $9.26 / 3 h 25 min → 76 turns / $2.26 / 42 min, trace 14% longer; Sonnet 195 turns / $3.23 /
90 min → 133 turns / $1.97 / 75 min, trace 27% longer.

- The tooling moved more than the model did: the same Sonnet needed fewer calls with exploration search than
  with beams and scores, and it found the HAL trick the same way the strong model did (define the object
  variable, put it in the cell).
- A coding-agent session is the harness. `kt` is stateless (one command, one process, the run directory is the
  state), so any agent with a shell can drive it, context management is the session's problem, and a
  subscription covers the tokens. The bespoke API loop (episodes, notes, handoffs, spend stop) is no longer
  needed for this.
- A strong orchestrator takes bigger strides (fewer, denser calls) and is the right choice for task authoring
  and for mechanics nobody has described in state terms. A cheaper driver with the card is enough to execute a
  task whose predicates are written.

## 8. A target without snapshots (L0)

Each probe is a replay, so candidates must be few and informative:

- the plan is a small script with parameters ("confirm every N frames from F", "hold right K frames");
- a batch sweeps the parameters in parallel; predicates are read from state dumps at chosen frames;
- the game's own saves are the checkpoints: a trace continued from a save keeps prefixes short;
- screenshots every N frames do the diagnosis that stepping does on an emulator.

What transfers unchanged: the task format, predicates before play, state naming by diffing, verification by
fresh replay and hash, look-before-accept, the library. What does not: exploration at tens of thousands of
frames per second. The single most valuable addition to such a target is a snapshot (a fork server or a
serialisable state), then per-frame predicate evaluation with stop-on-true.

Measured on Fortune Summoners (`transfer/opensummoners/`): a fresh agent with a one-page brief authored a
4,190-frame trace from boot through the title, New Game, the first scripted scenes, free movement, a
story-gating conversation and a room exit, with ten predicates passing on four identical replays. It took 13
batches, 73 replays and 50 minutes. Scene predicates were function-entry traps, state came from dumps at chosen
frames plus four hardware watchpoints, and 75-95% of every replay was the prefix before control.

## 9. Things that bit

- A predicate over a variable that does not mean what its name says. Lint it.
- An object listing that hid class-0 objects (pickups, Warp Stars): liveness is not "is an enemy".
- A search bounded by wall time is not reproducible: apply or save the result you got.
- A search that outlives its shell keeps writing: one command per run, enforced by a lock.
- "Any new room" is not "the room I meant": name the wrong rooms in `avoid`.
- Contact is not completion: rides, pickups and doors take frames after the touch. Search for the contact,
  then wait and read the events.
- The first-session API harness burned $22 idling after it was done and re-ran stale searches after reloads; a
  stateless CLI under a coding agent has neither failure.

## 10. Files

| file | what |
|---|---|
| `drive.py` (`kt`) | the stateless driver: new, play, look, strip, ram, room, search, go, simplify, lint, check, verify, render |
| `xsearch.py` | `explore`, `simplify`; `polish` (a beam on the learned frames-to-goal field) is unvalidated: it did not finish in 240 s |
| `DRIVER.md` | the one-page card a driving agent reads |
| `tasks/*.md` | tasks: ordered predicates, forbids, start prefix |
| `knowledge/secrets.md` | what the guides say (the only source for the secret tasks) |
| `V2-LEDGER.md` | every measurement of the v2 work |
| `RECIPE.md`, `SESSION-REPORT.md`, `agent.py` | the first session's per-game recipe, report and API harness |
