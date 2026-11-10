"""vm.py - the object-script bytecode as a second instruction set.

The game runs every object from scripts interpreted by a small virtual machine. To the CPU a script is data;
to the documentation it is code. This module gives scripts the same treatment the 6502 gets in rommodel.py:

  - evidence: a byte is a script instruction when the interpreter's opcode-fetch instruction read it
    ([vm] fetch in the database names that instruction);
  - a decoder driven by the [[opcode]] entries of the database (operand layout and control flow);
  - a static pass that follows fall-through and jump targets from the instructions that ran;
  - consistency problems: an opcode that ran but is not in the table, an operand byte that was fetched as an
    opcode (the declared length is wrong).

Operand types: u8 s8 var (1 byte), u16 s16 (2), mem (a RAM address, 2), addr (script address in the same
bank, 2), code (6502 address, 2), far (script address + bank, 3), codefar / datafar (6502 code / data address +
bank, 3), and the counted tables addrs / fars / codefars (a count byte, then that many addr / far / codefar).
Flow: next | stop | jump | branch | call | spawn | dyn. jump, branch, call and spawn use the addr / far
operands as targets; dyn continues wherever the opcode's handler decides (often the next instruction).
"""
import numpy as np

PRG = 0x80000
BANK = 0x2000
ARG_SIZE = {"u8": 1, "s8": 1, "var": 1, "u16": 2, "s16": 2, "mem": 2, "addr": 2, "code": 2, "far": 3,
            "codefar": 3, "datafar": 3}
TABLES = {"addrs": "addr", "fars": "far", "codefars": "codefar"}
ARGS = tuple(ARG_SIZE) + tuple(TABLES)
FLOWS = ("next", "stop", "jump", "branch", "call", "spawn", "dyn")
S, T = ord("s"), ord("t")


class SIns:
    __slots__ = ("off", "op", "spec", "len", "args", "targets", "falls", "short")

    @property
    def target(self):
        return self.targets[0] if self.targets else None


class VM:
    def __init__(self, db, model):
        self.db, self.m = db, model
        self.ok = bool(db.vm.get("fetch")) and bool(db.opcodes)
        self.table = [None] * 256
        for e in db.opcodes:
            for b in range(e["lo"], e["hi"] + 1):
                self.table[b] = e
        self.fetch = db.vm.get("fetch_off")
        self.starts = set()          # instruction starts (dynamic and static)
        self.dynamic = set()
        self.labels = set()          # script addresses that other instructions name, and run starts
        self.unknown = {}            # opcode byte -> [offsets] fetched at runtime but not in the table
        self.conflicts = []          # (instruction offset, operand offset that was fetched as an opcode)
        self.short_tables = []       # (offset, declared entries, real entries): see decode()
        self.fetched = set()
        if self.ok:
            f = self.fetch + 1
            ev = model.ev
            self.fetched = set(np.flatnonzero((ev.rdr1 == f) | (ev.rdr2 == f)).tolist())
            self._build()

    # ---- decoding ----
    def decode(self, off):
        m = self.m
        op = int(m.prg[off])
        spec = self.table[op]
        if spec is None:
            return None
        i = SIns()
        i.off, i.op, i.spec = off, op, spec
        i.args, i.targets, i.short = [], [], None
        p = off + 1
        end = (off | 0x1FFF) + 1
        todo = []
        for t in spec["args"]:
            if t in TABLES:
                if p >= end:
                    return None
                cnt = int(m.prg[p])
                i.args.append(("u8", cnt, None))
                p += 1
                todo += [TABLES[t]] * cnt
            else:
                todo.append(t)
            while todo:
                t2 = todo.pop(0)
                n = ARG_SIZE[t2]
                if t in TABLES and p in self.fetched:
                    # the table's declared count runs into an instruction that ran: the runtime wins. (A script
                    # can declare one entry more than it has when the index never gets that high.)
                    i.short = (cnt, cnt - len(todo) - 1)
                    todo = []
                    break
                if p + n > end:
                    return None
                v = int(m.prg[p]) | (int(m.prg[p + 1]) << 8 if n >= 2 else 0)
                bank = int(m.prg[p + 2]) if n == 3 else None
                tgt = None
                if t2 == "addr" and m.base[off >> 13] <= v < m.base[off >> 13] + BANK:
                    tgt = (off & ~0x1FFF) | (v & 0x1FFF)
                elif t2 == "far" and bank < 0x40 and m.base[bank] <= v < m.base[bank] + BANK:
                    tgt = bank * BANK + (v & 0x1FFF)
                i.args.append((t2, v, bank, tgt))
                if tgt is not None:
                    i.targets.append(tgt)
                p += n
        i.args = [a if len(a) == 4 else a + (None,) for a in i.args]
        i.len = p - off
        # after a dyn instruction (a call into 6502 code) the script may continue anywhere: the routine can
        # consume inline parameter bytes, so the static pass does not assume fall-through
        i.falls = spec["flow"] in ("next", "branch", "call", "spawn")
        return i

    def text(self, i, label_for=lambda off: None):
        parts = []
        for t, v, bank, tgt in i.args:
            if tgt is not None and label_for(tgt):
                parts.append(label_for(tgt))
            elif t in ("far", "codefar", "datafar"):
                parts.append(f"${bank:02X}:{v:04X}")
            elif t == "mem":
                parts.append(self.db.ram_name(v) or f"${v:04X}")
            elif t in ("u16", "addr", "code"):
                parts.append(f"${v:04X}")
            elif t == "s16":
                parts.append(str(v - 0x10000 if v > 0x7FFF else v))
            elif t == "s8":
                parts.append(str(v - 0x100 if v > 0x7F else v))
            elif t == "var":
                parts.append(f"var{v}")
            else:
                parts.append(f"${v:02X}")
        name = i.spec["mnemonic"]
        if i.spec["lo"] != i.spec["hi"]:
            parts.append(f"+{i.op - i.spec['lo']}")        # the family's low bits (a wait count)
        return (name + " " + ", ".join(parts)).strip()

    # ---- the model ----
    def _build(self):
        m = self.m
        k = m.kind
        dyn = sorted(self.fetched)
        C, A = ord("c"), ord("a")
        for o in dyn:
            o = int(o)
            if k[o] in (C, A):
                continue
            ins = self.decode(o)
            if ins is None:
                self.unknown.setdefault(int(m.prg[o]), []).append(o)
                continue
            self.dynamic.add(o)
        dynset = self.dynamic
        claimed = {}
        for o in sorted(dynset):
            ins = self.decode(o)
            for j in range(1, ins.len):
                if o + j in dynset:
                    self.conflicts.append((o, o + j))
            self.starts.add(o)
            claimed[o] = ins
        operand = set()
        for o, ins in claimed.items():
            operand.update(range(o + 1, o + ins.len))
        # static pass: follow fall-through and targets into bytes nothing else claims
        work = []
        for o, ins in claimed.items():
            if ins.falls:
                work.append(o + ins.len)
            for t in ins.targets:
                work.append(t)
                self.labels.add(t)
        self.static = set()
        while work:
            root = work.pop()
            if root in self.starts or root >= PRG:
                continue
            run, stack, ok = {}, [root], True
            while stack and ok:
                o = stack.pop()
                if o in run or o in self.starts:
                    continue
                if o in operand or k[o] in (C, A) or (o >> 13) != (root >> 13):
                    ok = False
                    break
                ins = self.decode(o)
                if ins is None or any((o + j) in self.starts or (o + j) in run or k[o + j] in (C, A)
                                      for j in range(1, ins.len)):
                    ok = False
                    break
                run[o] = ins
                if ins.falls:
                    stack.append(o + ins.len)
                for t in ins.targets:
                    if (t >> 13) == (o >> 13):
                        stack.append(t)
            if ok and run:
                body = set()
                for o, ins in run.items():
                    body.update(range(o + 1, o + ins.len))
                ok = not (body & set(run)) and not (body & self.starts)
            if not ok:
                continue
            for o, ins in run.items():
                self.starts.add(o)
                self.static.add(o)
                claimed[o] = ins
                operand.update(range(o + 1, o + ins.len))
                for t in ins.targets:
                    self.labels.add(t)
                    if t not in self.starts:
                        work.append(t)
        self.ins = claimed
        self.short_tables = sorted((o, *ins.short) for o, ins in claimed.items() if ins.short)
        for o, ins in claimed.items():
            k[o] = S
            for j in range(1, ins.len):
                if k[o + j] not in (C, A) and (o + j) not in claimed:
                    k[o + j] = T
        # a run start is a label too
        for o in claimed:
            if o & 0x1FFF == 0 or k[o - 1] not in (S, T):
                self.labels.add(o)
        self.labels &= set(claimed)

    def problems(self):
        out = []
        for op, offs in sorted(self.unknown.items()):
            out.append(f"script opcode ${op:02X} ran ({len(offs)} places, first {self.m.name(offs[0])}) "
                       f"but has no [[opcode]] entry")
        for o, j in self.conflicts[:10]:
            out.append(f"script instruction at {self.m.name(o)} ({self.table[int(self.m.prg[o])]['name']}): its "
                       f"operand byte {self.m.name(j)} was fetched as an opcode; the declared length is wrong")
        if len(self.conflicts) > 10:
            out.append(f"... and {len(self.conflicts) - 10} more operand/opcode conflicts")
        return out

    def script_end(self, start):
        """End (exclusive) of the script run starting at a label, stopping at the next label."""
        k = self.m.kind
        hi = (start | 0x1FFF) + 1
        o = start + 1
        while o < hi and k[o] in (S, T) and not (k[o] == S and (o in self.labels or o in self.cuts)):
            o += 1
        return o

    @property
    def cuts(self):
        return {e["off"] for e in self.db.scripts}

    def opcode_use(self):
        """opcode entry name -> (places that ran, total fetches, first (movie, frame))."""
        out = {}
        ev = self.m.ev
        for o in self.dynamic:
            e = self.table[int(self.m.prg[o])]
            n, c, first = out.get(e["name"], (0, 0, None))
            t = int(ev.first[o])
            out[e["name"]] = (n + 1, c + int(ev.dcount[o]), t if first is None or (t and t < first) else first)
        return out
