# Recipe v2 evidence ledger (2026-11-10, Fable review session)

Raw measurements behind PLAYBOOK.md and the showcase page. One row per run; numbers copied from tool output.

## Audit of the 2026-11-09 session (SESSION-REPORT.md)

- All six traces in `traces/` replay from power-on on a fresh FCEUmm core and end in the claimed state
  (main: room 17 world 6, 137,712 f; w12-opus: W3 hub; w12-sonnet: W3 hub, **0 lives**; w2-seq: room 173 with
  ability 18; 1-1-speed: W1 hub 3,159 f; w3-sonnet: W4 hub, 1 life).
- §8 candidate 5 ("trim `apply` to the goal frame") is moot for the built-in search: `env.search` already cuts
  the last action at `goal_at`. Only labkit `flow2` returns whole actions, and those extra frames fall inside
  the door transition (frame-neutral; the risk is a held Up re-entering the door).
- `stage` (`$0520`) stays 0 inside every stage of world 1 (w12-opus enters 1-2 with stage 0): it is not a
  stage index. My first HAL task used `stage == 1` and could never have passed. → predicate lint (`kt lint`).
- The harness `ram objects` view hid every object with collision class 0, which includes Warp Stars, pickups
  and the UFO-room UFO: the "roominfo doesn't list Warp Stars" wish. Liveness is the script id
  (`$6128+slot < $80`). Fixed in `drive.py`.

## Secret tasks: same task, five drivers

Tasks: `tasks/secret-ufo.md` (start 1-1-speed:r44_start, f1,413) and `tasks/secret-hal.md` (start
1-1-speed:final, f3,159). Knowledge given to every driver: `knowledge/secrets.md` (guide text only).

| task | driver | tools | result | frames (own part) | turns / tool calls | cost | wall |
|---|---|---|---|---|---|---|---|
| UFO | Sonnet 5.5, API harness | recipe v1.2 (beam + lab) | PASS | 3,893 (+2,480) | 37 turns | $0.58 | 11 min |
| UFO | Opus 5.5, API harness | recipe v1.2 | PASS | 3,605 (+2,192) | 36 turns | $1.15 | 15 min |
| UFO | Fable, Claude Code direct | kt + explore | PASS | 3,792 (+2,379) | 5 tool calls | plan | ~5 min |
| UFO | Sonnet subagent, Claude Code | kt + DRIVER.md | PASS | 3,759 (+2,346) | 26 tool calls, 66k tokens | plan | 9.6 min |
| HAL | Fable, Claude Code direct | kt + explore | PASS | 5,840 (+2,681) | 19 tool calls (4 picture reads) | plan | ~20 min |
| HAL | Sonnet subagent, Claude Code | kt + DRIVER.md | PASS | 6,104 (+2,945) | 44 tool calls, 88k tokens | plan | 18 min |
| HAL | Sonnet 5.5, API harness | recipe v1.2 | (see below) | | | | |
| HAL | Opus 5.5, API harness | recipe v1.2 | (see below) | | | | |

Explore search wall times in my own runs (machine shared with two API runs, load 20-38):
- hub → 1-2 door: 139 f in 5.7 s (first hit), 22.9 s total.
- room 44 → the invisible door (goal: "a room that is not 0/42/43/44/45", no coordinates): 821 f, 15.6 s.
- copy UFO (`ability == 23`): `B*48 D*2`, 7.2 s.
- `kt go --until "room == 42"` as UFO (3 rooms, avoid `ability != 23`): 122 + 260 + 691 f in 10 + 20 + 34 s.
- HAL trick, goal `nstar == 0 and x >= 930`, cell `(x//8, y//16, nstar)`: first hit 3.8 s, 316 f after 21 s.
  Camera max X `$05C2` goes 1024 → 1536 and max Kirby X `$05CA` 1007 → 1519 when the star object is gone.
- to the HAL blocks: 351 f, 8.3 s. Back to the Warp Star and room 48: 556 f, 16 s.

## Cheap models as visual judges (4 frames: HAL blocks / hub; pillar without star / with star)

| model | correct | per call |
|---|---|---|
| google/gemma-4-26b-a4b-it (OpenRouter) | 4/4 | 0.5-0.8 s, $0.000025 |
| Jev (OpenRouter Decisions) | 2/4 (always "no"; p(yes) 0.16 vs 0.17, 0.43 vs 0.40) | 0.2 s, $0.000014 |
| qwen/qwen3.7-flash | empty answers at max_tokens 120 (reasoning model) | 2 s |

## Passes

- `simplify --mode frames` on the explored path room-47 start → past the star (1,245 f, 164 holds): 51 edits in
  150 s → 1,221 f (-2%), 96 holds (-41%). It smooths; it does not find speed.
- Explore refine on 1-1 room 43 (goal `room != 43`, no damage): first path 1,266 f at 41 s, 1,087 f after 15 s
  more. References: w12-opus routine beam 1,063 f; 1-1-speed 844 f.

## Driver-card feedback folded in (from the two Sonnet subagents)

- A shell timeout moved a search to the background and it kept writing into the run → per-run lock, defaults
  75 s + 8 s, card says to give the shell 300 s.
- `kt go` goes to any unseen room (from the hub it went into 1-1 instead of 1-2) → card.
- Goal game / cutscenes need a time cell (`frame//20`); UFO doors may need a diagonal; a Warp Star needs
  standing on it ~20 f then ~100 f of ride; `kt strip` (read-only) instead of rewinding to look.

## Held-out tasks (final card, tasks nobody had tried)

| task | driver | result | frames (own part) | tool calls | tokens | wall | failed searches |
|---|---|---|---|---|---|---|---|
| secret-1up | Fable subagent | PASS | 11,196 (+2,852) | 16 (1 picture) | 64k | 6.2 min | 0 of 6 |

- 1-Up (Fable): hidden door in room 51 at tile (12, 2), px (40, 201), on the left wall; found by the "any room
  not in the known list" search (528 f, 32 s). `kt room` also lists it: the collision map marks invisible doors
  as doors, so door secrets are visible in state. The HAL trick is not.
- Task-authoring bug it caught: step 1 (`room not in (...)`) already held at frame 1,275 inside the library
  prefix, so the check did not prove the visit. `kt lint` had printed exactly that and I dismissed it. Fixed in
  the checker: steps are judged only after the task's start prefix (`task.check_job(after=)`); the same run now
  reports step 1 at frame 10,176.
- A script fed on stdin (`python - <<EOF`) broke the search workers (spawn re-imports `<stdin>`); fixed in
  `drive.py`.
| secret-1up | Sonnet subagent | PASS | 11,131 (+2,787) | 25 (4 pictures) | 67k | 11.3 min | 4 |
| ability-cycle | Fable subagent | PASS | 1,773 (+1,204) | 16 (2 pictures) | 77k | 4.4 min | 0 of 4 |

- 1-Up (Sonnet): its "room not in 47-51" search failed (75 s, 83 cells, machine load ~70); it then read the
  door list from `kt room`, searched to the door tile and pressed Up by hand.
- ability-cycle (Fable): Beam from a Waddle Doo (207 f, 25 s); hit by the slot-15 walker (72 f, 16 s); the
  knocked-out star is script id 5, spawned in slot 16 on the hit frame, bouncing up-right ~14 px per 10 f;
  regained with cell `(x//16, y//16, star, mouth, (sx-x)//16, (sy-y)//16)` in 106 f, 24 s; carried to room 44
  in 779 f, 54 s. Steps held at f776 / 888 / 994 / 1,773.
| ability-cycle | Sonnet subagent | PASS | 2,075 (+1,506) | 10 (1 picture) | 57k | 2.0 min | 0 of 4 |

## HAL on the API harness (v1.2 tools), final

| driver | result | frames (own part) | turns | cost | wall |
|---|---|---|---|---|---|
| Sonnet 5.5 | PASS | 8,322 (+5,163) | 117 (3 episodes) | $2.00 | 39 min |
| Opus 5.5 | PASS | 6,145 (+2,986) | 75 (3 episodes) | $2.84 | 39 min |

API credit used in this session so far: $0.58 + $1.15 + $2.00 + $2.84 = $6.57.

## More passes (machine load 40-50)

- `simplify --task tasks/secret-hal.md --mode smooth --slack 0.03` on the whole HAL trace (own part 2,441 f,
  285 holds): 73 edits in 405 s → 2,295 f (-6%), 170 holds (-40%); still PASS and MATCH (`runs/hal-demo`).
  It also deletes anything the task does not demand, e.g. a deliberate pause on the shot.
- `polish` (beam on the learned frames-to-goal field) on 1-1 room 43: no goal within 240 s at depth 70+
  (twice). Not validated; not part of the recipe.
- Explore on room 43 again (seed 1, refine 20 s): 1,156 f. Earlier run: 1,087 f. Wall-time-bounded searches
  are not reproducible.

## Transfer: Fortune Summoners under OpenSummoners' rhost (wine), replay-only (L0)

Fable-class subagent, one-page brief, read-only on /opt/src/OpenSummoners. Files: `transfer/opensummoners/`
(`NOTES.md` first; `final.spec` → `final.jsonl`; `rt.py` helper; `check.py` → `check.out` VERDICT: PASS).

- Trace: 516 input lines, last input f4,190, replayed 4,310 frames. Four replays in two batches:
  `frame=4310 tick=3116 rng=8a54b40d state_semv=4a00df1a54543412` each.
- Predicates and first-hold frames: title f47; new-game config f752; first room loaded f1,222
  (`room_id == 210110`); house interior f2,696; control f2,810 (`w2760 == 0 and dlg == 0`); Right moves the
  leader f2,826; crossed room + stairs f3,107; talked to the mother f3,225 (dialogue f3,271); control back by
  f3,505; left through the bedroom door f3,646 (`room_id` 210140 → 210141); control in the second room by f3,900.
- Cost: 13 batches (one crashed at frame 0), 73 replays (70 with a result), 279,740 frames; 9-33 fps per replay
  at load 45-70, 70-133 fps below load 30; ~50 min wall; 113 tool calls; 286k tokens.
- Adaptations: search → parameter sweeps (5-8 candidates per batch); scene predicates → function-entry traps;
  per-frame values from `--watch-write` (4 words) + dumps at chosen frames; "speculative continuation" (the
  same follow-up at several guessed start frames) instead of extending from a saved state.
- Missing in the target, by impact: snapshot/resume; per-frame predicate with stop-when; per-run batch options;
  fragile hardware watchpoints under wine; `--watch` on a heap address faults at frame 0 and hangs in winedbg.
- Incident: that hang (batch 2). The agent terminated its own six processes by PID after checking prefix,
  start time and command line, instead of waiting out the timeout as briefed. No by-name kills.
- Housekeeping: this session's 13 intermediate batch directories under the wine runs root (~6.5 GB) were
  deleted; the final check batch `20261110-022331-run` (1.2 GB) is kept. OpenSummoners' git tree is untouched.

## Fights with explore (Poppy Bros. Sr., 1 HP bar, from w12-opus:popsr; machine shared with two API runs)

- One hit: goal `bhp < 30 and hp == 7`, avoid `hp != 7 or room != 49`, cell
  `(x//16, y//16, mouth, inh, bx//32, bhp)`: found in 2.9 s, 83 f (30 → 20).
- Whole fight in one call (`bhp == 0`, 120 s): not found; 993 cells, all still at bhp 20. One hit per call, as
  in recipe v1.2, is the working pattern; the kill does not fall out of exploration on its own.

## World 1 from power-on on the API harness: v1.2 tools against v1.2 + explore/go (`KIRBY_V2=1`)

Task `tasks/w1-scratch.md` (power-on → Whispy Woods → W2 hub, reference forbidden). The v1.2 rows are the
first session's w12 runs cut at their W2-hub milestone (turns counted from `traces/*/spend.csv`).

| driver | tools | result | W2 hub at frame | turns | cost | wall | lives at the end |
|---|---|---|---|---|---|---|---|
| Sonnet 5.5 | v1.2 | pass | 24,819 | ~195 | $3.23 | ~90 min | (run later ended on 0) |
| Sonnet 5.5 | v1.2 + explore | pass | 31,447 (+27%) | 133 (8 episodes) | $1.97 | 75 min | 3 (one lost) |
| Opus 5.5 | v1.2 | pass | 20,222 | ~241 | $9.26 | ~3 h 25 min | 4 |
| Opus 5.5 | v1.2 + explore | pass | 22,957 (+14%) | 76 (5 episodes) | $2.26 | 42 min | 5 |

- Opus v2 per stage: 1-1 $0.34 (6 turns, one `go` of 3 steps); 1-2 $0.82 (Poppy Bros. Sr. in 3 explore
  calls); 1-3 $0.14 (one `go` call, 136 s); 1-4 $0.47 (`go` failed in Mr. Frosty's arena, then per-hit
  searches); Whispy + hub $0.49.
- Sonnet v2 spent $0.78 of its $1.97 in 1-2 (bad cells at Poppy Bros. Sr.: `frame//30` in a position cell
  made 14,418 cells; a 3-cell search) and $0.82 on Whispy.
- The two v2 runs ran concurrently for part of the time (load 15-35).

API credit used on 2026-11-10: $0.58 + $1.15 + $2.00 + $2.84 + $1.97 + $2.26 = $10.80.
