"""nes.py — a minimal headless libretro frontend for frame-exact NES control.

One `Core` per process (libretro cores keep global state). Everything is deterministic:
power-on with no battery save, then one `step(mask)` per frame. A movie is the list of per-frame
joypad masks from power-on; replaying it on a fresh core reproduces every frame.

Joypad mask bits (NES order, as in FCEUX .fm2 "RLDUTSBA" reversed):
  A=0x01 B=0x02 Select=0x04 Start=0x08 Up=0x10 Down=0x20 Left=0x40 Right=0x80
"""
import ctypes as C
import os
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CORES = {
    "mesen": os.path.join(HERE, "core-mesen/lib/retroarch/cores/mesen_libretro.so"),
    "fceumm": os.path.join(HERE, "core-fceumm/lib/retroarch/cores/fceumm_libretro.so"),
}
ROM = os.path.join(os.path.dirname(HERE), "roms/usa-rev-a.nes")

A, B, SELECT, START, UP, DOWN, LEFT, RIGHT = 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80
RESET = 0x100     # not a button: soft reset (console Reset button) at the start of that frame
BUTTONS = {"A": A, "B": B, "s": SELECT, "S": START, "U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
# libretro joypad ids for each NES bit
_RETRO_ID = {A: 8, B: 0, SELECT: 2, START: 3, UP: 4, DOWN: 5, LEFT: 6, RIGHT: 7}
_ID_TO_BIT = {v: k for k, v in _RETRO_ID.items()}

ENV_GET_CAN_DUPE = 3
ENV_GET_SYSTEM_DIRECTORY = 9
ENV_SET_PIXEL_FORMAT = 10
ENV_GET_VARIABLE = 15
ENV_GET_VARIABLE_UPDATE = 17
ENV_GET_SAVE_DIRECTORY = 31
ENV_GET_INPUT_BITMASKS = 51
MEM_SAVE_RAM, MEM_SYSTEM_RAM = 0, 2


def _exit_with_parent():
    """In a multiprocessing child, exit as soon as the parent is gone.

    Every worker pool here (kt search, kd checks, labkit scripts) uses the 'spawn' context, and a spawned worker
    holds both ends of its call-queue pipe, so it never sees EOF when the parent dies: a parent killed by a
    timeout or a stopped agent left its idle workers waiting on a futex for days (16 at a time, ~500 MB a pool).
    Every such worker imports this module, so the guard lives here and covers pools nobody remembers to close."""
    import multiprocessing
    import threading
    import time
    parent = multiprocessing.parent_process()
    if parent is None:
        return
    ppid = parent.pid

    def watch():
        while os.getppid() == ppid:
            time.sleep(1)
        os._exit(1)

    threading.Thread(target=watch, name="exit-with-parent", daemon=True).start()


_exit_with_parent()


class GameInfo(C.Structure):
    _fields_ = [("path", C.c_char_p), ("data", C.c_void_p), ("size", C.c_size_t), ("meta", C.c_char_p)]


class Geometry(C.Structure):
    _fields_ = [("base_width", C.c_uint), ("base_height", C.c_uint), ("max_width", C.c_uint),
                ("max_height", C.c_uint), ("aspect_ratio", C.c_float)]


class Timing(C.Structure):
    _fields_ = [("fps", C.c_double), ("sample_rate", C.c_double)]


class AVInfo(C.Structure):
    _fields_ = [("geometry", Geometry), ("timing", Timing)]


class Variable(C.Structure):
    _fields_ = [("key", C.c_char_p), ("value", C.c_char_p)]


ENV_CB = C.CFUNCTYPE(C.c_bool, C.c_uint, C.c_void_p)
VIDEO_CB = C.CFUNCTYPE(None, C.c_void_p, C.c_uint, C.c_uint, C.c_size_t)
AUDIO_CB = C.CFUNCTYPE(None, C.c_int16, C.c_int16)
AUDIO_BATCH_CB = C.CFUNCTYPE(C.c_size_t, C.c_void_p, C.c_size_t)
POLL_CB = C.CFUNCTYPE(None)
STATE_CB = C.CFUNCTYPE(C.c_int16, C.c_uint, C.c_uint, C.c_uint, C.c_uint)

# Core options pinned for determinism (unknown keys are simply never asked for).
OPTIONS = {
    b"mesen_ramstate": b"All 0s (Default)",
    b"fceumm_ramstate": b"fill $00",
    b"mesen_overclock": b"None",
    b"fceumm_overclocking": b"disabled",
    b"mesen_region": b"NTSC",
    b"fceumm_region": b"NTSC",
    b"fceumm_nospritelimit": b"disabled",
    b"mesen_nospritelimit": b"disabled",
}


_LIVE = {"pid": None}


class Core:
    def __init__(self, core="mesen", rom=ROM):
        # A libretro core is process-global: a second Core in the same process (or in a fork of a process that
        # had one) re-initialises the shared core and silently steals the first one's input/video callbacks.
        if _LIVE["pid"] is not None:
            raise RuntimeError("only one emulator core per process (use a spawned process for another)")
        _LIVE["pid"] = os.getpid()
        self.name = core
        self.lib = C.CDLL(CORES[core])
        L = self.lib
        L.retro_get_memory_data.restype = C.c_void_p
        L.retro_get_memory_size.restype = C.c_size_t
        L.retro_serialize_size.restype = C.c_size_t
        L.retro_serialize.restype = C.c_bool
        L.retro_unserialize.restype = C.c_bool
        L.retro_load_game.restype = C.c_bool
        self.pixfmt = 0
        self.mask = 0
        self.render = True
        self.frame = None          # last frame as HxWx3 uint8
        self._dirs = tempfile.mkdtemp(prefix="nes-core-")
        self._dir_buf = C.create_string_buffer(self._dirs.encode())
        self._opt_bufs = {k: C.create_string_buffer(v) for k, v in OPTIONS.items()}
        self.frames = 0            # frames run since power-on
        self.lag = 0               # lag frames (counted by the game-specific layer)
        # keep references so ctypes callbacks are not garbage-collected
        self._cbs = [ENV_CB(self._env), VIDEO_CB(self._video), AUDIO_CB(lambda l, r: None),
                     AUDIO_BATCH_CB(lambda d, n: n), POLL_CB(self._poll), STATE_CB(self._state)]
        L.retro_set_environment(self._cbs[0])
        L.retro_init()
        L.retro_set_video_refresh(self._cbs[1])
        L.retro_set_audio_sample(self._cbs[2])
        L.retro_set_audio_sample_batch(self._cbs[3])
        L.retro_set_input_poll(self._cbs[4])
        L.retro_set_input_state(self._cbs[5])
        self._rom = open(rom, "rb").read()
        self._rom_buf = C.create_string_buffer(self._rom, len(self._rom))
        gi = GameInfo(rom.encode(), C.cast(self._rom_buf, C.c_void_p), len(self._rom), None)
        if not L.retro_load_game(C.byref(gi)):
            raise RuntimeError(f"{core}: retro_load_game failed")
        L.retro_set_controller_port_device(0, 1)   # RETRO_DEVICE_JOYPAD
        av = AVInfo()
        L.retro_get_system_av_info(C.byref(av))
        self.fps = av.timing.fps
        sram = L.retro_get_memory_data(MEM_SAVE_RAM)
        n = L.retro_get_memory_size(MEM_SAVE_RAM)
        if sram and n:
            C.memset(sram, 0, n)    # clean battery save: the movie always starts from a fresh cart
        self._ram_ptr = L.retro_get_memory_data(MEM_SYSTEM_RAM)
        self._ram_n = L.retro_get_memory_size(MEM_SYSTEM_RAM)
        if not self._ram_ptr or self._ram_n < 0x800:
            raise RuntimeError(f"{core}: no system RAM exposed")
        self.ram = np.ctypeslib.as_array((C.c_uint8 * self._ram_n).from_address(self._ram_ptr))
        # cartridge PRG-RAM at $6000-$7FFF (battery-backed on this cart; zeroed above = clean save)
        if sram and n >= 0x2000:
            self.wram = np.ctypeslib.as_array((C.c_uint8 * 0x2000).from_address(sram))
        else:
            self.wram = np.zeros(0x2000, dtype=np.uint8)
        self.mem = Mem(self)

    # ---- libretro callbacks ----
    def _env(self, cmd, data):
        cmd &= 0xFFFF
        if cmd == ENV_GET_CAN_DUPE:
            C.cast(data, C.POINTER(C.c_bool))[0] = True
            return True
        if cmd == ENV_SET_PIXEL_FORMAT:
            self.pixfmt = C.cast(data, C.POINTER(C.c_int))[0]
            return self.pixfmt in (1, 2)
        if cmd in (ENV_GET_SYSTEM_DIRECTORY, ENV_GET_SAVE_DIRECTORY):
            C.cast(data, C.POINTER(C.c_void_p))[0] = C.addressof(self._dir_buf)
            return True
        if cmd == ENV_GET_VARIABLE:
            key = C.cast(data, C.POINTER(Variable))[0].key
            buf = self._opt_bufs.get(key)
            if buf is None:
                return False
            C.cast(data, C.POINTER(C.c_void_p))[1] = C.addressof(buf)   # Variable.value
            return True
        if cmd == ENV_GET_VARIABLE_UPDATE:
            C.cast(data, C.POINTER(C.c_bool))[0] = False
            return True
        if cmd == ENV_GET_INPUT_BITMASKS:
            return True
        return False

    def _video(self, data, w, h, pitch):
        if not data or not self.render:
            return
        raw = np.frombuffer(C.string_at(data, pitch * h), dtype=np.uint8).reshape(h, pitch)
        if self.pixfmt == 1:      # XRGB8888
            px = raw[:, : w * 4].reshape(h, w, 4)
            self.frame = px[:, :, [2, 1, 0]].copy()
        else:                     # RGB565
            v = raw[:, : w * 2].copy().view(np.uint16).reshape(h, w)
            r = ((v >> 11) & 0x1F) << 3
            g = ((v >> 5) & 0x3F) << 2
            b = (v & 0x1F) << 3
            self.frame = np.stack([r, g, b], axis=-1).astype(np.uint8)

    def _poll(self):
        pass

    def _state(self, port, device, index, id_):
        if port != 0 or device != 1:
            return 0
        if id_ == 256:            # RETRO_DEVICE_ID_JOYPAD_MASK
            m = 0
            for bit, rid in _RETRO_ID.items():
                if self.mask & bit:
                    m |= 1 << rid
            return m
        bit = _ID_TO_BIT.get(id_)
        return 1 if bit and (self.mask & bit) else 0

    # ---- control ----
    def step(self, mask=0, render=None):
        """Run one frame holding `mask` (our bit layout, see module doc). RESET soft-resets first."""
        if mask & RESET:
            self.lib.retro_reset()
        self.mask = mask & 0xFF
        if render is not None:
            self.render = render
        self.lib.retro_run()
        self.frames += 1

    def save(self):
        n = self.lib.retro_serialize_size()
        buf = C.create_string_buffer(n)
        if not self.lib.retro_serialize(buf, n):
            raise RuntimeError("serialize failed")
        return (buf.raw, self.frames, self.lag)

    def load(self, st):
        raw, frames, lag = st
        buf = C.create_string_buffer(raw, len(raw))
        if not self.lib.retro_unserialize(buf, len(raw)):
            raise RuntimeError("unserialize failed")
        self.frames, self.lag = frames, lag

    def ram_bytes(self):
        return bytes(self.ram[:0x800]) + bytes(self.wram)


class Mem:
    """CPU-address view of RAM: $0000-$07FF (mirrored to $1FFF) and $6000-$7FFF. Returns Python ints."""
    __slots__ = ("c",)

    def __init__(self, core):
        self.c = core

    def __getitem__(self, a):
        a = int(a)
        if 0 <= a < 0x2000:
            return int(self.c.ram[a & 0x7FF])
        if 0x6000 <= a < 0x8000:
            return int(self.c.wram[a - 0x6000])
        raise IndexError(f"address ${a:04X} is not RAM ($0000-$07FF, $6000-$7FFF)")

    def block(self, a, n):
        return [self[i] for i in range(a, a + n)]
