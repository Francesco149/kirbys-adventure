"""db.py - the documentation database (db/*.toml): the hand-written half of the project.

One file per unit (a subsystem, a table family, a script). Entries are keyed by address, never by position
in a listing, so they survive every re-analysis. Kinds of entry:

  [[sym]]    a routine or a code label      at = "3E:C1B6"  name  desc  [kind = "sub"|"part"|"label"]
             [comments = { "C1C0" = "inline comment", ... }]
  [[data]]   a data region in the ROM       at = "3E:C6DD"  len   name  desc  format
  [[ram]]    a variable in RAM              at = "003E"     [len] name  desc
  [[claim]]  a checkable statement          id  about = [names]  text  kind + its fields (see probe.py)
  [vm]       the script interpreter         fetch = "3E:CDDF" (the instruction that reads an opcode byte)
                                            step = "3E:CDAD" (the routine that runs one thread for a frame)
                                            advance = "3E:CE13" (where opcode handlers return to)
  [[opcode]] one script opcode or family    op = "06" | "50-5F"  name  args = ["u8", ...]  flow  desc
  [[script]] a script (bytecode routine)    at = "23:A120"  name  desc

A name is evidence-backed vocabulary: `kd check` fails on an entry that contradicts what ran (a sym that is
not an instruction, a data region over executed code) and reports each entry's level:
described (name + desc) or verified (a passing claim lists it in `about`).
"""
import glob
import os
import re
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
DBDIR = os.environ.get("KD_DB") or os.path.join(HERE, "db")      # KD_DB: a scratch database
PRG = 0x80000
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FORMATS = ("bytes", "rows", "ptr16", "ptr16m1", "lobytes", "hibytes", "fill", "sprites", "poses", "poseptr",
           "packed", "packlo", "packhi", "packbank")


def parse_rom_at(s):
    """'3E:C1B6' -> (PRG offset, cpu address)."""
    m = re.fullmatch(r"([0-9A-Fa-f]{2}):([0-9A-Fa-f]{4})", s.strip())
    if not m:
        raise ValueError(f"bad ROM address '{s}' (want BB:AAAA, hex)")
    bank, addr = int(m.group(1), 16), int(m.group(2), 16)
    if bank > 0x3F or addr < 0x8000:
        raise ValueError(f"bad ROM address '{s}'")
    return bank * 0x2000 + (addr & 0x1FFF), addr


def parse_ram_at(s):
    a = int(str(s).strip().lstrip("$"), 16)
    if not (0 <= a < 0x800 or 0x6000 <= a < 0x8000):
        raise ValueError(f"'{s}' is not a RAM address ($0000-$07FF, $6000-$7FFF)")
    return a


class _Tagged(list):
    """A list of problems that remembers which unit each one belongs to."""
    unit = None

    def append(self, p):
        super().append((self.unit, p))


def stamp(db):
    """Everything in the database that can change the outcome of a claim other than the claim itself:
    every name with its place and size, and the script interpreter's description. Text is left out, so
    editing a description does not re-run anything."""
    import json
    rows = [(n, k, e.get("at"), e.get("len"), e.get("kind"), e.get("format"), e.get("op"), e.get("args"),
             e.get("flow")) for n, (k, e) in db.by_name.items()]
    return json.dumps([sorted(rows, key=str), sorted(db.vm.items())], default=str)


class DB:
    def __init__(self, dbdir=DBDIR):
        self.syms, self.data, self.ram, self.claims, self.units = [], [], [], [], {}
        self.vm, self.opcodes, self.scripts = {}, [], []
        self.problems = _Tagged()      # (unit, text)
        for path in sorted(glob.glob(os.path.join(dbdir, "*.toml"))):
            self.problems.unit = os.path.basename(path)[:-5]
            self._load(path)
        self.by_name = {}
        for kind, lst in (("sym", self.syms), ("data", self.data), ("ram", self.ram), ("script", self.scripts),
                          ("opcode", self.opcodes)):
            for e in lst:
                self.problems.unit = e["unit"]
                if e["name"] in self.by_name:
                    self.problems.append(f"{e['file']}: name '{e['name']}' is defined twice")
                self.by_name[e["name"]] = (kind, e)
        seen = {}
        for e in self.opcodes:
            self.problems.unit = e["unit"]
            for b in range(e["lo"], e["hi"] + 1):
                if b in seen:
                    self.problems.append(f"script opcode ${b:02X} is defined by {seen[b]} and {e['name']}")
                seen[b] = e["name"]
        self.sym_at = {e["off"]: e for e in self.syms}
        self.data_sorted = sorted(self.data, key=lambda e: e["off"])
        for a, b in zip(self.data_sorted, self.data_sorted[1:]):
            self.problems.unit = b["unit"]
            if a["off"] + a["len"] > b["off"]:
                self.problems.append(f"data '{a['name']}' overlaps '{b['name']}'")
        self.ram_sorted = sorted(self.ram, key=lambda e: e["addr"])
        for a, b in zip(self.ram_sorted, self.ram_sorted[1:]):
            self.problems.unit = b["unit"]
            if a["addr"] + a["len"] > b["addr"]:
                self.problems.append(f"ram '{a['name']}' overlaps '{b['name']}'")
        ids = set()
        for c in self.claims:
            self.problems.unit = c["unit"]
            if c["id"] in ids:
                self.problems.append(f"claim id '{c['id']}' is used twice")
            ids.add(c["id"])
            for n in c.get("about", []):
                if n not in self.by_name:
                    self.problems.append(f"claim {c['id']}: about '{n}' is not a defined name")

    def _load(self, path):
        f = os.path.basename(path)
        try:
            t = tomllib.load(open(path, "rb"))
        except Exception as e:
            self.problems.append(f"{f}: {e}")
            return
        unit = t.get("unit", f[:-5])
        self.problems.unit = unit
        self.units[unit] = {"file": f, "title": t.get("title", unit), "summary": t.get("summary", "")}

        def need(e, what, keys):
            for k in keys:
                if k not in e:
                    self.problems.append(f"{f}: a [[{what}]] entry has no '{k}': {str(e)[:80]}")
                    return False
            if what != "claim" and not IDENT.match(e["name"]):
                self.problems.append(f"{f}: '{e['name']}' is not a valid name")
                return False
            return True

        for e in t.get("sym", []):
            if not need(e, "sym", ("at", "name")):
                continue
            try:
                off, addr = parse_rom_at(e["at"])
            except ValueError as x:
                self.problems.append(f"{f}: {x}")
                continue
            kind = e.get("kind", "sub")
            if kind not in ("sub", "part", "label"):
                self.problems.append(f"{f}: sym {e['name']}: kind '{kind}'")
            comments = {}
            for k, v in e.get("comments", {}).items():
                try:
                    comments[(off & ~0x1FFF) | (int(k, 16) & 0x1FFF)] = v
                except ValueError:
                    self.problems.append(f"{f}: sym {e['name']}: comment address '{k}'")
            self.syms.append({**e, "off": off, "addr": addr, "kind": kind, "desc": e.get("desc", "").strip(),
                              "comments": comments, "unit": unit, "file": f})
        for e in t.get("data", []):
            if not need(e, "data", ("at", "name", "len")):
                continue
            try:
                off, addr = parse_rom_at(e["at"])
            except ValueError as x:
                self.problems.append(f"{f}: {x}")
                continue
            fmt = e.get("format", "bytes")
            if fmt.split(":")[0] not in FORMATS:
                self.problems.append(f"{f}: data {e['name']}: unknown format '{fmt}'")
            if (off & 0x1FFF) + e["len"] > 0x2000 or e["len"] <= 0:
                self.problems.append(f"{f}: data {e['name']}: length runs past the end of the bank")
            self.data.append({**e, "off": off, "addr": addr, "format": fmt, "desc": e.get("desc", "").strip(),
                              "unit": unit, "file": f})
        for e in t.get("ram", []):
            if not need(e, "ram", ("at", "name")):
                continue
            try:
                addr = parse_ram_at(e["at"])
            except ValueError as x:
                self.problems.append(f"{f}: {x}")
                continue
            self.ram.append({**e, "addr": addr, "len": int(e.get("len", 1)), "desc": e.get("desc", "").strip(),
                             "unit": unit, "file": f})
        if "vm" in t:
            self.vm = dict(t["vm"])
            for k in ("fetch", "step", "advance"):
                if k in self.vm:
                    try:
                        self.vm[k + "_off"] = parse_rom_at(self.vm[k])[0]
                    except ValueError as x:
                        self.problems.append(f"{f}: [vm] {k}: {x}")
        for e in t.get("opcode", []):
            if not need(e, "opcode", ("op", "name")):
                continue
            try:
                lo, _, hi = str(e["op"]).partition("-")
                lo, hi = int(lo, 16), int(hi or lo, 16)
            except ValueError:
                self.problems.append(f"{f}: opcode {e['name']}: op '{e['op']}'")
                continue
            args, flow = list(e.get("args", [])), e.get("flow", "next")
            import vm as VMM
            bad = [a for a in args if a not in VMM.ARGS]
            if bad or flow not in VMM.FLOWS:
                self.problems.append(f"{f}: opcode {e['name']}: bad args {bad} or flow '{flow}'")
                continue
            self.opcodes.append({**e, "lo": lo, "hi": hi, "mnemonic": e["name"], "name": "op_" + e["name"],
                                 "args": args, "flow": flow, "desc": e.get("desc", "").strip(), "unit": unit,
                                 "file": f})
        for e in t.get("script", []):
            if not need(e, "script", ("at", "name")):
                continue
            try:
                off, addr = parse_rom_at(e["at"])
            except ValueError as x:
                self.problems.append(f"{f}: {x}")
                continue
            self.scripts.append({**e, "off": off, "addr": addr, "desc": e.get("desc", "").strip(), "unit": unit,
                                 "file": f})
        for e in t.get("claim", []):
            if not need(e, "claim", ("id", "kind", "text")):
                continue
            if e.get("about_formats"):
                # every data region of this unit in one of the formats (a unit of many generated regions)
                e = {**e, "about": list(e.get("about", [])) + [x["name"] for x in self.data if x["unit"] == unit
                                                                and x["format"].split(":")[0] in e["about_formats"]]}
            self.claims.append({**e, "unit": unit, "file": f})

    # ---- lookups ----
    def ram_name(self, addr):
        """RAM address -> 'name' or 'name+N' or None."""
        import bisect
        i = bisect.bisect_right([e["addr"] for e in self.ram_sorted], addr) - 1
        if i >= 0:
            e = self.ram_sorted[i]
            if addr < e["addr"] + e["len"]:
                return e["name"] if addr == e["addr"] else f"{e['name']}+{addr - e['addr']}"
        return None

    def data_at(self, off):
        """PRG offset -> (entry, index within it) or None."""
        import bisect
        i = bisect.bisect_right([e["off"] for e in self.data_sorted], off) - 1
        if i >= 0:
            e = self.data_sorted[i]
            if off < e["off"] + e["len"]:
                return e, off - e["off"]
        return None

    def off_of(self, name_or_at):
        """A sym/data name or 'BB:AAAA' -> PRG offset."""
        if name_or_at in self.by_name:
            kind, e = self.by_name[name_or_at]
            if kind in ("ram", "opcode"):
                raise KeyError(f"'{name_or_at}' is not a ROM location")
            return e["off"]
        return parse_rom_at(name_or_at)[0]

    def addr_of(self, name_or_addr):
        """A name -> CPU address (RAM variable address, or the CPU address of a sym / data)."""
        if isinstance(name_or_addr, int):
            return name_or_addr
        if name_or_addr in self.by_name:
            return self.by_name[name_or_addr][1]["addr"]
        if ":" in name_or_addr:
            return parse_rom_at(name_or_addr)[1]
        return parse_ram_at(name_or_addr)

    # ---- consistency with the model ----
    def check_against(self, model, tagged=False):
        """Entries that contradict the evidence: problem strings, or (unit, string) pairs when tagged."""
        res = self._check_against(model)
        return res if tagged else [p for _, p in res]

    def _check_against(self, model):
        out = _Tagged()
        C, A = ord("c"), ord("a")
        for e in self.syms:
            out.unit = e["unit"]
            if model.cpu(e["off"]) != e["addr"]:
                out.append(f"sym {e['name']}: bank {e['off'] >> 13:02X} is mapped at "
                           f"${model.base[e['off'] >> 13]:04X}, not where {e['at']} says")
            elif model.kind[e["off"]] != C:
                out.append(f"sym {e['name']} at {e['at']}: not the first byte of an instruction "
                           f"(the model has '{chr(model.kind[e['off']])}' there)")
            elif e["kind"] == "sub" and e["off"] not in model.entries:
                out.append(f"sym {e['name']} at {e['at']}: kind 'sub', but nothing calls or jumps here "
                           f"indirectly in the corpus; use kind 'part' or 'label', or add the trace that calls it")
        vm = getattr(model, "vm", None)
        for e in self.scripts:
            out.unit = e["unit"]
            if model.cpu(e["off"]) != e["addr"]:
                out.append(f"script {e['name']}: bank window mismatch for {e['at']}")
            elif vm is None or e["off"] not in vm.starts:
                out.append(f"script {e['name']} at {e['at']}: not a script instruction in the model")
        if vm is not None:
            out.unit = self.units.get("vm") and "vm"
            for p in vm.problems():
                out.append(p)
        for e in self.data:
            out.unit = e["unit"]
            if model.cpu(e["off"]) != e["addr"]:
                out.append(f"data {e['name']}: bank window mismatch for {e['at']}")
                continue
            seg = model.kind[e["off"]:e["off"] + e["len"]]
            dyn = model.dyn[e["off"]:e["off"] + e["len"]]
            bad = ((seg == C) | (seg == A)) & dyn
            if bad.any():
                out.append(f"data {e['name']}: {int(bad.sum())} of its bytes were executed as code")
        return out
