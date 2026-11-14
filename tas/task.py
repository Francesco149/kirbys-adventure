"""task.py — goal-directed runs: a task file names ordered RAM goals; a replay from power-on checks them.

A task file is Markdown with a small header:

    ---
    name: w1-from-scratch
    start: power-on                 # or a library prefix: <run>:<checkpoint> (main:ms-6-boss) or <run>@<frame> (main@11531)
    reference: forbidden            # forbidden: reference movies and their splits are hidden from the agent
    steps:
      - 1-1 entered: world == 0 and room == 43
      - World 2 hub: world == 1 and room == 1
    forbid:                         # optional; must never hold once step 1 has held
      - lost a life: lives < 4
    ---
    Free text for the agent: what the trace is for, constraints, what to report.

Each step is an expression over the named RAM vars (same language as search goals). A trace satisfies the task
when, replayed from power-on on a fresh core, every step becomes true in order: step i is checked from the
frame after step i-1 first held. `forbid` expressions must stay false on every frame from step 1 on (at
power-on most vars read 0, so they are not checked before the first step). The agent calls `finish` and the
harness runs this check.
"""
import os
import re

import env as E
import nes

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    txt = open(path).read()
    m = re.match(r"---\n(.*?)\n---\n?(.*)", txt, re.S)
    if not m:
        raise ValueError(f"{path}: needs a --- header ---")
    head, body = m.group(1), m.group(2).strip()
    t = {"name": os.path.splitext(os.path.basename(path))[0], "start": "power-on", "reference": "allowed",
         "steps": [], "forbid": [], "text": body}
    in_list = None
    for line in head.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        s = re.match(r"\s+-\s*(.+?):\s+(.+?)\s*(?:#.*)?$", line)   # name, expr: a colon inside the name (23:A658) is kept, the separator is ": "
        if in_list and s:
            t[in_list].append((s.group(1).strip(), s.group(2).strip()))
            continue
        k = re.match(r"(\w+):\s*(.*?)\s*(?:#.*)?$", line)
        if not k:
            raise ValueError(f"{path}: can't read header line {line!r}")
        in_list = k.group(1) if k.group(1) in ("steps", "forbid") else None
        if not in_list:
            t[k.group(1)] = k.group(2)
    if not t["steps"]:
        raise ValueError(f"{path}: no steps")
    if t["reference"] not in ("allowed", "forbidden"):
        raise ValueError("reference: allowed | forbidden")
    return t


def compile_steps(steps, names):
    return [(n, E.compile_expr(e, names)) for n, e in steps]


def _ev(code, env):
    try:
        return bool(eval(code, {"__builtins__": {}}, env))
    except Exception:  # noqa: BLE001 — a var reading None etc. counts as false
        return False


def check_job(core_name, vars_path, masks, steps, forbid=(), after=0):
    """Run in a fresh (spawned) process. Returns {"steps": [(name, first frame it held in order, or None)],
    "violations": [(forbid name, first frame it held)], "ok": bool}. `after`: frames up to this one are replayed
    but not judged (the task's start prefix: a step must be earned by the trace's own part, not by the prefix)."""
    c = nes.Core(core_name)
    rv = E.RamVars(vars_path)
    code = compile_steps(steps, set(rv.defs))
    fcode = compile_steps(forbid, set(rv.defs))
    out = [(n, None) for n, _ in steps]
    bad = {}
    i = 0
    for f, m in enumerate(masks, 1):
        c.step(m, render=False)
        if f <= after or (i >= len(code) and not fcode):
            continue
        env = dict(rv.read(c.mem, f), ram=c.mem, frame=f, **E._FUNCS)
        if i < len(code) and _ev(code[i][1], env):
            out[i] = (code[i][0], f)
            i += 1
        if i > 0:
            for n, fc in fcode:
                if n not in bad and _ev(fc, env):
                    bad[n] = f
    return {"steps": out, "violations": sorted(bad.items(), key=lambda kv: kv[1]),
            "ok": i == len(code) and not bad}


def check_async(env, task):
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor
    ex = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("spawn"))
    fut = ex.submit(check_job, env.core_name, env.vars.path, list(env.movie), task["steps"], task["forbid"])
    ex.shutdown(wait=False)
    return fut


def describe(task, result=None):
    rows = []
    for i, (n, e) in enumerate(task["steps"]):
        st = ""
        if result is not None:
            f = result["steps"][i][1]
            st = f" — held at frame {f}" if f else " — NOT reached (in order)"
        rows.append(f"{i + 1}. {n}: `{e}`{st}")
    for n, e in task["forbid"]:
        st = ""
        if result is not None:
            hit = dict(result["violations"]).get(n)
            st = f" — VIOLATED at frame {hit}" if hit else " — never held"
        rows.append(f"forbid {n}: `{e}`{st}")
    return "\n".join(rows)
