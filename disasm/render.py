"""render.py - the documented source, generated: model (what the bytes are) + database (what they mean).

  out/src/bankNN.s    ca65 source for each 8 KiB PRG bank, with names, comments and evidence notes
  out/src/ram.inc     RAM variables and hardware registers
  out/build/          assembled banks; `build()` compares the reassembled ROM with the original byte for byte

The source is never edited by hand: every name and comment lives in db/*.toml, so re-rendering after new
evidence loses nothing.
"""
import os
import subprocess
import textwrap
from concurrent.futures import ThreadPoolExecutor

import numpy as np

import rommodel as RM
from rommodel import BANK, PRG, BRANCHES, WRITES

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
CC65 = os.path.join(HERE, "core/cc65/bin")

HW = {0x2000: "PPUCTRL", 0x2001: "PPUMASK", 0x2002: "PPUSTATUS", 0x2003: "OAMADDR", 0x2004: "OAMDATA",
      0x2005: "PPUSCROLL", 0x2006: "PPUADDR", 0x2007: "PPUDATA", 0x4000: "SQ1_VOL", 0x4001: "SQ1_SWEEP",
      0x4002: "SQ1_LO", 0x4003: "SQ1_HI", 0x4004: "SQ2_VOL", 0x4005: "SQ2_SWEEP", 0x4006: "SQ2_LO",
      0x4007: "SQ2_HI", 0x4008: "TRI_LINEAR", 0x400A: "TRI_LO", 0x400B: "TRI_HI", 0x400C: "NOISE_VOL",
      0x400E: "NOISE_LO", 0x400F: "NOISE_HI", 0x4010: "DMC_FREQ", 0x4011: "DMC_RAW", 0x4012: "DMC_START",
      0x4013: "DMC_LEN", 0x4014: "OAMDMA", 0x4015: "SND_CHN", 0x4016: "JOY1", 0x4017: "JOY2"}
MMC3 = {0x8000: "MMC3 bank select", 0x8001: "MMC3 bank data", 0xA000: "MMC3 mirroring", 0xA001: "MMC3 PRG-RAM protect",
        0xC000: "MMC3 IRQ latch", 0xC001: "MMC3 IRQ reload", 0xE000: "MMC3 IRQ disable", 0xE001: "MMC3 IRQ enable"}
C, A_, D, FL, U = ord("c"), ord("a"), ord("d"), ord("f"), ord("?")


class Renderer:
    def __init__(self, model, db):
        self.m, self.db, self.ev = model, db, model.ev
        self.names = {}
        m = model
        for e in db.syms:
            self.names[e["off"]] = e["name"]
        for e in db.data:
            self.names[e["off"]] = e["name"]
        for e in db.scripts:
            self.names[e["off"]] = e["name"]
        if m.vm:
            for o in m.vm.labels:
                self.names.setdefault(o, "scr_" + self._tag(o))
        self.chunks = {b: self._bank_chunks(b) for b in range(64)}
        for b in range(64):
            for s, e, kind, entry in self.chunks[b]:
                if s in self.names:
                    continue
                if kind == "code":
                    self.names[s] = ("sub_" if s in m.entries else "loc_") + self._tag(s)
                elif kind == "data" and (s in m.data_refs or entry is None):
                    self.names[s] = "dat_" + self._tag(s)
        for o in m.labels:
            if o not in self.names and m.kind[o] == C:
                self.names[o] = "loc_" + self._tag(o)
        for o in m.data_refs:
            if o not in self.names and db.data_at(o) is None:
                self.names[o] = "dat_" + self._tag(o)
        # pointer tables in the database name their targets
        self.ptr_targets = {}
        for e in db.data:
            f = e["format"].split(":")
            if f[0] in ("ptr16", "ptr16m1"):
                for i in range(0, e["len"] - 1, 2):
                    v = int(m.prg[e["off"] + i]) | (int(m.prg[e["off"] + i + 1]) << 8)
                    t = self._ptr_off(e, v + (1 if f[0] == "ptr16m1" else 0), f)
                    if t is not None:
                        self.ptr_targets[e["off"] + i] = t
                        if t not in self.names and db.data_at(t) is None:
                            self.names[t] = ("loc_" if m.kind[t] == C else "dat_") + self._tag(t)
            elif f[0] == "poseptr" and m.base[int(f[1], 16)] == 0x8000:
                # pointers to sprite groups: a label at every group a table points to
                import sprites
                for i, t in enumerate(sprites.table_targets(m.prg, e)):
                    if t is not None:
                        self.ptr_targets[e["off"] + 2 * i] = t
                        d = db.data_at(t)
                        if t not in self.names and not (d and d[1] == 0):
                            self.names[t] = "spr_" + self._tag(t)

    def _tag(self, off):
        return f"{off >> 13:02X}_{self.m.cpu(off):04X}"

    def _ptr_off(self, e, addr, f):
        if len(f) > 1:
            bank = int(f[1], 16)
            if self.m.base[bank] <= addr < self.m.base[bank] + BANK:
                return bank * BANK + (addr & 0x1FFF)
            return None
        return self.m.resolve(e["off"], addr)

    def _bank_chunks(self, b):
        """[(start, end, kind, db data entry or None)] for a bank: database data regions first, the
        automatic partition around them."""
        out = []
        regs = [e for e in self.db.data_sorted if e["off"] >> 13 == b]
        ri = 0
        for s, e, kind in self.m.chunks(b):
            while s < e:
                while ri < len(regs) and regs[ri]["off"] + regs[ri]["len"] <= s:
                    ri += 1
                if ri < len(regs) and regs[ri]["off"] <= s:
                    r = regs[ri]
                    end = min(e, r["off"] + r["len"])
                    if out and out[-1][3] is r:
                        out[-1] = (out[-1][0], end, "data", r)
                    else:
                        out.append((s, end, "data", r))
                    s = end
                else:
                    end = min(e, regs[ri]["off"]) if ri < len(regs) and regs[ri]["off"] < e else e
                    out.append((s, end, kind, None))
                    s = end
        return out

    # ---- operands ----
    def label_for(self, off):
        """Name (possibly name+N) for a PRG offset, or None."""
        if off in self.names:
            return self.names[off]
        d = self.db.data_at(off)
        if d:
            return f"{d[0]['name']}+{d[1]}"
        return None

    def dyn_targets(self, ins):
        """Where the instruction really went / read, from the runtime: a list of PRG offsets (or [])."""
        if ins.op in (0x20, 0x4C):
            return sorted({t for f, t, k in self.ev.edges_from(ins.off, ins.off + 1) if t < PRG})
        lo, hi = int(self.ev.rdmin[ins.off]), int(self.ev.rdmax[ins.off])
        if lo != 0xFFFFFFFF and lo >> 13 == hi >> 13:
            return [lo]
        return []

    def operand(self, ins):
        """-> (operand text, comment or None, external PRG offsets referenced)."""
        m, mode, v = self.m, ins.mode, ins.operand
        if mode in ("imp",):
            return "", None
        if mode == "acc":
            return "a", None
        if mode == "imm":
            return f"#${v:02X}", None
        note = None
        if mode == "rel":
            t = ins.off + 2 + (v - 256 if v > 127 else v)
            return self.names.get(t) or f"${m.cpu(t):04X}", None
        if mode in ("zp", "zpx", "zpy", "izx", "izy"):
            txt = self.db.ram_name(v) or f"${v:02X}"
        elif v < 0x2000 or 0x6000 <= v < 0x8000:
            txt = self.db.ram_name(v) or f"${v:04X}"
            if v < 0x100:
                txt = "a:" + txt
        elif v < 0x8000:
            txt = HW.get(v, f"${v:04X}")
        elif ins.mn in WRITES:
            txt = f"${v:04X}"
            reg = MMC3.get(v & 0xE001)
            note = reg if reg else None
        else:
            t = m.resolve(ins.off, v)
            if t is None:
                dyn = self.dyn_targets(ins)
                banks = {o >> 13 for o in dyn}
                if len(banks) == 1 and ins.op in (0x20, 0x4C) and len(dyn) == 1 and m.cpu(dyn[0]) == v:
                    t = dyn[0]
                elif dyn:
                    note = "runtime: " + ", ".join(self.label_for(o) or m.name(o) for o in dyn[:4]) + \
                        (" ..." if len(dyn) > 4 else "")
            lab = self.label_for(t) if t is not None else None
            if lab and (t >> 13) != (ins.off >> 13):
                self.ext.add(t if t in self.names else self.db.data_at(t)[0]["off"])
            txt = lab or f"${v:04X}"
        suffix = {"zp": "", "abs": "", "zpx": ",x", "abx": ",x", "zpy": ",y", "aby": ",y"}.get(mode)
        if suffix is not None:
            return txt + suffix, note
        if mode == "ind":
            return f"({txt[2:] if txt.startswith('a:') else txt})", note
        if mode == "izx":
            return f"({txt},x)", note
        return f"({txt}),y", note

    # ---- one bank ----
    def bank_source(self, b):
        m, db = self.m, self.db
        self.ext = set()
        base = m.base[b]
        L = []
        lo = b * BANK

        def addr(o):
            return base + (o - lo)

        def label_lines(o):
            n = self.names.get(o)
            return [f"{n}:"] if n else []

        for s, e, kind, entry in self.chunks[b]:
            if kind == "code":
                L += self._routine_header(s, e)
                o = s
                while o < e:
                    if m.kind[o] != C:        # operand byte reached as a start (overlap) - cannot happen in a run
                        L.append(f"    .byte ${m.prg[o]:02X}")
                        o += 1
                        continue
                    ins = m.ins(o)
                    L += label_lines(o) if o != s else []
                    if o + ins.len > e:       # its operand is the next routine's first instruction (a skip trick)
                        raw = ", ".join(f"${x:02X}" for x in m.prg[o:e])
                        L.append(f"    .byte {raw:<22}; {ins.mn} with the following byte(s) as operand: skips them")
                        o = e
                        continue
                    inner = [i for i in range(1, ins.len) if (o + i) in self.names]
                    for i in inner:           # a label inside the instruction (overlapping code)
                        L.append(f"{self.names[o + i]} := * + {i}")
                    L.append(self._ins_line(ins))
                    o += ins.len
            elif kind == "data":
                L += self._data(s, e, entry)
            elif kind == "script":
                L += self._script(s, e)
            else:
                n = e - s
                L.append("")
                L += label_lines(s)
                v = int(m.prg[s])
                if kind == "fill":
                    L.append(f"    .res {n}, ${v:02X}        ; fill, never touched")
                else:
                    L.append(f"; {n} bytes never executed or read in the corpus")
                    L += self._bytes(s, e)
        head = [f"; Kirby's Adventure (USA, Rev A) - PRG bank ${b:02X}, mapped at ${base:04X}"
                + (" (window assumed: the corpus never touched this bank)" if b in m.assumed_base else ""),
                "; Generated by `kd render` from the ROM, the evidence and db/*.toml. Do not edit: edit the database.",
                "", '.include "ram.inc"', ""]
        ext = sorted(self.ext)
        if ext:
            head.append("; names defined in other banks")
            head += [f"{self.names[o]} := ${m.cpu(o):04X}        ; bank ${o >> 13:02X}" for o in ext]
            head.append("")
        head += [".segment \"CODE\"", f".org ${base:04X}", ""]
        return "\n".join(head + L) + "\n"

    def _ins_line(self, ins):
        m = self.m
        if ins.mn is None or ins.op == 0x00:
            txt = f".byte ${ins.op:02X}"
            note = "brk" if ins.op == 0 else "not an official opcode"
        else:
            opnd, note = self.operand(ins)
            txt = f"{ins.mn} {opnd}".rstrip()
            if ins.mode == "rel":
                t = ins.off + 2 + (ins.operand - 256 if ins.operand > 127 else ins.operand)
                if t not in self.names:
                    txt = f".byte ${ins.op:02X}, ${ins.operand:02X}"
                    note = f"{ins.mn} ${m.cpu(t):04X} (target is not an instruction)"
        cm = []
        sym = self.db_comment(ins.off)
        if sym:
            cm.append(sym)
        if note:
            cm.append(note)
        if not m.dyn[ins.off]:
            cm.append("[never ran]")
        return (f"    {txt:<28}; {' | '.join(cm)}" if cm else f"    {txt}")

    def db_comment(self, off):
        if not hasattr(self, "_comments"):
            self._comments = {}
            for e in self.db.syms:
                self._comments.update(e["comments"])
        return self._comments.get(off)

    def _routine_header(self, s, e):
        m, db = self.m, self.db
        sym = db.sym_at.get(s)
        L = ["", "; " + "-" * 76]
        kinds = sorted(m.entries.get(s, ()))
        if sym and sym["desc"]:
            for ln in sym["desc"].splitlines():
                L += ["; " + w for w in (textwrap.wrap(ln, 100) or [""])]
            for k in ("in", "out"):
                if sym.get(k):
                    L.append(f"; {k}: {sym[k]}")
        callers = sorted({f for f, t, k in self.ev.edges_to(s) if f != 0xFFFFF})
        ev = []
        cnt = int(self.ev.count[s])
        if cnt:
            first = self.ev.first_at(s)
            ev.append(f"ran {cnt}x, first {first[0]}@{first[1]}")
        else:
            ev.append("never ran in the corpus")
        if kinds:
            ev.append("entry: " + "/".join(kinds))
        if callers:
            ev.append(f"{len(callers)} call site(s)")
        L.append("; [" + "; ".join(ev) + "]")
        L.append(f"{self.names[s]}:")
        return L

    def _bytes(self, s, e, per=16):
        m = self.m
        L = []
        o = s
        while o < e:
            n = min(per, e - o)
            for i in range(1, n):
                if (o + i) in self.names:
                    n = i
                    break
            L.append("    .byte " + ", ".join(f"${x:02X}" for x in m.prg[o:o + n]))
            o += n
            if o < e and o in self.names:
                L.append(f"{self.names[o]}:")
        return L

    def _data(self, s, e, entry):
        m = self.m
        L = [""]
        if entry is None:
            readers = sorted({int(r) - 1 for r in np.unique(self.ev.rdr1[s:e]) if r})
            who = ", ".join(self.label_for(self._routine_start(r)) or m.name(r) for r in readers[:3])
            L.append(f"; data, {e - s} bytes" + (f", read by {who}" + (" ..." if len(readers) > 3 else "")
                                                 if readers else ", not read in the corpus"))
            if s in self.names:
                L.append(f"{self.names[s]}:")
            return L + self._bytes(s, e)
        if s == entry["off"]:
            L.append("; " + "-" * 76)
            for ln in entry["desc"].splitlines():
                L += ["; " + w for w in (textwrap.wrap(ln, 100) or [""])]
            L.append(f"; [format {entry['format']}, {entry['len']} bytes]")
            L.append(f"{entry['name']}:")
        f = entry["format"].split(":")
        if f[0] == "rows" and len(f) > 1:
            return L + self._bytes(s, e, per=int(f[1]))
        if f[0] == "fill":
            return L + [f"    .res {e - s}, ${m.prg[s]:02X}"]
        if f[0] in ("sprites", "poses"):
            return L + self._sprites(s, e, entry)
        if f[0] == "packed":
            return L + self._packed(s, e, entry)
        if f[0] in ("ptr16", "ptr16m1", "poseptr") and (s - entry["off"]) % 2 == 0 and (e - s) % 2 == 0:
            for o in range(s, e, 2):
                v = int(m.prg[o]) | (int(m.prg[o + 1]) << 8)
                t = self.ptr_targets.get(o)
                lab = self.label_for(t) if t is not None else None
                if lab and lab.endswith("+0"):
                    lab = lab[:-2]
                if lab and (t >> 13) != (o >> 13):
                    self.ext.add(t if t in self.names else self.db.data_at(t)[0]["off"])
                if lab:
                    L.append(f"    .addr {lab}" + ("-1" if f[0] == "ptr16m1" else ""))
                else:
                    L.append(f"    .word ${v:04X}")
            return L
        if f[0] in ("lobytes", "hibytes") and len(f) > 1 and f[1] in self.db.by_name:
            other = self.db.by_name[f[1]][1]
            lo_e, hi_e = (entry, other) if f[0] == "lobytes" else (other, entry)
            for o in range(s, e):
                i = o - entry["off"]
                v = int(m.prg[lo_e["off"] + i]) | (int(m.prg[hi_e["off"] + i]) << 8)
                t = m.resolve(o, v)
                lab = self.names.get(t) if t is not None else None
                if lab and (t >> 13) != (o >> 13):
                    self.ext.add(t)
                L.append(f"    .byte {'<' if f[0] == 'lobytes' else '>'}{lab}" if lab else f"    .byte ${m.prg[o]:02X}")
            return L
        return L + self._bytes(s, e)

    def _packed(self, s, e, entry):
        """A packed stream, one command per line; plain bytes when it does not parse."""
        import packed
        m = self.m
        rows = packed.listing(m.prg, entry["off"], entry["len"])
        if rows is None or s != entry["off"] or e != entry["off"] + entry["len"]:
            return self._bytes(s, e)
        L = []
        if not (m.flags[s] & 4):
            L.append("; [not unpacked in the corpus]")
        for o, n, what in rows:
            lines = self._bytes(o, o + n)
            lines[0] = f"{lines[0]:<44}; {what}" if len(lines[0]) <= 43 else lines[0] + f"  ; {what}"
            L += lines
        return L

    def _sprites(self, s, e, entry):
        """A sprites / poses region, one sprite per line; plain bytes when it does not parse."""
        import sprites
        m = self.m
        pose = entry["format"] == "poses"
        try:
            groups = sprites.parse(m.prg, entry["off"], entry["len"], entry["format"])
        except ValueError:
            return self._bytes(s, e)
        if s != entry["off"] or e != entry["off"] + entry["len"]:
            return self._bytes(s, e)
        L = []
        for o, n in groups:
            if o != s and o in self.names:
                L.append(f"{self.names[o]}:")
            c = o + (1 if pose else 0)
            never = "" if m.flags[c] & 4 else "   [not read in the corpus]"
            if pose:
                L.append(f"    .byte ${m.prg[o]:02X}" + " " * 19 + "; CHR bank" + (" (0: unchanged)" if m.prg[o] == 0 else ""))
            L.append(f"    .byte ${m.prg[c]:02X}" + " " * 19 + f"; {n} sprite{'s' if n > 1 else ''}: x, y, tile ^ 1, attribute{never}")
            for k in range(n):
                b = m.prg[c + 1 + 4 * k:c + 5 + 4 * k]
                L.append("    .byte " + ", ".join(f"${x:02X}" for x in b))
        return L

    def _script(self, s, e):
        m, vm = self.m, self.m.vm
        L = ["", "; " + "-" * 76]
        ent = next((x for x in self.db.scripts if x["off"] == s), None)
        if ent and ent["desc"]:
            for ln in ent["desc"].splitlines():
                L += ["; " + w for w in (textwrap.wrap(ln, 100) or [""])]
        ran = sum(1 for o in range(s, e) if o in vm.dynamic)
        tot = sum(1 for o in range(s, e) if o in vm.ins)
        L.append(f"; [script: {tot} instructions, {ran} ran in the corpus]")
        o = s
        while o < e:
            if o in self.names:
                L.append(f"{self.names[o]}:")
            ins = vm.ins.get(o)
            if ins is None:                     # an operand byte left over from an overlapping decode
                L.append(f"    .byte ${m.prg[o]:02X}")
                o += 1
                continue
            end = min(o + ins.len, e)
            parts = [f"${ins.op:02X}"]
            p = o + 1
            for t, v, bank, tgt in ins.args:
                n = 3 if bank is not None else (2 if t in ("u16", "s16", "mem", "addr", "code") else 1)
                lab = self.names.get(tgt) if tgt is not None else None
                if lab and p + n <= end:
                    if (tgt >> 13) != (o >> 13):
                        self.ext.add(tgt)
                    parts += [f"<{lab}", f">{lab}"] + ([f"${bank:02X}"] if bank is not None else [])
                else:
                    parts += [f"${x:02X}" for x in m.prg[p:min(p + n, end)]]
                p += n
            txt = ".byte " + ", ".join(parts)
            note = vm.text(ins, lambda off: self.names.get(off))
            if o not in vm.dynamic:
                note += "  [never ran]"
            L.append(f"    {txt:<40}; {note}")
            o = end
        return L

    def _routine_start(self, off):
        m = self.m
        if off >= PRG:
            return off
        lo = off & ~0x1FFF
        o = off
        while o > lo and not (m.kind[o] == C and (o in m.entries or o in m.cuts)) and m.kind[o - 1] in (C, A_):
            o -= 1
        return o

    # ---- everything ----
    def ram_inc(self):
        L = ["; RAM variables (db/*.toml) and hardware registers. Generated."]
        for a, n in sorted(HW.items()):
            L.append(f"{n:<24} := ${a:04X}")
        L.append("")
        for e in self.db.ram_sorted:
            d = e["desc"].splitlines()[0] if e["desc"] else ""
            L.append(f"{e['name']:<24} := ${e['addr']:04X}" + (f"    ; {d}" if d else ""))
        return "\n".join(L) + "\n"

    def write(self):
        src = os.path.join(OUT, "src")
        os.makedirs(src, exist_ok=True)
        open(os.path.join(src, "ram.inc"), "w").write(self.ram_inc())
        for b in range(64):
            open(os.path.join(src, f"bank{b:02X}.s"), "w").write(self.bank_source(b))
        return src


CFG = """MEMORY { PRG: start = $0000, size = $10000, file = %O, fill = no; }
SEGMENTS { CODE: load = PRG, type = ro; }
"""


def build(model, log=print):
    """Assemble out/src with ca65/ld65 and compare with the ROM. -> (ok, message)."""
    src, bld = os.path.join(OUT, "src"), os.path.join(OUT, "build")
    os.makedirs(bld, exist_ok=True)
    if not os.path.exists(os.path.join(CC65, "ca65")):
        return False, f"no assembler at {CC65}: run core/build.sh"
    open(os.path.join(bld, "bank.cfg"), "w").write(CFG)

    def one(b):
        o = os.path.join(bld, f"bank{b:02X}.o")
        r = subprocess.run([os.path.join(CC65, "ca65"), "-I", src, "-o", o, os.path.join(src, f"bank{b:02X}.s")],
                           capture_output=True, text=True)
        if r.returncode:
            return b, r.stderr.strip().splitlines()[:3]
        r = subprocess.run([os.path.join(CC65, "ld65"), "-C", os.path.join(bld, "bank.cfg"), "-o",
                            os.path.join(bld, f"bank{b:02X}.bin"), o], capture_output=True, text=True)
        return b, (r.stderr.strip().splitlines()[:3] if r.returncode else None)

    with ThreadPoolExecutor(16) as ex:
        res = list(ex.map(one, range(64)))
    errs = [(b, e) for b, e in res if e]
    if errs:
        return False, "; ".join(f"bank {b:02X}: {' / '.join(e)}" for b, e in errs[:4])
    out = b"".join(open(os.path.join(bld, f"bank{b:02X}.bin"), "rb").read() for b in range(64))
    ref = bytes(model.prg)
    if len(out) != len(ref):
        sizes = [(b, os.path.getsize(os.path.join(bld, f"bank{b:02X}.bin"))) for b in range(64)]
        bad = [f"{b:02X}:{n}" for b, n in sizes if n != BANK]
        return False, f"assembled PRG is {len(out)} bytes, not {len(ref)} (banks with a wrong size: {bad[:6]})"
    if out != ref:
        i = next(i for i in range(len(ref)) if out[i] != ref[i])
        return False, f"first difference at {model.name(i)}: built ${out[i]:02X}, ROM ${ref[i]:02X}"
    rom = model.ev.rom[:16] + out + model.ev.rom[16 + PRG:]
    open(os.path.join(bld, "rebuilt.nes"), "wb").write(rom)
    return rom == model.ev.rom, "rebuilt ROM is byte-identical"
