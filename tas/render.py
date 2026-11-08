"""render.py — replay a movie from power-on on a fresh core and encode it (with audio-free video) to MP4.
   python render.py runs/main/movie.txt out.mp4 [--from F] [--to F] [--scale 3]"""
import argparse
import subprocess
import sys

import env as E
import nes

ap = argparse.ArgumentParser()
ap.add_argument("movie")
ap.add_argument("out")
ap.add_argument("--from", dest="start", type=int, default=0)
ap.add_argument("--to", type=int, default=None)
ap.add_argument("--scale", type=int, default=3)
ap.add_argument("--core", default="mesen")
a = ap.parse_args()
masks = E.parse_spec(open(a.movie).read())
end = len(masks) if a.to is None else min(a.to, len(masks))
c = nes.Core(a.core)
w, h = 256 * a.scale, 240 * a.scale
ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                       "-r", "60.0988", "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", a.out],
                      stdin=subprocess.PIPE)
for i, m in enumerate(masks[:end]):
    show = i >= a.start
    c.step(m, render=show)
    if show and c.frame is not None:
        f = c.frame.repeat(a.scale, 0).repeat(a.scale, 1)
        ff.stdin.write(f.tobytes())
ff.stdin.close()
ff.wait()
print(f"wrote {a.out}: frames {a.start}-{end}", file=sys.stderr)
