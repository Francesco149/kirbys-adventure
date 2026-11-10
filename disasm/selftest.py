"""selftest.py - do the gates fail when they should?

Each case copies db/ to a scratch directory, plants one known error, runs `kd check` on the unit and expects
it to FAIL with the right complaint. Two more cases corrupt a corpus movie and a rendered source file. A gate
that cannot fail proves nothing, so this is run after every change to the tools (`kd selftest`).
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
KD = os.path.join(HERE, "kd.py")

# (name, unit, file, old text (regex), new text, what the output must contain)
CASES = [
    ("wrong model of a routine", "rng", "rng.toml",
     r'expect = "\(rx << 8 \| ra\) == a \* x"', 'expect = "(rx << 8 | ra) == a + x"', "FAIL  rng.mul8.model"),
    ("wrong formula for a table", "rng", "rng.toml",
     r"== n \* n // 2 for n", "== n * n // 4 for n", "FAIL  rng.tables.values"),
    ("'only X writes it' with a writer left out", "rng", "rng.toml",
     r"\{'random', '18:A000', '18:A1F7'\}", "{'random', '18:A000'}", "FAIL  rng.state.writers"),
    ("scratch claimed for a live variable", "rng", "rng.toml",
     r'poke = \{ "000D" = 0xA5,', 'poke = { "003E" = 0xA5,', "FAIL  rng.scratch.dead"),
    ("wrong per-frame relation", "rng", "rng.toml",
     r"== \(n\('random'\) > 0\)\"", "== (n('random') == 0)\"", "FAIL  rng.state.frames"),
    ("a name on an operand byte", "rng", "rng.toml",
     r'at = "3E:C8DD"', 'at = "3E:C8DE"', "not the first byte of an instruction"),
    ("a name in the wrong bank window", "rng", "rng.toml",
     r'at = "3E:C698"', 'at = "3E:8698"', "is mapped at"),
    ("a data region over executed code", "rng", "rng.toml",
     r'at = "3E:C7DD"\nlen = 256', 'at = "3E:C7DD"\nlen = 300', "were executed as code"),
    ("the same name twice", "rng", "rng.toml",
     r'name = "half_square_hi"', 'name = "half_square_lo"', "is defined twice"),
    ("a claim about a name that does not exist", "rng", "rng.toml",
     r'about = \["mul8"\]', 'about = ["mul9"]', "is not a defined name"),
    ("script opcode with an operand it does not have (the older notes' layout)", "vm", "vm.toml",
     r'name = "zero_e2"\nargs = \[\]', 'name = "zero_e2"\nargs = ["u8"]', "FAIL"),
    ("script opcode one byte short", "vm", "vm.toml",
     r'name = "set_vx_w"\nargs = \["u16"\]', 'name = "set_vx_w"\nargs = ["u8"]', "FAIL"),
    ("script opcode missing from the table", "vm", "vm.toml",
     r'\[\[opcode\]\]\nop = "38"\nname = "zero_vel"', '[[opcode]]\nop = "4F"\nname = "zero_vel"', "has no [[opcode]] entry"),
    ("wrong meaning for a script opcode", "vm", "vm.toml",
     r'expect = "wr\[0x6360 \+ thread\] == args\[0\] and length == 2"',
     'expect = "wr[0x6360 + thread] == args[0] + 1 and length == 2"', "FAIL  vm.op.wait"),
    ("jump condition inverted", "vm", "vm.toml",
     r"\(next == args\[0\]\) == \(rd\[0x63E0 \+ thread\] == 0\) or", "(next == args[0]) == (rd[0x63E0 + thread] != 0) or",
     "FAIL  vm.op.jeq"),
]


def run_kd(args, dbdir=None):
    env = dict(os.environ)
    if dbdir:
        env["KD_DB"] = dbdir
    r = subprocess.run([PY, KD] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def db_cases(log):
    ok = True
    for name, unit, fname, old, new, want in CASES:
        tmp = tempfile.mkdtemp(prefix="kd-selftest-")
        try:
            for f in os.listdir(os.path.join(HERE, "db")):
                shutil.copy(os.path.join(HERE, "db", f), tmp)
            p = os.path.join(tmp, fname)
            s = open(p).read()
            s2, n = re.subn(old, new.replace("\\", "\\\\"), s, count=1)
            if n != 1:
                log(f"  ??      {name}: the text to change was not found (update selftest.py)")
                ok = False
                continue
            open(p, "w").write(s2)
            code, out = run_kd(["check", "--unit", unit, "--no-build", "-v"], tmp)
            caught = code != 0 and want in out
            line = next((ln.strip() for ln in out.splitlines() if want in ln), "")
            log(f"  {'caught' if caught else 'MISSED'}  {name}" + (f"   <- {line[:110]}" if caught else ""))
            ok = ok and caught
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return ok


def movie_case(log):
    """A corpus movie with one frame of input changed must not reproduce its recorded RAM hash."""
    sys.path.insert(0, HERE)
    import multiprocessing as mp
    import evidence as EVD
    rows = EVD.manifest()
    mid, frames, sha = min(rows, key=lambda r: r[1])[:3]
    src = open(EVD.movie_path(mid)).read()
    tid = "_selftest"
    # hold Right+A for the last 600 frames instead of what the movie did
    sys.path.insert(1, os.path.join(os.path.dirname(HERE), "tas"))
    import env as E
    masks = E.parse_spec(src)
    masks[-600:] = [E.LETTERS["R"] | E.LETTERS["A"]] * 600
    open(EVD.movie_path(tid), "w").write(E.rle(masks) + "\n")
    try:
        with mp.get_context("spawn").Pool(1) as pool:
            _, good, msg, _ = pool.apply(EVD._movie_job, ((tid, 4000, sha),))
    finally:
        os.remove(EVD.movie_path(tid))
        shutil.rmtree(os.path.join(EVD.EV, "snaps", tid), ignore_errors=True)
        p = os.path.join(EVD.EV, "movie", tid + ".npz")
        if os.path.exists(p):
            os.remove(p)
    caught = not good and "RAM hash" in msg
    log(f"  {'caught' if caught else 'MISSED'}  a corpus movie ({mid}) with its last 600 frames of input replaced"
        + (f"   <- {msg[:60]}" if caught else ""))
    return caught


def build_case(log):
    """One byte changed in a rendered source file must fail the rebuild."""
    sys.path.insert(0, HERE)
    import db as DBM
    import evidence as EVD
    import kd
    import render
    import rommodel as RM
    d = DBM.DB()
    m = RM.Model(EVD.Evidence(), db=d)
    lock = kd.locked("build")
    try:
        render.Renderer(m, d).write()
        p = os.path.join(render.OUT, "src", "bank3E.s")
        s = open(p).read()
        s2 = s.replace("    ldx #$0B", "    ldx #$0C", 1)          # random: 11 rounds -> 12
        assert s2 != s
        open(p, "w").write(s2)
        good, msg = render.build(m)
        render.Renderer(m, d).write()
        back, _ = render.build(m)
    finally:
        lock.close()
    caught = not good and "first difference" in msg and back
    log(f"  {'caught' if caught else 'MISSED'}  one operand changed in the rendered source   <- {msg[:70]}")
    return caught


def main(log=print):
    log("planted errors that the gates must catch:")
    ok = db_cases(log)
    ok = movie_case(log) and ok
    ok = build_case(log) and ok
    log(f"selftest: {'PASS, every planted error was caught' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
