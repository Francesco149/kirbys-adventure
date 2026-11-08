"""Replay a reference .fm2 on our core and write per-room splits (frame of every room/world/stage change,
plus HP/lives/lag) as Markdown — a yardstick for the agent's own segments.
   python tools_refsplits.py knowledge/movies/3226M.fm2 knowledge/reference-3226M-splits.md [--core mesen]"""
import sys

import env as E
import nes

src, dst = sys.argv[1], sys.argv[2]
core = sys.argv[4] if len(sys.argv) > 4 and sys.argv[3] == "--core" else "fceumm"
masks = E.parse_fm2(src)
c = nes.Core(core)
m = c.mem
rows, last, lag, deaths = [], None, 0, 0
for i, mk in enumerate(masks):
    c0 = m[E.LAG_COUNTER]
    c.step(mk, render=False)
    lag += m[E.LAG_COUNTER] == c0
    key = (m[0x558], m[0x520], m[0x55E])
    if key != last:
        rows.append(f"| {i + 1} | {i + 1 - (rows and int(rows[-1].split('|')[1]) or 0)} | {lag} | {m[0x558]} | {m[0x520]} | "
                    f"{m[0x55E]} | {m[0x597]} | {m[0x599]} | {m[0x5E3]} |")
        last = key
    if m[0x56A] == 3:
        deaths += 1
    if m[0x599] == 0xFF:
        break
hdr = [f"# Reference splits: {src.split('/')[-1]} replayed on our ROM (USA Rev A / PRG1), core {core}", "",
       "Every change of (world $0558, stage $0520, room $055E). `since` = frames since the previous row; `lag` = "
       "cumulative lag/loading frames ($603D unchanged). The movie was made for PRG0 on FCEUX 2.2.2 and our ROM is "
       f"PRG1. Replay ended at f{i + 1} ({'game over' if m[0x599] == 0xFF else 'end of movie'}). Where it desyncs, "
       "rows stop being a valid reference: look for unexpected deaths (lives dropping), long `since` gaps, or a "
       "room that never changes. On Mesen this movie desyncs in world 2 (stuck in room 186 from f29755); on "
       "FCEUmm it clears worlds 1-4 and dies repeatedly in world 5 from ~f101600.", "",
       "| frame | since | lag | world | stage | room | hp | lives | ability |", "|---|---|---|---|---|---|---|---|---|"]
open(dst, "w").write("\n".join(hdr + rows) + "\n")
print(f"{len(rows)} rows, stopped at frame {i + 1}", file=sys.stderr)
