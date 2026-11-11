# Documentation playbook: every byte of the ROM, named from evidence

The method for documenting a game binary completely: every routine, every table, every RAM variable, and the
game's own scripting language with its scripts. It builds on the TAS work in `../tas` (a recipe for driving the
game into any behaviour and proving it with a replay) and replaces the hand-edited disassembly of
`/opt/src/nes-disasm-tool`. Numbers are measurements from this repo; `LEDGER.md` has the rounds.

## 1. The idea

1. **The ROM is a partition.** Every byte is code, data, script, graphics or fill. "100% documented" is a count,
   and `kd status` prints it.
2. **Evidence comes from running, not from reading.** An instrumented emulator replays verified input movies
   and records what the CPU did with every byte: executed it, read it (and which instruction read it), jumped
   to it. Reading the code forms the hypothesis; the recording and the checks decide.
3. **A description is paired with a claim that a replay can refute.** "`mul8` multiplies" is written as
   `(rx << 8 | ra) == a * x` and evaluated on 1,500 real calls. A name without a passing claim is only
   "described".
4. **Names live in a database, the source is generated.** Entries are keyed by address. The listing and the
   ca65 source are rendered from ROM + evidence + database, and the rendered source must reassemble to the
   original ROM byte for byte.
5. **Code that never ran is a task for the driver, not a guess.** A branch that went one way only, or a routine
   no movie reaches, becomes a `kt` task; the new movie joins the corpus and the evidence grows.
6. **The gates can fail, and that is tested.** `kd selftest` plants known errors and requires every one to be
   caught.

## 2. Pieces

| piece | what |
|---|---|
| `core/kd.patch`, `core/build.sh` | FCEUmm (the TAS workbench's core) plus recording hooks in the 6502 loop and the PPU fetch. Emulation is unchanged: every corpus movie must end with the RAM hash the stock core gives. 1,485 frames/s recording against 2,016 stock. |
| `corpus/` | the movies that count as evidence, with their stock-core RAM hash (`MANIFEST.tsv`). A movie is admitted only if it adds code, data, edges or CHR tiles. |
| `evidence.py` | replays the corpus in parallel (one process per movie, savestate every 1,000 frames), merges the tables. 488,371 frames in 108 s. |
| `rommodel.py` | which bytes are instructions / operands / data / fill, routine entries, labels, a conservative static pass from code that ran, one-sided branches. No names. |
| `vm.py` | the same for the object scripts: the interpreter's opcode fetch is the evidence, the `[[opcode]]` table is the decoder. |
| `db/*.toml` | **the product**: one file per unit with routines, data regions, RAM variables, opcodes, scripts and claims. |
| `sprites.py` | a structured data format end to end: which instruction reads which kind of byte, discovery of every table and group in the ROM (`kd sprites`), and the check behind the `format` claim. The template for other formats. |
| `packed.py` | the second format by the same recipe: the streams that the game's unpack routine expands, found from the reads and from the tables of stream addresses in the database (`kd packed`). |
| `probe.py` | seeks any corpus frame in under a second, captures calls of a routine (registers, reads, writes), and checks claims. |
| `render.py` | generates `out/src/bankNN.s` and reassembles with ca65/ld65. |
| `kd` (`kd.py`) | the stateless CLI over all of it. `CARD.md` is the page a documenting agent works from. |
| `selftest.py` | planted errors for the gates. |

`evidence/` and `out/` are derived (not in git): `core/build.sh`, `kd evidence`, `kd check` rebuild them.

## 3. Evidence

Recorded per PRG byte: executed as opcode / operand, read as data, how often, first (movie, frame), the first
and the last other instruction that read it, whether it was read through a pointer, the CPU window it was
mapped at. Per instruction: the range of ROM it read. As sets: every (instruction, address, read/write) pair
for RAM and I/O, and every control-flow edge (call, jump, indirect jump, RTS used as a jump, interrupt). Per
CHR tile: fetched by the PPU for the background or for a sprite. On request: an event log of every instruction
with registers and every read and write, either for a frame window or only while a watched routine is on the
stack; `kd io`, `kd trace` and the `call` claims are built on that.

What this buys, measured on the 18-movie corpus (512,371 frames, the whole game once plus variants):

- bank windows come from the runtime (two data banks are read through both `$8000` and `$A000`);
- 2,145 routine entries with their callers, 4,873 conditional branches of which 1,066 went one way only;
- every data byte knows its reader, so tables are found by who reads them, not by guessing where they end;
- cross-bank calls and table reads resolve to the bank that was really mapped.

Dummy bus cycles (page-crossing reads, the first write of a read-modify-write, stack pushes) are not
recorded: they are hardware detail, and the first version counted them as data reads.

## 4. Levels

Per byte: **unexplained** (never touched, nothing claims it), **seen** (the evidence classifies it),
**described** (inside a database entry with a description), **verified** (a passing claim is about that
entry). A round moves bytes up; `kd status` is the scoreboard. Routines, RAM variables, opcodes and scripts
are counted the same way. A byte of a data region that only a `format` claim verifies, and that nothing read,
counts as described: the claim compares readers, and there was none.

## 5. Claims

| kind | says | checked on |
|---|---|---|
| `call` | what a routine computes: an expression over registers in/out and the memory it read and wrote, with an optional Python model | every call in several windows of several movies |
| `frames` | a relation that holds every frame (`always` / `never`) and is not vacuous (`sometimes`) | frame windows |
| `effect` | causality: poke RAM, patch ROM or replace input at a frame, compare with the untouched run | two runs from one savestate |
| `xref` | completeness: "only these routines write it / read it / call it" | every instruction that ran in the whole corpus |
| `static` | table contents by formula, pointer tables pointing at code | ROM bytes and the model |
| `vmlen` | a script opcode's operand layout and control flow | every execution in windows: where the thread went next |
| `vmop` | what a script opcode does | what its handler read and wrote, per execution |
| `format` | structured data regions parse as their format, and every byte the corpus read was read by the instruction that reads that kind of byte; with `complete`, nothing those instructions read lies outside the regions | the reader evidence of every byte |

Passing results are cached on everything that can change them (the claim, the corpus, the core, the checker
code, every name's place and size, the opcode table); failures are never cached.

## 6. Gates

`kd check` fails on any of:

- a database entry that contradicts the evidence: a name on an operand byte, in the wrong bank window, a data
  region over executed code, a `sub` nothing calls, overlapping regions, a duplicate name;
- a script opcode that ran but is not in the table, or an operand byte that was fetched as an opcode;
- a failing claim;
- a rebuild that differs from the ROM;
- (`kd evidence`) a corpus movie that does not reproduce its stock-core RAM hash.

It also prints `WEAK` for what passes but proves little: a description no claim is about, a `call` claim with
one window, a `frames` claim without `sometimes`.

`kd selftest` plants 36 errors (wrong model, wrong formula, an omitted writer, a live variable called scratch,
an inverted relation, misplaced and duplicate names, a data region over code, wrong and missing script opcode
layouts, a wrong opcode meaning, a wrong data format, a table read by the wrong code, a region missing from
the database, a wrong copy direction in the model of unpack, a stream with a wrong expanded size, a table of
stream addresses without its banks, four misreadings of the room format, four of the tile drawing, four of the block lookups, a changed movie, a changed source line) and passes only when all are caught.
Its first run caught 15: the two misses were a claim cache that ignored the opcode table and a per-unit filter
that hid a bad `about` name. Both gates were fixed; that is what the selftest is for. A later miss was a claim,
not a gate: a model claim whose windows held only the calls on which a wrong model agrees (round 12). A planted
error per new model is the cheapest test of its windows.

## 7. A round

One unit, one agent, one file. The agent works from `CARD.md`:

1. find the unit's code and state (`kd xref`, `kd fn`, `kd next`);
2. look at the evidence (run counts, one-sided branches, callers, tables read);
3. watch it work (`kd io`, `kd trace`, `kd try`, `kd look`);
4. write entries and claims; `kd check --unit U` until PASS with no WEAK;
5. for code that never ran: a `kt` trace, `kd corpus add`, then document what the new evidence shows;
6. report what stays open.

Rounds run in parallel: each agent writes only its own file, `kd check --unit` judges only that unit, a lock
serialises rebuilds. Routine sets and the `calls` lists in claims compare by address, so one unit naming a routine cannot break
another unit's claim. The evidence is shared and grows: a claim that says "only" can start failing when
someone adds a movie, which is the system working (it happened twice in the first four rounds, see the
ledger).

Who does what: a strong orchestrator picks units and reviews; any agent with the card can execute a round
(Sonnet did one in 16 tool calls; Opus did one that needed a new trace in 82); the checker is local and free.
After a round the orchestrator reads the claims once: the gates cannot see a `text` that says more than its
expression checks.

## 8. Scripts

The object scripts are data to the CPU and code to the game, so they get a second instruction set:

- the interpreter's opcode-fetch instruction (`[vm] fetch`) marks every script byte that ran as an opcode;
- `[[opcode]]` entries give operand layout and flow; `vmlen` checks them against where the thread really
  continues; `vmop` checks what a handler does;
- a static pass follows fall-through and jump targets, so scripts the corpus only partly ran are decoded
  whole; instructions that never ran are marked in the source;
- `kd vm` is the opcode table with run counts, `kd script AT` a script listing, `kd next --kind script` the
  queue.

The opcode table started from an older static table (hal-actionscript-extractor, via the old disassembly).
The runtime agreed with most of it and corrected two entries (an opcode that takes no operand, a "call
table" that is a far jump table); it also found a script whose jump table declares one entry more than it
has, which the decoder now settles from the fetch evidence.

## 9. Where "100%" stands, and the way there

`kd status` after fourteen rounds is in `LEDGER.md`. The honest picture: the method is proven on small units; the
ROM is large. What remains, in the order that pays:

1. **Finish the instruction sets.** Done for the opcode handlers in round 5 (every opcode says what it does).
   The object pipeline they sit in is done in round 6 (unit `objects`): the loop over objects and threads,
   creation and deletion, the callers of the per-object code pointers. Round 7 (unit `motion`) has the move
   and position routines, the coordinates and the camera. Round 8 (unit `draw`) has the draw routines, the sprite
   group format and the two sprite buffers; round 9 (unit `sprites`) every pose table and sprite group as
   data. Round 11 (unit `rooms`) has the room loader: what a room number, a door, a tile set and a room's object
   list are. Round 12 (unit `tiles`) has the tile drawing, the scrolling and the queue of PPU writes; round 13
   (unit `inroom`) the lookup of the block at a point, the door finder and the column spawner; round 14 (unit
   `props`) the tables a block's property indexes and the small tests built on them. Next are the movement code
   that calls those tests, and rounds per object type.
2. **Tables by reader.** `kd next --kind data` lists data by use; each table belongs to the unit of the
   routine that reads it. Data with a structure gets a format: round 9 covered 13.7% of the PRG with one
   (`sprites.py`), checked by one claim against the reader of every byte, and round 10 another 27.7% (`packed.py`:
   the packed streams, and the routine that expands them against a full model). Next by size: the sound data.
3. **Coverage.** 21% of PRG is neither touched by 512K frames nor explained by a format. The queue is the one-sided branches and the
   untouched regions next to code that ran; each is a `kt` task (minigames, game over, the Extra Game, every
   ability, every boss pattern). The attract-mode round is the template.
4. **Scripts in bulk.** With handlers documented, scripts can be described per object, many per round.
5. **CHR.** Tile fetches are recorded (10,769 of 16,384 tiles seen) but the database has no CHR entries yet.
6. **RAM.** 8,599 addresses are touched; they get named unit by unit, each checked by its writers.

Fan-out is the natural scale-up: units are independent, so many agents can work at once.

## 10. Things that bit

- A module named `dis.py` shadows Python's own and breaks numpy on import.
- One emulator core per process: a worker pool must not reuse a process for a second movie.
- A spawned worker re-runs the main module: guard scripts with `if __name__ == "__main__"`.
- Counting "new (instruction, address) pairs" as coverage admitted near-duplicate movies; coverage is code,
  data, edges and tiles.
- A handler's returned length is not the instruction's length when the handler moved the pointer itself;
  measure where the thread goes next.
- After a call into 6502 code a script may continue anywhere (the routine can eat parameter bytes), so the
  static pass must not fall through it.
- A segment "from the opcode fetch to the next fetch" includes the interpreter's own bookkeeping; end it where
  the handler returns.
- numpy bytes overflow in `lo | hi << 8`; expressions get plain ints.
- With replacement input, the control run must still be the untouched movie.
- An emulator frame can end in the middle of the game's own pass (a slow frame): a per-frame invariant about
  a structure the pass is editing must be limited to frames in which the pass began and finished.
- A routine entry that ends without `rts` falls into the next routine; "returns with A unchanged" is then
  about the wrong routine. Look at the last instruction before writing the claim.
- Holding a RAM byte only sets it at frame boundaries; a byte the game rewrites every frame before using it
  is not held at all. Find what it is computed from (`kd xref`, then the writer) and set that instead.
- A routine that skips input bytes on some paths (a sprite off the screen) does not read them: a model that
  compares ROM reads must skip the same bytes.
- A table's end is not in the data. Evidence gives the entries that were read; beyond them the end is the next
  thing something points to, the first value that is not a pointer, or a byte another routine read. The unit
  says which ends are guesses.
- `kd xref` on one address of a per-object table shows that address only; use `--len 18` before writing
  "only X writes it" (the pose table pointer has four more writers than the first slot showed).
- A window can pass `kd when` for the movie and still hold no call; `kd io` on the exact window says.
- A call counts only when it begins and ends inside the window: a room load runs for about 9 frames.
- Read an index register's value where it is used, not where it was loaded: `tay` then `iny` then `lda (p),y`
  reads the byte after a table whose length is in Y, not byte 1 (round 11's object lists; the static claim over
  all 327 rooms said so at once).
- `kd xref X --len N` prints the first addresses in full and the list is long: count the routines over the
  whole range before writing "only" (round 12 missed two writers that way, and the claim said so).
- The evidence keeps two readers per data byte. `datareaders()` of a table that three routines read is short by
  one, so "only these read it" cannot be claimed for it.
- A call's log is what the routine and its callees did. What an interrupt wrote while the call ran is not in
  `wr`, and a routine that waits for the interrupt shows only its own writes.
- The same result can come from two paths ($30 is a block property and also the answer below the room): pick the
  cases of a path by what it wrote, not by what it returned.
- Rare paths are found with `kd when` on an instruction inside the routine, not by sampling windows.
- A routine that calls another leaves the callee's scratch behind: `$00` after a call that ends in block_draw
  is block_draw's, whatever the caller stored there first.
- `kd check --unit U` prints a status block that needs the claims of every unit. In a copy of the database with
  one changed name or model nothing is cached, so that block costs a full check; `--no-status` skips it (the
  selftest does).

## 11. Open

- Far-call helpers that take the target address and bank from the bytes after the `jsr` (3E:D805) hide the
  real call site and split the calling routine; the model should treat call + inline bytes as one instruction.
- Inline parameter bytes of 6502 routines called from scripts are not part of the script grammar yet.
- A 16-bit script address into the `$8000` window is resolved only from the runtime.
- Code that runs from RAM (the IRQ trampoline) is recorded but not rendered.
- Only two readers are kept per data byte; a third is not recorded.
- CHR and the iNES header have no database entries.
- The static passes can mis-decode data as code or script; everything they add is marked as never run.
