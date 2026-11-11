"""Sound data: what the sound engine of bank 1D plays, as data formats (the engine is documented in db/sound.toml).

  sndhdr     headers, one after the other: a count N = 1-5, then N records of 3 bytes: the address of a track
             stream (low, high) and its channel (0, 4, 8, $C). A sound's header and streams are in bank 1D
             ($8000); a song's are in the bank its entry of snd_song_bank names ($A000).
  sndtrack   track stream elements, one after the other. The first byte gives the length:
               $00-$BF  a note or rest, 1 byte (bits 7-5 a length code, bits 4-0 the pitch field)
               $C0-$DF  a note or rest with its length in a second byte
               $E0 a b  DMC sample address and length        $E3 n   add n to the period
               $F0 n    volume       $F1 n  add to the volume $F2 n   row of the length table
               $F3 n    wait         $F4 n  gate              $F5 n   transpose      $F6 n  instrument
               $F8 lo hi  jump       $FA lo hi  call          $FB     return
               $FC n    loop start   $FD    loop end          $FF     end
  sndenv     envelope stream elements, one after the other: every byte below $E0 is an element of its own
             ($00-$1F wait, $20-$3F period, $40-$5F volume, $60-$7F add to the volume, $80-$9F duty); $F8, $FA,
             $FB, $FC, $FD and $FF as in a track stream.

A region is a run of elements: a stream ends at $FF, $FB or $F8 and the next one usually starts on the next
byte. The format is defined by who reads it: an element's first byte is the only kind of byte the dispatch
reads see (1D:8250 for tracks, 1D:8543 for envelopes); the operands of a jump are read at 1D:8448 / 1D:844C; a
header's count at 1D:806F (sound) or 1D:813D (song), its records at 1D:80E9, 1D:80EF, 1D:80F5. The fetch of
snd_next_byte (1D:84E6) is allowed on every byte: it reads operands, and it reads ahead (db/sound.toml says where).
A region is checked by parsing it and by comparing, for every byte the corpus read, the instructions that read
it with what the parse says the byte is.
"""
import numpy as np

BANK = 0x2000
PRG = 0x80000
B1D = 0x1D * BANK - 0x8000
FORMATS = ("sndhdr", "sndtrack", "sndenv")

ADV = B1D + 0x84E6
TRACK_FIRST = B1D + 0x8250                                  # the dispatch read of a track element
TRACK_AGAIN = tuple(B1D + a for a in (0x8262, 0x8288, 0x8308, 0x8326, 0x8441))
ENV_FIRST = B1D + 0x8543
ENV_AGAIN = tuple(B1D + a for a in (0x8549, 0x864A, 0x855F, 0x8571, 0x859D, 0x85BA, 0x8441))
JUMP_OPS = (B1D + 0x8448, B1D + 0x844C)
HDR_COUNT = (B1D + 0x806F, B1D + 0x813D)
HDR_REC = (B1D + 0x80E9, B1D + 0x80EF, B1D + 0x80F5)

TRACK_LEN = {0xE0: 3, 0xE3: 2, 0xF0: 2, 0xF1: 2, 0xF2: 2, 0xF3: 2, 0xF4: 2, 0xF5: 2, 0xF6: 2,
             0xF8: 3, 0xFA: 3, 0xFB: 1, 0xFC: 2, 0xFD: 1, 0xFF: 1}
ENV_LEN = {0xF8: 3, 0xFA: 3, 0xFB: 1, 0xFC: 2, 0xFD: 1, 0xFF: 1}
ENDS = (0xFF, 0xFB, 0xF8)                                   # after these nothing follows in the same stream


def elen(b, fmt):
    """Length of the element that starts with byte b, or None when the engine has no such element (or one
    that never ran, which the format does not describe)."""
    if fmt == "sndtrack":
        return 1 if b < 0xC0 else 2 if b < 0xE0 else TRACK_LEN.get(b)
    return 1 if b < 0xA0 else ENV_LEN.get(b)


def elements(prg, off, end, fmt):
    """[(offset, length)] of the elements from off up to end, or None when one does not parse or the last
    one runs over the end."""
    o, out = off, []
    while o < end:
        n = elen(int(prg[o]), fmt)
        if n is None or o + n > end:
            return None
        out.append((o, n))
        o += n
    return out


def headers(prg, off, end):
    """[(offset, N)] of the headers from off up to end, or None."""
    o, out = off, []
    while o < end:
        n = int(prg[o])
        if not 1 <= n <= 5 or o + 1 + 3 * n > end:
            return None
        if any(int(prg[o + 3 + 3 * i]) not in (0, 4, 8, 0xC) for i in range(n)):
            return None
        out.append((o, n))
        o += 1 + 3 * n
    return out


def window(off):
    """CPU address of the first byte of the bank of off, as the engine maps it: bank 1D at $8000, the song
    banks at $A000."""
    return 0x8000 if off >> 13 == 0x1D else 0xA000


def target(off, lo, hi):
    """PRG offset of the address hi:lo seen from a stream at off (the same bank), or None when the address is
    outside the bank's window."""
    a = hi << 8 | lo
    w = window(off)
    return (off >> 13) * BANK + a - w if w <= a < w + BANK else None


def header_tables(db):
    """-> [(PRG offset of a header, how)] from the engine's tables in the database."""
    need = ("snd_sfx_lo", "snd_sfx_hi", "snd_song_lo", "snd_song_hi", "snd_song_bank")
    if any(n not in db.by_name for n in need):
        raise ValueError("the tables snd_sfx_lo/hi and snd_song_lo/hi/bank are not in the database")
    return [db.by_name[n][1] for n in need]


def roots(prg, db):
    """Header offsets: {offset: 'sound $NN' / 'song $NN'}; a bad entry maps to None."""
    slo, shi, mlo, mhi, mbank = header_tables(db)
    out = {}
    for i in range(slo["len"]):
        a = int(prg[shi["off"] + i]) << 8 | int(prg[slo["off"] + i])
        out.setdefault(B1D + a if 0x8000 <= a < 0xA000 else -1 - i, f"sound ${i:02X}")
    for i in range(mlo["len"]):
        a = int(prg[mhi["off"] + i]) << 8 | int(prg[mlo["off"] + i])
        b = int(prg[mbank["off"] + i])
        ok = 0xA000 <= a < 0xC000 and b < 0x40
        out.setdefault(b * BANK + a - 0xA000 if ok else -1000 - i, f"song ${i:02X}")
    return out


def env_roots(prg, db):
    """Envelope stream offsets from snd_inst_envs (pairs of addresses in bank 1D)."""
    if "snd_inst_envs" not in db.by_name:
        raise ValueError("snd_inst_envs is not in the database")
    e = db.by_name["snd_inst_envs"][1]
    out = {}
    for i in range(0, e["len"], 2):
        a = int(prg[e["off"] + i]) | int(prg[e["off"] + i + 1]) << 8
        out.setdefault(B1D + a if 0x8000 <= a < 0xA000 else -1 - i, f"instrument ${i // 4:02X}")
    return out


def follow(prg, starts, fmt, log):
    """Every element reachable from the stream starts, following jumps and calls.
    -> {offset: length}; streams that do not parse are logged and dropped."""
    seen, todo = {}, list(starts.items())
    while todo:
        o, how = todo.pop()
        if o < 0 or o >= PRG:
            log(f"  {how}: an address outside its bank")
            continue
        end = ((o >> 13) + 1) * BANK
        while o < end and o not in seen:
            b = int(prg[o])
            n = elen(b, fmt)
            if n is None or o + n > end:
                log(f"  {how}: no {fmt} element at {o >> 13:02X}:{window(o) + (o & 0x1FFF):04X} (byte ${b:02X})")
                break
            seen[o] = n
            if b in (0xF8, 0xFA):
                t = target(o, int(prg[o + 1]), int(prg[o + 2]))
                todo.append((t if t is not None else -1, f"{how}, {'jump' if b == 0xF8 else 'call'} at "
                                                         f"{o >> 13:02X}:{window(o) + (o & 0x1FFF):04X}"))
            if b in ENDS:
                break
            o += n
    return seen


def runs(els):
    """{offset: length} -> [(start, length)] of the maximal runs of elements that touch."""
    out, cur = [], None
    for o in sorted(els):
        if cur and cur[0] + cur[1] == o:
            cur[1] += els[o]
        else:
            cur = [o, els[o]]
            out.append(cur)
    return [(a, n) for a, n in out]


def _readers(ev, off):
    return [int(r) - 1 for r in (ev.rdr1[off], ev.rdr2[off]) if r]


def kinds(prg, e):
    """{offset: kind} for every byte of a region: 'first' (of an element), 'op', 'jump' (operand of $F8),
    'count', 'rec'; or None when the region does not parse."""
    s, n, fmt = e["off"], e["len"], e["format"]
    out = {}
    if fmt == "sndhdr":
        hs = headers(prg, s, s + n)
        if hs is None:
            return None
        for o, k in hs:
            out[o] = "count"
            for i in range(1, 1 + 3 * k):
                out[o + i] = "rec"
        return out
    els = elements(prg, s, s + n, fmt)
    if els is None:
        return None
    for o, k in els:
        out[o] = "first"
        for i in range(1, k):
            out[o + i] = "jump" if int(prg[o]) == 0xF8 else "op"
    return out


def check(db, m, ev, names, complete=False):
    """The `format` claim for sound regions: -> (problems, stats)."""
    prg = m.prg
    problems = []
    st = {"regions": 0, "bytes": 0, "read": 0, "elements": 0, "headers": 0}
    cover = {f: np.zeros(PRG, dtype=bool) for f in FORMATS}
    for e in db.data:
        if e["format"] in FORMATS:
            cover[e["format"]][e["off"]:e["off"] + e["len"]] = True
    first = {}
    for e in db.data:
        if e["format"] in ("sndtrack", "sndenv"):
            k = kinds(prg, e)
            for o, v in (k or {}).items():
                if v == "first":
                    first[o] = e["format"]
    for name in names:
        kind, e = db.by_name[name]
        fmt = e.get("format") if kind == "data" else None
        if fmt not in FORMATS:
            problems.append(f"{name}: not a sound region")
            continue
        s, n = e["off"], e["len"]
        st["regions"] += 1
        st["bytes"] += n
        seg = m.kind[s:s + n]
        if ((seg != ord("d")) & (seg != ord("?"))).any():
            problems.append(f"{name}: {int(((seg != ord('d')) & (seg != ord('?'))).sum())} of its bytes are code or script in the model")
        ks = kinds(prg, e)
        if ks is None:
            problems.append(f"{name}: does not parse as {fmt}")
            continue
        st["headers" if fmt == "sndhdr" else "elements"] += sum(1 for v in ks.values() if v in ("first", "count"))
        if fmt == "sndhdr":
            for o, k in headers(prg, s, s + n):
                for i in range(k):
                    t = target(o, int(prg[o + 1 + 3 * i]), int(prg[o + 2 + 3 * i]))
                    if first.get(t) != "sndtrack":
                        problems.append(f"{name}+{o - s}: track {i} does not point to an element of a sndtrack region")
                        break
        else:
            for o, v in ks.items():
                if v == "first" and int(prg[o]) in (0xF8, 0xFA):
                    t = target(o, int(prg[o + 1]), int(prg[o + 2]))
                    if first.get(t) != fmt:
                        problems.append(f"{name}+{o - s}: the {'jump' if int(prg[o]) == 0xF8 else 'call'} does not "
                                        f"point to an element of a {fmt} region")
                        break
        allowed = {"count": HDR_COUNT + (ADV,), "rec": HDR_REC + (ADV,), "jump": JUMP_OPS + (ADV,), "op": (ADV,),
                   "first": ((TRACK_FIRST,) + TRACK_AGAIN if fmt == "sndtrack" else (ENV_FIRST,) + ENV_AGAIN) + (ADV,)}
        for o in range(s, s + n):
            rs = _readers(ev, o)
            if not rs:
                continue
            st["read"] += 1
            if any(r not in allowed[ks[o]] for r in rs):
                what = {"count": "a header's count", "rec": "a header's record", "jump": "a jump's operand",
                        "op": "an operand", "first": "the first byte of an element"}[ks[o]]
                problems.append(f"{name}+{o - s}: {what} by the format, but read by {', '.join(m.name(r) for r in rs)}")
                break
    if complete:
        for fmt, ids, what in (("sndtrack", (TRACK_FIRST,), "the track dispatch"), ("sndenv", (ENV_FIRST,), "the envelope dispatch"),
                               ("sndhdr", HDR_COUNT + HDR_REC, "the header readers")):
            a = np.array([i + 1 for i in ids], dtype=ev.rdr1.dtype)
            rd = np.isin(ev.rdr1[:PRG], a) | np.isin(ev.rdr2[:PRG], a)
            out = np.flatnonzero(rd & ~cover[fmt])
            if len(out):
                problems.append(f"{len(out)} bytes read by {what} are in no {fmt} region, the first at {m.name(int(out[0]))}")
    return problems, st


# ---------------------------------------------------------------- discovery
def discover(db, m, ev, log=print):
    """Every header the engine's tables name, every track stream the headers name and every envelope stream
    snd_inst_envs names, with what their jumps and calls reach. -> [data entries] in address order, without
    those that are in the database already."""
    prg = m.prg
    hdr = {}
    rts = roots(prg, db)
    tracks = {}
    for o, how in sorted(rts.items()):
        hs = headers(prg, o, o + 1 + 3 * int(prg[o])) if 0 <= o < PRG and 1 <= int(prg[o]) <= 5 else None
        if not hs:
            log(f"  {how}: no header at its address")
            continue
        hdr[o] = 1 + 3 * hs[0][1]
        for i in range(hs[0][1]):
            t = target(o, int(prg[o + 1 + 3 * i]), int(prg[o + 2 + 3 * i]))
            tracks.setdefault(t if t is not None else -1, f"{how} track {i}")
    found = {"sndhdr": hdr, "sndtrack": follow(prg, tracks, "sndtrack", log),
             "sndenv": follow(prg, env_roots(prg, db), "sndenv", log)}
    out, total = [], 0
    for fmt in FORMATS:
        for s, n in runs(found[fmt]):
            total += n
            rd = int((ev.dcount[s:s + n] != 0).sum())
            other = m.kind[s:s + n]
            if ((other != ord("d")) & (other != ord("?"))).any():
                log(f"  {m.name(s)}: a {fmt} run of {n} bytes holds code or script in the model")
                continue
            if db.data_at(s) or db.data_at(s + n - 1):
                continue
            cnt = sum(1 for o in found[fmt] if s <= o < s + n)
            what = {"sndhdr": f"{cnt} sound or song header{'s' if cnt != 1 else ''}",
                    "sndtrack": f"Track streams, {cnt} elements", "sndenv": f"Envelope streams, {cnt} elements"}[fmt]
            out.append({"off": s, "len": n, "name": f"{fmt}_{s >> 13:02X}_{m.cpu(s):04X}", "format": fmt,
                        "desc": what + ("." if rd else "; not read in the corpus.")})
    log(f"  {len(found['sndhdr'])} headers, {len(found['sndtrack'])} track elements, {len(found['sndenv'])} envelope "
        f"elements, {total:,} bytes; {len(out)} regions are not in the database")
    return sorted(out, key=lambda e: e["off"])


def toml(entries, m):
    L = []
    for e in entries:
        L += ["[[data]]", f'at = "{m.name(e["off"])}"', f"len = {e['len']}", f'name = "{e["name"]}"',
              f'format = "{e["format"]}"', f'desc = "{e["desc"]}"', ""]
    return "\n".join(L)


NOTE = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _track(prg, o, n):
    b = int(prg[o])
    a = [int(x) for x in prg[o + 1:o + n]]
    if b < 0xE0:
        f = b & 0x1F
        ln = f"length ${a[0]:02X}" if b >= 0xC0 else f"length code {b >> 5}"
        return f"note field ${f:02X}, {ln}"
    return {0xE0: lambda: f"dmc sample ${a[0]:02X}, length ${a[1]:02X}", 0xE3: lambda: f"period += ${a[0]:02X}",
            0xF0: lambda: f"volume ${a[0]:02X}", 0xF1: lambda: f"volume += ${a[0]:02X}",
            0xF2: lambda: f"length row {a[0]}", 0xF3: lambda: f"wait {a[0]}", 0xF4: lambda: f"gate ${a[0]:02X}",
            0xF5: lambda: f"transpose ${a[0]:02X}", 0xF6: lambda: f"instrument ${a[0]:02X}",
            0xF8: lambda: f"jump ${a[1]:02X}{a[0]:02X}", 0xFA: lambda: f"call ${a[1]:02X}{a[0]:02X}",
            0xFB: lambda: "return", 0xFC: lambda: f"loop {a[0]}", 0xFD: lambda: "loop end",
            0xFF: lambda: "end"}[b]()


def _env(prg, o, n):
    b = int(prg[o])
    a = [int(x) for x in prg[o + 1:o + n]]
    if b < 0xA0:
        v = b & 0x0F
        stop = ", then next frame" if b & 0x10 else ""
        return (f"wait {b}" if b < 0x20 else f"period += nibble ${v:X}{stop}" if b < 0x40 else f"volume {v}{stop}"
                if b < 0x60 else f"volume += nibble ${v:X}{stop}" if b < 0x80 else f"duty {b & 3}{stop}")
    return {0xF8: lambda: f"jump ${a[1]:02X}{a[0]:02X}", 0xFA: lambda: f"call ${a[1]:02X}{a[0]:02X}",
            0xFB: lambda: "return", 0xFC: lambda: f"loop {a[0]}", 0xFD: lambda: "loop end", 0xFF: lambda: "end"}[b]()


def listing(prg, off, length, fmt):
    """[(start, length, comment)] per element or header of a sound region, for the rendered source."""
    if fmt == "sndhdr":
        hs = headers(prg, off, off + length)
        if hs is None:
            return None
        rows = []
        for o, n in hs:
            rows.append((o, 1, f"{n} track{'s' if n != 1 else ''}"))
            for i in range(n):
                p = o + 1 + 3 * i
                rows.append((p, 3, f"stream ${int(prg[p + 1]):02X}{int(prg[p]):02X}, channel ${int(prg[p + 2]):02X}"))
        return rows
    els = elements(prg, off, off + length, fmt)
    if els is None:
        return None
    return [(o, n, (_track if fmt == "sndtrack" else _env)(prg, o, n)) for o, n in els]
