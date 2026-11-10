# Kirby's Adventure: documented disassembly from runtime evidence

Goal: every byte of the ROM (code, data, the object scripts) named and explained, each statement backed by a
check that a replay can refute. Start with **[PLAYBOOK.md](PLAYBOOK.md)** (the method), **[CARD.md](CARD.md)**
(the page a documenting agent works from) and **[LEDGER.md](LEDGER.md)** (the rounds so far and the numbers).

```sh
core/build.sh          # instrumented FCEUmm -> core/result, cc65 -> core/cc65 (nix)
./kd evidence          # replay corpus/ on it -> evidence/ (2 minutes)
./kd check             # every gate: database vs evidence, claims, byte-exact rebuild
./kd selftest          # plant known errors, require each to be caught
./kd status            # how much is documented
./kd next              # what to do next
```

| path | in git | what |
|---|---|---|
| `db/*.toml` | yes | the documentation: routines, data, RAM, script opcodes, scripts, claims |
| `corpus/` | yes | the input movies that count as evidence, with their RAM hashes |
| `core/kd.patch` | yes | the recording hooks for the emulator core |
| `*.py`, `kd` | yes | tools |
| `evidence/`, `out/` | no | derived: recordings, generated source, rebuilt ROM |

The ROM itself is `../roms/usa-rev-a.nes` (not in git). The Python environment is the TAS workbench's
(`../tas/.venv`); movies are authored with `../tas/kt`.
