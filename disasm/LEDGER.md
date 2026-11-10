# Ledger: documentation rounds and what was measured

Session of 2026-11-10. Everything here was measured in this repo; `./kd status`, `./kd check` and
`./kd selftest` reproduce the current numbers.

## Setup

| what | measurement |
|---|---|
| instrumented core vs stock core | identical RAM hash at the end of all 18 corpus movies (the gate of `kd evidence`); 1,485 frames/s recording, 1,979 with the recorder off, 2,016 stock |
| corpus | 26 existing movies offered, 17 kept (a movie stays only if it adds code, data, edges or CHR tiles), plus `attract` from round 3: 18 movies, 512,371 frames |
| what one movie adds | `main` (the whole game): 73,891 code bytes, 216,480 data bytes. `w12-opus`: +4,534 / +12,797. `w12-sonnet`: +2,971 / +7,240. `w3-sonnet`: +2,238 / +5,212. Everything else under 200 code bytes each, until `attract`: +2,559 / +8,119 |
| evidence build | 488,371 frames in 108 s (12 processes) |
| rebuild | generated ca65 source for 64 banks (150K lines) reassembles to the original ROM, byte for byte, from the first run of the gate on |
| `kd check`, 61 claims | about 30 s uncached, 2-4 s cached |
| `kd selftest`, 17 planted errors | about 2-4 minutes |

## Status

| | before round 1 | after round 4 | after round 5 |
|---|---|---|---|
| PRG ran as code | 84,203 (16.1%) | 86,762 (16.5%) | same |
| PRG read as data (after round 4: without script bytes) | 244,091 (46.6%) | 214,394 (40.9%) | same |
| PRG decoded as script | not modelled | 43,415 (8.3%): 16,229 instructions, 14,456 ran | same |
| PRG never touched | 187,017 (35.7%) | 170,366 (32.5%) | same |
| PRG bytes verified | 0 | 2,248 (0.4%) | 3,945 (0.8%) |
| routines described and verified | 0 of 2,073 | 27 of 2,145 | 100 of 2,145 |
| RAM addresses named and verified | 0 of 8,592 | 124 of 8,599 | 319 of 8,599 |
| script opcodes with a checked layout | 0 | 72 of 72 (68 at runtime, 4 from their handlers) | layout as before; what the opcode does: 68 checked at runtime, 4 read from their handlers |
| scripts described | 0 | 1 of 3,424 | 1 of 3,424 |
| data regions | 0 | 9 | 13 |
| claims passing | 0 | 61 of 61 | 140 of 140 |
| conditional branches that went one way only | 1,039 of 4,757 | 1,066 of 4,873 | same |
| CHR tiles fetched | 10,305 of 16,384 | 10,769 of 16,384 | same |

The system is in place and the rounds prove the loop; the ROM is 0.8% verified. See "What it would take".

## Rounds

| round | unit | driver | cost | produced | result |
|---|---|---|---|---|---|
| 1 | `rng`: random numbers, 8x8 multiply | the orchestrator, while building the tools | not separated from tool building | 2 routines (118 bytes), 2 tables (512 bytes), 2 RAM variables, 7 claims using all five basic kinds | PASS |
| 2 | `joypad`: controller reading, held / new buttons, soft reset | Sonnet subagent, fresh, card only | 16 tool calls, 76K tokens, 3.6 min | 6 routines (119 bytes), 8 RAM variables, 12 claims (13 after review) | PASS, no WEAK |
| 3 | `attract`: title timeout and the self-playing demo, code no movie had run | Opus subagent, fresh, card + driver card | 82 tool calls, 192K tokens, 19.8 min | a 24,000-frame trace (+2,559 code bytes, +8,119 data bytes, +247 edges, +464 CHR tiles), 7 routines (441 bytes), 3 data regions (432 bytes), 7 RAM variables, 22 claims (9 of them experiments that poke RAM, patch ROM or replace input) | PASS, no WEAK |
| 4 | `vm`: the object-script interpreter and its instruction format | the orchestrator, with new tooling (`vm.py`, `vmlen`, `vmop`) | not separated | 13 routines (472 bytes), 4 handler tables, 8 RAM variables (164 bytes), 72 opcode entries, 1 script, 19 claims | PASS |
| 5 | `vm`, second pass: what every opcode does, the thread lists, the script stacks, the bank helpers | the orchestrator, in a second session (2026-11-10) | not separated | 73 routines, 4 tables, 7 RAM variables (598 bytes, 195 of them touched in the corpus), +1,697 verified PRG bytes, 79 claims; eight opcodes renamed after what they write | PASS, no WEAK |

Round 2 in a sentence: both leads it was given held (`$3A` held, `$3C` newly pressed), and its strongest claim
is end to end: the held byte equals the movie's input, bit-reversed, on 2,400 frames in three places.

Round 3 in a sentence: the game counts 6 seconds on the title (16 after the story pages), then plays demo 0 by
overwriting the pad copies at `$E6/$E7` from a table of 183 (buttons, frames) pairs; changing one entry from
Right to Left in the ROM makes Kirby walk left.

Round 4 in a sentence: with the opcode table checked against the interpreter, 43,415 bytes that were "data"
decode as 16,229 script instructions in 3,424 scripts.

Round 5 in a sentence: all 72 opcodes now say what they do, 68 of them checked on the handler's own reads and
writes at every execution in the windows; threads turn out to be linked lists (an object's chain, a free list),
each with a 16-byte stack for `call` and `loop`, and object variables 0-9 are ten 18-byte tables from `$61CA`.

## What the gates caught (real events, not planted)

| event | caught by | outcome |
|---|---|---|
| The corpus rebuild crashed half way (a worker process got a second movie) | `kd check`: three claims failed on missing savestates | pool fixed (one movie per process) |
| Round 1 said "only `random` and boot write `rng_state`". Round 3's movie showed the demo start routine reseeding it | `rng.state.writers` failed as soon as the movie joined the corpus | description and claim corrected |
| Round 2's "who writes the pad copies" changed for the same reason while that agent was working | its own `xref` claim | the agent documented the demo writers |
| Older notes: opcode `$39` takes one operand byte | `vmlen`: the thread continues one byte earlier | entry corrected: no operand |
| Older notes: opcode `$29` is a "call table" | reading the handler after `vmlen` questioned it; `vmop` confirms | entry corrected: an indexed far jump that also sets the thread's bank |
| A script's jump table declares 5 entries and has 4 (2C:AD72) | decoder conflict: an operand byte was fetched as an opcode | the decoder lets fetch evidence end a table |
| My first `wait` and `$5x` claims compared against a value the interpreter decrements afterwards | `vmop` failed | the handler's segment now ends where it returns to the interpreter |
| A claim's result was reused after the opcode table changed | `kd selftest` (planted error not caught) | the cache key now covers every name, place, size and the opcode table |
| A bad `about` name was hidden when judging one unit | `kd selftest` | every database problem carries its unit |
| Round 5 named 3E:D7AB and 3E:D787. Two round-4 claims compared the `calls` list with those addresses | `vm.op.asm_w` and `vm.op.asm_far` failed | claims use the names; `calls` holds strings, unlike the routine sets of `xref` (open, below) |
| Round 4 declared opcodes `$30`-`$37` as two one-byte operands | six round-5 claims written for a 16-bit operand failed | the table says `u16` / `s16`, as the handlers use them |
| "asm_far maps back the bank it found at `$8000`" | failed at 24:A325: the called routine (22:8470) overwrites the saved bank on the CPU stack to keep its own bank mapped | described; the claim says "the old bank or the operand's bank" |
| "Holding Kirby's X velocity moves him" (an `effect` with a held poke) | false: his control code recomputes the velocity from the pad every frame | replaced by an input experiment (Right held against no buttons) |

## Selftest

17 planted errors, all caught (first run: 15; the two misses are the last two rows above):
wrong routine model, wrong table formula, an omitted writer, a live variable declared scratch, an inverted
per-frame relation, a name on an operand byte, a name in the wrong bank window, a data region over executed
code, a duplicate name, an undefined `about` name, a script opcode with an extra operand, one a byte short,
one missing from the table, a wrong opcode meaning, an inverted jump condition, a corpus movie with changed
input, a changed line of rendered source.

## What the held-out rounds changed

Both subagents reported what got in their way; each item became a fix.

| reported by | problem | fix |
|---|---|---|
| round 2 | with replacement input, the control run got the same input | the control run is always the untouched movie |
| round 2, 3 | input letters not documented (`S` is Select, `T` is Start) | in the card |
| round 2 | the `pad` mask is the reverse of the game's bit order | in the card |
| round 2 | listings say `sub_3F_E45D`, claims want `3F:E45D` | in the card; routine sets now compare by address |
| round 3 | `{'a', 'b'} <= readers(x)` was false for a correct claim | routine sets are no longer a `set` subclass, so both operand orders work |
| round 3 | no command to see an address's values over time | `kd watch` |
| round 3 | `rd` / `wr` / `romrd` not described; lag frames; routines that run three times | in the card |
| round 3 | far calls through 3E:D805 hide the real call site, and split the caller | in the card; open (below) |
| review of round 2 | one claim's text said more than its expression checked | text tightened, the missing Up+Down check added (passes), rule added to the card |

## What it would take

A rough projection from two held-out rounds, to be replaced by measurement as rounds accumulate: a round
covers about 5 routines or 100-450 bytes of code with their RAM and tables, for 16-82 tool calls. 2,145 routine
entries are known, so code alone is some hundreds of rounds; 3,424 scripts and the tables come on top, and a
third of the PRG needs traces first. This is a fan-out job (units are independent and the gates are local),
not something a single session finishes.

## Open, in the order it should be attacked

1. The object pipeline around the interpreter: 3E:CCE5 and 3E:CD76 (the loop over objects and their threads,
   and the callers of the pointers that on_tick / on_move / on_draw / on_position store), object creation and
   deletion (3E:CBA2, 3E:CCA7, 3E:D655, 3E:D6B9), the far-call entry 3E:D7A5. That gives the object fields
   their meaning; round 5 describes them by address only.
2. Far-call helpers that take their target from the bytes after the `jsr` (3E:D805): the model should treat
   call + inline bytes as one instruction, so callers and callees connect.
3. Inline parameter bytes of 6502 routines called from scripts (the script-side form of the same problem).
4. Coverage tasks from `kd status`: 1,066 one-sided branches and 170,366 untouched bytes. Known targets:
   demos 1-7 (round 3 found their data but nothing plays them), the soft reset, game over, the minigames,
   the Extra Game.
5. Scripts in bulk, per object type, once the handlers are named.
6. CHR entries in the database; code that runs from RAM; a third reader per data byte.
7. In `call` and `vmop` claims the `calls` list is plain strings, so naming a routine breaks a claim that
   wrote it by address. It should compare by address like the routine sets of `xref`.
