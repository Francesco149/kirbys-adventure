#!/usr/bin/env python3
"""kd - the documentation driver: evidence, inspection, experiments and gates for the Kirby's Adventure
disassembly. Stateless: one command, one process; the state is corpus/, db/ and evidence/.

  kd evidence [--force]                 replay the corpus on the instrumented core, merge
  kd corpus list | add FILE --id ID [--note TEXT] [--origin TEXT] [--keep]
  kd status [--json]                    coverage and documentation levels
  kd next [--bank BB] [--kind code|data|unknown] [-n 20] [--min-count N]
                                        undocumented chunks, the most-used first
  kd fn AT|NAME                         a routine: annotated listing, callers, callees, RAM and data it touches
  kd dis AT [--len N]                   annotated listing of any range
  kd xref X                             who reads / writes a RAM address or name, or reads a ROM location
  kd io AT|NAME --on WINDOW [--calls N] [--rows N]    calls of a routine: registers in/out, reads, writes
  kd trace AT|NAME --on WINDOW [--call K]             one call, instruction by instruction
  kd when AT|NAME                       in which movies and at which frame it first ran
  kd watch ADDR|NAME ... --on WINDOW    the values of RAM addresses over a window, one line per change
  kd vm                                 the script opcode table: where and how often each opcode ran
  kd sprites [--toml]                   pose tables and sprite groups not in the database yet (as [[data]] entries)
  kd packed [--toml]                    packed streams (what unpack expands) not in the database yet
  kd snd [--toml]                       sound headers, track and envelope streams not in the database yet
  kd script AT|NAME [--len N]           a script (bytecode) listing with run counts
  kd look WINDOW [--scale 2]            a picture of a corpus frame -> out/view/
  kd try --on WINDOW --frames N [--poke ADDR=V ...] [--hold] [--patch AT=V ...] [--input SPEC]
                                        run twice (plain / treated), print what differs, save both pictures
  kd render                             write out/src/*.s
  kd check [--no-build] [--no-cache] [--no-status] [--unit U]   all gates: database, evidence consistency, claims, rebuild
  kd selftest [--unit U ...]            plant known errors and require every gate to catch them (--unit: only that unit's)

AT is BB:AAAA (bank, CPU address, hex). WINDOW is movie@frame+len or movie@start-end.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.join(os.path.dirname(HERE), "tas"))
import db as DBM  # noqa: E402
import evidence as EVD  # noqa: E402
import rommodel as RM  # noqa: E402
from rommodel import BANK, PRG  # noqa: E402

C, A_, D, FL, U = ord("c"), ord("a"), ord("d"), ord("f"), ord("?")
EDGE = {1: "call", 2: "jmp", 3: "jmpind", 4: "rtsjmp", 5: "reset", 6: "nmi", 7: "irq", 8: "brk"}


def load(static=True):
    d = DBM.DB()
    ev = EVD.Evidence()
    m = RM.Model(ev, db=d, static=static)
    return d, ev, m


def at(d, m, s):
    """NAME or BB:AAAA -> PRG offset (checks the bank window)."""
    off = d.off_of(s)
    if s not in d.by_name:
        addr = DBM.parse_rom_at(s)[1]
        if m.cpu(off) != addr:
            raise SystemExit(f"bank {off >> 13:02X} is mapped at ${m.base[off >> 13]:04X}: "
                             f"write {off >> 13:02X}:{m.cpu(off):04X}")
    return off


def routine_start(m, off):
    lo = off & ~0x1FFF
    o = off
    while o > lo and not (m.kind[o] == C and (o in m.entries or o in m.cuts)) and m.kind[o - 1] in (C, A_):
        o -= 1
    while m.kind[o] == A_ and o > lo:
        o -= 1
    return o


# ---------------------------------------------------------------- levels and status
def verified_names(d, results, without=()):
    """Names some passing claim is about (without: leave out claims of these kinds)."""
    out = set()
    for c in d.claims:
        r = results.get(c["id"])
        if r and r[0] and c["kind"] not in without:
            out.update(c.get("about", []))
    return out


def levels(d, m, results):
    """Per PRG byte: 0 never touched and unexplained, 1 classified by evidence, 2 described, 3 verified."""
    lvl = np.zeros(PRG, dtype=np.uint8)
    lvl[m.kind != U] = 1
    ok = verified_names(d, results)
    strong = verified_names(d, results, without=("format",))
    for e in d.syms:
        if e["kind"] == "label" or not e["desc"] or m.kind[e["off"]] != C:
            continue
        lvl[e["off"]:m.routine_end(e["off"])] = 3 if e["name"] in ok else 2
    for e in d.data:
        if not e["desc"]:
            continue
        s, n = e["off"], e["len"]
        v = e["name"] in ok
        if e["format"] == "fill":
            seg = m.prg[s:s + n]
            v = bool((seg == seg[0]).all() and not m.flags[s:s + n].any())
        lvl[s:s + n] = 3 if v else 2
        if v and e["name"] not in strong and e["format"] != "fill":
            # verified by a `format` claim only: that compares readers, so a byte nothing read is described
            lvl[s:s + n][(m.flags[s:s + n] & RM.F_DATA) == 0] = 2
    if m.vm:
        for e in d.scripts:
            if e["desc"] and e["off"] in m.vm.starts:
                lvl[e["off"]:m.vm.script_end(e["off"])] = 3 if e["name"] in ok else 2
    return lvl


def ram_touched(ev):
    a = np.unique(ev.pairs[:, 1])
    return [int(x) for x in a if x < 0x800 or 0x6000 <= x < 0x8000]


def status(d, ev, m, results):
    lvl = levels(d, m, results)
    k = m.kind
    code = (k == C) | (k == A_)
    ok = verified_names(d, results)
    touched = ram_touched(ev)
    named = [a for a in touched if d.ram_name(a)]
    rver = [a for a in named if d.ram_name(a).split("+")[0] in ok]
    routines = sorted(set(m.entries) | m.cuts)
    rsyms = [e for e in d.syms if e["kind"] != "label" and e["desc"]]
    one = m.one_sided()
    nbr = int(sum(1 for o in np.flatnonzero(m.flags & 1) if int(m.prg[o]) in RM.BRANCHES))
    s = {
        "prg_bytes": PRG,
        "code_ran": int((code & m.dyn).sum()), "code_static": int((code & ~m.dyn).sum()),
        "data_read": int(((k == D) & m.dyn).sum()), "data_db_only": int(((k == D) & ~m.dyn).sum()),
        "fill": int((k == FL).sum()), "never_touched": int((k == U).sum()),
        "script_bytes": int(((k == ord("s")) | (k == ord("t"))).sum()),
        "script_ins": len(m.vm.starts) if m.vm else 0, "script_ins_ran": len(m.vm.dynamic) if m.vm else 0,
        "scripts": len(m.vm.labels | m.vm.cuts) if m.vm else 0,
        "scripts_described": len([e for e in d.scripts if e["desc"]]),
        "scripts_verified": len([e for e in d.scripts if e["name"] in ok]),
        "opcodes": len(d.opcodes), "opcodes_verified": len([e for e in d.opcodes if e["name"] in ok]),
        "level": [int((lvl == i).sum()) for i in range(4)],
        "routines": len(routines), "routines_described": len(rsyms),
        "routines_verified": len([e for e in rsyms if e["name"] in ok]),
        "data_regions": len(d.data), "data_verified": len([e for e in d.data if e["name"] in ok]),
        "ram_touched": len(touched), "ram_named": len(named), "ram_verified": len(rver),
        "claims": len(d.claims), "claims_pass": sum(1 for c in d.claims if results.get(c["id"], (False,))[0]),
        "branches_ran": nbr, "branches_one_sided": len(one),
        "chr_tiles": (len(ev.rom) - 16 - PRG) // 16, "chr_tiles_fetched": int((ev.chrf != 0).sum()),
        "corpus_movies": len(EVD.manifest()), "corpus_frames": sum(r[1] for r in EVD.manifest()),
        "units": len(d.units),
    }
    return s


def print_status(s):
    p = s["prg_bytes"]

    def pc(n, of=p):
        return f"{n:>7,} ({100 * n / of:4.1f}%)"

    print(f"corpus   {s['corpus_movies']} movies, {s['corpus_frames']:,} frames")
    print(f"PRG      {p:,} bytes")
    print(f"  ran as code    {pc(s['code_ran'])}     read as data  {pc(s['data_read'])}")
    print(f"  static code    {pc(s['code_static'])}     fill          {pc(s['fill'])}")
    print(f"  never touched  {pc(s['never_touched'])}")
    if s["opcodes"]:
        print(f"  script         {pc(s['script_bytes'])}     {s['script_ins']:,} instructions ({s['script_ins_ran']:,} ran) "
              f"in {s['scripts']:,} scripts: described {s['scripts_described']}, verified {s['scripts_verified']}; "
              f"opcodes {s['opcodes']} ({s['opcodes_verified']} verified)")
    lv = s["level"]
    print(f"  documentation  verified {pc(lv[3])} | described {pc(lv[2])} | seen only {pc(lv[1])} | "
          f"unexplained {pc(lv[0])}")
    print(f"routines {s['routines']:,}: described {s['routines_described']}, verified {s['routines_verified']}"
          f"      data regions in the database: {s['data_regions']} ({s['data_verified']} verified)")
    print(f"RAM      {s['ram_touched']:,} addresses touched: named {s['ram_named']}, verified {s['ram_verified']}")
    print(f"branches {s['branches_ran']:,} conditional branches ran, {s['branches_one_sided']:,} went one way only")
    print(f"CHR      {s['chr_tiles_fetched']:,} of {s['chr_tiles']:,} tiles fetched by the PPU")
    print(f"claims   {s['claims_pass']} of {s['claims']} pass      units {s['units']}")


# ---------------------------------------------------------------- listings
def ins_listing(d, m, ev, R, lo, hi, counts=True):
    out = []
    o = lo
    while o < hi:
        kk = m.kind[o]
        if kk == C:
            ins = m.ins(o)
            R.ext = set()
            if ins.mn is None or ins.op == 0:
                txt, note = f".byte ${ins.op:02X}", None
            else:
                opnd, note = R.operand(ins)
                txt = f"{ins.mn} {opnd}".rstrip()
            raw = " ".join(f"{b:02X}" for b in m.prg[o:o + ins.len])
            lab = R.names.get(o)
            if lab:
                out.append(f"{lab}:")
            cnt = int(ev.count[o])
            extra = []
            if counts:
                extra.append(f"{cnt}x" if cnt else "never ran")
            if ins.op in RM.BRANCHES and cnt:
                t = o + 2 + (ins.operand - 256 if ins.operand > 127 else ins.operand)
                if not m.flags[t] & 1:
                    extra.append("NEVER TAKEN")
                elif not m.flags[o + 2] & 1:
                    extra.append("ALWAYS TAKEN")
            cm = R.db_comment(o)
            if cm:
                extra.append(cm)
            if note:
                extra.append(note)
            out.append(f"  {m.name(o)}  {raw:<9} {txt:<26} ; " + " | ".join(extra))
            o += ins.len
        elif kk == ord("s") and m.vm and o in m.vm.ins:
            ins = m.vm.ins[o]
            if o in R.names:
                out.append(f"{R.names[o]}:")
            raw = " ".join(f"{b:02X}" for b in m.prg[o:o + ins.len])
            cnt = int(ev.dcount[o]) if o in m.vm.dynamic else 0
            out.append(f"  {m.name(o)}  {raw:<14} {m.vm.text(ins, lambda t: R.names.get(t)):<30} ; script, "
                       + (f"{cnt}x" if cnt else "never ran"))
            o += ins.len
        else:
            e = o
            while e < hi and m.kind[e] == kk and e - o < 16 and (e == o or e not in R.names):
                e += 1
            lab = R.names.get(o)
            if lab:
                out.append(f"{lab}:")
            what = {D: "data", FL: "fill", U: "never touched", A_: "operand", ord("t"): "script operand",
                    ord("s"): "script"}[kk]
            rd = int(ev.rdr1[o])
            who = f" read by {m.name(routine_start(m, rd - 1))}" if rd and rd - 1 < PRG else ""
            out.append(f"  {m.name(o)}  " + " ".join(f"{b:02X}" for b in m.prg[o:e]) + f"   ; {what}{who}")
            o = e
    return out


def cmd_fn(a):
    import render
    d, ev, m = load()
    R = render.Renderer(m, d)
    off = at(d, m, a.at)
    if m.kind[off] != C:
        raise SystemExit(f"{a.at} is not an instruction (kind '{chr(m.kind[off])}'): try `kd dis`")
    s = routine_start(m, off) if not (off in m.entries or off in m.cuts) else off
    e = m.routine_end(s)
    sym = d.sym_at.get(s)
    print(f"{R.names.get(s)}  {m.name(s)}..{m.cpu(e - 1):04X}  ({e - s} bytes)"
          + (f"  [{sym['unit']}]" if sym else "  [not in the database]"))
    if sym and sym["desc"]:
        print("  " + sym["desc"].replace("\n", "\n  "))
    cnt = int(ev.count[s])
    first = ev.first_at(s)
    print(f"  ran {cnt:,}x" + (f", first {first[0]}@{first[1]}" if first else "")
          + f"; entry kinds: {'/'.join(sorted(m.entries.get(s, ['(code run start)'])))}")
    callers = {}
    for f, t, k in ev.edges_to(s):
        if f != 0xFFFFF:
            callers.setdefault(routine_start(m, f) if f < PRG else f, []).append(k)
    if callers:
        names = [R.label_for(c) or (m.name(c) if c < PRG else f"RAM:{c - PRG:04X}") for c in sorted(callers)]
        print(f"  called from {len(callers)} routine(s): " + ", ".join(names[:12]) + (" ..." if len(names) > 12 else ""))
    ints = [k for f, t, k in ev.edges_to(s) if f == 0xFFFFF]
    if ints:
        print("  interrupt entry: " + ", ".join({5: "reset", 6: "NMI", 7: "IRQ"}.get(k, str(k)) for k in ints))
    outs = {}
    for f, t, k in ev.edges_from(s, e):
        outs.setdefault(k, set()).add(t)
    for k, label in ((1, "calls"), (2, "jumps to"), (3, "jumps (indirect) to"), (4, "rts-jumps to")):
        ts = sorted(t for t in outs.get(k, ()) if not (s <= t < e))
        if ts:
            names = [R.label_for(t) or (m.name(t) if t < PRG else f"RAM:{t - PRG:04X}") for t in ts]
            print(f"  {label}: " + ", ".join(names[:14]) + (f" ... ({len(names)})" if len(names) > 14 else ""))
    rd, wr = set(), set()
    for c, addr, w in ev.code_xref(s, e):
        (wr if w else rd).add(addr)

    def fmt(addrs):
        out = []
        for x in sorted(addrs)[:40]:
            n = d.ram_name(x)
            out.append(f"${x:04X}" + (f"={n}" if n else ""))
        return " ".join(out) + (f" ... ({len(addrs)})" if len(addrs) > 40 else "")

    if rd:
        print("  reads : " + fmt(rd))
    if wr:
        print("  writes: " + fmt(wr))
    lo = ev.rdmin[s:e]
    hi_ = ev.rdmax[s:e]
    tabs = [(int(a_), int(b_)) for a_, b_ in zip(lo, hi_) if a_ != 0xFFFFFFFF]
    if tabs:
        seen = sorted(set(tabs))
        print("  ROM data read: " + ", ".join(f"{m.name(a_)}..{m.cpu(b_):04X}" + (f" ({R.label_for(a_)})"
              if R.label_for(a_) else "") for a_, b_ in seen[:10]) + (" ..." if len(seen) > 10 else ""))
    print()
    print("\n".join(ins_listing(d, m, ev, R, s, e)))


def cmd_dis(a):
    import render
    d, ev, m = load()
    R = render.Renderer(m, d)
    off = at(d, m, a.at)
    print("\n".join(ins_listing(d, m, ev, R, off, min(off + a.len, (off | 0x1FFF) + 1))))


def cmd_xref(a):
    import render
    d, ev, m = load()
    R = render.Renderer(m, d)
    x = a.x

    def rname(off):
        if off >= PRG:
            return f"RAM:{off - PRG:04X}"
        s = routine_start(m, off)
        return f"{R.label_for(s) or m.name(s)}"

    if x in d.by_name and d.by_name[x][0] == "ram" or (":" not in x and x not in d.by_name):
        if x in d.by_name:
            e = d.by_name[x][1]
            addrs = range(e["addr"], e["addr"] + e["len"])
        else:
            a0 = int(x.lstrip("$"), 16)
            addrs = range(a0, a0 + a.len)
        for addr in addrs:
            rows = ev.ram_xref(addr)
            print(f"${addr:04X} {d.ram_name(addr) or ''}: {sum(1 for r in rows if not r[1])} reading and "
                  f"{sum(1 for r in rows if r[1])} writing instructions")
            by = {}
            for off, w in rows:
                by.setdefault((rname(off), "W" if w else "R"), []).append(off)
            for (name, rw), offs in sorted(by.items()):
                print(f"   {rw} {name:<28} " + " ".join(m.name(o) if o < PRG else f"RAM:{o - PRG:04X}" for o in offs[:6])
                      + (" ..." if len(offs) > 6 else ""))
    else:
        off = at(d, m, x)
        n = a.len
        if x in d.by_name and d.by_name[x][0] == "data":
            n = d.by_name[x][1]["len"]
        if m.kind[off] == C:
            print(f"{m.name(off)} is code; callers / jumps in:")
            for f, t, k in ev.edges_to(off):
                print(f"   {EDGE[k]:<7}"
                      f" from {m.name(f) if f < PRG else 'hardware' if f == 0xFFFFF else f'RAM:{f - PRG:04X}'}"
                      + (f"  in {rname(f)}" if f < PRG else ""))
            return
        readers = {}
        for o in range(off, off + n):
            for arr in (ev.rdr1, ev.rdr2):
                r = int(arr[o])
                if r:
                    readers.setdefault(r - 1, [0, o, o])
                    readers[r - 1][0] += 1
                    readers[r - 1][2] = o
        print(f"{m.name(off)}..+{n}: read as data by {len(readers)} instruction(s)")
        for r, (cnt, lo, hi_) in sorted(readers.items()):
            ins = m.ins(r) if r < PRG and m.kind[r] == C else None
            R.ext = set()
            txt = f"{ins.mn} {R.operand(ins)[0]}" if ins and ins.mn else ""
            print(f"   {m.name(r) if r < PRG else f'RAM:{r - PRG:04X}'}  {txt:<24} in {rname(r):<26} "
                  f"bytes {m.name(lo)}..{m.cpu(hi_):04X}")


def cmd_next(a):
    import render
    d, ev, m = load()
    R = render.Renderer(m, d)
    lvl = levels(d, m, {})
    rows = []
    for b in ([int(a.bank, 16)] if a.bank else range(64)):
        for s, e, kind, entry in R.chunks[b]:
            if lvl[s] >= 2 or (a.kind and kind != a.kind):
                continue
            if kind == "code":
                cnt = int(ev.count[s])
                callers = len({f for f, t, k in ev.edges_to(s)})
                rows.append((cnt, s, e, kind, f"{callers} call sites" if callers else "jump target"))
            elif kind == "data":
                cnt = int(ev.dcount[s:e].sum())
                rows.append((cnt, s, e, kind, "read by " + (R.label_for(routine_start(m, int(ev.rdr1[s]) - 1))
                                                               or m.name(routine_start(m, int(ev.rdr1[s]) - 1)))
                             if ev.rdr1[s] and ev.rdr1[s] - 1 < PRG else ""))
            elif kind == "script":
                rows.append((int(ev.dcount[s]), s, e, kind, f"{sum(1 for o in range(s, e) if o in m.vm.ins)} instructions"))
            elif not a.kind or a.kind == kind:
                rows.append((0, s, e, kind, ""))
    rows = [r for r in rows if r[0] >= a.min_count]
    rows.sort(key=lambda r: (-r[0], r[1]))
    print(f"{len(rows):,} undocumented chunks" + (f" in bank {a.bank}" if a.bank else "") + "; the most used:")
    for cnt, s, e, kind, note in rows[:a.n]:
        first = ev.first_at(s)
        print(f"  {m.name(s)}  {kind:<7} {e - s:>5} bytes  used {cnt:>11,}x  "
              f"{(first[0] + '@' + str(first[1])) if first else '-':<16} {note}")


def cmd_script(a):
    import render
    d, ev, m = load()
    if not m.vm:
        raise SystemExit("the database does not describe the script interpreter yet ([vm], [[opcode]])")
    R = render.Renderer(m, d)
    R.ext = set()
    off = at(d, m, a.at)
    vm = m.vm
    if off not in vm.starts:
        raise SystemExit(f"{a.at} is not a script instruction in the model (kind '{chr(m.kind[off])}')")
    end = vm.script_end(off) if not a.len else min(off + a.len, (off | 0x1FFF) + 1)
    ent = next((x for x in d.scripts if x["off"] == off), None)
    print(f"{R.names.get(off, m.name(off))}  {m.name(off)}..{m.cpu(end - 1):04X}  ({end - off} bytes)"
          + (f"  [{ent['unit']}]" if ent else "  [not in the database]"))
    if ent and ent["desc"]:
        print("  " + ent["desc"].replace("\n", "\n  "))
    o = off
    while o < end:
        ins = vm.ins.get(o)
        if ins is None:
            print(f"  {m.name(o)}  {m.prg[o]:02X}   ; (operand left over)")
            o += 1
            continue
        if o in R.names and o != off:
            print(f"{R.names[o]}:")
        raw = " ".join(f"{b:02X}" for b in m.prg[o:o + ins.len])
        cnt = int(ev.dcount[o]) if o in vm.dynamic else 0
        first = ev.first_at(o)
        print(f"  {m.name(o)}  {raw:<14} {vm.text(ins, lambda t: R.names.get(t)):<34} ; "
              + (f"{cnt}x, first {first[0]}@{first[1]}" if cnt else "never ran"))
        o += ins.len


def cmd_sprites(a):
    """Pose tables and sprite groups that are not in the database yet (sprites.py); --toml prints entries."""
    import sprites
    d, ev, m = load()
    ents = sprites.discover(d, m, ev, log=lambda s: print(s, file=sys.stderr))
    if a.toml:
        print(sprites.toml(ents, m))
        return
    by = {}
    for e in ents:
        f = e["format"].split(":")[0]
        by[f] = (by.get(f, (0, 0))[0] + 1, by.get(f, (0, 0))[1] + e["len"])
    for f, (n, b) in sorted(by.items()):
        print(f"  {f:<8} {n:>4} regions, {b:>7,} bytes not in the database")
    if not ents:
        print("  nothing new: every table and group found is in the database")


def cmd_vm(a):
    d, ev, m = load()
    if not m.vm:
        raise SystemExit("the database does not describe the script interpreter yet ([vm], [[opcode]])")
    vm = m.vm
    use = vm.opcode_use()
    print(f"script instructions: {len(vm.starts):,} ({len(vm.dynamic):,} ran, {len(vm.static):,} static) in "
          f"{len(vm.labels | vm.cuts):,} scripts")
    for e in sorted(d.opcodes, key=lambda e: e["lo"]):
        n, c, first = use.get(e["name"], (0, 0, None))
        fr = EVD.tag_split(first) if first else None
        rng = f"{e['lo']:02X}" + (f"-{e['hi']:02X}" if e["hi"] != e["lo"] else "")
        print(f"  {rng:<6} {e['mnemonic']:<16} {' '.join(e['args']):<16} {e['flow']:<7} ran at {n:>5} places, "
              f"{c:>9,}x" + (f", first {fr[0]}@{fr[1]}" if fr else ""))
    for p in vm.problems():
        print("  PROBLEM", p)


def cmd_when(a):
    d, ev, m = load()
    off = at(d, m, a.at)
    print(f"{m.name(off)}: ran {int(ev.count[off]):,}x in the whole corpus")
    for mid, frames, *_ in EVD.manifest():
        z = np.load(os.path.join(EVD.EV, "movie", mid + ".npz"))
        f = int(z["first"][off])
        cnt = int(z["count"][off])
        if cnt:
            # the tag in a per-movie table is that movie's own
            print(f"  {mid:<18} {cnt:>10,}x   first at frame {(f - 1) & 0xFFFFF}")


def session():
    import probe
    return probe, probe.Session()


def cmd_io(a):
    probe, s = session()
    d, ev, m = load()
    off = at(d, m, a.at)
    calls = s.calls([off], a.on, max_calls=a.calls)
    if not calls:
        raise SystemExit(f"no call of {a.at} in {a.on} (try `kd when {a.at}` to find a window)")
    print(f"{len(calls)} calls of {m.name(off)} in {a.on}; "
          f"instructions per call {min(c.n for c in calls)}..{max(c.n for c in calls)}")

    def nm(x):
        n = d.ram_name(x)
        return f"${x:04X}" + (f"={n}" if n else "")

    for title, key in (("reads", "rd"), ("writes", "wr")):
        allk = {}
        for c in calls:
            for k, v in getattr(c, key).items():
                allk.setdefault(k, []).append(v)
        print(f"  {title} ({len(allk)} addresses):")
        for k in sorted(allk)[:a.addrs]:
            vs = allk[k]
            uniq = sorted(set(vs))
            print(f"     {nm(k):<28} in {len(vs):>4}/{len(calls)} calls   values "
                  + " ".join(f"{v:02X}" for v in uniq[:10]) + (" ..." if len(uniq) > 10 else ""))
        if len(allk) > a.addrs:
            print(f"     ... {len(allk) - a.addrs} more (use --addrs N)")
    rom = {}
    for c in calls:
        for k in c.romrd:
            rom[k] = rom.get(k, 0) + 1
    if rom:
        ks = sorted(rom)
        print(f"  ROM bytes read: {len(ks)} distinct, {m.name(ks[0])} .. {m.name(ks[-1])}")
    sub = {}
    for c in calls:
        for o in c.call_offs:
            sub[o] = sub.get(o, 0) + 1
    if sub:
        print("  calls: " + ", ".join(f"{m.name(o) if o < PRG else f'RAM:{o - PRG:04X}'} x{n}" for o, n in sorted(sub.items())[:16]))
    print("  frame      A  X  Y  P  ->  A  X  Y  P    n")
    for c in calls[:a.rows]:
        print(f"  {c.frame:>6}    {c.a:02X} {c.x:02X} {c.y:02X} {c.p:02X}     {c.ra:02X} {c.rx:02X} {c.ry:02X} {c.rp:02X} "
              f"{c.n:>5}" + ("" if c.complete else "  (aborted)"))


def cmd_trace(a):
    import render
    probe, s = session()
    d, ev, m = load()
    R = render.Renderer(m, d)
    off = at(d, m, a.at)
    movie, start, n = probe.parse_window(a.on)
    s.seek(movie, start)
    s.c.watch([off])
    s.c.log(2, 6_000_000)
    masks = s.movie_masks(movie)
    recs = []
    for _ in range(max(n, 1)):
        s.c.step(masks[s.c.frames], render=False)
        r, over = s.c.take()
        if len(r):
            recs.append(r)
        if recs and sum((x["type"] == probe.R_END).sum() for x in recs) > a.call:
            break
    if not recs:
        raise SystemExit("the routine did not run in that window")
    r = np.concatenate(recs)
    begins = np.flatnonzero(r["type"] == probe.R_BEGIN)
    ends = np.flatnonzero((r["type"] == probe.R_END) | (r["type"] == probe.R_ABORT))
    if a.call >= len(begins):
        raise SystemExit(f"only {len(begins)} calls in the window")
    b = int(begins[a.call])
    e = int(ends[ends > b][0]) if (ends > b).any() else len(r) - 1
    lines = 0
    for x in r[b:e + 1]:
        t = int(x["type"])
        if t == probe.R_EXEC:
            o = int(x["off"])
            ins = m.ins(o) if o < PRG else None
            R.ext = set()
            txt = (f"{ins.mn} {R.operand(ins)[0]}" if ins and ins.mn else f".byte ${int(x['val']):02X}")
            print(f"{m.name(o) if o < PRG else f'RAM:{o - PRG:04X}'}  {txt:<26} A={x['a']:02X} X={x['x']:02X} "
                  f"Y={x['y']:02X} P={x['p']:02X} S={x['s']:02X}")
            lines += 1
        elif t == probe.R_READ:
            print(f"           read  ${int(x['addr']):04X} = {int(x['val']):02X}  {d.ram_name(int(x['addr'])) or ''}")
        elif t == probe.R_WRITE:
            print(f"           write ${int(x['addr']):04X} = {int(x['val']):02X}  {d.ram_name(int(x['addr'])) or ''}")
        elif t == probe.R_END:
            print(f"-- returned: A={x['a']:02X} X={x['x']:02X} Y={x['y']:02X} P={x['p']:02X}")
        if lines >= a.max:
            print(f"... cut at {a.max} instructions (--max)")
            break


def _png(frame, path, scale):
    import env as E
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(E.png(frame, scale=scale))
    return path


def cmd_watch(a):
    """Values of RAM addresses over a window: one line whenever any of them changes."""
    probe, s = session()
    d = DBM.DB()
    movie, start, n = probe.parse_window(a.on)
    addrs = []
    for x in a.addrs:
        if x in d.by_name and d.by_name[x][0] == "ram":
            e = d.by_name[x][1]
            addrs += list(range(e["addr"], e["addr"] + e["len"]))
        else:
            addrs.append(int(x.lstrip("$"), 16))
    s.seek(movie, start)
    print("frame    " + " ".join(f"${x:04X}" for x in addrs))
    last, shown = None, 0
    for _ in range(n):
        s.run(1)
        v = probe.RamView(s.ram())
        cur = [v[x] for x in addrs]
        if cur != last:
            print(f"{s.c.frames - 1:>7}  " + " ".join(f"   {b:02X}" for b in cur))
            last = cur
            shown += 1
            if shown >= a.max:
                print(f"... cut at {a.max} changes (--max)")
                break


def cmd_look(a):
    probe, s = session()
    movie, start, _ = probe.parse_window(a.window)
    s.seek(movie, max(0, start - 1))
    s.run(1, render=True)
    p = _png(s.c.frame, os.path.join(HERE, "out/view", f"{movie}-{start}.png"), a.scale)
    print(p)


def cmd_try(a):
    import env as E
    probe, s = session()
    d, ev, m = load()
    movie, start, _ = probe.parse_window(a.on)
    poke = {}
    for kv in a.poke or []:
        k, v = kv.split("=")
        poke[d.addr_of(k) if k in d.by_name else int(k.lstrip("$"), 16)] = int(v, 0)
    patch = {}
    for kv in a.patch or []:
        k, v = kv.split("=")
        patch[at(d, m, k)] = int(v, 0)
    masks = E.parse_spec(a.input) if a.input else None
    if masks is not None:
        masks = (masks + [0] * a.frames)[:a.frames]

    def one(treated):
        s.seek(movie, start)
        saved = {o: int(s.c.prg[o]) for o in patch}
        cnt0 = s.c.count.copy()
        try:
            if treated:
                for o, v in patch.items():
                    s.c.prg[o] = v
            for i in range(a.frames):
                if treated and (i == 0 or a.hold):
                    for ad, v in poke.items():
                        if ad < 0x800:
                            s.c.ram[ad] = v
                        else:
                            s.c.wram[ad - 0x6000] = v
                s.run(1, render=(i == a.frames - 1),
                      masks=masks[i:i + 1] if (masks is not None and treated) else None)
        finally:
            for o, v in saved.items():
                s.c.prg[o] = v
        return s.ram(), s.c.frame.copy(), s.c.count.astype(np.int64) - cnt0

    cb, cf, cn = one(False)
    tb, tf, tn = one(True)
    diffs = [(i if i < 0x800 else 0x6000 + i - 0x800) for i in range(len(tb)) if tb[i] != cb[i]]
    print(f"{len(diffs)} RAM bytes differ after {a.frames} frames (address: control -> treated):")
    for ad in diffs[:a.max]:
        i = ad if ad < 0x800 else 0x800 + ad - 0x6000
        print(f"   ${ad:04X} {d.ram_name(ad) or '':<20} {cb[i]:02X} -> {tb[i]:02X}")
    if len(diffs) > a.max:
        print(f"   ... {len(diffs) - a.max} more (--max)")
    only_t = np.flatnonzero((tn[:PRG] > 0) & (cn[:PRG] == 0) & ((m.flags & 1) != 0) | ((tn[:PRG] > 0) & (cn[:PRG] == 0)))
    only_c = np.flatnonzero((cn[:PRG] > 0) & (tn[:PRG] == 0))
    for label, arr in (("ran only in the treated run", only_t), ("ran only in the control run", only_c)):
        starts = sorted({routine_start(m, int(o)) for o in arr if m.kind[int(o)] == C})
        if starts:
            print(f"   routines with instructions that {label}: " + " ".join(m.name(o) for o in starts[:12])
                  + (" ..." if len(starts) > 12 else ""))
    v = os.path.join(HERE, "out/view")
    print("pictures:", _png(cf, os.path.join(v, "try-control.png"), 2), _png(tf, os.path.join(v, "try-treated.png"), 2))
    print("picture differs" if (cf != tf).any() else "picture identical")


def cmd_evidence(a):
    t = time.time()
    ok = EVD.build(force=a.force)
    print("evidence", "built" if ok else "FAILED", f"in {time.time() - t:.0f} s;", EVD.coverage())
    sys.exit(0 if ok else 1)


def cmd_corpus(a):
    if a.action == "list":
        for mid, frames, sha, origin, note in EVD.manifest():
            print(f"{mid:<18} {frames:>7} frames  {sha[:10]}  {origin:<22} {note}")
        return
    EVD.add(a.file, a.id, a.origin or os.path.relpath(a.file, os.path.dirname(HERE)), a.note or "",
            keep_if_no_gain=a.keep)


def cmd_render(a):
    import render
    d, ev, m = load()
    print(render.Renderer(m, d).write())


def run_claims(d, use_cache=True, unit=None):
    import probe
    claims = [c for c in d.claims if unit is None or c["unit"] == unit]
    return probe.run_claims(claims, use_cache=use_cache, db_stamp=DBM.stamp(d)) if claims else {}


def cmd_status(a):
    d, ev, m = load()
    res = run_claims(d)
    s = status(d, ev, m, res)
    if a.json:
        print(json.dumps(s))
    else:
        print_status(s)


def locked(name):
    """One writer at a time for out/ (several agents may run kd at once). Blocks until free."""
    import fcntl
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    f = open(os.path.join(HERE, "out", name + ".lock"), "w")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print(f"(another kd is using out/: waiting)", file=sys.stderr)
        fcntl.flock(f, fcntl.LOCK_EX)
    return f


def cmd_check(a):
    import render
    t0 = time.time()
    d, ev, m = load()
    probs = list(d.problems) + d.check_against(m, tagged=True)
    print(f"database: {len(d.units)} units, {len(d.syms)} syms, {len(d.data)} data regions, {len(d.ram)} RAM "
          f"variables, {len(d.claims)} claims" + (f"   (judging unit '{a.unit}' only)" if a.unit else ""))
    if a.unit and a.unit not in d.units:
        bad = [p for u, p in probs if u is None or u == a.unit]
        raise SystemExit(f"no unit '{a.unit}' in db/ (units: {', '.join(sorted(d.units))})"
                         + "".join(f"\n  {p}" for p in bad))
    mine = []
    for unit, p in probs:
        ours = a.unit is None or unit is None or unit == a.unit
        print("  PROBLEM" if ours else f"  (unit {unit})", p)
        if ours:
            mine.append(p)
    res = run_claims(d, use_cache=not a.no_cache, unit=a.unit)
    fails = 0
    for c in d.claims:
        if c["id"] in res:
            ok, msg, _ = res[c["id"]]
            fails += not ok
            if not ok or a.verbose:
                print(f"  {'pass' if ok else 'FAIL'}  {c['id']:<34} {msg}")
    print(f"claims: {len(res) - fails} pass, {fails} fail")
    weak = [w for u, w in lint(d, res) if a.unit is None or u == a.unit]
    for w in weak:
        print("  WEAK", w)
    built = True
    if not a.no_build:
        lock = locked("build")
        R = render.Renderer(m, d)
        R.write()
        built, msg = render.build(m)
        lock.close()
        print("rebuild:", "OK," if built else "FAILED:", msg)
    if not a.no_status:     # with --unit the status needs every unit's claims: skip it when only the verdict counts
        print()
        print_status(status(d, ev, m, res if a.unit is None else run_claims(d)))
    ok = not mine and not fails and built
    print(f"\nkd check: {'PASS' if ok else 'FAIL'} ({time.time() - t0:.0f} s)" + (f", {len(weak)} weak" if weak else ""))
    sys.exit(0 if ok else 1)


def cmd_packed(a):
    """Packed streams that are not in the database yet (packed.py); --toml prints entries."""
    import packed
    d, ev, m = load()
    ents = packed.discover(d, m, ev, log=lambda s: print(s, file=sys.stderr))
    if a.toml:
        print(packed.toml(ents, m))
    elif ents:
        print(f"  packed   {len(ents):>4} regions, {sum(e['len'] for e in ents):>7,} bytes not in the database")
    else:
        print("  nothing new: every stream found is in the database")


def cmd_snd(a):
    """Sound headers and streams that are not in the database yet (sndfmt.py); --toml prints entries."""
    import sndfmt
    d, ev, m = load()
    ents = sndfmt.discover(d, m, ev, log=lambda s: print(s, file=sys.stderr))
    if a.toml:
        print(sndfmt.toml(ents, m))
    elif ents:
        for f in sndfmt.FORMATS:
            es = [e for e in ents if e["format"] == f]
            print(f"  {f:<9}{len(es):>4} regions, {sum(e['len'] for e in es):>7,} bytes not in the database")
    else:
        print("  nothing new: every header and stream found is in the database")


def lint(d, res):
    """Soft findings: things that pass but prove little."""
    out = []
    about = {}
    for c in d.claims:
        u = c["unit"]
        for n in c.get("about", []):
            about.setdefault(n, []).append(c)
        if c["kind"] == "call" and len(c["on"] if isinstance(c["on"], list) else [c["on"]]) < 2:
            out.append((u, f"claim {c['id']}: one window only; add a second from a different situation or movie"))
        if c["kind"] == "frames" and not c.get("sometimes"):
            out.append((u, f"claim {c['id']}: no `sometimes`, so it may hold only because nothing happened"))
        if not c.get("about"):
            out.append((u, f"claim {c['id']}: `about` is empty, it verifies nothing"))
    for kind, lst in (("sym", d.syms), ("data", d.data), ("ram", d.ram), ("script", d.scripts), ("opcode", d.opcodes)):
        for e in lst:
            if not e["desc"] and e.get("kind") != "label":
                out.append((e["unit"], f"{kind} {e['name']}: no desc"))
            elif e["name"] not in about and e.get("kind") != "label" and e.get("format") != "fill":
                out.append((e["unit"], f"{kind} {e['name']}: described, no claim is about it"))
    return out


def main():
    ap = argparse.ArgumentParser(prog="kd", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("evidence"); p.add_argument("--force", action="store_true"); p.set_defaults(f=cmd_evidence)
    p = sub.add_parser("corpus"); p.add_argument("action", choices=["list", "add"]); p.add_argument("file", nargs="?")
    p.add_argument("--id"); p.add_argument("--note"); p.add_argument("--origin"); p.add_argument("--keep", action="store_true")
    p.set_defaults(f=cmd_corpus)
    p = sub.add_parser("status"); p.add_argument("--json", action="store_true"); p.set_defaults(f=cmd_status)
    p = sub.add_parser("next"); p.add_argument("--bank"); p.add_argument("--kind"); p.add_argument("-n", type=int, default=20)
    p.add_argument("--min-count", type=int, default=0); p.set_defaults(f=cmd_next)
    p = sub.add_parser("fn"); p.add_argument("at"); p.set_defaults(f=cmd_fn)
    p = sub.add_parser("dis"); p.add_argument("at"); p.add_argument("--len", type=lambda s: int(s, 0), default=64)
    p.set_defaults(f=cmd_dis)
    p = sub.add_parser("xref"); p.add_argument("x"); p.add_argument("--len", type=lambda s: int(s, 0), default=1)
    p.set_defaults(f=cmd_xref)
    p = sub.add_parser("io"); p.add_argument("at"); p.add_argument("--on", required=True)
    p.add_argument("--calls", type=int, default=200); p.add_argument("--rows", type=int, default=12)
    p.add_argument("--addrs", type=int, default=40); p.set_defaults(f=cmd_io)
    p = sub.add_parser("trace"); p.add_argument("at"); p.add_argument("--on", required=True)
    p.add_argument("--call", type=int, default=0); p.add_argument("--max", type=int, default=400)
    p.set_defaults(f=cmd_trace)
    p = sub.add_parser("when"); p.add_argument("at"); p.set_defaults(f=cmd_when)
    p = sub.add_parser("script"); p.add_argument("at"); p.add_argument("--len", type=lambda s: int(s, 0), default=0)
    p.set_defaults(f=cmd_script)
    p = sub.add_parser("vm"); p.set_defaults(f=cmd_vm)
    p = sub.add_parser("sprites"); p.add_argument("--toml", action="store_true"); p.set_defaults(f=cmd_sprites)
    p = sub.add_parser("packed"); p.add_argument("--toml", action="store_true"); p.set_defaults(f=cmd_packed)
    p = sub.add_parser("snd"); p.add_argument("--toml", action="store_true"); p.set_defaults(f=cmd_snd)
    p = sub.add_parser("watch"); p.add_argument("addrs", nargs="+"); p.add_argument("--on", required=True)
    p.add_argument("--max", type=int, default=60); p.set_defaults(f=cmd_watch)
    p = sub.add_parser("look"); p.add_argument("window"); p.add_argument("--scale", type=int, default=2)
    p.set_defaults(f=cmd_look)
    p = sub.add_parser("try"); p.add_argument("--on", required=True); p.add_argument("--frames", type=int, required=True)
    p.add_argument("--poke", nargs="*"); p.add_argument("--hold", action="store_true"); p.add_argument("--patch", nargs="*")
    p.add_argument("--input"); p.add_argument("--max", type=int, default=40); p.set_defaults(f=cmd_try)
    p = sub.add_parser("render"); p.set_defaults(f=cmd_render)
    p = sub.add_parser("selftest"); p.add_argument("--unit", action="append")
    p.set_defaults(f=lambda a: sys.exit(0 if __import__("selftest").main(only=a.unit) else 1))
    p = sub.add_parser("check"); p.add_argument("--no-build", action="store_true")
    p.add_argument("--no-cache", action="store_true"); p.add_argument("--unit"); p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--no-status", action="store_true")
    p.set_defaults(f=cmd_check)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
