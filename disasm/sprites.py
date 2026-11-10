"""Sprite groups and pose tables as data: the format (documented in db/draw.toml), the discovery of every
table and group in the ROM, and the checks behind the `format` claim kind.

  sprites      a run of sprite groups: count, then count x (X offset, Y offset, tile, attribute)
  poses        a run of poses: a CHR bank byte, then a sprite group
  poseptr:BB   16-bit pointers to groups / poses in bank BB as mapped at $8000 (what the script opcode
               sprite_map gives an object, indexed by its pose)

The format is defined by who reads it: every kind of byte has the instructions of the draw routines (bank 3E)
that read it. A region is checked by parsing it and by comparing, for every byte the corpus read, the
instruction that read it with the kind of byte the parse says it is.
"""
import numpy as np

BANK = 0x2000
PRG = 0x80000
B3E = 0x3E * BANK - 0xC000
MAX_SPRITES = 64            # a sprite buffer has 64 entries

# kind of byte -> CPU addresses (bank 3E) of the instructions that read it
ROLE_READERS = {
    "chr": (0xDDB0, 0xDDC3, 0xDDDF),                    # pose_draw, kirby_draw_pal1, 3E:DDD9
    "count": (0xDA91, 0xDB4A, 0xDC31, 0xDCF4),          # sprite_group, mirror, masked, back
    "dx": (0xDAA0, 0xDAF2, 0xDB59, 0xDBC3, 0xDC40, 0xDC98, 0xDD03, 0xDD55),
    "dy": (0xDAB7, 0xDB09, 0xDB7B, 0xDBE5, 0xDC57, 0xDCAF, 0xDD1A, 0xDD6C),
    "tile": (0xDACA, 0xDB1C, 0xDB99, 0xDC03, 0xDC6A, 0xDCC2, 0xDD2D, 0xDD7F),
    "attr": (0xDAD2, 0xDB24, 0xDBA1, 0xDC0B, 0xDC72, 0xDCCA, 0xDD35, 0xDD87),
    "ptr": (0xCD5D, 0xCD61),                            # obj_run_all: entry obj_pose of the object's table
}
GROUP_ROLES = ("chr", "count", "dx", "dy", "tile", "attr")
FORMATS = ("sprites", "poses", "poseptr")


def role_masks(ev):
    """role -> bool array over PRG: the byte was read by one of the role's instructions."""
    out = {}
    for role, addrs in ROLE_READERS.items():
        ids = np.array([B3E + a + 1 for a in addrs], dtype=ev.rdr1.dtype)      # reader ids are offset + 1
        out[role] = np.isin(ev.rdr1[:PRG], ids) | np.isin(ev.rdr2[:PRG], ids)
    return out


def group_len(prg, off, pose, end):
    """Length of the group (or pose) at off, or None when it is not one that fits before end."""
    c = off + (1 if pose else 0)
    if c >= end:
        return None
    n = int(prg[c])
    if not 1 <= n <= MAX_SPRITES:
        return None
    ln = (1 if pose else 0) + 1 + 4 * n
    return ln if off + ln <= end else None


def parse(prg, off, length, fmt):
    """[(start, sprites)] for a sprites / poses region; ValueError when it does not tile exactly."""
    pose = fmt == "poses"
    out, o, end = [], off, off + length
    while o < end:
        ln = group_len(prg, o, pose, end)
        if ln is None:
            raise ValueError(f"no {'pose' if pose else 'sprite group'} fits at +{o - off}")
        out.append((o, (ln - (2 if pose else 1)) // 4))
        o += ln
    return out


def roles(prg, off, length, fmt):
    """[role] per byte of a sprites / poses region."""
    out = []
    for start, n in parse(prg, off, length, fmt):
        out += (["chr"] if fmt == "poses" else []) + ["count"] + ["dx", "dy", "tile", "attr"] * n
    return out


def table_targets(prg, e):
    """PRG offsets (or None) the entries of a poseptr region point to."""
    bank = int(e["format"].split(":")[1], 16)
    out = []
    for i in range(0, e["len"] - 1, 2):
        v = int(prg[e["off"] + i]) | int(prg[e["off"] + i + 1]) << 8
        out.append(bank * BANK + (v & 0x1FFF) if 0x8000 <= v < 0xA000 else None)
    return out


def _reader_addrs(ev, off):
    return [int(r) - 1 for r in (ev.rdr1[off], ev.rdr2[off]) if r]


def check(db, m, ev, names, complete=False):
    """The `format` claim: -> (problems, stats). names: the data regions the claim is about."""
    prg = m.prg
    problems = []
    starts = {}                      # group start -> "sprites" / "poses", over every region in the database
    covered = np.zeros(PRG, dtype=bool)
    tabcov = np.zeros(PRG, dtype=bool)
    for e in db.data:
        f = e["format"].split(":")[0]
        if f in ("sprites", "poses"):
            try:
                for s, n in parse(prg, e["off"], e["len"], f):
                    starts[s] = f
            except ValueError:
                pass
            covered[e["off"]:e["off"] + e["len"]] = True
        elif f == "poseptr":
            tabcov[e["off"]:e["off"] + e["len"]] = True
    st = {"regions": 0, "bytes": 0, "read": 0, "groups": 0, "pointers": 0}
    for name in names:
        kind, e = db.by_name[name]
        f = e.get("format", "").split(":")[0] if kind == "data" else None
        if f not in FORMATS:
            problems.append(f"{name}: not a sprites / poses / poseptr data region")
            continue
        s, n = e["off"], e["len"]
        st["regions"] += 1
        st["bytes"] += n
        seg = m.kind[s:s + n]
        if ((seg != ord("d")) & (seg != ord("?"))).any():
            problems.append(f"{name}: {int(((seg != ord('d')) & (seg != ord('?'))).sum())} of its bytes are code or script in the model")
        if f == "poseptr":
            if n % 2:
                problems.append(f"{name}: odd length")
                continue
            for i, t in enumerate(table_targets(prg, e)):
                st["pointers"] += 1
                if t is None or t not in starts:
                    problems.append(f"{name}: entry {i} does not point to the start of a sprite group or pose in a region")
                    break
            want = [("ptr",)] * n
        else:
            try:
                rl = roles(prg, s, n, f)
            except ValueError as x:
                problems.append(f"{name}: {x}")
                continue
            st["groups"] += rl.count("count")
            want = [(r,) for r in rl]
        for i in range(n):
            rs = _reader_addrs(ev, s + i)
            if not rs:
                continue
            st["read"] += 1
            ok = {B3E + a for a in ROLE_READERS[want[i][0]]}
            bad = [r for r in rs if r not in ok]
            if bad:
                problems.append(f"{name}+{i}: a {want[i][0]} byte by the format, but read by {m.name(bad[0])}")
                break
    if complete:
        masks = role_masks(ev)
        g = np.zeros(PRG, dtype=bool)
        for r in GROUP_ROLES:
            g |= masks[r]
        out = np.flatnonzero(g & ~covered)
        if len(out):
            problems.append(f"{len(out)} bytes read by the draw routines are in no sprites / poses region, the first at {m.name(int(out[0]))}")
        out = np.flatnonzero(masks["ptr"] & ~tabcov)
        if len(out):
            problems.append(f"{len(out)} bytes read as pose pointers are in no poseptr region, the first at {m.name(int(out[0]))}")
    return problems, st


# ---------------------------------------------------------------- discovery
def discover(db, m, ev, log=print):
    """Every pose table named by a sprite_map instruction, every group they point to, and every other group the
    corpus drew. -> [data entries as dicts], in address order. Regions that touch an existing database data
    region are left out."""
    prg = m.prg
    masks = role_masks(ev)
    op = next(e["lo"] for e in db.opcodes if e["mnemonic"] == "sprite_map")
    tables = {}
    for o, ins in sorted(m.vm.ins.items()):
        if ins.op != op:
            continue
        _, v, bank, _ = ins.args[0]
        if bank is not None and bank < 0x40 and 0x8000 <= v < 0xA000:
            tables.setdefault(bank * BANK + (v & 0x1FFF), []).append(o)
        else:
            log(f"  sprite_map at {m.name(o)} with ${v:04X} in bank ${bank:02X}: not a table in the ROM, skipped")
    bounds = set(tables)
    extent, entries = {}, {}
    anyread = (ev.rdr1[:PRG] != 0) | (ev.rdr2[:PRG] != 0)
    ptr_ids = [B3E + a + 1 for a in ROLE_READERS["ptr"]]
    other = anyread & ~(np.isin(ev.rdr1[:PRG], [0] + ptr_ids) & np.isin(ev.rdr2[:PRG], [0] + ptr_ids))
    for T in sorted(tables):
        hi = ((T >> 13) + 1) * BANK
        o, ents = T, []
        while o + 1 < hi and (o == T or o not in bounds):
            v = int(prg[o]) | int(prg[o + 1]) << 8
            if not 0x8000 <= v < 0xA000 or other[o] or other[o + 1]:
                break               # not a pointer, or read by something that is not the pose lookup
            t = (T & ~0x1FFF) | (v & 0x1FFF)
            if group_len(prg, t, False, hi) is None and group_len(prg, t, True, hi) is None:
                break
            ents.append(t)
            bounds.add(t)
            o += 2
        entries[T] = ents
        extent[T] = o
    known = np.zeros(PRG, dtype=bool)
    for T in tables:
        known[T:extent[T]] = True
    loose_tabs = []
    rd = np.flatnonzero(masks["ptr"] & ~known).tolist()
    for o in rd:
        if o - 1 in rd and (o - 1) not in loose_tabs or known[o]:
            continue
        hi = ((o >> 13) + 1) * BANK
        T, ents = o, []
        while o + 1 < hi and (o == T or o not in bounds) and not known[o]:
            v = int(prg[o]) | int(prg[o + 1]) << 8
            t = (T & ~0x1FFF) | (v & 0x1FFF)
            if not 0x8000 <= v < 0xA000 or (group_len(prg, t, False, hi) is None and group_len(prg, t, True, hi) is None):
                break
            ents.append(t)
            bounds.add(t)
            o += 2
        if ents:
            tables[T] = []
            entries[T], extent[T] = ents, o
            known[T:o] = True
            loose_tabs.append(T)
    # a table must not run into something another table points to (found after it was walked)
    for T in sorted(tables):
        ents = entries[T]
        for i in range(1, len(ents)):
            if T + 2 * i in bounds:
                entries[T] = ents[:i]
                extent[T] = T + 2 * i
                break
    bounds = set(tables)
    for ents in entries.values():
        bounds.update(ents)
    order = sorted(bounds)
    nxt = {a: b for a, b in zip(order, order[1:]) if a >> 13 == b >> 13}
    groups = {}                      # start -> (length, fmt)
    undecided = []
    for T, final in [(T, False) for T in sorted(tables)] + [(T, True) for T in sorted(tables)]:
        ents = entries[T]
        votes = [groups[t][1] for t in ents if t in groups]
        major = max(sorted(set(votes)), key=votes.count) if votes and final else None
        for t in ents:
            if t in groups:
                continue
            hi = ((t >> 13) + 1) * BANK
            nb = nxt.get(t, hi)
            lp, lg = group_len(prg, t, True, hi), group_len(prg, t, False, hi)
            if masks["chr"][t] and masks["count"][t]:
                log(f"  {m.name(t)}: read both as a CHR bank byte and as a count")
            if masks["chr"][t]:
                pick = "poses"
            elif masks["count"][t]:
                pick = "sprites"
            else:
                fits = [f for f, ln in (("poses", lp), ("sprites", lg)) if ln is not None and t + ln == nb]
                pick = fits[0] if len(fits) == 1 else major
                if pick is None or (lp if pick == "poses" else lg) is None:
                    pick = ("poses" if lg is None else "sprites" if lp is None else None) if final else None
            ln = lp if pick == "poses" else lg
            if pick is None or ln is None:
                if final:
                    undecided.append(t)
                continue
            groups[t] = (ln, pick)
    # groups the corpus drew through pointers that code passes (no table)
    loose = 0
    for o in np.flatnonzero(masks["count"]).tolist():
        pose = o > 0 and bool(masks["chr"][o - 1])
        s = o - 1 if pose else o
        if s in groups:
            continue
        inside = any(g < s < g + groups[g][0] for g in (x for x in (s - k for k in range(1, 2 + 4 * MAX_SPRITES + 1)) if x in groups))
        if inside:
            continue
        ln = group_len(prg, s, pose, ((s >> 13) + 1) * BANK)
        if ln is None:
            log(f"  {m.name(s)}: a count was read here but no group fits")
            continue
        groups[s] = (ln, "poses" if pose else "sprites")
        loose += 1
    # overlaps: a group that starts inside another one
    order = sorted(groups)
    drop = set()
    for a, b in zip(order, order[1:]):
        if a + groups[a][0] > b:
            log(f"  {m.name(b)} starts inside the group at {m.name(a)}: left out")
            drop.add(b)
    for b in drop:
        del groups[b]
    out = []
    order = sorted(groups)
    i = 0
    while i < len(order):
        s = order[i]
        ln, f = groups[s]
        e, n = s + ln, 1
        while i + 1 < len(order) and order[i + 1] == e and groups[e][1] == f:
            i += 1
            e += groups[order[i]][0]
            n += 1
        i += 1
        what = "poses (a CHR bank byte, then a sprite group)" if f == "poses" else "sprite groups"
        out.append({"off": s, "len": e - s, "name": f"{'poses' if f == 'poses' else 'sprites'}_{s >> 13:02X}_{m.cpu(s):04X}",
                    "format": f, "desc": f"{n} {what if n > 1 else what.replace('poses', 'pose', 1).replace('groups', 'group')}."})
    for T in sorted(tables):
        if not entries[T]:
            log(f"  table {m.name(T)}: no entry points to a sprite group, left out")
            continue
        ok = [k for k, t in enumerate(entries[T]) if t in groups]
        n = len(entries[T])
        if len(ok) != n:
            n = next(k for k, t in enumerate(entries[T]) if t not in groups)
            log(f"  table {m.name(T)}: cut to {n} of {len(entries[T])} entries (entry {n} points to no group)")
            if n == 0:
                continue
        users = [m.name(o) for o in tables[T]]
        desc = (f"Pose table of {n} pointers, given to objects by sprite_map at {', '.join(users[:3])}"
                + (f" and {len(users) - 3} more places" if len(users) > 3 else "") + "." if users else
                f"{n} pose pointers that obj_run_all read in the corpus (and those that follow them); no sprite_map "
                f"instruction names this address, code stores it in obj_sprite_lo/hi.")
        out.append({"off": T, "len": 2 * n, "name": f"pose_tab_{T >> 13:02X}_{m.cpu(T):04X}",
                    "format": f"poseptr:{T >> 13:02X}", "desc": desc})
    out.sort(key=lambda e: e["off"])
    kept, o_prev, have = [], -1, 0
    for e in out:
        if e["off"] < o_prev:
            log(f"  {e['name']} overlaps the region before it: left out")
            continue
        if db.data_at(e["off"]) or db.data_at(e["off"] + e["len"] - 1):
            have += 1
            continue
        kept.append(e)
        o_prev = e["off"] + e["len"]
    log(f"  {len(tables) - len(loose_tabs)} tables named by sprite_map, {len(loose_tabs)} found by their reads, "
        f"{sum(len(v) for v in entries.values())} pointers, "
        f"{len(groups)} groups ({loose} of them drawn without a table), {len(undecided)} targets undecided; "
        f"{have} of {len(out)} regions are in the database already")
    return kept


def toml(entries, m):
    L = []
    for e in entries:
        L += ["[[data]]", f'at = "{m.name(e["off"])}"', f"len = {e['len']}", f'name = "{e["name"]}"',
              f'format = "{e["format"]}"', f'desc = "{e["desc"]}"', ""]
    return "\n".join(L)
