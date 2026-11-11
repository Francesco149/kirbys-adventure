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
    ("poses (a CHR bank byte first) declared as plain sprite groups", "sprites", "sprites.toml",
     r'name = "poses_1C_8030"\nformat = "poses"', 'name = "poses_1C_8030"\nformat = "sprites"', "FAIL  sprites.format"),
    ("a pointer list that code indexes declared as a pose table", "sprites", "sprites.toml",
     r'name = "sprite_ptrs_31_9BC7"\nformat = "ptr16:31"', 'name = "sprite_ptrs_31_9BC7"\nformat = "poseptr:31"',
     "FAIL  sprites.format"),
    ("a sprite region left out of the database", "sprites", "sprites.toml",
     r'name = "sprites_38_A3DA"\nformat = "sprites"', 'name = "sprites_38_A3DA"\nformat = "bytes"', "FAIL  sprites.format"),
    ("the backwards copy of unpack modelled as a forwards copy", "unpack", "unpack.toml",
     r"v = out\[ref - i\] if c == 6 else out\[ref \+ i\]", "v = out[ref + i]", "FAIL  unpack.model"),
    ("a packed stream that expands to another number of bytes", "unpack", "unpack.toml",
     r'name = "packed_00_AA00"\nformat = "packed"\nunpacked = 2906', 'name = "packed_00_AA00"\nformat = "packed"\nunpacked = 2905',
     "FAIL  unpack.format"),
    ("a packed stream left out of the database", "unpack", "unpack.toml",
     r'name = "packed_00_AF9F"\nformat = "packed"', 'name = "packed_00_AF9F"\nformat = "bytes"', "FAIL  unpack.format"),
    ("a table of stream addresses without its table of banks", "unpack", "unpack.toml",
     r'format = "packlo:tileset_hi:tileset_bank"', 'format = "packlo:tileset_hi"', "FAIL  unpack.format"),
    ("a screen of 16 x 16 blocks instead of 16 x 12", "rooms", "rooms.toml",
     r"return \(len\(out\) == 218 \+ 192 \* \(max\(out\[8:8 \+ w \* h\]\) \+ 1\)\n            and all\(wr",
     "return (len(out) == 218 + 256 * (max(out[8:8 + w * h]) + 1)\n            and all(wr", "FAIL  rooms.load.data"),
    ("a door record of 4 bytes instead of 5", "rooms", "rooms.toml",
     r"\+ 5 \* rd\[0x56B\]", "+ 4 * rd[0x56B]", "FAIL  rooms.door.model"),
    ("Kirby's entry row read from the column nibble", "rooms", "rooms.toml",
     r"\(pos & 0x0F\) \* 16 \+ 9", "(pos >> 4) * 16 + 9", "FAIL  rooms.place.model"),
    ("an object list whose kinds start at byte 1 past the positions (not at the number of objects)", "rooms", "rooms.toml",
     r"and w\(0xF1\) == a \+ 2 \+ nc \+ total", "and w(0xF1) == a + 2 + nc + romrd[o + 1]", "FAIL  rooms.objs.head"),
    ("the lower tiles of a block taken from tables 1 and 2 instead of 2 and 3", "tiles", "tiles.toml",
     r"lower = 0x200 if py & 8 else 0", "lower = 0x100 if py & 8 else 0", "FAIL  tiles.row.model"),
    ("the second copy of a tile row 30 rows down the plane (a whole name table) instead of 24", "tiles", "tiles.toml",
     r"    p = t \+ 24\n", "    p = t + 30\n", "FAIL  tiles.row.model"),
    ("an attribute field whose vertical half is the same in both copies", "tiles", "tiles.toml",
     r"s = \(bx & 1\) \* 2 \+ \(r & 1\) \* 4", "s = (bx & 1) * 2 + (by & 1) * 4", "FAIL  tiles.attr_set.model"),
    ("a queue record with the address low byte first", "tiles", "tiles.toml",
     r"for b in \[n, hi, lo\] \+ data:", "for b in [n, lo, hi] + data:", "FAIL  tiles.ppu_write.model"),
    ("a block's index in its screen with column and row exchanged", "inroom", "inroom.toml",
     r"w\[0x10\] = rest & 0xF0 \| x >> 4", "w[0x10] = x & 0xF0 | rest >> 4", "FAIL  inroom.prop.model"),
    ("a door record's cell read from the high nibble of byte 0", "inroom", "inroom.toml",
     r"if romrd\[o\] & 15 == cell and", "if romrd[o] >> 4 == cell and", "FAIL  inroom.door.model"),
    ("a replaced block 8 after the old one instead of 8 before", "props", "props.toml",
     r"new = rd\[k\] - rd\[0x56D\] & 0xFF", "new = rd[k] + rd[0x56D] & 0xFF", "FAIL  props.break.model"),
    ("the two numbers of prop_extra exchanged", "props", "props.toml",
     r"return \(1, e\[0\] & 3, e\[0\] >> 2\)", "return (1, e[0] >> 2, e[0] & 3)", "FAIL  props.pair.model"),
    ("a current's direction and strength exchanged in the table index", "kblocks", "kblocks.toml",
     r"i = 3 \* \(e\[0\] & 3\) \+ \(e\[0\] >> 2\)", "i = 3 * (e[0] >> 2) + (e[0] & 3)", "FAIL  kblocks.current.model"),
    ("water_left answering carry set for a block that is water", "kblocks", "kblocks.toml",
     r"\[1 - \(rp & 1\)\] == bit7\(romrd\)", "[rp & 1] == bit7(romrd)", "FAIL  kblocks.water.left"),
    ("a sweep of Kirby's rectangle one column and one row short", "kblocks", "kblocks.toml",
     r"- first & 0xFF\) // 16 \+ 1", "- first & 0xFF) // 16", "FAIL  kblocks.break.rect0"),
    ("a broken block of shape 9 creating object $12 and one of shape $B object 3", "kblocks", "kblocks.toml",
     r"\(3 if s in small else 0x12\)", "(0x12 if s in small else 3)", "FAIL  kblocks.break.test0"),
    ("a camera that lets Kirby 144 pixels from its left edge instead of 128", "kmove", "kmove.toml",
     r"0xDD, 0x70, 0x80,", "0xDD, 0x70, 0x90,", "FAIL  kmove.move.model"),
    ("kirby_min_y applied as the largest Y instead of the smallest", "kmove", "kmove.toml",
     r"if s16\(\(py - u16\(rd, mem, 0x5CC\)\) & 0xFFFF\) < 0:", "if s16((py - u16(rd, mem, 0x5CC)) & 0xFFFF) >= 0:", "FAIL  kmove.move.model"),
    ("a locked camera whose right limit is its right edge (255) instead of 239", "kmove", "kmove.toml",
     r"cx \+ 0xEF & 0xFFFF", "cx + 0xFF & 0xFFFF", "FAIL  kmove.locked.model"),
    ("kirby_at_top answering for a downward velocity", "kmove", "kmove.toml",
     r"return bool\(rd\[0x5BE\] & 0x80\) and", "return not rd[0x5BE] & 0x80 and", "FAIL  kmove.at_top"),
    ("the two halves of a floor that rises over two blocks exchanged (classes 6 and 7)", "probes", "probes.toml",
     r"6: 15 - \(x >> 1\), 7: 7 - \(x >> 1\)", "6: 7 - (x >> 1), 7: 15 - (x >> 1)", "FAIL  probes.down.model"),
    ("a floor-only block (classes 2 and 3) that is a ceiling for probe_up as well", "probes", "probes.toml",
     r"    if c == 1:\n        c2 = below", "    if c in (1, 2, 3):\n        c2 = below", "FAIL  probes.up.model"),
    ("probe_left measuring to column 0 of a solid neighbour instead of its last column", "probes", "probes.toml",
     r"return \(0, -1 - x, k\)", "return (0, -x, k)", "FAIL  probes.left.model"),
    ("the handler at 3F:F600 given the formula of its sister cases (with the column)", "probes", "probes.toml",
     r"return \(0, -1 - 2 \* y, k\)", "return (0, y - 16 - x, k)", "FAIL  probes.right.model"),
    ("the block below the bottom row of a screen taken from the second row of the next screen", "probes", "probes.toml",
     r"i - 0xC0\)", "i - 0xB0)", "FAIL  probes.down.model"),
    ("the slope corrections of Kirby's left and right foot exchanged", "kcoll", "kcoll.toml",
     r"-6: \{4: 3, 6: 6, 3: -3, 5: -6\}, 6: \{3: 3, 5: 6, 4: -3, 6: -6\}", "-6: {3: 3, 5: 6, 4: -3, 6: -6}, 6: {4: 3, 6: 6, 3: -3, 5: -6}", "FAIL  kcoll.feet.left"),
    ("floor_approach with the velocity sums of the two 45 degree floors exchanged", "kcoll", "kcoll.toml",
     r"\{5: vx \+ vy, 6: vy - vx,", "{5: vy - vx, 6: vx + vy,", "FAIL  kcoll.approach.floor"),
    ("a foot that lands up to 16 pixels deep in a floor instead of 11", "kcoll", "kcoll.toml",
     r"if d == 0 or d >= 0xF5:\n        st\['land'\]", "if d == 0 or d >= 0xF0:\n        st['land']", "FAIL  kcoll.floor"),
    ("a wall that stops Kirby however deep he is in it", "kcoll", "kcoll.toml",
     r"return d if t < 0x80 else None", "return d", "FAIL  kcoll.wall"),
    ("the corrections of the side probes under a sloped ceiling with the wrong sign", "kcoll", "kcoll.toml",
     r"-6: \{7: -6, 8: 6\}, 6: \{7: 6, 8: -6\}", "-6: {7: 6, 8: -6}, 6: {7: -6, 8: 6}", "FAIL  kcoll.ceiling.model"),
    ("track streams declared as envelope streams", "snddata", "snddata.toml",
     r'format = "sndtrack"', 'format = "sndenv"', "FAIL  snddata.format"),
    ("a run of track streams left out of the database", "snddata", "snddata.toml",
     r'\[\[data\]\]\nat = "1D:9168"\n(?:.*\n){4}', "", "FAIL  snddata.format"),
    ("a run of track streams one byte short", "snddata", "snddata.toml",
     r'at = "1D:8DBC"\nlen = 932', 'at = "1D:8DBC"\nlen = 931', "FAIL  snddata.format"),
    ("a wrong note length in row 2 of the sound engine's length table", "sound", "sound.toml",
     r"\(2, 9\), \(3, 7\)", "(2, 8), (3, 7)", "FAIL  sound.tables.len"),
    ("the channels held by live sounds counted without the last slot", "sound", "sound.toml",
     r'rd\[0x6DA\] \| rd\[0x6DB\]"', 'rd[0x6DA]"', "FAIL  sound.sfx_chans"),
    ("a finished loop that drops two bytes of the stream's stack instead of three", "sound", "sound.toml",
     r"wr\[0x26\] == rd\[0x26\] \+ 3", "wr[0x26] == rd[0x26] + 2", "FAIL  sound.flow.loop"),
    ("an object's foot that counts as near a floor up to 7 pixels above it instead of 8", "ocoll", "ocoll.toml",
     r"1 if c or d >= 9 else 0", "1 if c or d >= 8 else 0", "FAIL  ocoll.test.land"),
    ("an object's wall test to the left that ignores a flat face at distance 0", "ocoll", "ocoll.toml",
     r"\(d >= 0 if flat else d > 0\)", "(d > 0)", "FAIL  ocoll.test.left.flat"),
    ("the answers of an object's walk for a wall and for a ledge exchanged", "ocoll", "ocoll.toml",
     r"9 if s == 1 else 5\)", "5 if s == 1 else 9)", "FAIL  ocoll.walk.model"),
    ("a speed above a profile's top braked whatever the keep flag says", "kvel", "kvel.toml",
     r"        if romrd\[O\('speed_keep'\) \+ y\]:\n            return sp\n", "", "FAIL  kvel.speed_step.model"),
    ("the slope table of Kirby's X velocity used on floor kind 6 instead of 5", "kvel", "kvel.toml",
     r"if rd\[0x5F4\] != 5:", "if rd[0x5F4] != 6:", "FAIL  kvel.vx_apply.model"),
    ("gravity's limit applied whatever the sign of the velocity", "kvel", "kvel.toml",
     r"    if \(v \^ acc\) & 0x8000:\n        return v\n", "", "FAIL  kvel.gravity.model"),
]


def run_kd(args, dbdir=None):
    env = dict(os.environ)
    if dbdir:
        env["KD_DB"] = dbdir
    r = subprocess.run([PY, KD] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def db_cases(log, only=None):
    ok = True
    for name, unit, fname, old, new, want in CASES:
        if only and unit not in only:
            continue
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
            code, out = run_kd(["check", "--unit", unit, "--no-build", "--no-status", "-v"], tmp)
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


def main(log=print, only=None):
    log("planted errors that the gates must catch:")
    ok = db_cases(log, only)
    if only:
        log(f"selftest (units {', '.join(only)} only): {'PASS, every planted error was caught' if ok else 'FAIL'}")
        return ok
    ok = movie_case(log) and ok
    ok = build_case(log) and ok
    log(f"selftest: {'PASS, every planted error was caught' if ok else 'FAIL'}")
    return ok


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
