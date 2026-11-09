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
