"""kdcore.py - the instrumented emulator core (FCEUmm + core/kd.patch) as a Python object.

Same emulation as the stock core the TAS workbench uses (tas/core-fceumm), so every verified movie in
tas/runs/*/movie.txt replays on it frame for frame. On top it records what the CPU did:

  c = kdcore.Core()             # one per process, like nes.Core
  c.run(masks)                  # replay a movie (list of joypad masks from power-on)
  c.flags, c.first, c.count ... # numpy views of the per-byte tables (see TABLES)
  c.pairs() / c.edges()         # (code_off, addr, is_write) and (from_off, to_off, kind) sets
  c.log(mode, cap); c.take()    # event log: every instruction / read / write as a numpy record array
  c.prg                         # the PRG ROM as loaded by the core, writable (mutation experiments)

Code offsets: a PRG-ROM offset (bank * 0x2000 + address % 0x2000), or PRG + address for code run from RAM.
"""
import ctypes as C
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TAS = os.path.join(os.path.dirname(HERE), "tas")
sys.path.insert(0, TAS)
import nes  # noqa: E402
import env as E  # noqa: E402

nes.CORES["kd"] = os.path.join(HERE, "core/result/lib/retroarch/cores/fceumm_libretro.so")

PRG = 0x80000
NOFF = PRG + 0x10000
NONE = 0xFFFFFFFF
HW = 0xFFFFF                    # "from" of interrupt edges

# per-byte flags
F_OP, F_ARG, F_DATA, F_CALL, F_JMP, F_IND, F_INT, F_PTR = 1, 2, 4, 8, 16, 32, 64, 128
FLAG_NAMES = {F_OP: "op", F_ARG: "arg", F_DATA: "data", F_CALL: "call", F_JMP: "jmp", F_IND: "ind", F_INT: "int",
              F_PTR: "ptr"}
EDGE_KINDS = {1: "call", 2: "jmp", 3: "jmpind", 4: "rtsjmp", 5: "reset", 6: "nmi", 7: "irq", 8: "brk"}
R_EXEC, R_READ, R_WRITE, R_INT, R_TAG, R_BEGIN, R_END, R_ABORT = 1, 2, 3, 4, 5, 6, 7, 8

REC = np.dtype([("off", "<u4"), ("addr", "<u2"), ("type", "u1"), ("val", "u1"), ("a", "u1"), ("x", "u1"),
                ("y", "u1"), ("p", "u1"), ("s", "u1"), ("depth", "u1"), ("pad", "<u2")])
assert REC.itemsize == 16

# name -> (index for retro_kd_ptr, dtype)
TABLES = {"flags": (0, np.uint8), "first": (1, np.uint32), "count": (2, np.uint32), "dcount": (3, np.uint32),
          "rdr1": (4, np.uint32), "rdr2": (5, np.uint32), "slot": (6, np.uint8), "rdmin": (7, np.uint32),
          "rdmax": (8, np.uint32), "chrf": (13, np.uint8), "chrfirst": (14, np.uint32)}


def movie_masks(path):
    """A movie file (tas spec language) -> list of per-frame masks."""
    return E.parse_spec(open(path).read())


def off_of(bank, addr):
    return bank * 0x2000 + (addr & 0x1FFF)


def fmt_off(off):
    """Code/data offset -> 'BB:AAAA' with the bank's native address window unknown (shown as offset in bank)."""
    if off >= PRG:
        return f"RAM:{off - PRG:04X}"
    return f"{off >> 13:02X}:{off & 0x1FFF:04X}"


class Core(nes.Core):
    def __init__(self, instrument=True, rom=nes.ROM):
        super().__init__("kd", rom)
        L = self.lib
        L.retro_kd_ptr.restype = C.c_void_p
        L.retro_kd_ptr.argtypes = [C.c_int, C.POINTER(C.c_uint32)]
        L.retro_kd_info.restype = C.c_uint32
        L.retro_kd_log.argtypes = [C.c_int, C.c_uint32]
        L.retro_kd_tag.argtypes = [C.c_uint32]
        L.retro_kd_watch.argtypes = [C.c_uint32, C.c_int]
        self.tag_base = 0
        self.instrumented = False
        if instrument:
            self.instrument(True)
        p, n = self._ptr(12)
        self.prg = np.ctypeslib.as_array((C.c_uint8 * n).from_address(p))
        if bytes(self.prg) != self._rom[16:16 + n]:
            raise RuntimeError("core PRG pointer does not match the ROM file")

    # ---- tables ----
    def _ptr(self, which):
        n = C.c_uint32(0)
        p = self.lib.retro_kd_ptr(which, C.byref(n))
        return p, n.value

    def instrument(self, on=True):
        self.lib.retro_kd_enable(1 if on else 0)
        self.instrumented = bool(on)
        if on and not hasattr(self, "flags"):
            for name, (idx, dt) in TABLES.items():
                p, n = self._ptr(idx)
                setattr(self, name, np.ctypeslib.as_array((C.c_uint8 * (n * np.dtype(dt).itemsize)).from_address(p))
                        .view(dt))

    def reset_stats(self):
        self.lib.retro_kd_reset()

    def _set(self, which):
        p, n = self._ptr(which)
        t = np.ctypeslib.as_array((C.c_uint64 * n).from_address(p))
        return t[t != 0] - 1

    def pairs(self):
        """Unique accesses to non-ROM addresses: array of (code_off, addr, is_write)."""
        if self.lib.retro_kd_info(2):
            raise RuntimeError("access-pair table overflowed")
        k = self._set(9)
        return np.stack([k >> 18, (k >> 2) & 0xFFFF, k & 3], axis=1).astype(np.uint32)

    def edges(self):
        """Unique control-flow edges: array of (from_off, to_off, kind). kind: see EDGE_KINDS."""
        if self.lib.retro_kd_info(3):
            raise RuntimeError("edge table overflowed")
        k = self._set(10)
        return np.stack([k >> 24, (k >> 4) & 0xFFFFF, k & 15], axis=1).astype(np.uint32)

    # ---- running ----
    def step(self, mask=0, render=None):
        if self.instrumented:
            self.lib.retro_kd_tag(self.tag_base + self.frames)
        super().step(mask, render)

    def load(self, st):
        super().load(st)
        if self.instrumented:
            self.lib.retro_kd_enable(1)      # forget the instruction before the load

    def run(self, masks, render=False):
        for m in masks:
            self.step(m, render=render)

    # ---- event log ----
    def log(self, mode, cap=4_000_000):
        """mode 0 off, 1 everything, 2 only while a watched routine is on the stack. cap = records (16 B each)."""
        self.lib.retro_kd_log(mode, cap)

    def watch(self, offs):
        self.lib.retro_kd_watch_clear()
        for o in offs:
            self.lib.retro_kd_watch(int(o), 1)

    def take(self):
        """The records logged since the last take (a copy), and whether the buffer overflowed."""
        p, n = self._ptr(11)
        over = bool(self.lib.retro_kd_info(4))
        recs = np.frombuffer(C.string_at(p, n * 16), dtype=REC).copy() if n else np.zeros(0, dtype=REC)
        self.lib.retro_kd_log_clear()
        return recs, over

    def int_depth(self):
        return self.lib.retro_kd_info(5)
