"""status.py — one-glance progress of a run:  python status.py [runs/main] [N log lines]"""
import json
import os
import sys

run = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs", "main")
n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
st = json.load(open(os.path.join(run, "harness.json")))
movie = open(os.path.join(run, "movie.txt")).read().split()
frames = sum(int(t.split("*")[1]) if "*" in t else 1 for t in movie)
print(f"run {run}: spent ${st['spent']:.2f} (jev ${st['jev_spent']:.4f}), episode {st['episode']}, "
      f"turns {st['turns']}, movie {frames} frames ({frames / 60.0988 / 60:.1f} min) since {st['started']}")
print("tools:", ", ".join(f"{k}={v}" for k, v in sorted(st["tool_counts"].items(), key=lambda kv: -kv[1])))
for m in st["milestones"]:
    print(f"  {m['name']:<14} f{m['frame']:>7} (+{m['segment']:>6}) ${m['spent']:>6} "
          f"{'ok ' if m['verified'] else 'BAD'} {m['summary'][:90]}")
lines = open(os.path.join(run, "log.jsonl")).read().splitlines()
for l in lines[-n:]:
    d = json.loads(l)
    if "tool" in d:
        print(f"  {d['t'][11:]} → {d['tool']}: {' '.join(d['result'])[:150]!r}")
    elif "turn" in d:
        txt = " ".join(d.get("text") or [])[:150]
        calls = ",".join(c["name"] for c in d.get("calls", []))
        print(f"  {d['t'][11:]} t{d['turn']} ${d['cost']:.3f} ctx={d['ctx']} [{calls}] {txt!r}")
    else:
        print(f"  {d['t'][11:]} {d}")
