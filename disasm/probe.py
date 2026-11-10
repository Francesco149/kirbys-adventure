"""probe.py - run things on the instrumented core at a point of a corpus movie, and check claims.

A window is 'movie@start+len' or 'movie@start-end' (frames of a corpus movie). Seeking uses the savestates
that the evidence build left every 1000 frames, so any window costs under a second to reach.

Claim kinds (fields in the [[claim]] entry; every `expect`-like field is a Python expression):

  call    fn = routine name or BB:AAAA, on = [windows], expect, [where], [min_calls = 5], [model = "python code"]
          evaluated on every call of fn in the windows. Names: a x y p s (entry registers), ra rx ry rp rs
          (at return), rd[addr] (first value read from an address before the call wrote it), wr[addr] (last
          value written), mem(addr) (value at return for an address the call read or wrote), reads, writes,
          romrd (PRG offset -> byte read), calls (names of the routines called, in order), n (instructions),
          frame, A("name") (CPU address of a name), O("name") (PRG offset).
  frames  on = [windows], any of always / never / sometimes (an expression or a list of them)
          evaluated at the end of every frame. Names: ram[addr], prev[addr] (previous frame), r("name") /
          pr("name") (a RAM variable by name, little-endian when len = 2), n("routine") (how many times its
          first instruction ran this frame), frame, pad (the joypad mask of this frame).
  effect  on = "movie@frame", frames = N, [poke = { "0599" = 9 }], [hold = true], [patch = { "3E:C6DD" = 0 }],
          [input = "R*60"], expect
          runs N frames twice from the same state: the control run is the movie as it is, the treated run
          has the pokes, the patches and the replacement input. Names: ram / ctl (RAM after the treated
          / the control run), n("routine") / cn("routine") (executions in the treated / control run),
          diff (addresses whose final value differs), r("name"), cr("name").
  xref    expect over the whole corpus: writers(x), readers(x) (routines touching a RAM name or address,
          x may be "name", an address, or (address, length)), callers(routine), callees(routine),
          datareaders(data name), touched(x) (was the address ever read or written).
  static  expect over the ROM bytes: rom[off], u8(at), u16(at), O(name), kind(off), executed(off), dataread(off).
  vmop    op = opcode name, on = [windows], expect, [at = script address], [min = 5]: evaluated on every
          execution of that script opcode. Names: args (operand values in order), banks (their bank bytes), op, low (the family's low
          bits), addr, length, next (address of the next instruction the thread ran, or None), thread (the
          thread index, $6F), rd / wr / reads / writes (what the handler read and wrote, RAM only, from the
          opcode fetch until the handler returns to [vm] advance), calls, rom.
  vmlen   ops = [opcode names], on = [windows], [min = 1]: every execution of those script opcodes in the
          windows continues at start + declared length (flow next / spawn), at the decoded target (jump /
          call), or at either (branch). This is what verifies an [[opcode]] entry's operand layout.
"""
import hashlib
import json
import multiprocessing as mp
import os
import sys
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(os.path.dirname(HERE), "tas"))
import evidence as EVD  # noqa: E402

PRG = 0x80000
NONE = 0xFFFFFFFF
R_EXEC, R_READ, R_WRITE, R_INT, R_TAG, R_BEGIN, R_END, R_ABORT = 1, 2, 3, 4, 5, 6, 7, 8


def parse_window(w):
    """'main@3000+600' -> ('main', 3000, 600); 'main@3000-3600' likewise; 'main@3000' -> length 0."""
    movie, rest = w.split("@", 1)
    if "+" in rest:
        a, n = rest.split("+", 1)
        return movie, int(a), int(n)
    if "-" in rest:
        a, b = rest.split("-", 1)
        return movie, int(a), int(b) - int(a)
    return movie, int(rest), 0


class Call:
    """One call of a watched routine, reconstructed from the event log."""

    def __init__(self, recs, frame, movie):
        b, e = recs[0], recs[-1]
        self.recs = recs
        self.fn = int(b["off"])
        self.movie, self.frame = movie, frame
        self.a, self.x, self.y, self.p, self.s = (int(b[k]) for k in "axyps")
        self.ra, self.rx, self.ry, self.rp, self.rs = (int(e[k]) for k in "axyps")
        self.complete = int(e["type"]) == R_END
        body = recs[1:-1]
        t = body["type"]
        ex = body[t == R_EXEC]
        self.n = len(ex)
        self.path = ex["off"]
        self.ops = ex["val"]
        jsr = np.flatnonzero(self.ops[:-1] == 0x20)
        self.call_offs = [int(self.path[i + 1]) for i in jsr]
        self.rd, self.wr, self.romrd = {}, {}, {}
        rw = body[(t == R_READ) | (t == R_WRITE)]
        for typ, addr, val, off in zip(rw["type"].tolist(), rw["addr"].tolist(), rw["val"].tolist(),
                                       rw["off"].tolist()):
            if typ == R_READ:
                if off != NONE:
                    self.romrd.setdefault(off, val)
                elif addr not in self.wr and addr not in self.rd:
                    self.rd[addr] = val
            else:
                self.wr[addr] = val

    def mem(self, addr):
        if addr in self.wr:
            return self.wr[addr]
        if addr in self.rd:
            return self.rd[addr]
        raise KeyError(f"${addr:04X} was neither read nor written by this call")


class Session:
    """One instrumented core, positioned anywhere in the corpus."""

    def __init__(self):
        import kdcore
        self.kd = kdcore
        self.c = kdcore.Core()
        self.masks = {}
        self.movie = None
        self._fresh = self.c.save()

    def movie_masks(self, movie):
        if movie not in self.masks:
            self.masks[movie] = self.kd.movie_masks(EVD.movie_path(movie))
        return self.masks[movie]

    def seek(self, movie, frame):
        masks = self.movie_masks(movie)
        if frame > len(masks):
            raise ValueError(f"{movie} has {len(masks)} frames, cannot seek to {frame}")
        base = (frame // EVD.SNAP_EVERY) * EVD.SNAP_EVERY
        sp = os.path.join(EVD.EV, "snaps", movie, f"{base:07d}")
        c = self.c
        if not os.path.exists(sp):
            raise FileNotFoundError(f"no snapshot {sp}: run `kd evidence`")
        c.load((open(sp, "rb").read(), base, 0))
        c.lib.retro_kd_enable(0)
        for f in range(base, frame):
            nes_step(c, masks[f])
        c.lib.retro_kd_enable(1)
        self.movie = movie

    def run(self, n, render=False, masks=None):
        """Advance n frames with the movie's inputs (or the given masks)."""
        m = self.movie_masks(self.movie)
        for i in range(n):
            f = self.c.frames
            mask = masks[i] if masks is not None else (m[f] if f < len(m) else 0)
            self.c.step(mask, render=render and i == n - 1)

    def ram(self):
        return self.c.ram_bytes()       # 0x800 bytes of RAM then 0x2000 of cartridge RAM

    # ---- calls ----
    def calls(self, fn_offs, window, max_calls=2000, cap=6_000_000):
        movie, start, n = parse_window(window)
        self.seek(movie, start)
        c = self.c
        c.watch(fn_offs)
        c.log(2, cap)
        out, pend = [], []
        m = self.movie_masks(movie)
        for _ in range(n):
            if c.frames >= len(m):
                break
            c.step(m[c.frames], render=False)
            recs, over = c.take()
            if over:
                raise RuntimeError(f"event log overflow in frame {c.frames} (watched routine too hot or too long)")
            if len(recs):
                pend.append(recs)
            if pend:
                allr = np.concatenate(pend) if len(pend) > 1 else pend[0]
                t = allr["type"]
                begins = np.flatnonzero(t == R_BEGIN)
                ends = np.flatnonzero((t == R_END) | (t == R_ABORT))
                done = 0
                for bi in begins:
                    ei = ends[ends > bi]
                    if not len(ei):
                        break
                    ei = int(ei[0])
                    tag = int(allr[bi - 1]["off"]) if bi > 0 and t[bi - 1] == R_TAG else 0
                    out.append(Call(allr[bi:ei + 1], tag & 0xFFFFF, movie))
                    done = ei + 1
                rest = allr[done:]
                pend = [rest] if len(rest) and (rest["type"] == R_BEGIN).any() else []
            if len(out) >= max_calls:
                break
        c.log(0, 0)
        c.watch([])
        return out[:max_calls]


def nes_step(c, mask):
    """A frame without tagging (used while seeking with the recorder off)."""
    import nes
    nes.Core.step(c, mask, render=False)


class RamView:
    """ram[addr] over a ram_bytes() blob (CPU addresses)."""
    __slots__ = ("b",)

    def __init__(self, b):
        self.b = b

    def __getitem__(self, a):
        a = int(a)
        if 0 <= a < 0x2000:
            return self.b[a & 0x7FF]
        if 0x6000 <= a < 0x8000:
            return self.b[0x800 + a - 0x6000]
        raise IndexError(f"${a:04X} is not RAM")


class Routines:
    """A set of routines, kept as addresses ('BB:AAAA'). Comparing it with names works whatever unit named
    a routine since the claim was written: 'random' and '3E:C8DD' are the same member. Deliberately not a
    subclass of set, so that `{'a', 'b'} <= readers(x)` is handed to this class too."""

    def __init__(self, db, items):
        self.db = db
        self.s = frozenset(self._norm(items))

    @classmethod
    def of(cls, db, items):
        return cls(db, items)

    def _norm(self, items):
        if isinstance(items, Routines):
            return items.s
        out = set()
        for x in ([items] if isinstance(items, str) else items):
            if x in self.db.by_name and self.db.by_name[x][0] == "sym":
                e = self.db.by_name[x][1]
                out.add(f"{e['off'] >> 13:02X}:{e['addr']:04X}")
            else:
                out.add(x.upper() if ":" in x and len(x) == 7 else x)
        return out

    def _o(self, other):
        return frozenset(self._norm(other))

    def __eq__(self, other):
        return self.s == self._o(other)

    def __ne__(self, other):
        return self.s != self._o(other)

    def __hash__(self):
        return hash(self.s)

    def __le__(self, other):
        return self.s <= self._o(other)

    def __ge__(self, other):
        return self.s >= self._o(other)

    def __lt__(self, other):
        return self.s < self._o(other)

    def __gt__(self, other):
        return self.s > self._o(other)

    def __contains__(self, x):
        return next(iter(self._norm([x]))) in self.s

    def __iter__(self):
        return iter(sorted(self.s))

    def __len__(self):
        return len(self.s)

    def __bool__(self):
        return bool(self.s)

    def __sub__(self, other):
        return Routines(self.db, self.s - self._o(other))

    def __rsub__(self, other):
        return Routines(self.db, self._o(other) - self.s)

    def __or__(self, other):
        return Routines(self.db, self.s | self._o(other))

    __ror__ = __or__

    def __and__(self, other):
        return Routines(self.db, self.s & self._o(other))

    __rand__ = __and__

    def isdisjoint(self, other):
        return self.s.isdisjoint(self._o(other))

    def __repr__(self):
        names = {f"{e['off'] >> 13:02X}:{e['addr']:04X}": e["name"] for e in self.db.syms}
        return "{" + ", ".join(sorted(names.get(x, x) for x in self.s)) + "}"


SAFE = {"abs": abs, "min": min, "max": max, "len": len, "set": set, "sorted": sorted, "all": all, "any": any,
        "sum": sum, "range": range, "int": int, "bool": bool, "list": list, "tuple": tuple, "dict": dict,
        "enumerate": enumerate, "zip": zip, "hex": hex, "bin": bin, "divmod": divmod, "isinstance": isinstance,
        "True": True, "False": False, "None": None, "print": print, "str": str, "bytes": bytes, "map": map,
        "filter": filter, "reversed": reversed, "KeyError": KeyError, "frozenset": frozenset}


class RoutineRef(str):
    """A routine in a `calls` list: reads as its name, and equals both the name and 'BB:AAAA', so a claim
    written with the address keeps passing after some unit names the routine."""

    def __new__(cls, name, addr):
        self = super().__new__(cls, name)
        self.addr = addr
        return self

    def __eq__(self, other):
        if isinstance(other, RoutineRef):
            return self.addr == other.addr
        return isinstance(other, str) and (str.__eq__(self, other) or other.upper() == self.addr)

    def __ne__(self, other):
        return not self.__eq__(other)

    __hash__ = str.__hash__


class Checker:
    """Evaluates claims. Holds the DB, the model and (lazily) one Session."""

    def __init__(self, db, model):
        self.db, self.model, self.ev = db, model, model.ev
        self._sess = None

    @property
    def sess(self):
        if self._sess is None:
            self._sess = Session()
        return self._sess

    @property
    def rom_bytes(self):
        if not hasattr(self, "_rom"):
            self._rom = bytes(self.model.prg)      # indexing gives plain ints
        return self._rom

    # ---- names ----
    def O(self, name):
        return self.db.off_of(name)

    def A(self, name):
        return self.db.addr_of(name)

    def routine_name(self, off):
        """Code offset -> the name of the routine (or part) containing it, or BB:AAAA of its start."""
        if off >= PRG:
            return f"RAM:{off - PRG:04X}"
        m = self.model
        C, Aa = ord("c"), ord("a")
        cuts = self.cuts
        lo = off & ~0x1FFF
        o = off
        while o > lo and not (m.kind[o] == C and o in cuts) and m.kind[o - 1] in (C, Aa):
            o -= 1
        e = self.db.sym_at.get(o)
        return e["name"] if e else m.name(o)

    def routine_ref(self, off):
        """The same routine as an element of a `calls` list: equal to its name and to its address."""
        name = self.routine_name(off)
        e = self.db.by_name.get(name)
        if e and e[0] == "sym":
            return RoutineRef(name, f"{e[1]['off'] >> 13:02X}:{e[1]['addr']:04X}")
        return RoutineRef(name, name)

    @property
    def cuts(self):
        if not hasattr(self, "_cuts"):
            self._cuts = set(self.model.entries) | self.model.cuts
        return self._cuts

    def _base_env(self, claim):
        env = dict(SAFE)
        env.update(A=self.A, O=self.O)
        if claim.get("model"):
            exec(claim["model"], env)
        return env

    # ---- kinds ----
    def check(self, claim):
        """-> (ok, message, stats dict). Never raises."""
        try:
            return getattr(self, "_k_" + claim["kind"])(claim)
        except Exception as e:
            tb = traceback.format_exc(limit=3).strip().splitlines()[-1]
            return False, f"error: {type(e).__name__}: {e} ({tb})", {}

    def _k_call(self, c):
        fn = self.O(c["fn"])
        wins = c["on"] if isinstance(c["on"], list) else [c["on"]]
        env = self._base_env(c)
        expect = compile(c["expect"], "expect", "eval")
        where = compile(c["where"], "where", "eval") if c.get("where") else None
        total = used = 0
        for w in wins:
            for call in self.sess.calls([fn], w, max_calls=int(c.get("max_calls", 400))):
                total += 1
                if not call.complete:
                    return False, f"{w}: a call at frame {call.frame} did not return (aborted)", {"calls": total}
                e = dict(env)
                e.update(a=call.a, x=call.x, y=call.y, p=call.p, s=call.s, ra=call.ra, rx=call.rx, ry=call.ry,
                         rp=call.rp, rs=call.rs, rd=call.rd, wr=call.wr, mem=call.mem, reads=set(call.rd),
                         writes=set(call.wr), romrd=call.romrd, n=call.n, frame=call.frame,
                         calls=[self.routine_ref(o) for o in call.call_offs])
                if where is not None and not eval(where, e):
                    continue
                used += 1
                try:
                    ok = eval(expect, e)
                except Exception as x:
                    return False, f"{w} frame {call.frame}: {type(x).__name__}: {x}", {"calls": used}
                if not ok:
                    return False, (f"{w} frame {call.frame}: false for a={call.a:02X} x={call.x:02X} "
                                   f"y={call.y:02X} -> ra={call.ra:02X} rx={call.rx:02X} ry={call.ry:02X}"), \
                        {"calls": used}
        need = int(c.get("min_calls", 5))
        if used < need:
            return False, f"only {used} matching calls in the windows (min_calls = {need}, {total} calls seen)", \
                {"calls": used}
        return True, f"{used} calls", {"calls": used, "windows": len(wins)}

    def _exprs(self, c, key):
        v = c.get(key, [])
        return [(s, compile(s, key, "eval")) for s in ([v] if isinstance(v, str) else v)]

    def _k_frames(self, c):
        wins = c["on"] if isinstance(c["on"], list) else [c["on"]]
        env = self._base_env(c)
        always, never, some = self._exprs(c, "always"), self._exprs(c, "never"), self._exprs(c, "sometimes")
        if not (always or never or some):
            return False, "a frames claim needs always, never or sometimes", {}
        hit = [0] * len(some)
        frames = 0
        s = self.sess
        for w in wins:
            movie, start, n = parse_window(w)
            s.seek(movie, start)
            masks = s.movie_masks(movie)
            prev = RamView(s.ram())
            for _ in range(n):
                if s.c.frames >= len(masks):
                    break
                cnt0 = s.c.count.copy()
                pad = masks[s.c.frames]
                s.c.step(pad, render=False)
                ram = RamView(s.ram())
                cnt = s.c.count

                def n_(name, cnt=cnt, cnt0=cnt0):
                    o = self.O(name)
                    return int(cnt[o]) - int(cnt0[o])

                def r_(name, view=ram):
                    kind, e = self.db.by_name[name]
                    return sum(view[e["addr"] + i] << (8 * i) for i in range(min(e["len"], 2)))

                e = dict(env)
                e.update(ram=ram, prev=prev, n=n_, r=r_, pr=lambda name, pv=prev: r_(name, pv),
                         frame=s.c.frames - 1, pad=pad)
                for src, code in always:
                    if not eval(code, e):
                        return False, f"{w}: always `{src}` is false at frame {s.c.frames - 1}", {"frames": frames}
                for src, code in never:
                    if eval(code, e):
                        return False, f"{w}: never `{src}` is true at frame {s.c.frames - 1}", {"frames": frames}
                for i, (src, code) in enumerate(some):
                    if eval(code, e):
                        hit[i] += 1
                prev = ram
                frames += 1
        for i, (src, _) in enumerate(some):
            if not hit[i]:
                return False, f"sometimes `{src}` never held in {frames} frames", {"frames": frames}
        return True, f"{frames} frames" + (f", sometimes held {hit}" if some else ""), {"frames": frames}

    def _k_effect(self, c):
        import env as E
        movie, start, _ = parse_window(c["on"])
        n = int(c["frames"])
        s = self.sess
        env = self._base_env(c)
        masks = E.parse_spec(c["input"]) if c.get("input") else None
        if masks is not None:
            masks = (masks + [0] * n)[:n]
        poke = {self.A(k) if not _ishex(k) else int(k, 16): int(v) for k, v in c.get("poke", {}).items()}
        patch = {self.O(k): int(v) for k, v in c.get("patch", {}).items()}

        def one(treated):
            s.seek(movie, start)
            cnt0 = s.c.count.copy()
            saved = {o: int(s.c.prg[o]) for o in patch}
            try:
                if treated:
                    for o, v in patch.items():
                        s.c.prg[o] = v
                for i in range(n):
                    if treated and (i == 0 or c.get("hold")):
                        for a, v in poke.items():
                            if a < 0x800:
                                s.c.ram[a] = v
                            else:
                                s.c.wram[a - 0x6000] = v
                    s.run(1, masks=masks[i:i + 1] if (masks is not None and treated) else None)
            finally:
                for o, v in saved.items():
                    s.c.prg[o] = v
            return s.ram(), s.c.count.astype(np.int64) - cnt0

        ctl_b, ctl_n = one(False)
        ram_b, ram_n = one(True)
        ram, ctl = RamView(ram_b), RamView(ctl_b)
        diff = {(i if i < 0x800 else 0x6000 + i - 0x800) for i in range(len(ram_b)) if ram_b[i] != ctl_b[i]}

        def r_(name, view=ram):
            kind, e = self.db.by_name[name]
            return sum(view[e["addr"] + i] << (8 * i) for i in range(min(e["len"], 2)))

        env.update(ram=ram, ctl=ctl, diff=diff, n=lambda name: int(ram_n[self.O(name)]),
                   cn=lambda name: int(ctl_n[self.O(name)]), r=r_, cr=lambda name: r_(name, ctl))
        ok = eval(compile(c["expect"], "expect", "eval"), env)
        return bool(ok), ("holds" if ok else "expect is false") + f" ({len(diff)} RAM bytes differ from control)", \
            {"frames": n}

    def _k_vmlen(self, c):
        """Every execution of the listed script opcodes continues where the opcode table says: at the next
        instruction (start + declared length) or at its decoded target."""
        vm = self.model.vm
        if vm is None:
            return False, "the database has no [vm] / [[opcode]] entries", {}
        want = {}
        for n in c["ops"]:
            kind, e = self.db.by_name["op_" + n]           # ops are given by mnemonic
            want[e["name"]] = 0
        fetch, step = self.db.vm["fetch_off"], self.db.vm["step_off"]
        wins = c["on"] if isinstance(c["on"], list) else [c["on"]]
        m = self.model
        for w in wins:
            for call in self.sess.calls([step], w, max_calls=int(c.get("max_calls", 100000))):
                r = call.recs
                t, off = r["type"], r["off"]
                seq = []
                for i in np.flatnonzero((t == R_EXEC) & (off == fetch)):
                    k = i + 1
                    while k < len(r) and not (t[k] == R_READ and off[k] != NONE):
                        k += 1
                    if k < len(r):
                        seq.append((int(off[k]), int(r[k]["addr"])))
                for j, (o, addr) in enumerate(seq):
                    spec = vm.table[int(m.prg[o])]
                    if spec is None or spec["name"] not in want:
                        continue
                    ins = vm.decode(o)
                    flow = spec["flow"]
                    # a 16-bit script address may point into the other bank window: compare CPU addresses
                    cpu_targets = {v for t_, v, bank, tgt in ins.args if t_ in ("addr", "far")}
                    if j + 1 < len(seq):
                        nxt, nxt_addr = seq[j + 1]
                        fall = nxt == o + ins.len
                        hit = nxt in ins.targets or nxt_addr in cpu_targets
                    else:                        # last instruction of the step: the saved script pointer
                        x = call.rd.get(0x6F)
                        lo = call.wr.get(0x6380 + x) if x is not None else None
                        hi = call.wr.get(0x63A0 + x) if x is not None else None
                        if lo is None or hi is None:
                            want[spec["name"]] += flow == "stop"
                            continue             # the thread ended or was replaced: nothing to compare
                        nxt_addr = lo | hi << 8
                        fall = nxt_addr == addr + ins.len
                        hit = nxt_addr in cpu_targets
                    if flow == "dyn":            # the handler decides: count only the fall-throughs
                        want[spec["name"]] += fall
                        continue
                    ok = {"next": fall, "spawn": fall, "branch": fall or hit, "jump": hit, "call": hit,
                          "stop": True}[flow]
                    if not ok:
                        return False, (f"{w} frame {call.frame}: {spec['mnemonic']} at {m.name(o)} (declared "
                                       f"length {ins.len}, flow {flow}) continued at ${nxt_addr:04X}"), {}
                    want[spec["name"]] += 1
        need = int(c.get("min", 1))
        missing = [n for n, k in want.items() if k < need]
        if missing:
            return False, f"not executed {need}x in the windows: {', '.join(missing)}", {}
        return True, ", ".join(f"{n[3:]} x{k}" for n, k in want.items()), {"execs": sum(want.values())}

    def _k_vmop(self, c):
        """A statement about every execution of one script opcode: what its handler read and wrote."""
        vm = self.model.vm
        if vm is None:
            return False, "the database has no [vm] / [[opcode]] entries", {}
        kind, spec = self.db.by_name["op_" + c["op"]]
        only = self.O(c["at"]) if c.get("at") else None
        fetch, step = self.db.vm["fetch_off"], self.db.vm["step_off"]
        adv = self.db.vm.get("advance_off")
        wins = c["on"] if isinstance(c["on"], list) else [c["on"]]
        env = self._base_env(c)
        expect = compile(c["expect"], "expect", "eval")
        m = self.model
        used = 0
        for w in wins:
            for call in self.sess.calls([step], w, max_calls=int(c.get("max_calls", 100000))):
                r = call.recs
                t, off = r["type"], r["off"]
                fx = np.flatnonzero((t == R_EXEC) & (off == fetch)).tolist()
                for j, i in enumerate(fx):
                    k = i + 1
                    while k < len(r) and not (t[k] == R_READ and off[k] != NONE):
                        k += 1
                    if k >= len(r):
                        continue
                    o, addr = int(off[k]), int(r[k]["addr"])
                    if vm.table[int(m.prg[o])] is not spec or (only is not None and o != only):
                        continue
                    end = fx[j + 1] if j + 1 < len(fx) else len(r) - 1
                    if adv is not None:          # the handler is over when it comes back to the interpreter
                        back = np.flatnonzero((t[k + 1:end] == R_EXEC) & (off[k + 1:end] == adv))
                        if len(back):
                            end = k + 1 + int(back[0])
                    seg = r[k + 1:end]
                    rd, wr = {}, {}
                    st = seg["type"]
                    rw = seg[(st == R_READ) | (st == R_WRITE)]
                    for typ, a_, v_, o_ in zip(rw["type"].tolist(), rw["addr"].tolist(), rw["val"].tolist(),
                                               rw["off"].tolist()):
                        if typ == R_READ:
                            if o_ == NONE and a_ not in wr and a_ not in rd:
                                rd[a_] = v_
                        else:
                            wr[a_] = v_
                    ins = vm.decode(o)
                    if j + 1 < len(fx):
                        k2 = fx[j + 1] + 1
                        while k2 < len(r) and not (t[k2] == R_READ and off[k2] != NONE):
                            k2 += 1
                        nxt = int(r[k2]["addr"]) if k2 < len(r) else None
                    else:
                        x = call.rd.get(0x6F)
                        lo, hi = call.wr.get(0x6380 + (x or 0)), call.wr.get(0x63A0 + (x or 0))
                        nxt = (lo | hi << 8) if lo is not None and hi is not None else None
                    e = dict(env)
                    e.update(rom=self.rom_bytes, args=[v for t_, v, b_, g_ in ins.args],
                             banks=[b_ for t_, v, b_, g_ in ins.args],
                             op=ins.op, low=ins.op - spec["lo"], addr=addr,
                             length=ins.len, next=nxt, rd=rd, wr=wr, reads=set(rd), writes=set(wr),
                             thread=call.rd.get(0x6F), frame=call.frame,
                             calls=[self.routine_ref(int(seg["off"][q + 1])) for q in
                                    np.flatnonzero((seg["type"][:-1] == R_EXEC) & (seg["val"][:-1] == 0x20))
                                    if seg["type"][q + 1] == R_EXEC])
                    try:
                        ok = eval(expect, e)
                    except Exception as x:
                        return False, f"{w} frame {call.frame} at {m.name(o)}: {type(x).__name__}: {x}", {}
                    if not ok:
                        return False, f"{w} frame {call.frame}: false for {vm.text(ins)} at {m.name(o)}", {}
                    used += 1
        need = int(c.get("min", 5))
        if used < need:
            return False, f"only {used} executions in the windows (min = {need})", {}
        return True, f"{used} executions", {"execs": used}

    def _xref_addrs(self, x):
        if isinstance(x, tuple):
            return range(x[0], x[0] + x[1])
        if isinstance(x, int):
            return range(x, x + 1)
        kind, e = self.db.by_name[x]
        if kind != "ram":
            raise KeyError(f"'{x}' is not a RAM variable")
        return range(e["addr"], e["addr"] + e["len"])

    def _k_xref(self, c):
        env = self._base_env(c)
        ev = self.ev

        def touching(x, want_write):
            out = set()
            for a in self._xref_addrs(x):
                for off, w in ev.ram_xref(a):
                    if bool(w) == want_write:
                        out.add(self.routine_name(off))
            return Routines.of(self.db, out)

        def callers(name):
            return Routines.of(self.db, {self.routine_name(f) for f, t, k in ev.edges_to(self.O(name))
                                         if f != 0xFFFFF})

        def callees(name):
            o = self.O(name)
            return Routines.of(self.db, {self.routine_name(t) for f, t, k in
                                         ev.edges_from(o, self.model.routine_end(o)) if k == 1})

        def datareaders(name):
            kind, e = self.db.by_name[name]
            out = set()
            for arr in (ev.rdr1, ev.rdr2):
                for r in np.unique(arr[e["off"]:e["off"] + e["len"]]):
                    if r:
                        out.add(self.routine_name(int(r) - 1))
            return Routines.of(self.db, out)

        env.update(writers=lambda x: touching(x, True), readers=lambda x: touching(x, False), callers=callers,
                   callees=callees, datareaders=datareaders,
                   touched=lambda x: any(ev.ram_xref(a) for a in self._xref_addrs(x)))
        ok = eval(compile(c["expect"], "expect", "eval"), env)
        if ok:
            return True, "holds over the corpus", {}
        # show what the sets are, so the reader sees which member is new
        import re
        shown = []
        for fn, arg in re.findall(r"(writers|readers|callers|callees|datareaders)\(([^()]*)\)", c["expect"]):
            try:
                shown.append(f"{fn}({arg}) = {eval(f'{fn}({arg})', env)!r}")
            except Exception:
                pass
        return False, "expect is false over the corpus" + ("; " + "; ".join(dict.fromkeys(shown)) if shown else ""), {}

    def _k_format(self, c):
        """Structured data regions against their format and against who read every byte (sprites.py for
        sprite data, packed.py for packed streams and their tables)."""
        import packed
        import sprites
        names = c.get("about", [])
        fam = {}
        for n in names:
            kind, e = self.db.by_name[n]
            f = e.get("format", "").split(":")[0] if kind == "data" else ""
            fam.setdefault(packed if f in packed.FORMATS else sprites, []).append(n)
        problems, st = [], {}
        for mod, ns in fam.items():
            pr, s = mod.check(self.db, self.model, self.ev, ns, bool(c.get("complete")))
            problems += pr
            for k, v in s.items():
                st[k] = st.get(k, 0) + v
        if problems:
            return False, f"{len(problems)} problems, the first: {problems[0]}", {}
        if not st.get("read"):
            return False, "no byte of these regions was read in the corpus", {}
        return True, (f"{st['regions']} regions, {st['bytes']:,} bytes ({st['read']:,} read in the corpus), "
                      + ", ".join(f"{v:,} {k}" for k, v in st.items() if k not in ("regions", "bytes", "read"))), st

    def _k_static(self, c):
        env = self._base_env(c)
        m = self.model
        prg = m.prg

        def u16(at):
            o = at if isinstance(at, int) else self.O(at)
            return int(prg[o]) | (int(prg[o + 1]) << 8)

        env.update(rom=self.rom_bytes, u8=lambda at: int(prg[at if isinstance(at, int) else self.O(at)]), u16=u16,
                   kind=lambda o: chr(m.kind[o]), executed=lambda o: bool(m.flags[o] & 3),
                   dataread=lambda o: bool(m.flags[o] & 4))
        ok = eval(compile(c["expect"], "expect", "eval"), env)
        return bool(ok), "holds" if ok else "expect is false", {}


def _ishex(k):
    try:
        int(k, 16)
        return len(k) <= 4
    except ValueError:
        return False


# ---------------------------------------------------------------- running many claims
_W = {}


def _w_init():
    sys.path.insert(0, HERE)
    import db as DBM
    import rommodel
    d = DBM.DB()
    m = rommodel.Model(EVD.Evidence(), db=d)
    _W["ck"] = Checker(d, m)


def _w_check(claim):
    ok, msg, stats = _W["ck"].check(claim)
    return claim["id"], ok, msg, stats


def claim_key(claim, stamp):
    return hashlib.sha1((json.dumps(claim, sort_keys=True, default=str) + stamp).encode()).hexdigest()


def run_claims(claims, workers=8, use_cache=True, db_stamp=""):
    """-> {id: (ok, message, stats)}. Passes are cached on (claim, corpus, core, names, checker code), so
    unchanged claims are free and anything that could change an outcome changes the key."""
    cache_path = os.path.join(EVD.EV, "claims-cache.json")
    cache = json.load(open(cache_path)) if use_cache and os.path.exists(cache_path) else {}
    stamp = (open(os.path.join(EVD.EV, "core.sha1")).read() + open(EVD.MANIFEST).read() + db_stamp
             + "".join(hashlib.sha1(open(os.path.join(HERE, f), "rb").read()).hexdigest()
                       for f in ("probe.py", "kdcore.py", "rommodel.py", "db.py", "vm.py", "sprites.py", "packed.py")))
    out, todo = {}, []
    for c in claims:
        k = claim_key(c, stamp)
        if k in cache:
            out[c["id"]] = tuple(cache[k])
        else:
            todo.append((k, c))
    if todo:
        n = max(1, min(workers, len(todo)))
        with mp.get_context("spawn").Pool(n, initializer=_w_init) as pool:
            for (k, c), (cid, ok, msg, stats) in zip(todo, pool.imap(_w_check, [c for _, c in todo])):
                out[cid] = (ok, msg, stats)
                if ok:                      # only passes are cached: a failure is always looked at again
                    cache[k] = [ok, msg, stats]
        tmp = cache_path + f".{os.getpid()}.tmp"
        json.dump(cache, open(tmp, "w"))
        os.replace(tmp, cache_path)
    return out
