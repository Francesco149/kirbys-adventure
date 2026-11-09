# Session report: Kirby TAS agent, 2026-11-08 → 2026-11-09 (handoff for review)

This is a dense handoff for the reviewing agent (Fable, in Claude Code on the owner's subscription; usage is
limited, so read in the order of §1). It covers everything the build-and-run session produced and learned that
isn't obvious from the code. Numbers come from the run logs; `traces/` has the raw data behind every table.

## 0. What the owner wants from you

1. **Audit this work.** Read the recipe, check that its claims hold against the traces and logs, and fix what's
   wrong.
2. **Test your own optimisations** (§8 has candidates with baselines). Then fold what you measure into
   `RECIPE.md`.
3. **Produce the human-facing visual report:** a summary page showcasing the whole project and its findings,
   "ideally with some video comparing the LLM-authored TASes and interesting parts of them" (§7 has clip
   ranges and tooling). Publish it as an Artifact page (load the `artifact-design` skill first; video files go
   through the page's `assets` capability, see the `artifact-capabilities` skill; 16 MB page cap; no external
   fetches).

The original brief, from the owner's own words at the start of the session:
- Spend expiring Claude API credit on autonomous work, within ToS.
- Showcase: an agent that runs tools on the owner's machine and uses Jev (TypeSafe's decision model, via
  OpenRouter) to learn Kirby's Adventure and produce a reproducible TAS.
- Test how much low-latency control to hand Jev versus its own reasoning.
- It should have savestates, a walkthrough and speedrun knowledge, and look at the screen and step frames.
- Later additions:
  - if Jev's vision is weak, the agent should work out which game-state data to feed it;
  - evaluate classic input brute force;
  - evaluate a tiny game-specific ML model.
- "It doesn't need to finish the game as long as it makes meaningful progress on the recipe to drive such
  autonomous TAS discovery tasks." The recipe is the deliverable.

## 1. Read order (minimal)

1. This file.
2. `RECIPE.md` (v1.2, ~19 KB): the distilled method, with every measurement; §0 holds all run results.
3. `README.md`: the pieces and how to run them.
4. `traces/stage-splits.csv` and `traces/<run>/report.md`: the agents' own reports, as needed.
5. Only if needed: `runs/<run>/log.jsonl`, which records every turn (cost, context, thinking summary, tool
   calls and results).

## 2. System in one paragraph

`nes.py` is a headless libretro frontend over ctypes (FCEUmm core from nixpkgs; Mesen also present) with
savestates, RAM ($0000-$07FF and cart WRAM $6000-$7FFF) and the framebuffer.

`env.py` is the workbench:
- the movie, a per-frame input list that always starts at power-on, in a run-length spec language
  (`R*20 RA*8 .*30`);
- checkpoints, rewind, named RAM variables with a safe expression language;
- parallel beam/random search (16 spawned workers, RAM-hash dedupe);
- verification by replaying from power-on in a fresh process;
- `.fm2` export.

`agent.py` is the Claude tool loop (Messages API, manual loop, adaptive thinking, effort medium). It provides:
- tools: play, look, rewind, checkpoint, ram (including `objects`), search, jev, python (bwrap sandbox, no
  network, 8 GB scope), jobs, notes (notes/recipe/journal), knowledge, milestone, handoff, finish;
- episodes that each start a fresh conversation from notes, with a handoff at about 70K context;
- server-side tool-result clearing at 90K; a hard spend stop; an operator inbox (`runs/<run>/inbox.md`,
  delivered once); a reload flag.

Other pieces:
- `task.py`: task mode. A task is ordered RAM-predicate steps plus `forbid` invariants, checked on a replay
  from power-on by `finish`. A run can start from a library prefix (`<run>:<checkpoint>` or `<run>@<frame>`).
- `labkit/`: the main run's proven lab helpers (roominfo, flowsearch/flow2 distance-field beam, goalscan).
- `knowledge/`: walkthrough, mechanics, speedrun notes, RAM map, the reference TAS 3226M plus its splits on
  our core, and `ram-seed.json`.

**Driving the workbench yourself (no API needed).** One emulator core per process: a second core in the same
process, or a fork of one, silently hijacks the first one's callbacks.

```python
# from /opt/src/kirbys-adventure/tas, with .venv/bin/python
import env as E
e = E.Env("runs/fable-x", "fceumm")      # new dir = power-on; to start from a trace, first write
                                          # runs/fable-x/movie.txt = prefix of traces/<run>/movie.txt
e.play_masks(E.parse_spec("T .*30"))      # append inputs; e.status_line(), e.frame, e.core.mem[0x0597]
r = e.search(["R*8", ". R*7", "UR*8", "U*5 .*3"], goal="room != 43 and hp < 48",
             score="x", avoid="hp > 47 or hp < 7", max_depth=60, beam=512)   # free, ~2,000 f/s per worker
e.ck_save("name"); e.ck_load("name"); e.truncate(n); e.verify_async()      # (future, hash) -> compare
```

- Search spawns 16 workers, and the machine has 20 cores. Run heavy jobs inside a memory-capped scope: the
  harness uses `systemd-run --user --scope -p MemoryMax=8G`; nix-lab's `utils/cap-run.sh` also works.
- Render a clip with `python render.py <movie.txt> out.mp4 --from F --to F --scale 3`. It replays from
  power-on (fast) and encodes only the range.
- `python status.py runs/<run>` prints a run's progress.
- `python verify_ck.py runs/<run> <checkpoint>` replays a checkpoint's movie and compares it to the savestate.
- `KIRBY_CORE=fceumm` must match the run's core; movies only replay on the core they were made on.

## 3. Results (all runs passed their checks unless noted)

| run (driver) | what | trace | cost | turns / episodes | wall time | steering |
|---|---|---|---|---|---|---|
| `main` (Opus 5.5) | open research run | game complete: Nightmare Wizard killed at f136,812, ending at f137,712; replay verified MATCH 2026-11-09 | $100.04, of which $4.01 was an archived Mesen attempt | 1,161 / 124 | 18:36 → 03:36 | 5 inbox messages (harness fixes, core switch, Jev/model experiments) |
| `w12-opus` (Opus) | task: power-on → W3 hub, reference inputs hidden | W3 hub at f51,207 | $23.84 | 606 / 20 | 08:45 → 16:47 | crash fix plus "stop optimising, run the routine"; harness-update notice |
| `w12-sonnet` (Sonnet 5.5) | the same task | W3 hub at f69,751 (ended on its last life) | $14.44 | 837 / 22 | 08:45 → 17:32 | harness notice; Mr. Frosty boss-HP method |
| `w2-seq` (Opus) | sequence task from library prefix `w12-sonnet:ms-1-whispy` (f24,870): enter 2-1 → copy Tornado → clear 2-1 → hub holding Tornado → enter 2-2; forbid losing a life | +4,347 f (f29,217) | $1.50 | 44 / 1 | ~16:48 → 17:05 | none |
| `1-1-speed` (Opus) | speed task: shortest power-on → 1-1 cleared → W1 hub | 3,159 f | $2.95 | 71 / 2 | 17:54 → ~19:25 | none |
| `w3-sonnet` (Sonnet) | continuation from `w12-opus:final` (f51,310): World 3 and Mr. Shine & Mr. Bright → W4 hub | W4 hub at f87,667 (+36,357) | $10.58 | 602 / 18 | 17:10 → 23:19 | harness notice (objects, hex); Bugzzy HP-slot steer |
| `pilot` | 7-turn smoke test | — | $0.33 | | | |

- **API total:** ~$153.7 of the $200 credit. That's an estimate at list prices from `usage`: Opus $4/$20 per
  MTok, cache writes $5, cache reads $0.40; Sonnet half that. The Console is authoritative. About $46 is left
  and expires within days; the harness can use it (`--model claude-opus-5-5|claude-sonnet-5-5`).
- **Jev:** OpenRouter, $0.22 in total.

### What is LLM-authored (be precise in the report)

- `main` frames 0-78,090 are **the reference TAS 3226M replayed verbatim**: worlds 1-4 and half of world 5.
  - In episode 9 the agent noticed (it had skipped a KB header saying so) that 3226M syncs on our ROM/core
    (USA Rev A = PRG1, FCEUmm). Before that, its own W1 play was 70% slower than the reference.
  - Its own play runs from 5-6 (f78,090) to the end: 59,622 frames, 30% slower than 3226M over the same span
    (45,847 frames).
- **Carried UFO:** the reference uses the UFO glitch in 1-1, so `main` played all of worlds 6-7 and the bosses
  with a glitched UFO (`ability` reads $FF).
- **Fully LLM-authored traces, normal Kirby, no reference inputs:** `w12-opus`, `w12-sonnet` and `1-1-speed`.
  `w2-seq` and `w3-sonnet` are LLM-authored segments on top of LLM-authored prefixes.

### Stage splits: the frame at which each stage clear's hub return happens

Computed the same way for every trace (`traces/stage-splits.csv`): goal-game room 42, then the world's hub
room. W1 hub is room 0, W2 room 1, W3 room 2, W4 room 3.

| split | reference 3226M | w12-opus | w12-sonnet | w3-sonnet |
|---|---|---|---|---|
| 1-1 | 2,625 | 3,683 | 4,417 | |
| 1-2 | 5,398 | 8,965 | 10,418 | |
| 1-3 | 7,846 | 12,839 | 16,369 | |
| 1-4 | 10,055 | 17,049 | 20,420 | |
| W2 hub (Whispy) | 11,531 | 20,222 | 24,819 | |
| 2-1 | 13,550 | 23,333 | 28,772 | |
| 2-2 | 16,543 | 28,768 | 36,933 | |
| 2-3 | 19,741 | 34,660 | 44,094 | |
| 2-4 | 22,895 | 43,085 | 55,468 | |
| 2-5 | 26,207 | 48,271 | 64,387 | |
| W3 hub (Paint Roller) | 27,650 | 51,207 | 69,751 | (prefix = w12-opus) |
| 3-1 … 3-6 | 29,506 / 32,098 / 34,327 / 36,801 / 38,608 / 41,159 | | | 54,929 / 61,483 / 64,799 / 69,027 / 73,076 / 81,013 |
| W4 hub (Shine & Bright) | 42,710 | | | 87,667 |

**World lengths against the reference:**

| world | reference | Opus | Sonnet |
|---|---|---|---|
| World 1 | 11,531 | 1.75x | 2.15x |
| World 2 | 16,119 | 1.92x | 2.79x |
| World 3 | 15,060 | — | 2.42x |

- Outliers worth showing:
  - w12-sonnet's 2-4: 11,374 frames against the reference's 3,154, mostly a Mr. Frosty fight read off
    screenshots.
  - w12-opus's 2-4: 8,425 frames, including ~2,650 lost by entering the Crane Fever minigame door.
- `main` equals the reference through f78,090, so it isn't shown in this table.

### Driver models (the same task and recipe)

- Opus traces are 26% shorter; Sonnet costs 39% less per trace and gets 2.25x the frames per dollar
  (4,840 against 2,150).
- Mean cost per turn: Opus ~$0.039, Sonnet ~$0.017.
- Sonnet tends to read state off screenshots, while Opus over-builds lab tooling. Each needed one steer at a
  fight.
- Recipe recommendation: produce traces with Sonnet, and spend a stronger model on segment optimisation. That
  mixed strategy is **untested**; see §8.

### Speed task curve (1-1)

| version | frames | cost |
|---|---|---|
| routine (w12-opus) | 3,683 to the hub | |
| speed v1: recipe plus lab-scanned menus (569 f to 1-1 room 43) and phased scores | 3,229 | ~$2.2 |
| speed v2: plus run macros `. R*7` / `R . R*6` and one phased search per room | 3,159 | $2.95 |
| 3226M | 2,625 | |

- The run macros alone saved 72 frames on an 800-pixel stretch.
- The remaining ~530 frames to 3226M come from the UFO-glitch route: inhale 2+ ability enemies in room 43 and
  mix to UFO. An `inab >= 2` beam found only one reachable enemy on this RNG.

### Controllers (main run, Experiments 1-5; same checkpoints: 7-3 rooms 145/144, 7-4 room 148, UFO, one HP bar)

| controller | room 145 | room 144 | room 148 |
|---|---|---|---|
| beam search | 561 | 715 | 555 |
| tiny random-forest clone of search (650 samples, flow hint; trained in 2 s) | 624 | 672 | died |
| Jev with RAM features | died | timeout | died |
| shield + RF clone | timeout | 672 | 784 |
| shield + Jev | 1,448 | timeout | 880 |

- Offline agreement with search labels on 160 states:
  - Jev without the hint 0.56, Jev with the hint 0.73;
  - the hint alone 0.74, always-right 0.51.
- Verdict: Jev adds nothing beyond the feature it is fed. Reactive policies die without lookahead. Search wins.
  Hand-written greedy controllers in the lab pay off on grinds: the Nightmare Orb went from 3,312 to 1,952
  frames with a 6-run x-target sweep.
- Jev also called the title screen "gameplay".

### Cost mechanics (measured)

**Cost per turn by context size (main run):**

| context | 20-40K | 40-60K | 60-80K | 80-100K |
|---|---|---|---|---|
| mean $/turn | $0.04 | $0.05 | $0.09 | $0.17 |

- The jump above 60K was cache rewrites after each server-side clear (then at 70K).
- Fresh episodes are 5x cheaper per turn: 7-3 cost $0.95 fresh, against 7-2's $5.9 late in a long episode.
- After the handoff and notes fixes, task runs started each episode at ~31-36K, cost $0.012-0.05 per turn and
  saw no loops.

## 4. Timeline and incidents (each fix is a commit in this repo)

- **11-08 18:30, build.**
  - The ToS reasoning: a client-side tool loop on an API key is ordinary use. Screenshots and RAM go to the
    API; the ROM never does. Using a claude.ai subscription login for this custom harness would not be
    appropriate.
  - Managed Agents was assessed but not used. A self-hosted environment needs a Console environment key;
    sessions cost $0.08/h; custom tool results are text only; the Console session viewer would suit a
    showcase.
- **18:36, the main run starts on Mesen.** Five bugs surfaced and were fixed live:
  - forked search workers ignored inputs (fixed with spawn);
  - the milestone verify created a second core in the harness process and hijacked the live one (the
    one-core-per-process rule followed);
  - lab paths and the sandbox's Python;
  - score-only search wall-pinning (trimmed to peak);
  - the switch to FCEUmm, which is ~5x faster and the core 3226M syncs on. The Mesen movie desynced by a frame
    on FCEUmm, so the run was archived and restarted.
- **~20:56, episode 9:** the agent discovered the reference syncs and pasted 78,090 frames for ~$0.2.
- **11-09 01:58, operator steer:** the Jev and tiny-model experiments were still undone, so the agent was told
  to run them. The handoff threshold went from 160K to 62K.
  - Side effect: notes had grown into a 73 KB diary, so each kickoff was 67K, above 62K, and every episode
    handed off after about 3 turns (episodes 46-62).
  - Fix: handoff relative to the episode's start size; notes capped at 16 KB as current state; history moved
    to a `journal`.
- **03:24:** the game was complete at $78.4. **03:36: the budget was reached at $100** after ~60 empty
  episodes, because there was no stop tool. Fix: a `finish` tool, and a stop after 3 idle episodes.
- **08:30:** recipe v1, task mode and the labkit, then the w12 runs launched.
- Bugs found during those runs:
  - an empty PNG crashed w12-opus with an API 400, because `lab.load` left rendering off;
  - `search` didn't accept recipe-style quoted actions;
  - `apply` applied failed goal searches;
  - reloads leaked search pools: 34 orphan workers pushed load to 67 on 20 cores. Spawned workers re-imported
    `agent.py` and its module-level SIGTERM handler, so they ignored SIGTERM. Fixed with handlers in `main()`
    and terminating children before `execv`;
  - milestone verifies were lost on reload (startup re-verify added);
  - addresses like "6200" were parsed as decimal (now hex everywhere);
  - flowsearch's one-way check was inverted and treated ladders as one-way.
- **16:47-23:19:** w12-opus passed, then w2-seq, w12-sonnet, 1-1-speed and w3-sonnet. Each run's lessons were
  folded into the recipe as v1.1 and v1.2.

## 5. Recipe gist (details and evidence in RECIPE.md)

- **Orient first.** Test every existing movie against the core. Read KB headers fully. Name the verified RAM.
- **Per room, about 3 turns.**
  1. `.*45`, checkpoint, `roominfo` (the map buffer lags the room var).
  2. One search to the door:
     - open rooms: the built-in beam (8-frame actions including run macros, x-first scores, depth scaled to
       room width);
     - vertical, blocked or low-HP rooms: the labkit distance-field beam;
     - breakables: a random search with a tile-byte goal;
     - time-varying doors: wait actions in the alphabet.
  3. Apply the result.
- **Fights:** random mode, one hit per call. Find the boss HP slot by mark, hit, diff, and do it again in every
  branch, since the slot depends on spawn order. After a boss, collect the Star Rod piece.
- **Cost:** milestone at every stage clear (fresh episodes); notes as state; `finish` when done.
- **Goal-directed traces:** RAM predicates, the longest verified library prefix, guards on later constraints
  in every search, an ordered check on replay.

## 6. Artifacts map

| path | contents | in git |
|---|---|---|
| `traces/<run>/movie.txt` | the verified trace (spec language, from power-on). Replay: `E.parse_spec(open(p).read())` | yes |
| `traces/<run>/rooms.csv` | every (world, stage, room) change on replay, with hp/lives/ability/trans/x/y | yes |
| `traces/<run>/spend.csv` | every turn: time, episode, turn, cost, cumulative cost, frame, context tokens, tools (frames-per-dollar curves) | yes |
| `traces/<run>/harness.json` | splits (milestones with frame, cost, verified, summary), tool counts, finish | yes |
| `traces/<run>/report.md`, `notes.md`, `task.md`, `result.json`, `checkpoints.json`, `steering/` | the agent's own report and state notes, the task, the check result, the operator messages it received | yes |
| `traces/stage-splits.csv` | the table in §3 | yes |
| `runs/<run>/log.jsonl`, `episodes/` | full turn logs, including thinking summaries: quotes and anecdotes for the report | no (runtime, ~80 MB total) |
| `runs/<run>/frames/*.png` | **every image the agent looked at**, named `<turn>-<frame>.png`, good for "what the agent saw" visuals (main: 688) | no |
| `runs/<run>/checkpoints/*.state` | savestates (e.g. `ms-*` at each split) | no |
| `runs/<run>/lab/` | the agents' own scripts, datasets and models (main: Orb/Wizard controllers, RF clone, Jev eval) | no |
| `runs/main/archive-mesen/` | the archived first Mesen attempt | no |
| `knowledge/movies/3226M.fm2` | the reference TAS (FCEUX, PRG0). On our core it is `traces/main/movie.txt` up to f78,090 | yes |

## 7. Video material (frame ranges for `render.py --from/--to`; 60.0988 fps, 256x240)

Each range is in its own trace's frames. For side-by-sides, render each, then `ffmpeg -filter_complex hstack`
(pad to equal length, label each panel).

1. **1-1 four ways (best opener):**
   - 3226M = `traces/main/movie.txt` 0-2,625;
   - `1-1-speed` 0-3,159;
   - `w12-opus` 0-3,683;
   - `w12-sonnet` 0-4,417.

   It shows UFO-glitch routing against search-optimised normal Kirby against routine play.
2. **Whispy Woods (arena entry → W2 hub):** reference 10,401-11,531; w12-opus 17,501-20,222; w12-sonnet
   21,148-24,819.
3. **Paint Roller:** reference 26,704-27,650; w12-opus 48,834-51,207; w12-sonnet 65,215-69,751.
4. **Mr. Shine & Mr. Bright:** reference 41,454-42,710; w3-sonnet 81,543-87,667 (the fight is about the first
   800 frames, then the piece and the cutscene).
5. **Reference → LLM handoff in `main`:** 5-6 at ~77,780-79,500 (W5 hub room 4, then 5-6 rooms 49/50; the
   reference stops at 78,090).
6. **`main` own-play bosses with the carried UFO:**
   - Heavy Mole: rooms 12/13, 81,128-82,633;
   - Meta Knight: room 108, 105,393-107,599;
   - King Dedede: room 14, 129,211-130,264;
   - Nightmare's Orb: room 15, 130,450-133,556 (the greedy-controller grind);
   - Nightmare Wizard: room 16, 133,557-137,528 (killed at 136,812);
   - ending: room 17, from 137,529.
   - 6-6 Meta-Knights gauntlet (random search, one kill per call): inside 99,927-105,092.
7. **The sequence task's Tornado copy (w2-seq):** ~27,300-27,700 (copied at 27,394-27,575). The full task runs
   24,870-29,217.
8. **Bugzzy (w3-sonnet, 3-2 room 210):** 59,518-~61,025.

Good still images: `runs/<run>/frames/` (what the agent saw), plus `roominfo` ASCII maps from lab output.

## 8. Optimisation candidates (baselines; untested unless noted)

**Caveat for all of them:** changing an early segment changes RNG and positions, so the rest of the trace
desyncs. Test as segment re-searches from the same start checkpoint (before/after frames), or as task runs
from a library prefix (`start: <run>@<frame>`). Re-verify any full trace you change.

1. **Mixed strategy, the main untested recipe claim:** re-optimise one Sonnet stage with a stronger driver.
   - Candidate: w12-sonnet 2-4 (11,374 frames, against Opus's 8,425 and the reference's 3,154). Start from
     w12-sonnet's 2-3-cleared state; end when back in the W2 hub after 2-4.
   - Measure the frames recovered against the cost.
2. **Run macros everywhere:** re-search one w12-opus room with `. R*7` and `R . R*6` added. The 1-1-speed run
   measured -72 frames per 800 px.
3. **Hub-wait scan:** input seems to be accepted ~205-210 frames after hub arrival, not 240. In w12-opus, one
   door search failed during the unlock cutscene, and 2-1 accepted input right after the fade. That's ~30
   frames per stage start, never verified with real door inputs.
4. **The 1-1 UFO-glitch route:** 2,625 against 3,159; the method is in `knowledge/speedrun.md` and
   `mechanics.md`. It needs two ability enemies inhaled in room 43 under our RNG; try manipulating with
   menu/press timing.
5. **Trim `apply` to the goal frame:** a found result keeps the rest of its last action (up to 7 frames for
   8-frame actions, and `R*27` was seen). Re-play the last action frame by frame. That's ~3-10 frames over
   ~100 rooms.
6. **Bonkers in 6-3 (`main`):** 453 frames, against the mid-boss template's ~110.
7. Harness wishes still open: a distance-field score in the built-in `search` (saves 6-10 min of lab wall time
   per call), and `roominfo` listing Warp Star objects and marking minigame/arena doors.

## 9. Honesty notes for the visual report

- **Steering:** say which runs were steered and how (§3 table; the messages are in `traces/<run>/steering/`).
- **Costs are list-price estimates** from token usage.
- **Traces:**
  - The `.fm2` exports have not been checked on FCEUX or BizHawk; the traces are verified on FCEUmm only.
  - The ROM is PRG1, while 3226M was made for PRG0.
- **Search results don't reproduce exactly:** they depend on wall-time limits and CPU load (some runs ran
  concurrently), so re-running a search may find a different result.
- **`main`'s 30% gap** to the reference is over the span it played itself. Its total is not comparable,
  because the first 78k frames are the reference.
- **Ideal showcase framing:** "a $15-25 autonomous agent produces a verified, from-scratch trace through two
  worlds at 1.75-2.8x reference length", plus a reusable recipe and a goal-directed task mode.
