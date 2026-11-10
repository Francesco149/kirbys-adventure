"""Packed data: the streams that `unpack` (3E:C43A) expands, as a data format (documented in db/unpack.toml).

  packed            one stream: commands up to and including the terminator $FF. `unpacked = N` in the entry
                    is the number of bytes it expands to.
  packlo:HI[:BANK]  the low bytes of a table of stream addresses. HI names the region with the high bytes;
                    BANK names the region with the bank numbers (bit 7 of a bank byte is not part of the
                    number), or is the bank as two hex digits, or is left out for the table's own bank. An
                    entry whose address is 0 is empty.
  packhi:LO, packbank:LO   the other halves of such a table.

A command byte is `ccc nnnnn` (count n + 1) or `111 ccc nn` + one byte (count ((nn << 8) | byte) + 1):

  c = 0  count literal bytes follow            4  count bytes copied from the output, from a 16-bit offset
  c = 1  one byte, written count times            (high byte first) into what this call has written so far
  c = 2  two bytes, written count times        5  the same, each byte with its bits reversed
  c = 3  one byte, then +1 per byte written    6  the same, reading backwards from the offset
                                               7  as 4

The format is defined by who reads it: a command byte (and the terminator) is first read by the peek at
3E:C446, every other byte only by the fetch at 3E:C54D. A region is checked by parsing it and by comparing,
for every byte the corpus read, the instructions that read it with what the parse says the byte is.
"""
import numpy as np

BANK = 0x2000
PRG = 0x80000
B3E = 0x3E * BANK - 0xC000
PEEK, PEEK2, FETCH = B3E + 0xC446, B3E + 0xC453, B3E + 0xC54D
FORMATS = ("packed", "packlo", "packhi", "packbank")
NAMES = ("literal", "fill", "fill2", "count_up", "copy", "copy_rev", "copy_back", "copy")


def commands(prg, off, end):
    """[(offset, c, count, header length, operand length)] of the stream at off, then the terminator's offset.
    -> (commands, length including the terminator, bytes it expands to), or None when no terminator comes
    before end or a copy starts beyond what has been written."""
    o, out, cmds = off, 0, []
    while o < end:
        b = int(prg[o])
        if b == 0xFF:
            return cmds, o + 1 - off, out
        if b & 0xE0 == 0xE0:
            if o + 1 >= end:
                return None
            c, n, h = b >> 2 & 7, ((b & 3) << 8 | int(prg[o + 1])) + 1, 2
        else:
            c, n, h = b >> 5, (b & 0x1F) + 1, 1
        k = n if c == 0 else 1 if c in (1, 3) else 2
        if o + h + k > end:
            return None
        if c >= 4:
            ref = int(prg[o + h]) << 8 | int(prg[o + h + 1])
            if ref >= out or (c == 6 and ref + 1 < n):
                return None                 # a copy from where nothing has been written yet
        cmds.append((o, c, n, h, k))
        out += 2 * n if c == 2 else n
        o += h + k
    return None


def unpack(prg, off, end):
    """The bytes the stream at off expands to (the model of 3E:C43A), or None."""
    p = commands(prg, off, end)
    if p is None:
        return None
    out = []
    for o, c, n, h, k in p[0]:
        a = [int(x) for x in prg[o + h:o + h + k]]
        if c == 0:
            out += a
        elif c == 1:
            out += a * n
        elif c == 2:
            out += a * n
        elif c == 3:
            out += [(a[0] + i) & 0xFF for i in range(n)]
        else:
            ref = a[0] << 8 | a[1]
            for i in range(n):
                v = out[ref - i] if c == 6 else out[ref + i]
                out.append(int(f"{v:08b}"[::-1], 2) if c == 5 else v)
    return out


def table_parts(db, e):
    """A packlo entry -> (hi entry, bank entry or bank number), or raises ValueError."""
    f = e["format"].split(":")
    if len(f) < 2 or f[1] not in db.by_name or db.by_name[f[1]][0] != "data":
        raise ValueError("no region with the high bytes")
    hi = db.by_name[f[1]][1]
    if len(f) > 2 and f[2] in db.by_name and db.by_name[f[2]][0] == "data":
        bank = db.by_name[f[2]][1]
    elif len(f) > 2:
        try:
            bank = int(f[2], 16)
        except ValueError:
            raise ValueError(f"'{f[2]}' is neither a region nor a bank")
    else:
        bank = e["off"] >> 13
    for other in (hi, bank):
        if isinstance(other, dict) and other["len"] != e["len"]:
            raise ValueError(f"{other['name']} has another length")
    return hi, bank


def table_targets(prg, db, e):
    """PRG offsets the entries of a packlo table point to: None for an empty entry, -1 for an address outside
    $8000-$BFFF or a bank that does not exist."""
    hi, bank = table_parts(db, e)
    out = []
    for i in range(e["len"]):
        a = int(prg[hi["off"] + i]) << 8 | int(prg[e["off"] + i])
        b = (int(prg[bank["off"] + i]) & 0x7F) if isinstance(bank, dict) else bank
        out.append(None if a == 0 else b * BANK + (a & 0x1FFF) if 0x8000 <= a < 0xC000 and b < 0x40 else -1)
    return out


def _readers(ev, off):
    return [int(r) - 1 for r in (ev.rdr1[off], ev.rdr2[off]) if r]


def check(db, m, ev, names, complete=False):
    """The `format` claim for packed regions and their tables: -> (problems, stats)."""
    prg = m.prg
    problems = []
    starts, covered = {}, np.zeros(PRG, dtype=bool)
    for e in db.data:
        if e["format"] == "packed":
            starts[e["off"]] = e
            covered[e["off"]:e["off"] + e["len"]] = True
    st = {"regions": 0, "bytes": 0, "read": 0, "streams": 0, "pointers": 0}
    for name in names:
        kind, e = db.by_name[name]
        f = e.get("format", "").split(":") if kind == "data" else [None]
        if f[0] not in FORMATS:
            problems.append(f"{name}: not a packed stream or a table of them")
            continue
        s, n = e["off"], e["len"]
        st["regions"] += 1
        st["bytes"] += n
        seg = m.kind[s:s + n]
        if ((seg != ord("d")) & (seg != ord("?"))).any():
            problems.append(f"{name}: {int(((seg != ord('d')) & (seg != ord('?'))).sum())} of its bytes are code or script in the model")
        if f[0] in ("packhi", "packbank"):
            lo = db.by_name.get(f[1] if len(f) > 1 else "")
            if not lo or lo[0] != "data" or not lo[1]["format"].startswith("packlo:"):
                problems.append(f"{name}: '{f[1] if len(f) > 1 else ''}' is not a packlo region")
            elif e["name"] not in lo[1]["format"].split(":")[1:]:
                problems.append(f"{name}: {lo[1]['name']} does not name it")
            st["read"] += int((ev.dcount[s:s + n] != 0).sum())
            continue
        if f[0] == "packlo":
            try:
                targets = table_targets(prg, db, e)
            except ValueError as x:
                problems.append(f"{name}: {x}")
                continue
            for i, t in enumerate(targets):
                if t is None:
                    continue
                st["pointers"] += 1
                if t not in starts:
                    problems.append(f"{name}: entry {i} does not point to the start of a packed region"
                                    + (f" ({m.name(t)})" if t >= 0 else ""))
                    break
            st["read"] += int((ev.dcount[s:s + n] != 0).sum())
            continue
        p = commands(prg, s, ((s >> 13) + 1) * BANK)
        if p is None:
            problems.append(f"{name}: no stream parses here")
            continue
        cmds, ln, out = p
        if ln != n:
            problems.append(f"{name}: the stream is {ln} bytes long, the region {n}")
            continue
        if e.get("unpacked") != out:
            problems.append(f"{name}: the stream expands to {out} bytes, the entry says {e.get('unpacked')}")
            continue
        st["streams"] += 1
        head = {c[0] for c in cmds} | {s + n - 1}
        for o in range(s, s + n):
            rs = _readers(ev, o)
            if not rs:
                continue
            st["read"] += 1
            if o in head:
                bad = rs[0] != PEEK or any(r not in (PEEK, PEEK2, FETCH) for r in rs)
            else:
                bad = any(r != FETCH for r in rs)
            if bad:
                problems.append(f"{name}+{o - s}: {'a command byte' if o in head else 'an operand byte'} by the "
                                f"format, but read by {', '.join(m.name(r) for r in rs)}")
                break
    if complete:
        ids = np.array([PEEK + 1, PEEK2 + 1, FETCH + 1], dtype=ev.rdr1.dtype)
        rd = np.isin(ev.rdr1[:PRG], ids) | np.isin(ev.rdr2[:PRG], ids)
        out = np.flatnonzero(rd & ~covered)
        if len(out):
            problems.append(f"{len(out)} bytes read by unpack are in no packed region, the first at {m.name(int(out[0]))}")
    return problems, st


# ---------------------------------------------------------------- discovery
def discover(db, m, ev, log=print):
    """Every stream the corpus unpacked and every stream a packlo table of the database points to.
    -> [data entries as dicts] in address order, without those that are in the database already."""
    prg = m.prg
    ids = np.array([PEEK + 1, PEEK2 + 1, FETCH + 1], dtype=ev.rdr1.dtype)
    rd = np.isin(ev.rdr1[:PRG], ids) | np.isin(ev.rdr2[:PRG], ids)
    found = {}                               # start -> (length, expands to, how it was found)
    done = np.zeros(PRG, dtype=bool)
    for o in np.flatnonzero(rd).tolist():
        if done[o]:
            continue
        p = commands(prg, o, ((o >> 13) + 1) * BANK)
        if p is None or ev.rdr1[o] != PEEK + 1:
            log(f"  {m.name(o)}: read by unpack, but no stream starts here")
            continue
        found[o] = (p[1], p[2], "unpacked in the corpus")
        done[o:o + p[1]] = True
    nread = len(found)
    for e in db.data:
        if not e["format"].startswith("packlo:"):
            continue
        try:
            targets = table_targets(prg, db, e)
        except ValueError as x:
            log(f"  {e['name']}: {x}")
            continue
        for i, t in enumerate(targets):
            if t is None or t in found:
                continue
            p = commands(prg, t, ((t >> 13) + 1) * BANK) if t >= 0 else None
            if p is None:
                log(f"  {e['name']}: entry {i} points to no stream")
                continue
            have = db.data_at(t)
            if not (have and have[0]["format"] == "packed" and have[1] == 0) and (m.kind[t:t + p[1]] != ord("?")).any():
                log(f"  {e['name']}: entry {i} ({m.name(t)}) points into bytes something else read or ran")
                continue
            found[t] = (p[1], p[2], f"entry {i} of {e['name']}")
    order = sorted(found)
    for a, b in zip(order, order[1:]):
        if a + found[a][0] > b:
            log(f"  {m.name(b)} starts inside the stream at {m.name(a)}")
    out = []
    for s in order:
        ln, n, how = found[s]
        if db.data_at(s) or db.data_at(s + ln - 1):
            continue
        ncmd = len(commands(prg, s, s + ln)[0])
        out.append({"off": s, "len": ln, "name": f"packed_{s >> 13:02X}_{m.cpu(s):04X}", "format": "packed",
                    "unpacked": n,
                    "desc": f"Packed stream of {ncmd} command{'s' if ncmd != 1 else ''} that expands to {n} bytes"
                            + ("." if how.startswith("unpacked") else f"; not unpacked in the corpus, found as {how}.")})
    log(f"  {len(found)} streams, {sum(v[0] for v in found.values()):,} bytes: {nread} unpacked in the corpus, "
        f"{len(found) - nread} more from tables; {len(found) - len(out)} are in the database already")
    return out


def toml(entries, m):
    L = []
    for e in entries:
        L += ["[[data]]", f'at = "{m.name(e["off"])}"', f"len = {e['len']}", f'name = "{e["name"]}"',
              f'format = "{e["format"]}"', f"unpacked = {e['unpacked']}", f'desc = "{e["desc"]}"', ""]
    return "\n".join(L)


def listing(prg, off, length):
    """[(start, length, comment)] per command of a packed region, for the rendered source."""
    p = commands(prg, off, off + length)
    if p is None or p[1] != length:
        return None
    rows = []
    for o, c, n, h, k in p[0]:
        a = [int(x) for x in prg[o + h:o + h + k]]
        if c == 0:
            what = f"{n} literal byte{'s' if n > 1 else ''}"
        elif c == 1:
            what = f"${a[0]:02X} x {n}"
        elif c == 2:
            what = f"${a[0]:02X} ${a[1]:02X} x {n}"
        elif c == 3:
            what = f"${a[0]:02X}, ${(a[0] + 1) & 0xFF:02X}, ... x {n}"
        else:
            what = (f"copy {n} from output +${a[0] << 8 | a[1]:04X}"
                    + {5: ", bits reversed", 6: ", backwards"}.get(c, ""))
        rows.append((o, h + k, what))
    rows.append((off + length - 1, 1, "end"))
    return rows
