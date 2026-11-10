#!/usr/bin/env python
"""build.py — assemble the showcase page (showcase/index.html + showcase/clips/*.mp4) from the runs.

    .venv/bin/python showcase/build.py            # render missing clips, rebuild the page
    .venv/bin/python showcase/build.py --force    # re-render every clip

Clips are replays of verified movies (render.py), so the page is reproducible from runs/ + traces/. Text lives
in showcase/parts/body.html; numbers in tables come from showcase/data.json; this script only fills the tokens
@@CLIPS@@ (JSON for the players), @@ARCHIVE@@ (the exploration figure's data) and @@TABLE:name@@.
"""
import html
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TAS = os.path.dirname(HERE)
sys.path.insert(0, TAS)
import env as E  # noqa: E402

PY = os.path.join(TAS, ".venv", "bin", "python")
CLIPS = os.path.join(HERE, "clips")
os.makedirs(CLIPS, exist_ok=True)
FORCE = "--force" in sys.argv


def movie(run):
    p = run if os.path.isfile(run) else os.path.join(TAS, "runs", run, "movie.txt")
    return p, E.parse_spec(open(p).read())


def render(run, start, end, out, scale=2):
    """One clip of one movie; skipped when the file exists."""
    dst = os.path.join(CLIPS, out)
    if os.path.exists(dst) and not FORCE:
        return dst
    p, _ = movie(run)
    subprocess.run([PY, os.path.join(TAS, "render.py"), p, dst, "--from", str(start), "--to", str(end),
                    "--scale", str(scale)], check=True, cwd=TAS)
    return dst


def hstack(parts, out):
    """Side-by-side panels, each (run, start, end); shorter ones hold their last frame."""
    dst = os.path.join(CLIPS, out)
    if os.path.exists(dst) and not FORCE:
        return dst
    files, longest = [], 0
    for i, (run, start, end) in enumerate(parts):
        f = render(run, start, end, f"_{os.path.splitext(out)[0]}-{i}.mp4", scale=1)
        files.append(f)
        longest = max(longest, end - start)
    ins, filt = [], []
    for i, ((run, start, end), f) in enumerate(zip(parts, files)):
        ins += ["-i", f]
        pad = (longest - (end - start)) / 60.0988 + 1.0
        filt.append(f"[{i}:v]tpad=stop_mode=clone:stop_duration={pad:.3f}[v{i}]")
    filt.append("".join(f"[v{i}]" for i in range(len(parts))) + f"hstack=inputs={len(parts)}[o]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[o]",
                    "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "60.0988", dst], check=True)
    for f in files:
        os.unlink(f)
    return dst


def steps_of(run):
    p = os.path.join(TAS, "runs", run, "result.json")
    if not os.path.exists(p):
        return []
    r = json.load(open(p))
    chk = r.get("check") or {}
    return [{"name": n, "frame": f} for n, f in chk.get("steps", []) if f]


def main():
    data = json.load(open(os.path.join(HERE, "data.json")))
    clip_data, files = {}, {}
    for c in data["clips"]:
        if "panels" in c:
            dst = hstack([(p["run"], p["from"], p["to"]) for p in c["panels"]], c["id"] + ".mp4")
            clip_data[c["id"]] = {"start": 0, "fps": 60.0988}
        else:
            _, masks = movie(c["run"])
            end = c.get("to") or len(masks)
            dst = render(c["run"], c["from"], end, c["id"] + ".mp4", scale=c.get("scale", 2))
            steps = c.get("steps") or steps_of(c["run"])
            clip_data[c["id"]] = {"start": c["from"], "end": end, "fps": 60.0988,
                                  "spec": E.rle(masks[c["from"]:end]),
                                  "steps": [s for s in steps if c["from"] <= s["frame"] <= end]}
        files["clips/" + os.path.basename(dst)] = dst
        jpg = os.path.splitext(dst)[0] + ".jpg"
        if not os.path.exists(jpg) or FORCE:
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(c.get("poster_t", 5)), "-i", dst,
                            "-frames:v", "1", "-q:v", "3", jpg], check=True)
        files["clips/" + os.path.basename(jpg)] = jpg
        print(f"{c['id']}: {os.path.getsize(dst) / 1e6:.1f} MB")
    body = open(os.path.join(HERE, "parts", "body.html")).read()
    css = open(os.path.join(HERE, "parts", "style.css")).read()
    js = open(os.path.join(HERE, "parts", "player.js")).read()

    def chips(cid):
        return "".join(f'<li><button type="button" data-frame="{s["frame"]}">{html.escape(s["name"])}'
                       f'<span class="f">f{s["frame"]}</span></button></li>' for s in clip_data[cid].get("steps", []))

    out = body.replace("@@STYLE@@", css).replace("@@SCRIPT@@", js)
    out = out.replace("@@CLIPS@@", json.dumps(clip_data, separators=(",", ":")))
    arch = os.path.join(HERE, "archive.json")
    out = out.replace("@@ARCHIVE@@", open(arch).read() if os.path.exists(arch) else "{}")
    for cid in clip_data:
        out = out.replace(f"@@STEPS:{cid}@@", chips(cid))
        out = out.replace(f'src="clips/{cid}.mp4"', f'src="clips/{cid}.mp4" poster="clips/{cid}.jpg"')
    for fn in sorted(os.listdir(os.path.join(HERE, "parts"))):      # parts/frag-NAME.html fills @@NAME@@
        if fn.startswith("frag-") and fn.endswith(".html"):
            out = out.replace(f"@@{fn[5:-5]}@@", open(os.path.join(HERE, "parts", fn)).read())
    missing = sorted(set(t for t in __import__("re").findall(r"@@[A-Za-z0-9:_-]+@@", out)))
    if missing:
        print("UNFILLED TOKENS:", missing)
    open(os.path.join(HERE, "index.html"), "w").write(out)
    json.dump(files, open(os.path.join(HERE, "files.json"), "w"), indent=1)
    print(f"index.html: {len(out) / 1e3:.0f} KB; {len(files)} files, {sum(os.path.getsize(f) for f in files.values()) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
