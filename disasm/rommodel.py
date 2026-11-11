"""rommodel.py - the code/data model of the PRG ROM, built from evidence (what ran, what was read) plus a
conservative static pass (code reachable from code that ran).

Nothing here knows any name: it only says which bytes are instructions, where routines start, which bytes
are data and who reads them. Names and meaning come from the database (db.py).
"""
import numpy as np

PRG = 0x80000
BANK = 0x2000
F_OP, F_ARG, F_DATA, F_CALL, F_JMP, F_IND, F_INT, F_PTR = 1, 2, 4, 8, 16, 32, 64, 128

_T = """
00 brk imp  01 ora izx  05 ora zp   06 asl zp   08 php imp  09 ora imm  0A asl acc  0D ora abs  0E asl abs
10 bpl rel  11 ora izy  15 ora zpx  16 asl zpx  18 clc imp  19 ora aby  1D ora abx  1E asl abx
20 jsr abs  21 and izx  24 bit zp   25 and zp   26 rol zp   28 plp imp  29 and imm  2A rol acc  2C bit abs
2D and abs  2E rol abs
30 bmi rel  31 and izy  35 and zpx  36 rol zpx  38 sec imp  39 and aby  3D and abx  3E rol abx
40 rti imp  41 eor izx  45 eor zp   46 lsr zp   48 pha imp  49 eor imm  4A lsr acc  4C jmp abs  4D eor abs
4E lsr abs
50 bvc rel  51 eor izy  55 eor zpx  56 lsr zpx  58 cli imp  59 eor aby  5D eor abx  5E lsr abx
60 rts imp  61 adc izx  65 adc zp   66 ror zp   68 pla imp  69 adc imm  6A ror acc  6C jmp ind  6D adc abs
6E ror abs
70 bvs rel  71 adc izy  75 adc zpx  76 ror zpx  78 sei imp  79 adc aby  7D adc abx  7E ror abx
81 sta izx  84 sty zp   85 sta zp   86 stx zp   88 dey imp  8A txa imp  8C sty abs  8D sta abs  8E stx abs
90 bcc rel  91 sta izy  94 sty zpx  95 sta zpx  96 stx zpy  98 tya imp  99 sta aby  9A txs imp  9D sta abx
A0 ldy imm  A1 lda izx  A2 ldx imm  A4 ldy zp   A5 lda zp   A6 ldx zp   A8 tay imp  A9 lda imm  AA tax imp
AC ldy abs  AD lda abs  AE ldx abs
B0 bcs rel  B1 lda izy  B4 ldy zpx  B5 lda zpx  B6 ldx zpy  B8 clv imp  B9 lda aby  BA tsx imp  BC ldy abx
BD lda abx  BE ldx aby
C0 cpy imm  C1 cmp izx  C4 cpy zp   C5 cmp zp   C6 dec zp   C8 iny imp  C9 cmp imm  CA dex imp  CC cpy abs
CD cmp abs  CE dec abs
D0 bne rel  D1 cmp izy  D5 cmp zpx  D6 dec zpx  D8 cld imp  D9 cmp aby  DD cmp abx  DE dec abx
E0 cpx imm  E1 sbc izx  E4 cpx zp   E5 sbc zp   E6 inc zp   E8 inx imp  E9 sbc imm  EA nop imp  EC cpx abs
ED sbc abs  EE inc abs
F0 beq rel  F1 sbc izy  F5 sbc zpx  F6 inc zpx  F8 sed imp  F9 sbc aby  FD sbc abx  FE inc abx
"""
OPS = {}
_tok = _T.split()
for _i in range(0, len(_tok), 3):
    OPS[int(_tok[_i], 16)] = (_tok[_i + 1], _tok[_i + 2])
MODE_LEN = {"imp": 1, "acc": 1, "imm": 2, "zp": 2, "zpx": 2, "zpy": 2, "izx": 2, "izy": 2, "rel": 2, "abs": 3,
            "abx": 3, "aby": 3, "ind": 3}
BRANCHES = {0x10, 0x30, 0x50, 0x70, 0x90, 0xB0, 0xD0, 0xF0}
STOPS = {0x40, 0x60, 0x4C, 0x6C, 0x00}          # rti rts jmp jmp() brk: no fall-through
WRITES = {"sta", "stx", "sty", "inc", "dec", "asl", "lsr", "rol", "ror"}


def op_len(op):
    return MODE_LEN[OPS[op][1]] if op in OPS else 1


class Ins:
    __slots__ = ("off", "op", "mn", "mode", "len", "operand", "static")

    def __init__(self, prg, off, static=False):
        self.off = off
        self.op = int(prg[off])
        self.mn, self.mode = OPS.get(self.op, (None, None))
        self.len = MODE_LEN[self.mode] if self.mn else 1
        self.static = static
        if self.len == 2:
            self.operand = int(prg[off + 1])
        elif self.len == 3:
            self.operand = int(prg[off + 1]) | (int(prg[off + 2]) << 8)
        else:
            self.operand = None


class Model:
    """kind[off]: 'c' instruction start, 'a' operand byte, 'd' data, 'f' fill, '?' never touched,
    's' / 't' script instruction start / operand (when the database describes the script interpreter).
    dyn[off]: True when the classification comes from the runtime (executed / read), False when static."""

    def __init__(self, ev, db=None, static=True):
        self.ev = ev
        self.db = db
        self.prg = ev.prg
        f = ev.flags[:PRG]
        self.flags = f
        self.base = [ev.bank_base(b) for b in range(64)]
        # banks never touched by the corpus: assume the window of the nearest touched bank below
        last = 0x8000
        for b in range(64):
            if self.base[b] is None:
                self.base[b] = last
                self.assumed_base = getattr(self, "assumed_base", []) + [b]
            else:
                last = self.base[b]
        self.assumed_base = getattr(self, "assumed_base", [])
        self.kind = np.full(PRG, ord("?"), dtype=np.uint8)
        self.dyn = np.zeros(PRG, dtype=bool)
        self.kind[(f & F_DATA) != 0] = ord("d")
        self.dyn[(f & F_DATA) != 0] = True
        ops = np.flatnonzero(f & F_OP)
        self.kind[ops] = ord("c")
        self.dyn[ops] = True
        self.overlaps = []          # instruction starts inside another executed instruction (kept as executed)
        for o in ops:
            n = op_len(int(self.prg[o]))
            for i in range(1, n):
                if o + i < PRG and (o + i) >> 13 == o >> 13:
                    if self.kind[o + i] == ord("c"):
                        self.overlaps.append(int(o + i))
                    else:
                        self.kind[o + i] = ord("a")
                        self.dyn[o + i] = True
        self.entries = {}           # off -> set of kinds ('call', 'int', 'ind', 'static')
        self.labels = set()         # branch / jump targets
        for o in np.flatnonzero(f & (F_CALL | F_INT | F_IND)):
            k = set()
            if f[o] & F_CALL:
                k.add("call")
            if f[o] & F_INT:
                k.add("int")
            if f[o] & F_IND:
                k.add("ind")
            self.entries[int(o)] = k
        for o in np.flatnonzero(f & F_JMP):
            self.labels.add(int(o))
        self.static_rejected = 0
        self.cuts = set()           # database syms of kind sub / part: routine boundaries of their own
        # routines that take parameter bytes from behind the jsr and return past them ([[sym]] inline = N):
        # the bytes belong to the call, and the code after them is the same routine going on
        self.inline_subs = {e["off"]: int(e["inline"]) for e in db.syms if e.get("inline")} if db is not None else {}
        self.inline = {}            # offset of an inline parameter byte -> offset of its jsr
        db_roots = []
        if db is not None:
            for e in db.data:       # a database data region claims never-touched bytes as data
                seg = self.kind[e["off"]:e["off"] + e["len"]]
                seg[seg == ord("?")] = ord("d")
            for e in db.syms:
                if e["kind"] in ("sub", "part"):
                    self.cuts.add(e["off"])
                    if self.kind[e["off"]] == ord("?"):
                        db_roots.append(e["off"])
        if static:
            self._static_pass(db_roots)
        self._inline_calls()
        self.vm = None
        if db is not None and db.opcodes and db.vm.get("fetch_off") is not None:
            import vm as VMM
            self.vm = VMM.VM(db, self)       # scripts: marks kind 's' (opcode) and 't' (operand)
        self._fill()
        self._labels_from_code()

    # ---- addresses ----
    def cpu(self, off):
        return self.base[off >> 13] + (off & 0x1FFF)

    def name(self, off):
        if off == 0xFFFFF:
            return "hardware"
        if off >= PRG:
            return f"RAM:{off - PRG:04X}"
        return f"{off >> 13:02X}:{self.cpu(off):04X}"

    def resolve(self, ins_off, addr):
        """CPU address used by the instruction at ins_off -> PRG offset, or None when it is not ROM or the
        bank cannot be known statically (another switchable window)."""
        if addr < 0x8000:
            return None
        bank = ins_off >> 13
        if self.base[bank] <= addr < self.base[bank] + BANK:
            return bank * BANK + (addr & 0x1FFF)
        if addr >= 0xC000:
            fixed = 0x3E if addr < 0xE000 else 0x3F
            if self.base[fixed] == (addr & 0xE000):
                return fixed * BANK + (addr & 0x1FFF)
        return None

    def ins(self, off):
        return Ins(self.prg, off, static=not self.dyn[off])

    def successors(self, ins):
        """Statically known next instruction offsets (same-bank / fixed-bank only)."""
        out = []
        nxt = ins.off + ins.len + self.inline_n(ins)
        if ins.op not in STOPS and nxt >> 13 == ins.off >> 13:
            out.append(nxt)
        if ins.op in BRANCHES:
            d = ins.operand - 256 if ins.operand > 127 else ins.operand
            t = ins.off + 2 + d
            if t >> 13 == ins.off >> 13:
                out.append(t)
        elif ins.op in (0x4C, 0x20):
            t = self.resolve(ins.off, ins.operand)
            if t is not None:
                out.append(t)
        return out

    def inline_n(self, ins):
        """Number of parameter bytes behind this instruction: nonzero for a jsr to an `inline` routine."""
        if ins.op != 0x20 or not self.inline_subs:
            return 0
        t = self.resolve(ins.off, ins.operand)
        return self.inline_subs.get(t, 0) if t is not None else 0

    def _inline_calls(self):
        """Parameter bytes behind a jsr to an `inline` routine become operand bytes of the call, and the code
        after them stops being a routine entry when the only way in is the helper's return."""
        k = self.kind
        C, A = ord("c"), ord("a")
        named = {e["off"] for e in self.db.syms} if self.db is not None else set()
        for o in np.flatnonzero(k == C):
            o = int(o)
            if self.prg[o] != 0x20:
                continue
            ins = Ins(self.prg, o)
            n = self.inline_n(ins)
            if not n or (o + 3 + n) >> 13 != o >> 13 or any(k[o + 3 + i] == C for i in range(n)):
                continue
            for i in range(n):
                k[o + 3 + i] = A
                self.dyn[o + 3 + i] = False
                self.inline[o + 3 + i] = o
            cont = o + 3 + n
            if cont in self.entries and cont not in named and self.entries[cont] <= {"ind"} \
                    and all(kind == 4 for _, _, kind in self.ev.edges_to(cont)):
                del self.entries[cont]

    # ---- static pass: code reachable from executed code, never overriding the runtime ----
    def _static_pass(self, db_roots=()):
        k = self.kind
        C, A, U = ord("c"), ord("a"), ord("?")
        roots = [(o, False) for o in db_roots]
        for o in np.flatnonzero(k == C):
            ins = Ins(self.prg, int(o))
            for t in self.successors(ins):
                if k[t] == U:
                    roots.append((t, ins.op == 0x20))
        seen_static = {}
        while roots:
            root, is_call = roots.pop()
            if k[root] != U:
                continue
            # speculative run from this root: all-or-nothing
            run, stack, ok, new_roots = {}, [root], True, []
            while stack and ok:
                o = stack.pop()
                if o in run or k[o] == C:
                    continue
                if k[o] != U:                       # lands on an operand or on data: not code
                    ok = False
                    break
                ins = Ins(self.prg, o, static=True)
                if ins.mn is None or ins.op == 0x00 or (o + ins.len - 1) >> 13 != o >> 13:
                    ok = False
                    break
                if any(k[o + i] != U or (o + i) in run for i in range(1, ins.len)):
                    ok = False
                    break
                run[o] = ins
                for t in self.successors(ins):
                    if ins.op == 0x20 and t != o + ins.len + self.inline_n(ins):
                        new_roots.append((t, True))   # callee: its own speculative run
                    else:
                        stack.append(t)
            # a run must not put an instruction start inside another instruction of the same run
            if ok:
                covered = set()
                for o, ins in run.items():
                    for i in range(1, ins.len):
                        covered.add(o + i)
                ok = not (covered & set(run))
            if not ok:
                self.static_rejected += 1
                continue
            for o, ins in run.items():
                k[o] = C
                for i in range(1, ins.len):
                    k[o + i] = A
                seen_static[o] = ins
            if is_call:
                self.entries.setdefault(root, set()).add("static")
            roots.extend(new_roots)
        self.static_ops = len(seen_static)

    def _fill(self):
        """Never-touched runs of one repeated byte value ($FF or $00), 16 bytes or longer -> 'f'."""
        k = self.kind
        unk = (k == ord("?")).astype(np.int8)
        d = np.diff(np.concatenate(([0], unk, [0])))
        for s, e in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1)):
            seg = self.prg[s:e]
            if e - s >= 16 and seg[0] in (0x00, 0xFF) and (seg == seg[0]).all():
                k[s:e] = ord("f")

    def _labels_from_code(self):
        C = ord("c")
        self.data_refs = {}         # data offset -> set of instruction offsets that name it as an operand
        for o in np.flatnonzero(self.kind == C):
            ins = Ins(self.prg, int(o))
            if ins.op in BRANCHES:
                d = ins.operand - 256 if ins.operand > 127 else ins.operand
                t = ins.off + 2 + d
                if t >> 13 == ins.off >> 13:
                    self.labels.add(t)
            elif ins.op == 0x4C:
                t = self.resolve(ins.off, ins.operand)
                if t is not None:
                    self.labels.add(t)
            elif ins.op == 0x20:
                t = self.resolve(ins.off, ins.operand)
                if t is not None and self.kind[t] == C:
                    self.entries.setdefault(t, set()).add("static")
            elif ins.mode in ("abs", "abx", "aby") and ins.operand >= 0x8000:
                t = self.resolve(ins.off, ins.operand)
                if t is not None and self.kind[t] != C:
                    self.data_refs.setdefault(t, set()).add(ins.off)

    # ---- chunks: the automatic partition ----
    def chunks(self, bank=None):
        """[(start, end, kind)] covering the bank(s): kind 'code' (starts at an entry or at the start of a
        code run), 'data', 'fill', 'unknown'. Code is cut at routine entries, data at referenced addresses
        and where the reading instruction changes."""
        out = []
        banks = range(64) if bank is None else [bank]
        k = self.kind
        C, A, D, FL = ord("c"), ord("a"), ord("d"), ord("f")
        S, T = ord("s"), ord("t")
        # a documented script runs over its own labels (vm.extent): only labels outside them cut a chunk
        slabels = ((self.vm.labels - self.vm.covered()) | self.vm.cuts) if self.vm else set()
        for b in banks:
            lo, hi = b * BANK, (b + 1) * BANK
            o = lo
            while o < hi:
                kk = k[o]
                s = o
                if kk in (C, A):
                    o += 1
                    while o < hi and k[o] in (C, A) and not (k[o] == C and (o in self.entries or o in self.cuts)):
                        o += 1
                    out.append((s, o, "code"))
                elif kk in (S, T):
                    o += 1
                    while o < hi and k[o] in (S, T) and not (k[o] == S and o in slabels):
                        o += 1
                    out.append((s, o, "script"))
                elif kk == D:
                    o += 1
                    while o < hi and k[o] == D and o not in self.data_refs:
                        o += 1
                    out.append((s, o, "data"))
                else:
                    o += 1
                    while o < hi and k[o] == kk and o not in self.data_refs:
                        o += 1
                    out.append((s, o, "fill" if kk == FL else "unknown"))
        return out

    def routine_end(self, entry):
        """End (exclusive) of the code run that starts at entry, stopping at the next entry."""
        k = self.kind
        C, A = ord("c"), ord("a")
        hi = ((entry >> 13) + 1) * BANK
        o = entry + 1
        while o < hi and k[o] in (C, A) and not (k[o] == C and (o in self.entries or o in self.cuts)):
            o += 1
        return o

    def walk(self, lo, hi):
        """Instructions in [lo, hi) in address order (starting at an instruction start)."""
        o = lo
        C = ord("c")
        while o < hi:
            if self.kind[o] == C:
                ins = self.ins(o)
                yield ins
                o += ins.len
            else:
                o += 1

    def one_sided(self, lo=0, hi=PRG):
        """Executed conditional branches of which one side never ran: [(off, 'taken'|'fallthrough' missing)]."""
        out = []
        f = self.flags
        for o in np.flatnonzero((f[lo:hi] & F_OP) != 0) + lo:
            op = int(self.prg[o])
            if op in BRANCHES:
                d = int(self.prg[o + 1])
                t = o + 2 + (d - 256 if d > 127 else d)
                if t >> 13 != o >> 13:
                    continue
                if not f[t] & F_OP:
                    out.append((int(o), "taken"))
                elif not f[o + 2] & F_OP:
                    out.append((int(o), "fallthrough"))
        return out
