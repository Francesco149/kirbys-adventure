# Kirby's Adventure — autonomous TAS agent

Claude Opus 5.5 (Claude API, Messages + tool use) plays Kirby's Adventure (USA Rev A) on a local, deterministic
emulator and builds a tool-assisted speedrun. It also evaluates, on the same segments, how much of the work can
be handed off from Claude to cheaper controllers:

- **manual**: Claude picks the inputs itself from screenshots and RAM
- **brute force**: beam/random search
- **Jev**: TypeSafe's decision model on OpenRouter, fed with RAM features
- **tiny models**: trained in a sandbox on CPU

The agent loop and every tool run on this machine. Only the conversation goes to the API, which is ordinary
client-side tool use under the API's commercial terms.

## Results (2026-11-09)

The distilled method is **[RECIPE.md](RECIPE.md)**: what to do in what order, per segment type, with measured
costs, and §0 has every run's numbers. Credit spent ≈ $154 (list prices).

| run | driver | what | result |
|---|---|---|---|
| `runs/main` | Opus 5.5 | open-ended research run, power-on to the ending | game complete (137,712 f, verified); worlds 1-5 are the replayed reference TAS; $100 |
| `runs/w12-opus` | Opus 5.5 | task: power-on to the W3 hub, no reference | passed: 51,207 f, $23.84 |
| `runs/w12-sonnet` | Sonnet 5.5 | the same task | passed: 69,751 f, $14.44 |
| `runs/w2-seq` | Opus 5.5 | ordered, constrained task from a library prefix | passed: 4,347 f, $1.50 |
| `runs/1-1-speed` | Opus 5.5 | speed task, 1-1 | passed: 3,159 f against the routine's 3,713 and the TAS's 2,625; $2.95 |
| `runs/w3-sonnet` | Sonnet 5.5 | continuation through World 3 from the w12-opus trace | passed: W4 hub, +36,357 f, $10.58 |

`runs/` is not in git (runtime state: logs, frames, savestates, lab work). The verified traces and the data behind
every table are in [traces/](traces/) (movie, room timeline, spend curve, splits, the agents' reports and the operator
messages they got). The handoff for review and the visual report is [SESSION-REPORT.md](SESSION-REPORT.md).

## Pieces

| file | what |
|---|---|
| `nes.py` | minimal headless libretro frontend (ctypes): frame step, savestates, system RAM + cart WRAM, framebuffer. Cores from nixpkgs (`core-mesen`, `core-fceumm` out-links). |
| `env.py` | the workbench: movie (per-frame inputs from power-on), input-spec language, checkpoints, rewind, named RAM vars + safe expressions, parallel beam/random search, `.fm2` export, replay verification |
| `jev.py` | Jev client (OpenRouter Decisions API; key from `~/.omp/agent/.env`) |
| `lab.py` | helper imported by the agent's own scripts in the sandbox (`python` tool) |
| `agent.py` | the Claude loop: tools, episodes (fresh context from notes at each split/handoff), server-side context editing, spend accounting with a hard stop, `finish`, idle stop |
| `task.py` | goal-directed runs: task files with ordered RAM steps and `forbid` invariants, checked on a replay from power-on |
| `prompts/` | `workbench.md` (shared tool brief) + `research.md` (open-ended research run) or `task.md` (task run) |
| `RECIPE.md` | **the distilled recipe** (v1, from `runs/main`); inlined into task runs' system prompt |
| `labkit/` | the previous run's proven lab helpers (room map, distance-field search, goal-game scan), on the sandbox's `PYTHONPATH` |
| `tasks/` | task files |
| `knowledge/` | game knowledge base (walkthrough, speedrun/TAS notes, mechanics, RAM map) + `ram-seed.json` |
| `status.py` | progress at a glance |
| `render.py` | replay a movie from power-on → MP4 |

Run state lives in `runs/<name>/`: `movie.txt` (the TAS, spec language, run-length), `kirby.fm2` (FCEUX export,
written at each split), `checkpoints/`, `ram.json` (the agent's named RAM vars), `notes.md` (its notebook),
`log.jsonl` (every turn: cost, text, thinking summary, tool calls/results), `episodes/`, `frames/` (every image
it saw), `lab/` (its scripts, data, models, background jobs).

## Run

```sh
uv venv --python 3.13 .venv && uv pip install --python .venv/bin/python anthropic numpy pillow
uv pip install --python .venv/bin/python --index-url https://download.pytorch.org/whl/cpu \
  --extra-index-url https://pypi.org/simple torch scikit-learn
nix build --inputs-from /opt/src/nix-lab nixpkgs#libretro.mesen --out-link core-mesen
nix build --inputs-from /opt/src/nix-lab nixpkgs#libretro.fceumm --out-link core-fceumm

# detached, memory-capped; the key is read from ~/claude-platform.txt by agent.py
systemd-run --user --unit kirby-tas -p MemoryMax=6G -p MemorySwapMax=0 \
  -p StandardOutput=append:$PWD/runs/main/agent.out -p StandardError=append:$PWD/runs/main/agent.out \
  --working-directory=$PWD .venv/bin/python -u agent.py --run $PWD/runs/main --budget 100 --core fceumm

# a task run (goal-directed trace), e.g. power-on -> World 2 hub without reference inputs
systemd-run --user --unit kirby-w1 -p MemoryMax=6G -p MemorySwapMax=0 \
  -p StandardOutput=append:$PWD/runs/w1-opus/agent.out -p StandardError=append:$PWD/runs/w1-opus/agent.out \
  --working-directory=$PWD .venv/bin/python -u agent.py --run $PWD/runs/w1-opus --budget 18 \
  --task tasks/w1-scratch.md --model claude-opus-5-5

python status.py runs/main          # progress
systemctl --user stop kirby-tas      # stop (SIGTERM: finishes the current turn's tools, exits)
python render.py runs/main/movie.txt kirby.mp4
```

`--budget` is cumulative for the run dir (spend is persisted in `runs/<name>/harness.json`); restart with a
higher number to continue. Spend is computed from `usage` at list prices (cache reads priced at 0.1x input, a
little conservative). Jev spend is tracked separately and the lab's Jev proxy has its own $3 cap.

## Task runs

A task file (`tasks/*.md`, format in `task.py`'s docstring and `RECIPE.md` §6) gives ordered steps as RAM
expressions, optional `forbid` invariants, a `start` (power-on, or `<run>:<checkpoint>` to begin from a verified
movie prefix) and `reference: allowed|forbidden` (forbidden hides `knowledge/movies/` and `knowledge/reference-*`
from the agent and its sandbox). The agent ends the run with `finish`, which replays the movie from power-on and
checks the steps in order; the result goes to `runs/<name>/result.json`. Notes are kept as a current-state
document under 16 KB (history goes to `journal.md`), and the run stops after 3 idle episodes in a row.
`--model` picks the driver (`claude-opus-5-5`, `claude-sonnet-5-5`); a run dir keeps its model.

## Sandbox (`python` tool)

`bwrap` with no network and no home directory. The code and the run are read-only, and only `runs/<name>/lab` is
writable. Inside a systemd scope with `MemoryMax=8G` and a timeout. Jev is reachable only through a Unix-socket
proxy in `lab/.jev.sock` that holds the key and enforces the lab budget.

## Determinism notes

- Power-on with zeroed battery RAM (`$6000-$7FFF`) and the core's RAM init pinned (`All 0s`). Replaying
  `movie.txt` on a fresh core reproduces the run, and `milestone` checks that at every split.
- FCEUmm is the canonical core (~2,200 fps per process headless, FCEUX lineage). Mesen (~400 fps) is more
  accurate but 5x slower for search. The reference TAS 3226M (FCEUX, PRG0) replays on our PRG1 ROM through
  world 4 on FCEUmm, but desyncs in world 2 on Mesen. A movie is only valid on the core it was made on; the
  harness records the run's core and refuses another. The first ~$4 of `runs/main` was on Mesen and is
  archived in `runs/main/archive-mesen/`.
- One emulator core per process. Libretro cores are global, and a second `nes.Core` in the same process (or a
  fork of one) silently steals the first one's callbacks; `nes.Core` refuses it. Use spawned processes.
- The `.fm2` export is for convenience: sync on FCEUX or BizHawk has not been verified.
