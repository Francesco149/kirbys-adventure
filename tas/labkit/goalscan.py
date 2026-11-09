"""goalscan.scan(ck, room): from checkpoint `ck` (standing in `room`, e.g. the goal-game room 42), press
`button` for `hold` frames starting at frame k, for every k in `ks`, and measure the frames until the room
changes. Returns the 8 best (frames_to_change, k). The previous run found k between 54 and 58 for the goal
game depending on the stage, so always scan instead of reusing a k.  (18-35 s per scan.)"""
import lab


def scan(ck, room, ks=range(20, 120), button=None, hold=1, horizon=900):
    button = lab.A if button is None else button
    c = lab.load(ck)
    st = c.save()
    res = []
    for k in ks:
        c.load(st)
        n = None
        for i in range(horizon):
            c.step(button if k <= i < k + hold else 0)
            if i > k and lab.vars(c)["room"] != room:
                n = i + 1
                break
        res.append((n if n else 10**9, k))
    return sorted(res)[:8]
