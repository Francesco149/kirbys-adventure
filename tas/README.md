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

## Pieces

| file | what |
|---|---|
| `nes.py` | minimal headless libretro frontend (ctypes): frame step, savestates, system RAM + cart WRAM, framebuffer. Cores from nixpkgs (`core-mesen`, `core-fceumm` out-links). |
| `env.py` | the workbench: movie (per-frame inputs from power-on), input-spec language, checkpoints, rewind, named RAM vars + safe expressions, parallel beam/random search, `.fm2` export, replay verification |
| `jev.py` | Jev client (OpenRouter Decisions API; key from `~/.omp/agent/.env`) |
| `lab.py` | helper imported by the agent's own scripts in the sandbox (`python` tool) |
| `agent.py` | the Claude loop: tools, episodes (fresh context from notes at each split/handoff), server-side context editing, spend accounting with a hard stop |
| `prompts/system.md` | the agent's standing brief |
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
  --working-directory=$PWD .venv/bin/python -u agent.py --run runs/main --budget 60

python status.py runs/main          # progress
systemctl --user stop kirby-tas      # stop (SIGTERM: finishes the current turn's tools, exits)
python render.py runs/main/movie.txt kirby.mp4
```

`--budget` is cumulative for the run dir (spend is persisted in `runs/<name>/harness.json`); restart with a
higher number to continue. Spend is computed from `usage` at list prices (cache reads priced at 0.1x input, a
little conservative). Jev spend is tracked separately and the lab's Jev proxy has its own $3 cap.

## Sandbox (`python` tool)

`bwrap` with no network and no home directory. The code and the run are read-only, and only `runs/<name>/lab` is
writable. Inside a systemd scope with `MemoryMax=8G` and a timeout. Jev is reachable only through a Unix-socket
proxy in `lab/.jev.sock` that holds the key and enforces the lab budget.

## Determinism notes

- Power-on with zeroed battery RAM (`$6000-$7FFF`) and the core's RAM init pinned (`All 0s`). Replaying
  `movie.txt` on a fresh core reproduces the run, and `milestone` checks that at every split.
- Mesen is the canonical core (accurate; ~400 fps per process headless). FCEUmm (~2200 fps) is available, but
  a movie is only valid on the core it was made on.
- The `.fm2` export is for convenience: sync on FCEUX or BizHawk has not been verified.
