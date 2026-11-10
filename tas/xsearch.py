"""xsearch.py — score-free exploration search (Go-Explore style) over a deterministic simulator with savestates.

The beam in env.py needs a hand-written score per room. This one needs only:
  goal  — expression; the search ends when it holds (the shortest arrival found is returned)
  cell  — tuple expression that buckets states, e.g. "(room, x//16, y//16)"; one state is kept per cell
  avoid — optional expression that prunes a branch

It keeps an archive {cell: fastest state seen}. Each iteration it picks cells (rarely-picked and freshly found ones
first), runs short random action sequences from them in parallel, and files every state it passes through under its
cell when it is new or got there in fewer frames. After the first goal hit it keeps going for `refine` seconds as
branch-and-bound: only cells reached earlier than the best goal time are expanded, so the path can only get shorter.

Nothing here is game-specific: the simulator is whatever env.py's workers hold (step, save, load, named variables).
"""
import math
import os
import random
import time

import env as E


class _Entry:
    __slots__ = ("state", "frames", "parent", "add", "chosen", "born", "score", "key")

    def __init__(self, state, frames, parent, add, born, score=0.0, key=None):
        self.state, self.frames, self.parent, self.add = state, frames, parent, add
        self.chosen, self.born, self.score, self.key = 0, born, score, key

    def masks(self):
        parts, e = [], self
        while e is not None:
            parts.append(e.add)
            e = e.parent
        out = []
        for p in reversed(parts):
            out.extend(p)
        return out


GOAL = "__goal__"


def togo_field(edges):
    """Frames-to-goal estimate per cell: Dijkstra backwards over the cell transitions the exploration saw."""
    import heapq
    back = {}
    for (a, b), w in edges.items():
        back.setdefault(b, []).append((a, w))
    dist = {GOAL: 0}
    pq = [(0, 0, GOAL)]
    n = 0
    while pq:
        d, _, b = heapq.heappop(pq)
        if d > dist.get(b, 1 << 30):
            continue
        for a, w in back.get(b, ()):
            if d + w < dist.get(a, 1 << 30):
                dist[a] = d + w
                n += 1
                heapq.heappush(pq, (d + w, n, a))
    dist.pop(GOAL, None)
    return dist


def _p_run(args):
    """Polish worker: from each state run every action; report goal hits, and (cell, fine key, state) otherwise."""
    states, acts, goal, avoid, cell, fine, vars_path, mtime = args
    W = E._W
    if mtime != W["mtime"]:
        W["vars"] = E.RamVars(vars_path)
        W["mtime"] = mtime
        W["exprs"] = {}
    c, V = W["core"], W["vars"]
    names = set(V.defs)

    def comp(e):
        if e not in W["exprs"]:
            W["exprs"][e] = E.compile_expr(e, names)
        return W["exprs"][e]

    g, a, k = comp(goal), (comp(avoid) if avoid else None), comp(cell)
    fk = comp(fine) if fine else None
    out = []
    for raw, frames in states:
        row = []
        for masks in acts:
            c.load((raw, frames, 0))
            res = None
            env = None
            for i, m in enumerate(masks):
                c.step(m, render=False)
                env = dict(V.read(c.mem, frames + i + 1), ram=c.mem, frame=frames + i + 1, lag=0, **E._FUNCS)
                if eval(g, {"__builtins__": {}}, env):
                    res = ("goal", i + 1)
                    break
                if a and eval(a, {"__builtins__": {}}, env):
                    res = ("pruned",)
                    break
            if res is None:
                key = eval(k, {"__builtins__": {}}, env)
                f2 = eval(fk, {"__builtins__": {}}, env) if fk else None
                res = ("ok", key, f2, c.save()[0])
            row.append(res)
        out.append(row)
    return out


def polish(env, actions, goal, cell, togo, avoid=None, fine=None, beam=192, max_depth=400, time_limit=120,
           workers=16, bound=None, log=None):
    """Beam search from the current position scored by a learned frames-to-goal field (`togo`, from explore).
    States in cells the exploration never connected to the goal are dropped. `bound`: give up past this many
    frames (the exploration's own path length). Returns the same shape as explore()."""
    acts = [E.parse_spec(a.strip().strip("\"'`").strip()) for a in actions]
    pool = env.pool(workers)
    vp = env.vars.path
    mt = os.path.getmtime(vp) if os.path.exists(vp) else 0
    t0 = time.time()
    f0 = env.frame
    states = [(env.core.save()[0], 0, [])]          # (raw, frames since root, action index list)
    explored = 0
    for depth in range(max_depth):
        if time.time() - t0 > time_limit:
            break
        per = max(1, -(-len(states) // workers))
        chunks = [states[i:i + per] for i in range(0, len(states), per)]
        res = pool.map(_p_run, [([(raw, f0 + f) for raw, f, _ in ch], acts, goal, avoid, cell, fine, vp, mt)
                                for ch in chunks])
        hits, cand = [], []
        for ch, rows in zip(chunks, res):
            for (raw, f, seq), row in zip(ch, rows):
                for ai, r in enumerate(row):
                    explored += len(acts[ai])
                    if r[0] == "goal":
                        hits.append((f + r[1], seq + [ai], r[1]))
                    elif r[0] == "ok" and r[1] in togo:
                        nf = f + len(acts[ai])
                        if bound is None or nf + togo[r[1]] * 0.5 < bound:
                            cand.append((nf + togo[r[1]], nf, r[1], r[2], r[3], seq + [ai]))
        if hits:
            tot, seq, last = min(hits, key=lambda h: h[0])
            masks = []
            for i in seq[:-1]:
                masks.extend(acts[i])
            masks.extend(acts[seq[-1]][:last])
            return {"found": True, "frames": len(masks), "masks": masks, "spec": E.rle(masks), "depth": depth + 1,
                    "explored_frames": explored, "seconds": round(time.time() - t0, 1)}
        cand.sort(key=lambda t: (t[0], t[1]))
        seen, states = set(), []
        for est, nf, key, f2, raw, seq in cand:
            dk = (key, f2)
            if dk in seen:
                continue
            seen.add(dk)
            states.append((raw, nf, seq))
            if len(states) >= beam:
                break
        if not states:
            break
        if log and depth % 10 == 9:
            log(f"depth {depth + 1}: best estimate {cand[0][0]} frames, {len(states)} states, {time.time() - t0:.0f}s")
    return {"found": False, "explored_frames": explored, "seconds": round(time.time() - t0, 1)}


def _x_run(args):
    raw, frames, seqs, goal, avoid, cell, score, vars_path, mtime, max_frames = args
    W = E._W
    if mtime != W["mtime"]:
        W["vars"] = E.RamVars(vars_path)
        W["mtime"] = mtime
        W["exprs"] = {}
    c, V = W["core"], W["vars"]
    names = set(V.defs)

    def comp(e):
        if e not in W["exprs"]:
            W["exprs"][e] = E.compile_expr(e, names)
        return W["exprs"][e]

    g = comp(goal) if goal else None
    a = comp(avoid) if avoid else None
    k = comp(cell)
    s = comp(score) if score else None
    c.load((raw, frames, 0))
    out, n = [], 0
    for masks in seqs:
        hit, pruned, env = None, False, None
        for i, m in enumerate(masks):
            c.step(m, render=False)
            n += 1
            env = dict(V.read(c.mem, frames + n), ram=c.mem, frame=frames + n, lag=0, **E._FUNCS)
            if g and eval(g, {"__builtins__": {}}, env):
                hit = i + 1
                break
            if a and eval(a, {"__builtins__": {}}, env):
                pruned = True
                break
        if hit is not None:
            out.append(("goal", hit))
            break
        if pruned:
            out.append(("pruned",))
            break
        key = eval(k, {"__builtins__": {}}, env)
        sc = float(eval(s, {"__builtins__": {}}, env)) if s else 0.0
        out.append(("ok", key, c.save()[0], sc))
        if max_frames and n >= max_frames:
            break
    return out


def explore(env, actions, goal, cell, avoid=None, score=None, time_limit=60, refine=10, batch=96, max_len=8,
            sticky=0.6, seed=0, workers=16, max_iters=100000, log=None, dump=None):
    """Returns {"found", "frames", "masks", "spec", "cells", "iters", "seconds", ...}. Without a goal hit, the
    result carries the archive's summary and (with `score`) the best-scoring cell's path."""
    names = set(env.vars.defs)
    for e in (goal, avoid, cell, score):
        if e:
            E.compile_expr(e, names)
    acts = [E.parse_spec(a.strip().strip("\"'`").strip()) for a in actions]
    if not acts or any(not a for a in acts):
        raise ValueError("actions must be non-empty input specs")
    pool = env.pool(workers)
    vp = env.vars.path
    mt = os.path.getmtime(vp) if os.path.exists(vp) else 0
    rng = random.Random(seed)
    root = env.core.save()
    v0 = dict(env.vars.read(env.core.mem, env.frame), ram=env.core.mem, frame=env.frame, lag=0, **E._FUNCS)
    root_key = eval(E.compile_expr(cell, names), {"__builtins__": {}}, v0)
    archive = {root_key: _Entry(root[0], 0, None, [], 0, key=root_key)}
    edges = {}                  # (cell a, cell b) -> fewest frames seen for that step; b may be GOAL
    best = None                 # (frames, entry, tail masks)
    best_t = None
    first_seen, goal_iters = {root_key: 0}, []
    t0 = time.time()
    it = explored = 0
    f0 = env.frame
    while it < max_iters:
        now = time.time()
        if best is None and now - t0 > time_limit:
            break
        if best is not None and now - best_t > refine:
            break
        it += 1
        keys = [k for k, e in archive.items() if best is None or e.frames < best[0] - 1]
        if not keys:
            break
        if score:
            order = sorted(keys, key=lambda k: archive[k].score)
            rank = {k: i / max(1, len(order) - 1) for i, k in enumerate(order)}
        ws = []
        for k in keys:
            e = archive[k]
            w = 1.0 / math.sqrt(1 + e.chosen)
            if it - e.born <= 2:
                w *= 3.0
            if score:
                w *= 0.25 + 3.0 * rank[k] ** 2
            ws.append(w)
        picks = rng.choices(keys, ws, k=batch)
        jobs = []
        for k in picks:
            e = archive[k]
            e.chosen += 1
            a = rng.randrange(len(acts))
            seq = []
            for _ in range(rng.randint(2, max_len)):
                if rng.random() > sticky:
                    a = rng.randrange(len(acts))
                seq.append(a)
            cap = (best[0] - e.frames) if best is not None else 0
            jobs.append((e, seq, cap))
        res = pool.map(_x_run, [(e.state, f0 + e.frames, [acts[i] for i in seq], goal, avoid, cell, score, vp, mt, cap)
                                for e, seq, cap in jobs], chunksize=max(1, len(jobs) // (workers * 2)))
        for (e, seq, _), steps in zip(jobs, res):
            tail = []
            at = e.key
            for i, st in enumerate(steps):
                if st[0] == "goal":
                    tot = e.frames + len(tail) + st[1]
                    explored += st[1]
                    if st[1] < edges.get((at, GOAL), 1 << 30):
                        edges[(at, GOAL)] = st[1]
                    if best is None or tot < best[0]:
                        best = (tot, e, tail + acts[seq[i]][:st[1]])
                        best_t = time.time()
                        goal_iters.append([it, tot])
                        if log:
                            log(f"goal in {tot} frames (iter {it}, {len(archive)} cells, {best_t - t0:.1f}s)")
                    break
                tail = tail + acts[seq[i]]
                explored += len(acts[seq[i]])
                if st[0] == "pruned":
                    break
                f = e.frames + len(tail)
                n_a = len(acts[seq[i]])
                if st[1] != at and n_a < edges.get((at, st[1]), 1 << 30):
                    edges[(at, st[1])] = n_a
                at = st[1]
                cur = archive.get(st[1])
                if cur is None:
                    first_seen[st[1]] = it
                if cur is None or f < cur.frames:
                    ne = _Entry(st[2], f, e, tail, it, st[3], key=st[1])
                    if cur is not None:
                        ne.chosen = cur.chosen // 2
                    archive[st[1]] = ne
                    tail_parent = ne
                    # later steps of this rollout hang off the new entry (keeps chains short)
                    e, tail = tail_parent, []
    out = {"cells": len(archive), "iters": it, "explored_frames": explored, "seconds": round(time.time() - t0, 1)}
    out["togo"] = togo_field(edges)
    if dump:                    # the archive as data (for figures): cell, iteration it was first seen, frames
        import json
        json.dump({"cells": [[list(k) if isinstance(k, tuple) else k, first_seen.get(k, e.born), e.frames]
                             for k, e in archive.items()],
                   "iters": it, "goal_iters": goal_iters, "best": best[0] if best else None}, open(dump, "w"))
    if best is not None:
        masks = best[1].masks() + best[2]
        out.update(found=True, frames=len(masks), masks=masks, spec=E.rle(masks))
        return out
    out["found"] = False
    if score:
        k = max(archive, key=lambda k: archive[k].score)
        masks = archive[k].masks()
        out.update(best_score=archive[k].score, best_cell=repr(k), masks=masks, spec=E.rle(masks))
    else:
        far = sorted(archive.items(), key=lambda kv: -kv[1].born)[:8]
        out["newest_cells"] = [repr(k) for k, _ in far]
    return out


# ------------------------------------------------------------------------------------------- simplify
def _s_run(args):
    """Evaluate candidates: each is (state, frames at that state, masks, index of the next goal). `goals` is an
    ordered list; returns the 1-based frame (within its masks) where the LAST goal first holds after the earlier
    ones held in order, or None (pruned by `avoid`, or never)."""
    cands, goals, avoid, vars_path, mtime = args
    W = E._W
    if mtime != W["mtime"]:
        W["vars"] = E.RamVars(vars_path)
        W["mtime"] = mtime
        W["exprs"] = {}
    c, V = W["core"], W["vars"]
    names = set(V.defs)

    def comp(e):
        if e not in W["exprs"]:
            W["exprs"][e] = E.compile_expr(e, names)
        return W["exprs"][e]

    gs, a = [comp(g) for g in goals], (comp(avoid) if avoid else None)
    out = []
    for raw, frames, masks, gi in cands:
        c.load((raw, frames, 0))
        hit = None
        for i, m in enumerate(masks):
            c.step(m, render=False)
            env = dict(V.read(c.mem, frames + i + 1), ram=c.mem, frame=frames + i + 1, lag=0, **E._FUNCS)
            if a and eval(a, {"__builtins__": {}}, env):
                break
            if eval(gs[gi], {"__builtins__": {}}, env):
                gi += 1
                if gi == len(gs):
                    hit = i + 1
                    break
        out.append(hit)
    return out


def _runs(masks):
    out = []
    for m in masks:
        if out and out[-1][0] == m:
            out[-1][1] += 1
        else:
            out.append([m, 1])
    return out


def simplify(env, masks, goal, avoid=None, mode="frames", slack=0.0, time_limit=120, workers=16, log=None):
    """Delta-debug a path. `masks` reaches `goal` (one expression, or an ordered list of them: a task's remaining
    steps) from the current position; edits (delete a hold, shorten it,
    merge it into the previous hold) are kept when the goal is still reached and the path got better.
    mode "frames": fewer frames first, then fewer input changes (a speed pass).
    mode "smooth": fewer input changes first, within (1 + slack) x the original frame count (a demo/test pass).
    Returns {"masks", "spec", "frames", "changes", "frames_before", "changes_before", "rounds", "seconds"}."""
    pool = env.pool(workers)
    vp = env.vars.path
    mt = os.path.getmtime(vp) if os.path.exists(vp) else 0
    root = env.core.save()
    f0 = env.frame
    t0 = time.time()
    goals = [goal] if isinstance(goal, str) else list(goal)
    names = set(env.vars.defs)
    gcode = [E.compile_expr(g, names) for g in goals]
    first = pool.submit(_s_run, ([(root[0], f0, masks, 0)], goals, avoid, vp, mt)).result()[0]
    if first is None:
        raise ValueError("the given path does not reach the goal from here")
    masks = list(masks[:first])
    budget = int(len(masks) * (1 + slack)) if mode == "smooth" else None
    before = (len(masks), len(_runs(masks)))

    def key(frames, nruns):
        return (frames, nruns) if mode == "frames" else (nruns, frames)

    cur = key(*before)
    rounds = accepted = 0
    win = max(2, workers // 3)

    def run_starts(runs, upto):
        """(savestate, frames into the path, index of the next unmet goal) at the start of each hold."""
        env.core.load(root)
        starts, pos, gi = [], 0, 0
        for m, n in runs[:upto + 1]:
            starts.append((env.core.save()[0], pos, gi))
            for _ in range(n):
                env.core.step(m, render=False)
                pos += 1
                if gi < len(gcode) - 1:
                    ev = dict(env.vars.read(env.core.mem, f0 + pos), ram=env.core.mem, frame=f0 + pos, lag=0,
                              **E._FUNCS)
                    if eval(gcode[gi], {"__builtins__": {}}, ev):
                        gi += 1
        return starts

    changed = True
    while changed and time.time() - t0 < time_limit:
        changed = False
        rounds += 1
        runs = _runs(masks)
        pos = len(runs) - 1
        starts = run_starts(runs, pos)
        # sweep from the end of the path to its start: an edit at hold i leaves the holds before it untouched
        while pos >= 0 and time.time() - t0 < time_limit:
            cands = []
            for i in range(pos, max(-1, pos - win), -1):
                m, n = runs[i]
                tail = runs[i + 1:]
                cands.append((i, tail, "del"))
                for k in sorted({n // 2, n - 1, n - 2, n - 4}):
                    if 0 < k < n:
                        cands.append((i, [[m, k]] + tail, "cut"))
                if i > 0 and runs[i - 1][0] != m:
                    cands.append((i, [[runs[i - 1][0], n]] + tail, "merge"))
                if i + 1 < len(runs) and runs[i + 1][0] != m:
                    cands.append((i, [[runs[i + 1][0], n]] + tail, "merge"))
            jobs = []
            for i, tail, _ in cands:
                tm = [m for m, n in tail for _ in range(n)]
                if mode == "smooth" and tm:
                    room = budget - starts[i][1] - len(tm)
                    if room > 0:
                        tm = tm + [tm[-1]] * room      # keep holding the last input up to the frame budget
                jobs.append((starts[i][0], f0 + starts[i][1], tm, starts[i][2]))
            per = max(1, -(-len(jobs) // workers))
            chunks = [jobs[j:j + per] for j in range(0, len(jobs), per)]
            res = [h for part in pool.map(_s_run, [(ch, goals, avoid, vp, mt) for ch in chunks]) for h in part]
            best = None
            for (i, tail, tag), job, hit in zip(cands, jobs, res):
                if hit is None:
                    continue
                new = [m for m, n in runs[:i] for _ in range(n)] + job[2][:hit]
                if budget and len(new) > budget:
                    continue
                k = key(len(new), len(_runs(new)))
                if k < cur and (best is None or k < best[0]):
                    best = (k, new, tag, i)
            if best is None:
                pos -= win
                continue
            cur, masks = best[0], best[1]
            accepted += 1
            changed = True
            runs = _runs(masks)
            pos = min(best[3], len(runs) - 1)
            starts = run_starts(runs, pos)
            if log and accepted % 10 == 0:
                log(f"{accepted} edits: {len(masks)} frames, {len(runs)} holds ({time.time() - t0:.0f}s)")
    env.core.load(root)
    return {"masks": masks, "spec": E.rle(masks), "frames": len(masks), "changes": len(_runs(masks)),
            "frames_before": before[0], "changes_before": before[1], "rounds": rounds, "edits": accepted,
            "seconds": round(time.time() - t0, 1)}
