"""evidence.py - replay the movie corpus on the instrumented core and merge what it recorded.

The corpus (corpus/MANIFEST.tsv + corpus/*.movie, in git) is the set of verified input traces that count as
evidence. Each movie is replayed from power-on in its own process; its end-of-movie RAM hash must equal the
one in the manifest (the determinism gate). Per-movie tables are cached in evidence/movie/ (not in git) and
merged into evidence/merged.npz, which every other tool reads through the Evidence class.
"""
import hashlib
import json
import multiprocessing as mp
import os
import shutil
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "corpus")
MANIFEST = os.path.join(CORPUS, "MANIFEST.tsv")
EV = os.path.join(HERE, "evidence")
SNAP_EVERY = 1000
PRG = 0x80000
NOFF = PRG + 0x10000
NONE = 0xFFFFFFFF
TABLES = ("flags", "first", "count", "dcount", "rdr1", "rdr2", "slot", "rdmin", "rdmax", "chrf", "chrfirst")


# ---------------------------------------------------------------- corpus
def manifest():
    """[(id, frames, ram_sha1, origin, note)] in manifest order (the order decides which movie 'first' names)."""
    rows = []
    if os.path.exists(MANIFEST):
        for ln in open(MANIFEST):
            if ln.strip() and not ln.startswith("#"):
                mid, frames, sha, origin, note = (ln.rstrip("\n").split("\t") + [""] * 5)[:5]
                rows.append((mid, int(frames), sha, origin, note))
    return rows


def movie_path(mid):
    return os.path.join(CORPUS, mid + ".movie")


def write_manifest(rows):
    with open(MANIFEST, "w") as f:
        f.write("# id\tframes\tram_sha1 at the last frame\torigin\tnote\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")


def _stock_job(path):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tas"))
    import env as E
    import nes
    masks = E.parse_spec(open(path).read())
    c = nes.Core("fceumm")
    for m in masks:
        c.step(m, render=False)
    return len(masks), hashlib.sha1(c.ram_bytes()).hexdigest()


def coverage(ev=None):
    """(code bytes, data bytes, edges, access pairs, CHR tiles) in merged.npz, or zeros when there is none."""
    p = os.path.join(EV, "merged.npz")
    if not os.path.exists(p):
        return (0, 0, 0, 0, 0)
    z = np.load(p)
    f = z["flags"][:PRG]
    return (int(((f & 3) != 0).sum()), int(((f & 4) != 0).sum()), len(z["edges"]), len(z["pairs"]),
            int((z["chrf"] != 0).sum()))


def add(src, mid, origin, note="", keep_if_no_gain=False, log=print):
    """Add a movie to the corpus if it replays and covers something new. Returns the coverage gain tuple."""
    rows = manifest()
    if any(r[0] == mid for r in rows):
        raise SystemExit(f"corpus already has '{mid}'")
    os.makedirs(CORPUS, exist_ok=True)
    shutil.copyfile(src, movie_path(mid))
    with mp.get_context("spawn").Pool(1) as pool:      # reference hash from the stock core, in its own process
        frames, sha = pool.apply(_stock_job, (movie_path(mid),))
    before = coverage()
    write_manifest(rows + [(mid, frames, sha, origin, note)])
    if not build(log=lambda *_: None):
        write_manifest(rows)
        os.remove(movie_path(mid))
        raise SystemExit(f"{mid}: the instrumented core does not reproduce the stock core's RAM hash")
    after = coverage()
    gain = tuple(a - b for a, b in zip(after, before))
    # new access pairs alone (the same instruction reaching another element of a table) do not earn a place
    if not (gain[0] or gain[1] or gain[2] or gain[4]) and not keep_if_no_gain:
        write_manifest(rows)
        os.remove(movie_path(mid))
        os.remove(os.path.join(EV, "movie", mid + ".npz"))
        merge([r[0] for r in rows])
        log(f"{mid}: {frames} frames, nothing new: not added")
    else:
        log(f"{mid}: {frames} frames, +{gain[0]} code bytes, +{gain[1]} data bytes, +{gain[2]} edges, "
            f"+{gain[3]} access pairs, +{gain[4]} CHR tiles")
    return gain


def movie_index(mid):
    return [r[0] for r in manifest()].index(mid)


def tag_split(tag):
    """A 'first' value (tag + 1) -> (movie id, frame) or None."""
    if not tag:
        return None
    t = int(tag) - 1
    return manifest()[t >> 20][0], t & 0xFFFFF


# ---------------------------------------------------------------- one movie
def _movie_job(args):
    mid, idx, want_sha = args
    sys.path.insert(0, HERE)
    import kdcore
    t0 = time.time()
    masks = kdcore.movie_masks(movie_path(mid))
    c = kdcore.Core()
    c.tag_base = idx << 20
    sd = os.path.join(EV, "snaps", mid)
    shutil.rmtree(sd, ignore_errors=True)
    os.makedirs(sd)
    for i, m in enumerate(masks):
        if i % SNAP_EVERY == 0:
            open(os.path.join(sd, f"{i:07d}"), "wb").write(c.save()[0])
        c.step(m, render=False)
    sha = hashlib.sha1(c.ram_bytes()).hexdigest()
    if want_sha and sha != want_sha:
        return mid, False, f"RAM hash {sha} != manifest {want_sha}", 0
    out = {t: getattr(c, t).copy() for t in TABLES}
    out["pairs"] = c.pairs()
    out["edges"] = c.edges()
    msha = hashlib.sha1(open(movie_path(mid), "rb").read()).hexdigest()
    np.savez_compressed(os.path.join(EV, "movie", mid + ".npz"), meta=np.array(json.dumps(
        {"id": mid, "idx": idx, "frames": len(masks), "ram_sha1": sha, "movie_sha1": msha})), **out)
    return mid, True, sha, round(time.time() - t0, 1)


def _cached_ok(mid, idx):
    p = os.path.join(EV, "movie", mid + ".npz")
    if not os.path.exists(p):
        return False
    try:
        meta = json.loads(str(np.load(p)["meta"]))
    except Exception:
        return False
    msha = hashlib.sha1(open(movie_path(mid), "rb").read()).hexdigest()
    return meta.get("movie_sha1") == msha and meta.get("idx") == idx and core_sha() == _core_stamp()


def core_sha():
    import kdcore
    p = os.path.realpath(kdcore.nes.CORES["kd"])
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def _core_stamp():
    p = os.path.join(EV, "core.sha1")
    return open(p).read().strip() if os.path.exists(p) else None


def build(force=False, workers=12, log=print):
    """Replay every corpus movie that changed, then merge. Returns True when every movie reproduced its hash."""
    sys.path.insert(0, HERE)
    os.makedirs(os.path.join(EV, "movie"), exist_ok=True)
    rows = manifest()
    todo = [(r[0], i, r[2]) for i, r in enumerate(rows) if force or not _cached_ok(r[0], i)]
    ok = True
    if todo:
        log(f"replaying {len(todo)} of {len(rows)} movies ({sum(rows[i][1] for _, i, _ in todo)} frames)")
        # one movie per process: an emulator core cannot be created twice in a process
        with mp.get_context("spawn").Pool(min(workers, len(todo)), maxtasksperchild=1) as pool:
            for mid, good, msg, secs in pool.imap_unordered(_movie_job, sorted(todo, key=lambda t: -rows[t[1]][1])):
                log(f"  {mid}: {'ok ' + str(secs) + ' s' if good else 'FAILED ' + msg}")
                ok = ok and good
    if not ok:
        return False
    open(os.path.join(EV, "core.sha1"), "w").write(core_sha())
    merge([r[0] for r in rows])
    return True


def merge(ids):
    acc = None
    pairs, edges = [], []
    for mid in ids:
        z = np.load(os.path.join(EV, "movie", mid + ".npz"))
        pairs.append(z["pairs"])
        edges.append(z["edges"])
        if acc is None:
            acc = {t: z[t].copy() for t in TABLES}
            continue
        a = acc
        a["flags"] |= z["flags"]
        a["slot"] |= z["slot"]
        a["chrf"] |= z["chrf"]
        for t in ("first", "chrfirst"):
            f = z[t]
            a[t] = np.where((a[t] == 0) | ((f != 0) & (f < a[t])), f, a[t])
        for t in ("count", "dcount"):
            a[t] = np.minimum(a[t].astype(np.uint64) + z[t], 0xFFFFFFFF).astype(np.uint32)
        r1, r2 = z["rdr1"], z["rdr2"]
        other = np.where((r1 != 0) & (a["rdr1"] != 0) & (r1 != a["rdr1"]), r1, r2)
        a["rdr2"] = np.where(a["rdr2"] == 0, other, a["rdr2"])
        a["rdr1"] = np.where(a["rdr1"] == 0, r1, a["rdr1"])
        a["rdmin"] = np.minimum(a["rdmin"], z["rdmin"])
        mx, zm = a["rdmax"], z["rdmax"]
        a["rdmax"] = np.where(mx == NONE, zm, np.where(zm == NONE, mx, np.maximum(mx, zm)))
    acc["pairs"] = np.unique(np.concatenate(pairs), axis=0)
    acc["edges"] = np.unique(np.concatenate(edges), axis=0)
    tmp = os.path.join(EV, "merged.tmp.npz")
    np.savez_compressed(tmp, **acc)
    os.replace(tmp, os.path.join(EV, "merged.npz"))      # readers never see a half-written file


# ---------------------------------------------------------------- reading
class Evidence:
    """merged.npz with the lookups the tools need."""

    def __init__(self, path=None):
        z = np.load(path or os.path.join(EV, "merged.npz"))
        for t in TABLES + ("pairs", "edges"):
            setattr(self, t, z[t])
        self.rom = open(os.path.join(os.path.dirname(HERE), "roms/usa-rev-a.nes"), "rb").read()
        self.prg = np.frombuffer(self.rom[16:16 + PRG], dtype=np.uint8)
        self._by_addr = self._by_code = self._out = self._in = None

    # bank origin: the CPU slot(s) a bank was seen mapped at
    def bank_slots(self, bank):
        s = int(np.bitwise_or.reduce(self.slot[bank * 0x2000:(bank + 1) * 0x2000]))
        return [0x8000 + 0x2000 * i for i in range(4) if s & (1 << i)]

    def bank_base(self, bank):
        """The window the bank is used at: the one most of its touched bytes were seen in."""
        s = self.slot[bank * 0x2000:(bank + 1) * 0x2000]
        n = [int(((s >> i) & 1).sum()) for i in range(4)]
        return 0x8000 + 0x2000 * n.index(max(n)) if max(n) else None

    def cpu_addr(self, off):
        """PRG offset -> CPU address in the bank's (first observed) window; RAM code offsets map to themselves."""
        if off >= PRG:
            return off - PRG
        base = self.bank_base(off >> 13)
        return (base if base is not None else 0x8000) + (off & 0x1FFF)

    def name(self, off):
        if off >= PRG:
            return f"RAM:{off - PRG:04X}"
        return f"{off >> 13:02X}:{self.cpu_addr(off):04X}"

    def first_at(self, off):
        return tag_split(self.first[off])

    # xrefs
    def ram_xref(self, addr):
        """[(code_off, is_write)] touching a non-ROM address."""
        if self._by_addr is None:
            o = np.lexsort((self.pairs[:, 0], self.pairs[:, 1]))
            self._by_addr = self.pairs[o]
        p = self._by_addr
        lo, hi = np.searchsorted(p[:, 1], addr), np.searchsorted(p[:, 1], addr, side="right")
        return [(int(c), int(w)) for c, _, w in p[lo:hi]]

    def code_xref(self, lo, hi):
        """[(code_off, addr, is_write)] for instructions in [lo, hi)."""
        p = self.pairs
        a, b = np.searchsorted(p[:, 0], lo), np.searchsorted(p[:, 0], hi)
        return [(int(c), int(ad), int(w)) for c, ad, w in p[a:b]]

    def edges_from(self, lo, hi):
        e = self.edges
        a, b = np.searchsorted(e[:, 0], lo), np.searchsorted(e[:, 0], hi)
        return [(int(f), int(t), int(k)) for f, t, k in e[a:b]]

    def edges_to(self, off):
        if self._in is None:
            self._in = self.edges[np.argsort(self.edges[:, 1], kind="stable")]
        e = self._in
        a, b = np.searchsorted(e[:, 1], off), np.searchsorted(e[:, 1], off, side="right")
        return [(int(f), int(t), int(k)) for f, t, k in e[a:b]]


if __name__ == "__main__":
    ok = build(force="--force" in sys.argv)
    sys.exit(0 if ok else 1)
