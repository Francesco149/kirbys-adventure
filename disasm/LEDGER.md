# Ledger: documentation rounds and what was measured

Sessions of 2026-11-10. Everything here was measured in this repo; `./kd status`, `./kd check` and
`./kd selftest` reproduce the current numbers.

## Setup

| what | measurement |
|---|---|
| instrumented core vs stock core | identical RAM hash at the end of all 18 corpus movies (the gate of `kd evidence`); 1,485 frames/s recording, 1,979 with the recorder off, 2,016 stock |
| corpus | 26 existing movies offered, 17 kept (a movie stays only if it adds code, data, edges or CHR tiles), plus `attract` from round 3: 18 movies, 512,371 frames |
| what one movie adds | `main` (the whole game): 73,891 code bytes, 216,480 data bytes. `w12-opus`: +4,534 / +12,797. `w12-sonnet`: +2,971 / +7,240. `w3-sonnet`: +2,238 / +5,212. Everything else under 200 code bytes each, until `attract`: +2,559 / +8,119 |
| evidence build | 488,371 frames in 108 s (12 processes) |
| rebuild | generated ca65 source for 64 banks (150K lines) reassembles to the original ROM, byte for byte, from the first run of the gate on |
| `kd check`, 61 claims | about 30 s uncached, 2-4 s cached (223 claims after round 8: about 220 s uncached) |
| `kd selftest`, 20 planted errors | 2-4 minutes at first; over 10 with the 223 claims of round 8 (each planted error re-checks its unit uncached) |

## Status

| | before round 1 | after round 4 | after round 5 | after round 6 | after round 7 | after round 8 | after round 9 |
|---|---|---|---|---|---|---|---|
| PRG ran as code | 84,203 (16.1%) | 86,762 (16.5%) | same | same | same | same | same |
| PRG read as data (after round 4: without script bytes) | 244,091 (46.6%) | 214,394 (40.9%) | same | same | same | same | same |
| PRG decoded as script | not modelled | 43,415 (8.3%): 16,229 instructions, 14,456 ran | same | same | same | same | same |
| PRG never touched | 187,017 (35.7%) | 170,366 (32.5%) | same | 170,336 (32.5%) | same | same | 138,137 (26.3%): 32,199 bytes are sprite data by structure |
| PRG bytes verified | 0 | 2,248 (0.4%) | 3,945 (0.8%) | 5,264 (1.0%) | 5,676 (1.1%) | 6,630 (1.3%) | 46,345 (8.8%), and 32,199 (6.1%) described |
| routines described and verified | 0 of 2,073 | 27 of 2,145 | 100 of 2,145 | 124 of 2,148 | 140 of 2,149 | 152 of 2,152 | same |
| RAM addresses named and verified | 0 of 8,592 | 124 of 8,599 | 319 of 8,599 | 665 of 8,599 | 985 of 8,599 | 1,508 of 8,599 | same |
| script opcodes with a checked layout | 0 | 72 of 72 (68 at runtime, 4 from their handlers) | layout as before; what the opcode does: 68 checked at runtime, 4 read from their handlers | same | same | same | same |
| scripts described | 0 | 1 of 3,424 | 1 of 3,424 | same | same | same | same |
| data regions | 0 | 9 | 13 | 17 | same | 18 | 374 |
| claims passing | 0 | 61 of 61 | 140 of 140 | 181 of 181 | 201 of 201 | 223 of 223 | 226 of 226 |
| conditional branches that went one way only | 1,039 of 4,757 | 1,066 of 4,873 | same | same | same | same | same |
| CHR tiles fetched | 10,305 of 16,384 | 10,769 of 16,384 | same | same | same | same | same |

The system is in place and the rounds prove the loop; the ROM is 8.8% verified and another 6.1% described. See "What it would take".

## Rounds

| round | unit | driver | cost | produced | result |
|---|---|---|---|---|---|
| 1 | `rng`: random numbers, 8x8 multiply | the orchestrator, while building the tools | not separated from tool building | 2 routines (118 bytes), 2 tables (512 bytes), 2 RAM variables, 7 claims using all five basic kinds | PASS |
| 2 | `joypad`: controller reading, held / new buttons, soft reset | Sonnet subagent, fresh, card only | 16 tool calls, 76K tokens, 3.6 min | 6 routines (119 bytes), 8 RAM variables, 12 claims (13 after review) | PASS, no WEAK |
| 3 | `attract`: title timeout and the self-playing demo, code no movie had run | Opus subagent, fresh, card + driver card | 82 tool calls, 192K tokens, 19.8 min | a 24,000-frame trace (+2,559 code bytes, +8,119 data bytes, +247 edges, +464 CHR tiles), 7 routines (441 bytes), 3 data regions (432 bytes), 7 RAM variables, 22 claims (9 of them experiments that poke RAM, patch ROM or replace input) | PASS, no WEAK |
| 4 | `vm`: the object-script interpreter and its instruction format | the orchestrator, with new tooling (`vm.py`, `vmlen`, `vmop`) | not separated | 13 routines (472 bytes), 4 handler tables, 8 RAM variables (164 bytes), 72 opcode entries, 1 script, 19 claims | PASS |
| 5 | `vm`, second pass: what every opcode does, the thread lists, the script stacks, the bank helpers | the orchestrator, in a second session (2026-11-10) | not separated | 73 routines, 4 tables, 7 RAM variables (598 bytes, 195 of them touched in the corpus), +1,697 verified PRG bytes, 79 claims; eight opcodes renamed after what they write | PASS, no WEAK |
| 6 | `objects`: the per-frame object pass, the slot lists, creation and deletion | the orchestrator, third session (2026-11-10) | not separated | 24 routines and parts, 3 tables (336 bytes) + 1 inline parameter, 31 RAM variables (346 addresses), +1,319 verified PRG bytes, 41 claims (8 of them experiments); `calls` lists compare by address | PASS, no WEAK |
| 7 | `motion`: coordinates, velocities, the move and position routines, the camera | the orchestrator, same session as round 6 | not separated | 16 routines and parts (412 bytes), 25 RAM variables (320 addresses), 20 claims, each routine against a full model of its writes | PASS, no WEAK |
| 8 | `draw`: sprite groups, the two sprite buffers, the draw routines, the CHR bank registers | the orchestrator, fourth session (2026-11-10) | not separated | 12 routines and parts (952 bytes), 1 table (2 bytes), 8 RAM variables (523 addresses), 22 claims: every draw routine against a full model of its writes and its ROM reads, 2 experiments | PASS, no WEAK |
| 9 | `sprites`: every pose table and sprite group in the ROM, as data | the orchestrator, same session as round 8, with new tooling (`sprites.py`: discovery, the formats `sprites` / `poses` / `poseptr`, the claim kind `format`, rendering) | not separated | 356 data regions, 71,914 bytes (13.7% of PRG): 188 pose tables with 3,903 pointers, 3,501 groups in 167 regions, 1 pointer list that code indexes; 39,715 of the bytes were read in the corpus; 3 claims; 3 more planted errors | PASS, no WEAK |

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

Round 6 in a sentence: every frame `obj_run_all` walks a linked list of active objects (threads, move routine,
tick routine per object), sorts them by depth into a second list and walks that one for the position and draw
routines; an object is created by `obj_spawn` from three per-type tables in bank 18, and the pose byte picks a
pointer whose only effect in an experiment is on the sprite buffers.

Round 7 in a sentence: an object's move routine turns position plus velocity into a 16-bit world position
(plain, relative to Kirby, or relative to the camera) and its position routine turns that into a draw position
by subtracting the camera, in one variant deleting the object once it is 16 pixels off a 256 x 192 window.

Round 8 in a sentence: a draw routine turns a sprite group (a count, then X offset, Y offset, tile, attribute per
sprite) into entries of one of two sprite buffers that alternate by pass, so the interrupt always shows the one
the last finished pass wrote; a pose is a CHR bank byte followed by a group, and Kirby blinks through a variant
that forces palette 1 while bit 2 of a countdown is set.

Round 9 in a sentence: the format of round 8 applied to the whole ROM: every address a `sprite_map` instruction
names is a table of pointers to groups, the corpus read 39,715 of the 71,914 bytes found that way, and each of
those was read by exactly the instruction its place in the format predicts, while no byte that the draw routines
read lies outside the regions.

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
| Round 6: "the entry at 3E:CB78 resets the spawn parameters and returns with A unchanged" | the `call` claim failed on the first call: A came back as a slot number | the entry has no `rts`: it falls into `obj_spawn` (now `obj_spawn_plain`) |
| Round 6: "at the end of every frame the slot lists and the thread lists are a partition" | failed at main@464 and main@60845: a pass can still be running when the frame ends, with a thread taken and not yet linked | the claims hold for frames in which a pass began and finished |
| Round 6: "only `obj_spawn`'s tail, `obj_free` and init write `obj_type`" | `xref`: three more routines store a type directly | described; the claim lists them |
| Round 6: "holding Kirby's pose at $FF stops his draw routine" | false: his code rewrites the pose before the draw pass every frame | the experiment holds all 18 poses and counts the default draw routine |
| Round 6: naming the side entry 3E:CC4B (`obj_retype`) moved the writes after it to the new name | `vm.thread.lists` and two of the round's own `xref` claims failed | the shared tail has its own name (`obj_spawn_tail`); the claims name the pieces |
| Round 6: `vm.op.end` and `vm.op.clear_tick` compared `calls` with addresses that now have names | both failed | open item 7 closed: elements of `calls` equal their name and their address |
| Review of round 6 (by the orchestrator, of its own claims): "the draw routine gets the table entry" was checked on two bytes the draw routine writes itself | no gate; reading the claims once | replaced by an experiment that patches one table entry in the ROM |
| Round 7: three move routines ran in one stretch of one movie each (41, 168 and 8 calls) | `WEAK`: one window only | no entry; listed under the unit's Open with what the code reads as, until a second movie reaches those scenes |
| Round 7: "holding the camera 64 pixels off moves the sprites" (tried with `kd try` before writing a claim) | nothing differed: other code sets the camera from Kirby's position every frame | the camera is tied to the game by a per-frame relation with Kirby's world position instead |
| Round 8: "holding $05F2 at 1 makes Kirby's draw routine take its palette branch" (tried with `kd try`) | nothing differed: 21:805B recomputes $05F2 every frame from the countdown $05F9 | the experiment sets the countdown once |
| Round 8: "only the interrupt routine and obj_run_all write sprites_taken" | `xref`: 18:A000 clears it at power-on | described; the claim lists it |
| Round 8: `callers('kirby_draw_pal1') == {'kirby_draw'}` for a `part` reached by a branch | `xref`: the set is empty, a branch is not a recorded edge | the statement is left to the `call` claim on kirby_draw, which covers both halves |
| Round 8: the 233 bytes of the mirroring draw code sat inside `sprites_draw` and counted as verified with no claim about them | no gate; the status number after the first pass | the code has its own `part` and a claim on all 228 calls, with "one scene" in its text (open item 9) |
| Round 9, first discovery: 34 bytes read as pose pointers were in no table | the completeness half of the `format` check | four routines (16:B8EE, 2B:BBC2, 3B:B1D8, 3B:B429) store table addresses themselves; such tables are found by their reads |
| Round 9: "every byte of a pose table that was read was read by obj_run_all" | `format` failed at pose_tab_31_9B35+146: 2C:BE48 indexes five pointers there itself and calls sprites_draw_back | the last five pointers are a list of their own (`sprite_ptrs_31_9BC7`); discovery ends a table where another reader was seen |
| Round 9: three tables nothing drew were cut short because their last group could not be told from a pose | the discovery log (not a gate) | undrawn targets take the kind their table's other targets have |

## Selftest

20 planted errors, all caught (first run of the first 17: 15; the two misses are in the table above):
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

1. Rounds per object type: `type_script_lo/hi/bank` (round 6) give a type's first script, its `sprite_map`
   instructions name its pose tables (unit `sprites` has them under address names), its `on_draw` /
   `on_move` / `on_tick` operands its routines. A round names the tables after the object and describes the
   script. The four routines that store a table address themselves (16:B8EE, 2B:BBC2, 3B:B1D8, 3B:B429)
   belong to their objects' rounds.
2. Far-call helpers that take their target from the bytes after the `jsr` (3E:D805): the model should treat
   call + inline bytes as one instruction, so callers and callees connect. Round 6 documents one such site by
   hand (`obj_init_all_far`: a routine, a 3-byte data region and a `part`).
3. Inline parameter bytes of 6502 routines called from scripts (the script-side form of the same problem).
4. Coverage tasks from `kd status`: 1,066 one-sided branches and 138,137 untouched bytes, and 32,199 bytes of
   sprite data that nothing drew (`[not read in the corpus]` in the rendered source says which poses). Known targets:
   demos 1-7 (round 3 found their data but nothing plays them), the soft reset, game over, the minigames,
   the Extra Game.
5. Scripts in bulk, per object type: `type_script_lo/hi/bank` (round 6) give every type's first script, so a
   round can be "type N: its script, its tick / move / draw routines".
6. CHR entries in the database; code that runs from RAM; a third reader per data byte.
7. A `part` in the middle of a routine takes over the attribution of everything after it (round 6 needed
   `obj_spawn_tail` for that reason); `xref` sets could instead be told which names belong to one routine.
8. `frames` claims are evaluated at emulator frame ends, which can fall inside a pass of the game's main loop;
   a hook "at the end of routine R" would let invariants be stated without the began-and-finished condition.
9. A byte inside a named routine counts as verified when any claim is about the routine, also for code the
   claim's calls never ran (found in round 8). The count should take executed-in-the-claim's-calls into
   account, or at least never-ran bytes should stay "described". Done for data that only a `format` claim
   verifies (round 9): bytes nothing read count as described.
10. The interrupt routine 3E:C341 (PPU mask, sprite DMA, scroll, the mapper's IRQ, `chr_banks_apply`) and the
    other writers of `chr_bank`: a unit `video`. What the CHR registers select needs a claim that can see the
    PPU (the CHR fetch evidence is per tile, not per frame).
11. Other structured data by the same recipe (a format defined by the instructions that read each kind of
    byte, discovery, one `format` claim with completeness): `kd next --kind data` lists the candidates by use.
12. `kd check` re-runs every claim when a checker module changes (about 135 s with 226 claims) and `kd selftest`
    takes over 10 minutes; the cache key could depend on the claim's kind.
