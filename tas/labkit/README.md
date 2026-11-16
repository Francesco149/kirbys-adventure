# labkit — helpers promoted from runs/main/lab

Mounted read-only and on `PYTHONPATH` in every run's `python` sandbox. Written by the agent in runs/main and
copied here unchanged (except `goalscan.py`, generalised from its per-stage scans). Measured results are in
[../RECIPE.md](../RECIPE.md).

| file | what |
|---|---|
| `roominfo.py` | ASCII collision map + legend of every attribute value + door pixel coordinates (`python -c` or `roominfo.info(lab.load(ck))`) |
| `flowsearch.py` | collision grid reader, Dijkstra distance field, beam search on it (static field) |
| `flow2.py` | the same beam, field recomputed per tilemap signature (breakable blocks); `solids` per tileset |
| `runflow2.py` | CLI: `ACTS='R*8|UR*8|…' SOLIDS='0d,60' python runflow2.py <ck> <door_x> <door_y> <room> <prev_room> <out_name> [beam] [depth]` |
| `goalscan.py` | best press frame for the goal game or a cutscene |

Added in coverage batch 11 (2026-11-16), written by its subagents; run with `../.venv/bin/python` from `tas/`:

| file | what |
|---|---|
| `hits.py` | `hits.py RUN FROM_FRAME BB:AAAA ...`: replays a run's tail on the instrumented core and prints, per address, how often it ran and the first frame: seconds instead of a `kd gain` |
| `rbrute.py` | `SEED=n rbrute.py RUN CKPT "BB:AAAA ..." "AVOID" N LEN "tok1\|tok2\|..." [prefix]`: random input sequences from a checkpoint until the target addresses run; prints the shortest hit per target (found most of batch 11's boss movies) |
| `roomtables.py` | rooms read straight from the ROM: block/collision maps (`show`), object placements per room (`objs`, `placements`, `scan`), kind -> type tables, water and floor segments |
