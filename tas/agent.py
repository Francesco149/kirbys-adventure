"""agent.py — Claude (Opus 5.5, Messages API) plays Kirby's Adventure on the local workbench and builds a TAS.

The loop runs here; every tool executes on this machine (emulator, search pool, Jev calls). Claude only sees
what the tools return. Episodes: each starts a fresh conversation from the run's notes + status (simple
compaction); within an episode the history is append-only and server-side context editing clears old
tool results. Spend is accounted from `usage` at list prices and is a hard stop.

  python agent.py --run runs/main --budget 80
"""
import argparse
import base64
import datetime as dt
import json
import os
import re
import shutil
import signal
import socketserver
import subprocess
import sys
import threading
import time
import traceback

import anthropic

import env as E
import jev
import nes
import task as TK

HERE = os.path.dirname(os.path.abspath(__file__))
# list prices, $/MTok; cache writes are the 5-minute ones
PRICES = {"claude-opus-5-5": {"input": 4.0, "cache_write": 5.0, "cache_read": 0.40, "output": 20.0},
          "claude-sonnet-5-5": {"input": 2.0, "cache_write": 2.5, "cache_read": 0.20, "output": 10.0}}
BETAS = ["context-management-2025-06-27", "server-side-fallback-2026-07-01"]
CONTEXT_MGMT = {"edits": [{"type": "clear_tool_uses_20250919",
                           "trigger": {"type": "input_tokens", "value": 90000},
                           "keep": {"type": "tool_uses", "value": 10},
                           "clear_at_least": {"type": "input_tokens", "value": 20000}}]}
# ask for a handoff once context passes max(EPISODE_TOKENS, start of episode + EPISODE_GROWTH): turns cost ~2x
# past ~60K (clears rewrite the cache), and a fixed threshold below a fat kickoff hands off every episode at once
EPISODE_TOKENS = 70_000
EPISODE_GROWTH = 35_000
EPISODE_TURNS = 250
NOTES_MAX = 16_000            # bytes; notes are inlined at every episode start
IDLE_EPISODES = 3             # stop the run after this many episodes in a row without work tools
WORK_TOOLS = {"play", "look", "rewind", "checkpoint", "ram", "search", "jev", "python", "jobs", "milestone"}

STOP = False


def _sig(*_):
    global STOP
    STOP = True


# handlers are installed in main() only: spawned workers re-import this module as __mp_main__, and a
# module-level handler made them ignore SIGTERM (so terminate() could not clean them up)


def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _truthy(v):
    return v is not None and not isinstance(v, str) and bool(v)


# ------------------------------------------------------------------------------------------- tools
def T(name, desc, props, required=()):
    return {"name": name, "description": desc,
            "input_schema": {"type": "object", "properties": props, "required": list(required)}}


TOOLS = [
    T("play", "Append inputs to the movie and run them. Returns the status line (frame, named RAM vars), RAM "
              "events that happened (vars flagged event=true changing), and a picture: view='end' (final frame, "
              "2x), 'strip' (contact sheet of every `every`-th frame, labelled with frame numbers), or 'none'. "
              "Inputs use the spec language: tokens like R*20 RA*8 .*30 T, groups like (B*2 .*2)x10.",
      {"inputs": {"type": "string"}, "view": {"type": "string", "enum": ["end", "strip", "none"]},
       "every": {"type": "integer", "description": "strip spacing in frames (default: inputs length / 8)"},
       "inputs_file": {"type": "string", "description": "instead of inputs: a spec file your python lab wrote "
                                                         "with lab.save_spec(name, …) (give the name)"}}),
    T("look", "Show the current frame. scale 1-4 (default 2); optional crop [x0,y0,x1,y1] in NES pixels (256x240).",
      {"scale": {"type": "integer"}, "crop": {"type": "array", "items": {"type": "integer"}}}),
    T("rewind", "Move back in the movie (truncates it): by `frames`, or to absolute `to_frame`.",
      {"frames": {"type": "integer"}, "to_frame": {"type": "integer"}}),
    T("checkpoint", "save: store the current position (movie prefix + state) under a name. load: switch to that "
                    "checkpoint's movie (replaces the current movie — save first if you want to keep it). "
                    "list: all checkpoints with frame and status.",
      {"action": {"type": "string", "enum": ["save", "load", "list"]}, "name": {"type": "string"},
       "note": {"type": "string"}}, ["action"]),
    T("ram", "RAM workbench: NES system RAM $0000-$07FF and cartridge WRAM $6000-$7FFF (this game keeps state in "
             "both). status: named vars now. read: hex dump (addr, length<=256). mark: remember RAM now; diff: "
             "bytes changed since mark (both regions, up to 96 rows; optional addr+length limits the range) — use "
             "mark → play → diff to find addresses. define: name a var (addr,size 1|2,signed) or a "
             "derived var (expr over other vars, e.g. 'x_page*256+x_pix'); event=true makes play report its changes. "
             "remove: delete a var. list: all definitions. objects: the 18 object slots now (class, x, y and "
             "the $61CA+slot value, which holds boss HP) — use it to find bosses, Warp Stars and pickups. "
             "Addresses are hex ('$61CA', '0x61CA' or '61CA').",
      {"action": {"type": "string", "enum": ["status", "read", "mark", "diff", "define", "remove", "list",
                                             "objects"]},
       "addr": {"type": "string"}, "length": {"type": "integer"}, "name": {"type": "string"},
       "size": {"type": "integer"}, "signed": {"type": "boolean"}, "expr": {"type": "string"},
       "desc": {"type": "string"}, "event": {"type": "boolean"}}, ["action"]),
    T("search", "Local input search (free, parallel over 16 emulator processes). From the current position, tries "
                "sequences of macro-actions (input specs) up to max_depth long. mode 'beam' (default): keeps the "
                "`beam` best states per depth (RAM-deduplicated; beam up to 4096 ≈ exhaustive for short windows). "
                "mode 'random': BasicBot-style, `samples` random sequences of max_depth actions. goal: expression; "
                "returns the sequence reaching it in the fewest frames. score: expression maximised otherwise "
                "(e.g. 'x'). avoid: expression that prunes a branch (e.g. 'hp < 6'). Expressions use named RAM vars, "
                "ram[addr], frame, + - * / // % & | ^ << >> comparisons and/or/not, min max abs s8 s16. "
                "apply=true appends the result to the movie.",
      {"actions": {"type": "array", "items": {"type": "string"}}, "goal": {"type": "string"},
       "score": {"type": "string"}, "avoid": {"type": "string"}, "max_depth": {"type": "integer"},
       "beam": {"type": "integer"}, "mode": {"type": "string", "enum": ["beam", "random"]},
       "samples": {"type": "integer"}, "seed": {"type": "integer"},
       "time_limit": {"type": "integer", "description": "seconds, default 120"},
       "apply": {"type": "boolean"}}, ["actions"]),
    T("jev", "Delegate low-level control to Jev (TypeSafe's fast decision model on OpenRouter: ~0.4 s and "
             "~$0.00002 per decision; weak vision, so you'll likely do better feeding it game state as text). Each "
             "decision Jev sees `instructions`, the `features` you define (name → RAM expression, e.g. distance to "
             "the nearest enemy, tile ahead, vertical speed), the status line (show_status), its last choices, and "
             "the screen if image=true; it picks one of `options` (name → {input, desc}) and that input is played. "
             "Stops after max_decisions, or when stop_when / abort_when (expressions) become true; abort_when also "
             "rewinds the last option. Returns the choice trace with probabilities and the final picture.",
      {"instructions": {"type": "string"},
       "options": {"type": "object", "additionalProperties": {
           "type": "object", "properties": {"input": {"type": "string"}, "desc": {"type": "string"}},
           "required": ["input", "desc"]}},
       "features": {"type": "object", "additionalProperties": {"type": "string"}},
       "show_status": {"type": "boolean"}, "history": {"type": "integer"},
       "max_decisions": {"type": "integer"}, "stop_when": {"type": "string"}, "abort_when": {"type": "string"},
       "image": {"type": "boolean"}}, ["instructions", "options"]),
    T("python", "Run a Python script in a sandbox on this machine (no network; numpy, pillow, torch CPU, "
                "scikit-learn; ~16 cores; 8 GB RAM cap). `import lab` gives emulator cores at any checkpoint, "
                "named RAM vars, the spec language, lab.save_spec() for results you then `play` with inputs_file, "
                "lab.show() for pictures, and lab.jev() for Jev decisions (own small budget) — see lab.py's "
                "docstring (print(lab.__doc__)). The cwd persists across calls "
                "(keep your scripts, data and models there). Use it for your own brute-force bots, RL / behaviour "
                "cloning of tiny models on RAM features, Jev prompt evaluations at scale, data analysis. "
                "background=true starts a long job (see `jobs`). show: up to 4 PNG names in out/ to look at.",
      {"code": {"type": "string"}, "timeout": {"type": "integer", "description": "seconds, default 300, max 1800"},
       "background": {"type": "boolean"}, "show": {"type": "array", "items": {"type": "string"}}}, ["code"]),
    T("jobs", "Background python jobs: list | tail (id, lines) | kill (id).",
      {"action": {"type": "string", "enum": ["list", "tail", "kill"]}, "id": {"type": "string"},
       "lines": {"type": "integer"}}, ["action"]),
    T("notes", "Your persistent documents (survive episodes; with the knowledge base they are all a future episode "
               "knows). doc='notes' (default): the current state, shown in full at every episode start — verified "
               "RAM, route & door coordinates, what each checkpoint is, open problems, next step; rewrite it "
               "(write) to keep it under 16 KB. doc='recipe': the deliverable (see the brief). doc='journal': "
               "append-only history, not shown at episode start. "
               "read | append (text) | write (replace the whole doc with text; keep it organized).",
      {"action": {"type": "string", "enum": ["read", "append", "write"]}, "text": {"type": "string"},
       "doc": {"type": "string", "enum": ["notes", "recipe", "journal"]}}, ["action"]),
    T("knowledge", "The game knowledge base (walkthrough, speedrun/TAS notes, mechanics, RAM map). "
                   "list | read (file, optional section heading substring) | grep (query regex).",
      {"action": {"type": "string", "enum": ["list", "read", "grep"]}, "file": {"type": "string"},
       "section": {"type": "string"}, "query": {"type": "string"}}, ["action"]),
    T("milestone", "Record a split when you finish a stage/boss/world: saves checkpoint ms-<name>, verifies the "
                   "movie replays from power-on, exports the FCEUX .fm2, logs the split. Ends this episode after "
                   "this turn (the next one starts from your notes), so update notes first.",
      {"name": {"type": "string"}, "summary": {"type": "string"}}, ["name", "summary"]),
    T("handoff", "End this episode now (e.g. context is long or you are stuck in a loop). Update notes first; "
                 "summary goes to the next episode.",
      {"summary": {"type": "string"}}, ["summary"]),
    T("finish", "End the whole run. In a task run this first replays your movie from power-on and checks the "
                "task's steps in order (and its forbid list); the run ends only if they pass, otherwise you get "
                "the first failing step back and continue. Update notes and the recipe/report first.",
      {"summary": {"type": "string"}}, ["summary"]),
]


class Harness:
    def __init__(self, run_dir, budget, core="mesen", effort="medium", model="claude-opus-5-5", task_path=None):
        run_dir = os.path.abspath(run_dir)
        self.run_dir = run_dir
        if model not in PRICES:
            raise SystemExit(f"no prices for {model}; have {sorted(PRICES)}")
        self.model = model
        self.price = PRICES[model]
        os.makedirs(os.path.join(run_dir, "lab"), exist_ok=True)
        tp = os.path.join(run_dir, "task.md")
        if task_path and not os.path.exists(tp):
            shutil.copy(task_path, tp)
        self.task = TK.load(tp) if os.path.exists(tp) else None
        if self.task and self.task["start"] != "power-on" and not os.path.exists(os.path.join(run_dir, "movie.txt")):
            # library prefix: <run>:<checkpoint> or <run>@<frame>; Env replays it from power-on below
            start = self.task["start"]
            if "@" in start:
                src_run, n = start.split("@", 1)
                masks = E.parse_spec(open(os.path.join(HERE, "runs", src_run, "movie.txt")).read())[:int(n)]
                open(os.path.join(run_dir, "movie.txt"), "w").write(E.rle(masks) + "\n")
            else:
                src_run, ck = start.split(":", 1)
                shutil.copy(os.path.join(HERE, "runs", src_run, "checkpoints", ck + ".movie"),
                            os.path.join(run_dir, "movie.txt"))
        os.makedirs(os.path.join(run_dir, "frames"), exist_ok=True)
        os.makedirs(os.path.join(run_dir, "episodes"), exist_ok=True)
        seed = os.path.join(HERE, "knowledge", "ram-seed.json")
        rp = os.path.join(run_dir, "ram.json")
        if not os.path.exists(rp) and os.path.exists(seed):
            open(rp, "w").write(open(seed).read())
        sp = os.path.join(run_dir, "harness.json")
        prev_core = json.load(open(sp)).get("core") if os.path.exists(sp) else None
        if prev_core and prev_core != core:
            raise SystemExit(f"run {run_dir} is on core {prev_core}; movies don't transfer between cores "
                             f"(archive the movie/checkpoints to switch)")
        self.env = E.Env(run_dir, core)
        self.budget = budget
        self.effort = effort
        self.client = anthropic.Anthropic(max_retries=6)
        self.state_path = os.path.join(run_dir, "harness.json")
        self.st = json.load(open(self.state_path)) if os.path.exists(self.state_path) else {
            "spent": 0.0, "jev_spent": 0.0, "episode": 0, "turns": 0, "milestones": [], "tool_counts": {},
            "started": now(), "core": core}
        prev_model = self.st.setdefault("model", model)
        if prev_model != model:
            raise SystemExit(f"run {run_dir} was driven by {prev_model}; start a new run dir for {model}")
        self.mark = None
        self.notes_path = os.path.join(run_dir, "notes.md")
        self.recipe_path = os.path.join(run_dir, "recipe.md")
        if not os.path.exists(self.notes_path):
            open(self.notes_path, "w").write("# Notes\n\n(empty — first episode)\n")
        self.log_f = open(os.path.join(run_dir, "log.jsonl"), "a")
        self.end_episode = None
        self.st.setdefault("jev_lab_spent", 0.0)
        self.jev_lab_budget = 3.0
        self.jev_lock = threading.Lock()
        self.jobs = {}
        self.verifying = []
        # milestones whose background verify was lost (reload/crash while it ran): re-check them from the
        # checkpoint in a subprocess (verify_ck.py replays its movie and compares with its savestate)
        self.reverify = []
        for i, m in enumerate(self.st["milestones"]):
            if m.get("verified") is None and "ms-" + m["name"] in self.env.cks:
                p = subprocess.Popen([sys.executable, os.path.join(HERE, "verify_ck.py"), run_dir, "ms-" + m["name"]],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                     env=dict(os.environ, KIRBY_CORE=core), cwd=HERE)
                self.reverify.append((i, p))
        self.finished = None
        self.journal_path = os.path.join(run_dir, "journal.md")
        self.start_jev_proxy()

    def save_state(self):
        json.dump(self.st, open(self.state_path, "w"), indent=1)

    def log(self, **kw):
        kw["t"] = now()
        self.log_f.write(json.dumps(kw, default=str) + "\n")
        self.log_f.flush()

    def footer(self):
        spent_here = self.st["spent"] - self.st.get("archived_mesen", {}).get("spent_at_archive", 0)
        pace = self.env.frame / spent_here if spent_here > 0 else 0
        return (f"[frame {self.env.frame} ({self.env.frame / 60.0988:.1f}s) | spent ${self.st['spent']:.2f} of "
                f"${self.budget:.2f} | pace {pace:.0f} frames/$ (target ≥3000) | jev ${self.st['jev_spent']:.4f} | "
                f"episode {self.st['episode']} turn {self.st['turns']}]")

    def inbox(self):
        """Operator channel: text in <run>/inbox.md is delivered once, appended after the next tool results."""
        p = os.path.join(self.run_dir, "inbox.md")
        if not os.path.exists(p):
            return None
        txt = open(p).read().strip()
        os.replace(p, os.path.join(self.run_dir, f"inbox.{dt.datetime.now():%Y%m%d-%H%M%S}.done"))
        if not txt:
            return None
        self.log(event="inbox", text=txt)
        return {"type": "text", "text": f"Message from the owner (operator inbox): {txt}"}

    def img(self, data):
        n = self.st["turns"]
        p = os.path.join(self.run_dir, "frames", f"{n:06d}-{self.env.frame:07d}.png")
        open(p, "wb").write(data)
        return {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                            "data": base64.b64encode(data).decode()}}

    def frame_png(self, scale=2, crop=None):
        f = self.env.core.frame
        if f is None:
            import numpy as np
            f = np.zeros((240, 256, 3), dtype="uint8")
        return E.png(f, scale, tuple(crop) if crop else None)

    # ---- tool implementations: return list of content blocks ----
    def t_play(self, inputs=None, view="end", every=None, inputs_file=None):
        if inputs_file:
            name = re.sub(r"\.txt$", "", os.path.basename(inputs_file))
            inputs = open(os.path.join(self.run_dir, "lab", "out", name + ".txt")).read()
        if not inputs:
            raise ValueError("give inputs or inputs_file")
        masks = E.parse_spec(inputs)
        if not masks:
            raise ValueError("empty inputs")
        if len(masks) > 3600:
            raise ValueError("at most 3600 frames per play call")
        if view == "strip":
            every = max(1, int(every or max(1, len(masks) // 8)))
            if len(masks) / every > 16:
                every = -(-len(masks) // 16)
        caps, events = self.env.play_masks(masks, capture_every=every if view == "strip" else 0)
        txt = f"played {len(masks)} frames ({self.env.last_lag} lag).\n{self.env.status_line()}"
        if events:
            txt += "\nevents: " + "; ".join(events[:40]) + (" …" if len(events) > 40 else "")
        out = [{"type": "text", "text": txt}]
        if view == "end":
            out.append(self.img(self.frame_png(2)))
        elif view == "strip":
            out.append(self.img(E.contact_sheet([c[1] for c in caps], [f"f{c[0]}" for c in caps], cols=4)))
        return out

    def t_look(self, scale=2, crop=None):
        scale = max(1, min(4, int(scale or 2)))
        return [{"type": "text", "text": self.env.status_line()}, self.img(self.frame_png(scale, crop))]

    def t_rewind(self, frames=None, to_frame=None):
        target = int(to_frame) if to_frame is not None else self.env.frame - int(frames or 0)
        self.env.truncate(target)
        self.env.persist()
        return [{"type": "text", "text": f"now at frame {self.env.frame}.\n{self.env.status_line()}"},
                self.img(self.frame_png(2))]

    def t_checkpoint(self, action, name=None, note=""):
        if action == "save":
            self.env.ck_save(name, note)
            return [{"type": "text", "text": f"saved {name} at frame {self.env.frame}"}]
        if action == "load":
            self.env.ck_load(name)
            return [{"type": "text", "text": f"loaded {name}.\n{self.env.status_line()}"}, self.img(self.frame_png(2))]
        rows = [f"{k}: frame {v['frame']} — {v.get('note', '')} [{v.get('status', '')}]" for k, v in
                sorted(self.env.cks.items(), key=lambda kv: kv[1]["frame"])]
        return [{"type": "text", "text": "\n".join(rows) or "(none)"}]

    def t_ram(self, action, addr=None, length=16, name=None, size=1, signed=False, expr=None, desc="", event=False):
        mem = self.env.core.mem
        regions = [(0, 0x800), (0x6000, 0x8000)]
        if action == "status":
            return [{"type": "text", "text": self.env.status_line()}]
        if action == "objects":
            rows = ["slot class   x     y   $61CA+s"]
            for sl in range(18):
                cl = mem[0x6200 + sl]
                if cl == 0 and sl != 1:
                    continue
                x = mem[0x6086 + sl] * 256 + mem[0x6074 + sl]
                y = mem[0x60AA + sl] * 256 + mem[0x6098 + sl]
                rows.append(f"{sl:4d} {cl:5d} {x:5d} {y:5d}   {mem[0x61CA + sl]:3d}" + ("  <- Kirby" if sl == 1 else ""))
            return [{"type": "text", "text": f"objects at frame {self.env.frame} (class 0 = empty, hidden):\n"
                                             + "\n".join(rows)}]
        if action == "read":
            a = E.parse_addr(addr)
            n = max(1, min(256, int(length or 16)))
            rows = []
            for base in range(a, a + n, 16):
                bs = [f"{mem[i]:02X}" for i in range(base, min(base + 16, a + n))]
                rows.append(f"${base:04X}: " + " ".join(bs))
            return [{"type": "text", "text": "\n".join(rows)}]
        if action == "mark":
            self.mark = (self.env.frame, {a: mem[a] for lo, hi in regions for a in range(lo, hi)})
            return [{"type": "text", "text": f"marked RAM at frame {self.env.frame}"}]
        if action == "diff":
            if not self.mark:
                raise ValueError("mark first")
            old = self.mark[1]
            lo_f, hi_f = (E.parse_addr(addr), E.parse_addr(addr) + int(length or 256)) if addr else (0, 0x10000)
            rows = [f"${a:04X}: {v:02X} → {mem[a]:02X} ({mem[a] - v:+d})"
                    for a, v in old.items() if lo_f <= a < hi_f and v != mem[a]]
            head = f"{len(rows)} bytes changed between frame {self.mark[0]} and {self.env.frame}"
            return [{"type": "text", "text": head + "\n" + "\n".join(rows[:96]) + ("\n…" if len(rows) > 96 else "")}]
        if action == "define":
            self.env.vars.define(name, addr=addr, size=size or 1, signed=signed, expr=expr, desc=desc, event=event)
            return [{"type": "text", "text": f"defined {name}.\n{self.env.status_line()}"}]
        if action == "remove":
            self.env.vars.remove(name)
            return [{"type": "text", "text": f"removed {name}"}]
        return [{"type": "text", "text": self.env.vars.describe() or "(no vars)"}]

    def t_search(self, actions, goal=None, score=None, avoid=None, max_depth=8, beam=24, time_limit=120,
                 apply=False, mode="beam", samples=2000, seed=0):
        actions = [a.strip().strip("\"'`").strip() for a in actions]   # RECIPE-style quoting is not part of a spec
        r = self.env.search(actions, goal=goal, score=score, avoid=avoid, max_depth=int(max_depth or 8),
                            beam=max(1, min(4096, int(beam or 24))), time_limit=min(900, int(time_limit or 120)),
                            mode=mode or "beam", samples=max(1, min(200000, int(samples or 2000))),
                            seed=int(seed or 0))
        masks = r.pop("masks", None)
        txt = json.dumps(r)
        out = []
        if apply and masks and goal and not r.get("found"):
            txt += ("\nnot applied: the goal was not reached (with a goal, apply only applies a found result; "
                    "search again from here, or drop the goal for a score-only partial).")
        elif apply and masks:
            self.env.play_masks(masks)
            txt += f"\napplied.\n{self.env.status_line()}"
            out.append(self.img(self.frame_png(2)))
        return [{"type": "text", "text": txt}] + out

    def t_jev(self, instructions, options, max_decisions=30, stop_when=None, abort_when=None, image=True,
              features=None, show_status=True, history=8):
        names = set(self.env.vars.defs)
        stop_c = E.compile_expr(stop_when, names) if stop_when else None
        abort_c = E.compile_expr(abort_when, names) if abort_when else None
        feats = {k: E.compile_expr(v, names) for k, v in (features or {}).items()}
        opts = {k: (E.parse_spec(v["input"]), v.get("desc", "")) for k, v in options.items()}
        if not 2 <= len(opts) <= 26:
            raise ValueError("2-26 options")
        q = {"action": {"type": "choice", "instructions": "Pick the next input for Kirby.",
                        "criteria": {k: v[1] or None for k, v in opts.items()}}}
        trace, recent = [], []
        c0, t0 = jev.USAGE.cost, time.time()
        reason = "max_decisions"

        def ev(code):
            envd = dict(self.env.vars.read(self.env.core.mem, self.env.frame), ram=self.env.core.mem,
                        frame=self.env.frame, **E._FUNCS)
            try:
                return eval(code, {"__builtins__": {}}, envd)
            except Exception as ex:  # noqa: BLE001
                return f"error:{ex}"

        for i in range(max(1, min(300, int(max_decisions or 30)))):
            if STOP:
                reason = "harness stopping"
                break
            parts = [instructions, ""]
            if feats:
                parts.append("Game state: " + ", ".join(f"{k}={ev(c)}" for k, c in feats.items()))
            if show_status:
                parts.append("Status: " + self.env.status_line())
            if history:
                parts.append(f"Your last choices: {', '.join(recent[-int(history):]) or '(none)'}")
            state = "\n".join(parts)
            png = self.frame_png(1) if image else None
            ans, _ = jev.decide(state, q, png=png)
            a = ans["action"]
            choice = a["choice"]
            start = self.env.frame
            self.env.play_masks(opts[choice][0], watch_events=False)
            recent.append(choice)
            p = a.get("probabilities", {}).get(choice)
            trace.append(f"f{start}:{choice}({p:.2f})" if isinstance(p, (int, float)) else f"f{start}:{choice}")
            if abort_c and _truthy(ev(abort_c)):
                self.env.truncate(start)
                reason = f"abort_when true after {choice} at f{start} (rewound it)"
                break
            if stop_c and _truthy(ev(stop_c)):
                reason = "stop_when true"
                break
        cost = jev.USAGE.cost - c0
        self.st["jev_spent"] += cost
        self.env.persist()
        txt = (f"jev: {len(trace)} decisions in {time.time() - t0:.1f}s, ${cost:.5f}; ended: {reason}\n"
               f"trace: {' '.join(trace)}\n{self.env.status_line()}")
        return [{"type": "text", "text": txt}, self.img(self.frame_png(2))]

    # ---- the python lab (sandboxed) ----
    def sandbox_cmd(self, script, timeout):
        lab = os.path.join(self.run_dir, "lab")
        # uv-managed interpreters (the venv's python symlinks into here, through a version alias dir)
        py_root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.realpath(os.path.join(HERE, ".venv", "bin", "python")))))
        rom_dir = os.path.dirname(nes.ROM)
        cmd = ["systemd-run", "--user", "--quiet", "--scope", "-p", "MemoryMax=8G", "-p", "MemorySwapMax=0", "--",
               "timeout", "-k", "10", str(int(timeout)),
               "bwrap", "--unshare-all", "--die-with-parent", "--new-session",
               "--ro-bind", "/usr", "/usr", "--symlink", "usr/lib", "/lib", "--symlink", "usr/lib", "/lib64",
               "--symlink", "usr/bin", "/bin", "--symlink", "usr/bin", "/sbin",
               "--ro-bind", "/nix/store", "/nix/store",
               "--ro-bind-try", "/etc/ld.so.cache", "/etc/ld.so.cache",
               "--ro-bind-try", "/etc/ld.so.conf", "/etc/ld.so.conf",
               "--ro-bind-try", "/etc/ld.so.conf.d", "/etc/ld.so.conf.d",
               "--ro-bind-try", "/etc/localtime", "/etc/localtime",
               "--ro-bind-try", "/sys/devices/system/cpu", "/sys/devices/system/cpu",
               "--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
               "--ro-bind", py_root, py_root,
               "--ro-bind", HERE, HERE, "--ro-bind", rom_dir, rom_dir,
               "--ro-bind", self.run_dir, self.run_dir, "--bind", lab, lab,
               *self.hidden_binds(),
               "--setenv", "HOME", lab, "--setenv", "PYTHONPATH", f"{HERE}:{os.path.join(HERE, 'labkit')}:{lab}",
               "--setenv", "KIRBY_RUN", self.run_dir, "--setenv", "KIRBY_CORE", self.env.core_name,
               "--setenv", "PYTHONUNBUFFERED", "1", "--setenv", "OMP_NUM_THREADS", "16",
               # numpy's BLAS pool in every spawned emulator worker oversubscribed the CPU (load ~65 on 20 cores)
               "--setenv", "OPENBLAS_NUM_THREADS", "1", "--setenv", "MKL_NUM_THREADS", "1",
               "--chdir", lab, os.path.join(HERE, ".venv", "bin", "python"), script]
        return cmd

    def hidden(self, name):
        """Knowledge files a task with `reference: forbidden` may not see (reference movies and their splits)."""
        return bool(self.task and self.task["reference"] == "forbidden" and name.startswith("reference"))

    def hidden_binds(self):
        if not (self.task and self.task["reference"] == "forbidden"):
            return []
        kdir = os.path.join(HERE, "knowledge")
        out = ["--tmpfs", os.path.join(kdir, "movies")]
        for f in os.listdir(kdir):
            if self.hidden(f):
                out += ["--ro-bind", "/dev/null", os.path.join(kdir, f)]
        return out

    def t_python(self, code, timeout=300, background=False, show=None):
        lab = os.path.join(self.run_dir, "lab")
        os.makedirs(os.path.join(lab, "out"), exist_ok=True)
        os.makedirs(os.path.join(lab, "scripts"), exist_ok=True)
        self.py_n = getattr(self, "py_n", 0) + 1
        sid = f"{self.st['turns']:06d}-{self.py_n}"
        script = os.path.join(lab, "scripts", f"s{sid}.py")
        open(script, "w").write(code)
        timeout = max(5, min(1800 if not background else 6 * 3600, int(timeout or 300)))
        cmd = self.sandbox_cmd(script, timeout)
        if background:
            os.makedirs(os.path.join(lab, "jobs"), exist_ok=True)
            logp = os.path.join(lab, "jobs", f"j{sid}.log")
            p = subprocess.Popen(cmd, stdout=open(logp, "w"), stderr=subprocess.STDOUT, start_new_session=True)
            self.jobs[f"j{sid}"] = {"p": p, "log": logp, "started": now(), "script": script}
            return [{"type": "text", "text": f"started job j{sid} (timeout {timeout}s); log via jobs tail"}]
        before = {f: os.path.getmtime(os.path.join(lab, "out", f)) for f in os.listdir(os.path.join(lab, "out"))}
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = (r.stdout or "") + ("\n[stderr]\n" + r.stderr if r.stderr.strip() else "")
        if len(out) > 8000:
            out = out[:1500] + "\n…[cut]…\n" + out[-6000:]
        changed = [f for f in os.listdir(os.path.join(lab, "out"))
                   if before.get(f) != os.path.getmtime(os.path.join(lab, "out", f))]
        txt = (f"exit {r.returncode} in {time.time() - t0:.1f}s" + (" (timeout)" if r.returncode in (124, 137) else "")
               + (f"; out/ changed: {', '.join(sorted(changed)[:30])}" if changed else "") + "\n" + out)
        blocks = [{"type": "text", "text": txt}]
        for name in (show or [])[:4]:
            fp = os.path.join(lab, "out", os.path.basename(name if name.endswith(".png") else name + ".png"))
            data = open(fp, "rb").read() if os.path.exists(fp) else b""
            if data.startswith(b"\x89PNG"):
                blocks.append(self.img(data))
            else:   # an empty/partial PNG in a tool result makes the API reject the whole request (400)
                blocks.append({"type": "text", "text": f"(show {name}: {'missing' if not data else 'not a valid PNG'})"})
        return blocks

    def t_jobs(self, action, id=None, lines=40):
        if action == "list":
            rows = [f"{k}: {'running' if v['p'].poll() is None else 'exit ' + str(v['p'].returncode)} since "
                    f"{v['started']}" for k, v in self.jobs.items()]
            return [{"type": "text", "text": "\n".join(rows) or "(no jobs)"}]
        j = self.jobs.get(id)
        if not j:
            raise ValueError("unknown job")
        if action == "kill":
            if j["p"].poll() is None:
                os.killpg(j["p"].pid, signal.SIGTERM)
            return [{"type": "text", "text": f"killed {id}"}]
        tail = open(j["log"]).read().splitlines()[-max(1, min(200, int(lines or 40))):]
        state = "running" if j["p"].poll() is None else f"exit {j['p'].returncode}"
        return [{"type": "text", "text": f"{id} {state}\n" + "\n".join(tail)}]

    def start_jev_proxy(self):
        sock = os.path.join(self.run_dir, "lab", ".jev.sock")
        os.makedirs(os.path.dirname(sock), exist_ok=True)
        if os.path.exists(sock):
            os.unlink(sock)
        h = self

        class Handler(socketserver.StreamRequestHandler):
            def handle(self):
                try:
                    req = json.loads(self.rfile.readline())
                    with h.jev_lock:
                        if h.st["jev_lab_spent"] >= h.jev_lab_budget:
                            raise RuntimeError(f"lab Jev budget ${h.jev_lab_budget} used up")
                    png = base64.b64decode(req["png_b64"]) if req.get("png_b64") else None
                    c0 = jev.USAGE.cost
                    ans, _ = jev.decide(req["state"], req["questions"], png=png)
                    with h.jev_lock:
                        d = jev.USAGE.cost - c0
                        h.st["jev_lab_spent"] += d
                        h.st["jev_spent"] += d
                    self.wfile.write(json.dumps({"answers": ans}).encode() + b"\n")
                except Exception as e:  # noqa: BLE001
                    self.wfile.write(json.dumps({"error": f"{type(e).__name__}: {e}"}).encode() + b"\n")

        class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
            daemon_threads = True

        self.jev_server = Server(sock, Handler)
        threading.Thread(target=self.jev_server.serve_forever, daemon=True).start()

    def t_notes(self, action, text="", doc="notes"):
        path = {"recipe": self.recipe_path, "journal": self.journal_path}.get(doc, self.notes_path)
        if not os.path.exists(path):
            open(path, "w").write("")
        if action == "read":
            return [{"type": "text", "text": open(path).read()[-60000:] or "(empty)"}]
        if action == "append":
            open(path, "a").write("\n" + text.rstrip() + "\n")
        else:
            if doc == "journal":
                raise ValueError("the journal is append-only")
            if len(text) < 50:
                raise ValueError("refusing to replace the document with almost nothing")
            open(path, "w").write(text.rstrip() + "\n")
        size = os.path.getsize(path)
        warn = (f" — over the {NOTES_MAX // 1000} KB limit: rewrite it as the current state (action=write) and move "
                f"history to doc='journal'") if doc == "notes" and size > NOTES_MAX else ""
        return [{"type": "text", "text": f"{doc}: {size} bytes{warn}"}]

    def t_knowledge(self, action, file=None, section=None, query=None):
        kdir = os.path.join(HERE, "knowledge")
        files = sorted(f for f in os.listdir(kdir) if f.endswith(".md") and not self.hidden(f))
        if action == "list":
            return [{"type": "text", "text": "\n".join(f"{f} ({os.path.getsize(os.path.join(kdir, f))} bytes)"
                                                       for f in files)}]
        if action == "grep":
            rx = re.compile(query, re.I)
            hits = []
            for f in files:
                for n, line in enumerate(open(os.path.join(kdir, f)), 1):
                    if rx.search(line):
                        hits.append(f"{f}:{n}: {line.rstrip()[:200]}")
            return [{"type": "text", "text": "\n".join(hits[:80]) or "(no match)"}]
        if file not in files:
            raise ValueError(f"unknown file; have {files}")
        txt = open(os.path.join(kdir, file)).read()
        if section:
            lines = txt.split("\n")
            idx = [i for i, l in enumerate(lines) if l.startswith("#") and section.lower() in l.lower()]
            if not idx:
                raise ValueError("no heading matches that section")
            i = idx[0]
            level = len(lines[i]) - len(lines[i].lstrip("#"))
            j = i + 1
            while j < len(lines) and not (lines[j].startswith("#") and
                                          len(lines[j]) - len(lines[j].lstrip("#")) <= level):
                j += 1
            txt = "\n".join(lines[i:j])
        return [{"type": "text", "text": txt[:40000]}]

    def t_milestone(self, name, summary):
        name = re.sub(r"[^A-Za-z0-9_.-]", "_", name)[:50]
        self.env.ck_save("ms-" + name, summary[:200])
        fut, target = self.env.verify_async()
        self.env.export_fm2(os.path.join(self.run_dir, "kirby.fm2"))
        prev = self.st["milestones"][-1]["frame"] if self.st["milestones"] else 0
        self.st["milestones"].append({"name": name, "frame": self.env.frame, "segment": self.env.frame - prev,
                                      "spent": round(self.st["spent"], 2), "verified": None, "summary": summary,
                                      "t": now()})
        self.verifying.append((len(self.st["milestones"]) - 1, fut, target))
        self.save_state()
        self.end_episode = f"milestone {name}: {summary}"
        return [{"type": "text", "text": f"split {name} at frame {self.env.frame} (+{self.env.frame - prev}); "
                                         f"replay-from-power-on check running in the background (result in the "
                                         f"next episode's splits); episode ends after this turn."}]

    def poll_verifies(self):
        for item in list(self.reverify):
            i, p = item
            if p.poll() is not None:
                out = p.stdout.read()
                self.st["milestones"][i]["verified"] = " MATCH " in out
                self.log(event="reverify", milestone=self.st["milestones"][i]["name"], out=out[-300:])
                self.reverify.remove(item)
                self.save_state()
        for item in list(self.verifying):
            i, fut, target = item
            if fut.done():
                try:
                    self.st["milestones"][i]["verified"] = fut.result() == target
                except Exception as e:  # noqa: BLE001
                    self.st["milestones"][i]["verified"] = False
                    self.log(event="verify_error", err=str(e)[:300])
                self.verifying.remove(item)
                self.save_state()

    def t_finish(self, summary):
        if self.task:
            t0 = time.time()
            r = TK.check_async(self.env, self.task).result(timeout=900)
            desc = TK.describe(self.task, r)
            self.log(event="task_check", ok=r["ok"], result=r, secs=round(time.time() - t0, 1))
            if not r["ok"]:
                return [{"type": "text", "text": f"task check FAILED (replay from power-on, {self.env.frame} frames, "
                                                 f"{time.time() - t0:.0f}s) — the run continues:\n{desc}"}]
        else:
            r, desc = None, "(no task: run ended by the agent)"
        self.env.ck_save("final", summary[:200])
        self.env.export_fm2(os.path.join(self.run_dir, "kirby.fm2"))
        self.finished = {"summary": summary, "frame": self.env.frame, "spent": round(self.st["spent"], 4),
                         "episodes": self.st["episode"], "turns": self.st["turns"], "t": now(), "check": r}
        self.st["finished"] = self.finished
        self.save_state()
        json.dump(self.finished, open(os.path.join(self.run_dir, "result.json"), "w"), indent=1, default=str)
        self.end_episode = f"finished: {summary}"
        return [{"type": "text", "text": f"run finished at frame {self.env.frame}.\n{desc}"}]

    def t_handoff(self, summary):
        self.end_episode = f"handoff: {summary}"
        return [{"type": "text", "text": "episode ends after this turn."}]

    def run_tool(self, name, inp):
        fn = getattr(self, "t_" + name, None)
        if fn is None:
            raise ValueError(f"unknown tool {name}")
        return fn(**inp)

    # ---- prompts ----
    def system_prompt(self):
        rd = lambda *p: open(os.path.join(HERE, *p)).read()
        if self.task:
            ref = ("Reference inputs are FORBIDDEN in this task: produce every input yourself. The reference "
                   "movies and their splits are hidden; text about routes and tricks is fine."
                   if self.task["reference"] == "forbidden" else
                   "Reference movies in the knowledge base may be used (test their sync first, recipe §1).")
            task_txt = (f"Task `{self.task['name']}` (start: {self.task['start']}).\n\nSteps, in order:\n"
                        f"{TK.describe(self.task)}\n\n{self.task['text']}\n\n{ref}")
            sp = (rd("prompts", "task.md").replace("{{TASK}}", task_txt).replace("{{RECIPE}}", rd("RECIPE.md"))
                  .replace("{{WORKBENCH}}", rd("prompts", "workbench.md")))
        else:
            sp = rd("prompts", "research.md").replace("{{WORKBENCH}}", rd("prompts", "workbench.md"))
        kdir = os.path.join(HERE, "knowledge")
        inline = []
        for f in ("mechanics.md", "speedrun.md"):
            p = os.path.join(kdir, f)
            if os.path.exists(p):
                inline.append(f"<knowledge file=\"{f}\">\n{open(p).read()}\n</knowledge>")
        return sp + ("\n\n# Knowledge base (inline copies; more via the knowledge tool)\n\n" + "\n\n".join(inline)
                     if inline else "")

    def kickoff(self, why):
        ms = self.st["milestones"]
        splits = "\n".join(f"- {m['name']}: frame {m['frame']} (+{m['segment']}), ${m['spent']}, "
                           f"{ {True: 'replay verified', False: 'REPLAY MISMATCH', None: 'verifying'}[m['verified']] }"
                           f" — {m['summary'][:160]}"
                           for m in ms[-30:]) or "(none yet)"
        cks = "\n".join(f"- {k}: frame {v['frame']} — {v.get('note', '')[:100]}" for k, v in
                        sorted(self.env.cks.items(), key=lambda kv: kv[1]["frame"])[-25:]) or "(none)"
        nsize = os.path.getsize(self.notes_path)
        guard = (f"\n\nHarness: your notebook is {nsize // 1000} KB (limit {NOTES_MAX // 1000} KB) and is inlined at every "
                 f"episode start. Before anything else, rewrite it as the current state (notes write) and move "
                 f"history to doc='journal'." if nsize > NOTES_MAX else "")
        txt = (f"Episode {self.st['episode']} begins ({why}).\n\n"
               f"Budget: ${self.st['spent']:.2f} of ${self.budget:.2f} spent (Jev ${self.st['jev_spent']:.4f}).\n"
               f"Movie: frame {self.env.frame} ({self.env.frame / 60.0988:.1f}s).\n"
               f"Status: {self.env.status_line()}\n\nSplits so far:\n{splits}\n\nCheckpoints (latest 25):\n{cks}\n\n"
               f"Your notebook:\n<notes>\n{open(self.notes_path).read()}\n</notes>\n\n"
               f"Your recipe so far:\n<recipe>\n"
               f"{open(self.recipe_path).read() if os.path.exists(self.recipe_path) else '(not started)'}\n</recipe>\n\n"
               f"Current frame below. Continue the run.{guard}")
        blocks = [{"type": "text", "text": txt}]
        msg = self.inbox()
        if msg:
            blocks.append(msg)
        return blocks + [self.img(self.frame_png(2))]

    # ---- the loop ----
    def cost_of(self, u):
        P = self.price
        c = (u.input_tokens * P["input"] + (u.cache_creation_input_tokens or 0) * P["cache_write"]
             + (u.cache_read_input_tokens or 0) * P["cache_read"] + u.output_tokens * P["output"]) / 1e6
        return c

    def call(self, system, messages):
        # explicit breakpoint after tools+system: that prefix is identical across episodes, so each new episode
        # reads it from cache instead of rewriting it with the kickoff
        system = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        kw = dict(model=self.model, max_tokens=32000, system=system, messages=messages, tools=TOOLS,
                  thinking={"type": "adaptive", "display": "summarized"},
                  output_config={"effort": self.effort}, cache_control={"type": "ephemeral"},
                  betas=BETAS, context_management=CONTEXT_MGMT, extra_body={"fallbacks": "default"})
        with self.client.beta.messages.stream(**kw) as s:
            return s.get_final_message()

    def episode(self):
        self.st["episode"] += 1
        self.save_state()
        ep = self.st["episode"]
        why = self.st.pop("next_why", "start" if ep == 1 else "resume")
        system = self.system_prompt()
        messages = [{"role": "user", "content": self.kickoff(why)}]
        self.end_episode = None
        handoff_asked = False
        idle_ends = 0
        first_ctx = None
        self.work_calls = 0
        transcript_path = os.path.join(self.run_dir, "episodes", f"{ep:04d}.jsonl")
        tf = open(transcript_path, "a")
        for turn in range(EPISODE_TURNS):
            if STOP or self.st["spent"] >= self.budget:
                break
            self.poll_verifies()
            resp = self.call(system, messages)
            u = resp.usage
            cost = self.cost_of(u)
            self.st["spent"] += cost
            self.st["turns"] += 1
            ctx = u.input_tokens + (u.cache_read_input_tokens or 0) + (u.cache_creation_input_tokens or 0)
            first_ctx = first_ctx or ctx
            messages.append({"role": "assistant", "content": resp.content})
            texts = [b.text for b in resp.content if b.type == "text"]
            thinks = [getattr(b, "thinking", "") for b in resp.content if b.type == "thinking"]
            calls = [b for b in resp.content if b.type == "tool_use"]
            self.log(ep=ep, turn=self.st["turns"], stop=resp.stop_reason, cost=round(cost, 5), ctx=ctx,
                     out=u.output_tokens, cache_read=u.cache_read_input_tokens, text=texts,
                     thinking=[t for t in thinks if t], calls=[{"name": c.name, "input": c.input} for c in calls],
                     frame=self.env.frame)
            tf.write(json.dumps({"role": "assistant", "content": [b.model_dump() for b in resp.content]},
                                default=str) + "\n")
            print(f"[{now()}] ep{ep} t{self.st['turns']} ${self.st['spent']:.2f} ctx={ctx} out={u.output_tokens} "
                  f"{resp.stop_reason} {[c.name for c in calls]} f{self.env.frame}", flush=True)
            if resp.stop_reason == "refusal":
                self.log(event="refusal", details=str(getattr(resp, "stop_details", None)))
                self.st["next_why"] = "previous episode ended on a refusal"
                break
            results = []
            for c in calls:
                self.st["tool_counts"][c.name] = self.st["tool_counts"].get(c.name, 0) + 1
                self.work_calls += c.name in WORK_TOOLS
                try:
                    content = self.run_tool(c.name, dict(c.input))
                    is_err = False
                except Exception as e:  # noqa: BLE001 — tool errors go back to the model
                    content = [{"type": "text", "text": f"error: {type(e).__name__}: {e}"}]
                    is_err = True
                    self.log(event="tool_error", tool=c.name, err=traceback.format_exc()[-800:])
                content.append({"type": "text", "text": self.footer()})
                results.append({"type": "tool_result", "tool_use_id": c.id, "content": content, "is_error": is_err})
                self.log(ep=ep, tool=c.name, result=[b["text"] for b in content if b["type"] == "text"])
            self.save_state()
            if self.end_episode and not results:
                break
            if results:
                user = results
                msg = self.inbox()
                if msg:
                    user = results + [msg]
                if ctx > max(EPISODE_TOKENS, first_ctx + EPISODE_GROWTH) and not handoff_asked and not self.end_episode:
                    user = user + [{"type": "text", "text": "Harness: your context is long. Bring your notes up to "
                                                               "date now, then call handoff."}]
                    handoff_asked = True
                messages.append({"role": "user", "content": user})
                tf.write(json.dumps({"role": "user", "content": [
                    {k: v for k, v in r.items() if k != "content"} | {"text": [b.get("text") for b in r["content"]
                                                                              if b["type"] == "text"]}
                    for r in results if r["type"] == "tool_result"]}) + "\n")
                if self.end_episode:
                    # let the model see its tool results? No: the episode ends; the next one starts from notes.
                    break
                idle_ends = 0
                continue
            # end_turn without tools: nudge to keep going autonomously
            idle_ends += 1
            if idle_ends >= 3:
                self.st["next_why"] = "previous episode stalled (ended turns without tool calls)"
                break
            messages.append({"role": "user", "content": [{"type": "text", "text":
                             "Harness: nobody is reading chat in real time — this run is autonomous. Keep going with "
                             "tools. If you are blocked, write what you tried into notes and pick a different "
                             "approach. " + self.footer()}]})
        tf.close()
        if self.end_episode:
            self.st["next_why"] = self.end_episode
        elif turn >= EPISODE_TURNS - 1:
            self.st["next_why"] = "turn limit of the previous episode"
        self.save_state()

    def run(self):
        print(f"[{now()}] run {self.run_dir} budget ${self.budget} spent ${self.st['spent']:.2f}", flush=True)
        while not STOP and self.st["spent"] < self.budget:
            flag = os.path.join(self.run_dir, "reload")
            if os.path.exists(flag):       # operator: pick up new harness code at an episode boundary
                os.unlink(flag)
                self.save_state()
                for j in self.jobs.values():
                    if j["p"].poll() is None:
                        os.killpg(j["p"].pid, signal.SIGTERM)
                print(f"[{now()}] reloading harness code", flush=True)
                # execv keeps our PID but forgets our children: the persistent search pool's workers would
                # stay alive as orphans and keep burning CPU (w12 runs: 17 per reload, ~40% CPU each)
                import multiprocessing as mp
                for p in mp.active_children():
                    p.terminate()
                os.execv(sys.executable, [sys.executable, "-u"] + sys.argv)
            if self.st.get("finished"):
                print(f"[{now()}] run already finished: {self.st['finished']['summary'][:200]}", flush=True)
                break
            try:
                self.episode()
                self.st["bad_requests"] = 0
                idle = self.st.get("idle_episodes", 0) + 1 if self.work_calls == 0 else 0
                self.st["idle_episodes"] = idle
                self.save_state()
                if self.finished:
                    break
                if idle >= IDLE_EPISODES:
                    self.st["stopped"] = f"{idle} episodes in a row without work tools ({now()})"
                    self.save_state()
                    print(f"[{now()}] stopping: {self.st['stopped']}", flush=True)
                    break
            except anthropic.APIStatusError as e:
                self.log(event="api_error", status=e.status_code, err=str(e)[:500])
                print(f"API error {e.status_code}: {str(e)[:300]}", flush=True)
                if e.status_code in (401, 403, 404):
                    raise
                if e.status_code == 400:
                    # a malformed message poisons this episode's history only: start a fresh episode from notes
                    self.st["bad_requests"] = self.st.get("bad_requests", 0) + 1
                    self.st["next_why"] = ("the previous episode ended on an API error (a tool result was rejected: "
                                           f"{str(e)[:160]}); continue from your notes")
                    self.save_state()
                    if self.st["bad_requests"] >= 3:
                        raise
                    continue
                time.sleep(60)
            except anthropic.APIConnectionError as e:
                self.log(event="api_conn", err=str(e)[:300])
                time.sleep(30)
        for j in self.jobs.values():
            if j["p"].poll() is None:
                os.killpg(j["p"].pid, signal.SIGTERM)
        self.env.export_fm2(os.path.join(self.run_dir, "kirby.fm2"))
        print(f"[{now()}] done: spent ${self.st['spent']:.2f}, frame {self.env.frame}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default=os.path.join(HERE, "runs", "main"))
    ap.add_argument("--budget", type=float, required=True, help="hard stop in USD (list prices) for this run dir")
    ap.add_argument("--core", default="fceumm")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--model", default="claude-opus-5-5", choices=sorted(PRICES))
    ap.add_argument("--task", help="task file (tasks/*.md); copied into the run dir on the first start")
    a = ap.parse_args()
    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        os.environ["ANTHROPIC_API_KEY"] = open(os.path.expanduser("~/claude-platform.txt")).read().strip()
    Harness(a.run, a.budget, a.core, a.effort, a.model, a.task).run()
    import multiprocessing as mp
    for p in mp.active_children():      # verify/check workers left by shutdown(wait=False)
        p.terminate()
    sys.stdout.flush()
    os._exit(0)   # don't hang on executor/proxy threads at interpreter exit (the main run's unit timed out here)


if __name__ == "__main__":
    main()
