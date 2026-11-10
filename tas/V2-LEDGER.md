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
