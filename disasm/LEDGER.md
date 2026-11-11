# Ledger: documentation rounds and what was measured

Sessions of 2026-11-10 and 2026-11-11. Everything here was measured in this repo; `./kd status`, `./kd check` and
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
| `kd selftest`, 20 planted errors | 2-4 minutes at first; over 10 with the 223 claims of round 8 (each planted error re-checks its unit uncached); at round 14, 45 minutes for the first 12 of 32 cases, and about 4 minutes for all 36 once the per-case check skips the status block (`--no-status`); 10 minutes for the 40 of round 15 |

## Status

| | before round 1 | after round 4 | after round 5 | after round 6 | after round 7 | after round 8 | after round 9 | after round 10 | after round 11 | after round 12 | after round 13 | after round 14 | after round 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PRG ran as code | 84,203 (16.1%) | 86,762 (16.5%) | same | same | same | same | same | same | same | same | same | same | same |
| PRG read as data (after round 4: without script bytes) | 244,091 (46.6%) | 214,394 (40.9%) | same | same | same | same | same | same | same | same | same | same | same |
| PRG decoded as script | not modelled | 43,415 (8.3%): 16,229 instructions, 14,456 ran | same | same | same | same | same | same | same | same | same | same | same |
| PRG never touched | 187,017 (35.7%) | 170,366 (32.5%) | same | 170,336 (32.5%) | same | same | 138,137 (26.3%): 32,199 bytes are sprite data by structure | 114,325 (21.8%): 23,812 more bytes are packed streams and table entries by structure | 109,393 (20.9%): 4,932 more bytes are object lists and room tables by structure | same | same | 109,188 (20.8%): 205 more bytes are entries of the two property tables that nothing read | 109,172 (20.8%): 16 more bytes are entries of the current tables that nothing read |
| PRG bytes verified | 0 | 2,248 (0.4%) | 3,945 (0.8%) | 5,264 (1.0%) | 5,676 (1.1%) | 6,630 (1.3%) | 46,345 (8.8%), and 32,199 (6.1%) described | 169,882 (32.4%), and 55,582 (10.6%) described | 186,002 (35.5%), and 55,582 (10.6%) described | 188,175 (35.9%), and 55,582 (10.6%) described | 188,715 (36.0%), and 55,582 (10.6%) described | 189,196 (36.1%), and 55,582 (10.6%) described | 189,993 (36.2%), and 55,582 (10.6%) described |
| routines described and verified | 0 of 2,073 | 27 of 2,145 | 100 of 2,145 | 124 of 2,148 | 140 of 2,149 | 152 of 2,152 | same | 156 of 2,152 | 184 of 2,162 | 201 of 2,162 | 204 of 2,162 | 212 of 2,162 | 227 of 2,162 |
| RAM addresses named and verified | 0 of 8,592 | 124 of 8,599 | 319 of 8,599 | 665 of 8,599 | 985 of 8,599 | 1,508 of 8,599 | same | same | 6,117 of 8,599 | 6,549 of 8,599 | same | 6,550 of 8,599 | 6,568 of 8,599 |
| script opcodes with a checked layout | 0 | 72 of 72 (68 at runtime, 4 from their handlers) | layout as before; what the opcode does: 68 checked at runtime, 4 read from their handlers | same | same | same | same | same | same | same | same | same | same |
| scripts described | 0 | 1 of 3,424 | 1 of 3,424 | same | same | same | same | same | same | same | same | same | same |
| data regions | 0 | 9 | 13 | 17 | same | 18 | 374 | 806 | 840 | 869 | same | 871 | 873 |
| claims passing | 0 | 61 of 61 | 140 of 140 | 181 of 181 | 201 of 201 | 223 of 223 | 226 of 226 | 231 of 231 | 260 of 260 | 295 of 295 | 307 of 307 | 325 of 325 | 355 of 355 |
| conditional branches that went one way only | 1,039 of 4,757 | 1,066 of 4,873 | same | same | same | same | same | same | same | same | same | same | same |
| CHR tiles fetched | 10,305 of 16,384 | 10,769 of 16,384 | same | same | same | same | same | same | same | same | same | same | same |

The system is in place and the rounds prove the loop; the ROM is 36.2% verified and another 10.6% described, most of it by two data formats (rounds 9 and 10) and the room data that round 11 gave a meaning; rounds 12 to 15 are code again (how the room is drawn and scrolled, how it is asked what is at a point, what the answer is looked up in, and what Kirby's code does with it). See "What it would take".

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
| 10 | `unpack`: the routine that expands packed data, every packed stream, the tables of stream addresses | the orchestrator, fifth session (2026-11-10), with new tooling (`packed.py`: the formats `packed` / `packlo` / `packhi` / `packbank`, discovery, rendering) | not separated | 4 routines (305 bytes), 422 streams (145,383 bytes: 280 that the corpus unpacked with 122,000 bytes, 142 more that only the tables point to), 10 table regions (1,232 bytes), 5 claims: the routine against a full model of its output on every call in six windows, 1 experiment; 4 more planted errors | PASS, no WEAK |
| 11 | `rooms`: the room loader, the room format, doors, tile sets, the rooms' object lists, the bank helpers | the orchestrator, sixth session (2026-11-11) | not separated | 28 routines and parts, 34 data regions (13,471 bytes: 16 tables of the loader with 8,729, and the 327 object lists as 18 runs, 4,742), 36 RAM variables (4,609 addresses: the room header, the map, the block tables), 29 claims: eleven of them whole room loads against models of what the load leaves behind, 2 static claims over all 327 rooms, 1 experiment; 4 more planted errors | PASS, no WEAK |
| 12 | `tiles`: the row, column and block drawers, the attribute copy, scrolling, the PPU write queue | the orchestrator, seventh session (2026-11-11) | not separated | 18 routines, parts and entries (1,739 bytes), 29 tables and inline records (434 bytes), 16 RAM variables (432 addresses), 35 claims: the three drawers, the queue writer and the queue reader each against a full model of their writes, 1 experiment; 4 more planted errors | PASS, no WEAK |
| 13 | `inroom`: the block at a point, the door finder, the column spawner | the orchestrator, same session as round 12 | not separated | 3 routines (540 bytes), 12 claims: each routine against a model on every path the corpus took, 1 experiment that patches a door record | PASS, no WEAK |
| 14 | `props`: the two tables by block property, the tests on the block at a point, block replacement | the orchestrator, same session as round 12 | not separated | 8 routines (227 bytes), 2 tables (254 bytes), 1 RAM variable, 17 claims: every routine against a model, 1 experiment that patches a table entry; `kd check --no-status` | PASS, no WEAK |
| 15 | `kblocks`: what Kirby's code asks of the blocks: water, currents, the Down test, breaking blocks | the orchestrator, eighth session (2026-11-11) | not separated | 15 routines and parts (767 bytes), 2 tables (30 bytes), 4 RAM variables (18 addresses), 30 claims: every routine against a model, 1 experiment that zeroes the current tables; 4 more planted errors | PASS, no WEAK |

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

Round 10 in a sentence: one routine (3E:C43A, twelve callers) expands a quarter of the PRG, room layouts, tile sets
and screens, from a stream of eight commands (literal, fill, pair fill, counting run, and copies from its own output:
plain, bit-reversed, backwards); the stream of every room is found through three 327-byte tables indexed by room
number, and replacing one room's entry by another's makes the game load the other room's bytes.

Round 11 in a sentence: a room is a number; loading it looks up the door that was taken in a list of 5-byte records
(position, destination room, cell and position, a kind), expands a tile set into six tables of 256 blocks and the
room into a 218-byte header plus 192 block numbers per screen (16 x 12 blocks of 16 pixels, and a table that says
which screen each cell shows), puts Kirby and the camera at the entry, and creates the objects of a per-room list
(per cell an end index, then a position byte and a kind byte per object) for the rows of blocks at the camera.

Round 12 in a sentence: the background is a plane of 32 x 48 tiles in which every tile of the 24-row screen is written
twice, 24 rows apart, so the picture scrolls through 192 pixels without a seam; a block is four tiles (top left, top
right, bottom left, bottom right) and a palette number that goes into a RAM copy of the attribute tables, and all
of it reaches the PPU as records in a ring that the interrupt empties up to a budget, one column or row per 8 pixels
the camera moves.

Round 13 in a sentence: one routine (3F:EF90, 1.4 million calls) turns a position into a cell, a block and that
block's property byte, the door finder is that lookup plus a search of the room's 5-byte door records for the
block's cell and position, and changing one record's position byte in the ROM keeps Kirby out of the next room.

Round 14 in a sentence: a block's property indexes two tables of 127 bytes (a shape number with three flags, and
either a pair of small numbers or a "can be replaced" bit), the code that moves Kirby and the objects asks for one
part of them at a time through five small routines, and a replaceable block turns into the block 8 before it,
which is what round 11's tileset_byte holds; clearing the bit for one property in the ROM leaves the block
standing.

Round 15 in a sentence: bit 7 of a block's shape byte is water (a flag follows it, and three small routines tell
Kirby's states when he enters and leaves), the pair of prop_extra is a current (a direction and a strength that index
a table of velocities added to his every frame, or one index for the whole room), and shapes 9, $A and $B are blocks
that break, tested at one point or on every block under a rectangle around Kirby, with two tests that differ in
whether $A breaks.

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
| Round 10: "nothing in the corpus tested bit 7 of a room's bank byte" (written in the unit's Open) | `xref`: 13:A115 reads the table too, and branches on bit 7 when the room number changes | described: a room flag; what it means is left to the room loader's round |
| Round 10: a packed region with a wrong expanded size passed | `kd selftest` (planted error not caught): the claim cache key did not cover the `unpacked` field | the key covers it |
| Round 10: the discovery, run again after its regions were in the database, reported all 142 unread streams as "bytes something else read" | its own log | a stream that is already a packed region is not a conflict |
| Round 11: "byte 1 of a room's object list is the distance from the positions to the kinds" (read off the code as `iny` after loading byte 0) | the `static` claim over all rooms failed for 202 of 327 | Y holds the cell count at that point: the loader reads the last cell's end index, the number of objects; byte 1 is read by nothing. With the right reading the 327 lists tile 18 runs without a gap |
| Round 11: "after a load the map is the room's expansion" | the `call` claim failed at the first load (room 0) and at main@101332 (room $67) | rooms 0-6 rewrite their map after unpacking (13:ABD2), and 38:AD5E replaces single blocks during the load; the claim says header exact, map but for 2 blocks, rooms 0-6 left out |
| Round 11: `tileset_byte` declared with 49 entries like the other tile set tables | `xref`: 13:AC94 reads the bytes from entry 31 on | they are another table; the region has 31 entries |
| Round 11: "only room_pick and 38:A000 read the door tables" | `xref`: 3F:EDA2 reads them too | the claim lists it |
| Round 11: naming the part of the loader at 3F:E640 moved its call of `unpack` to the new name | `unpack.callers` and `unpack.tables.readers` failed | those claims name the part (open item 7 once more) |
| Round 11: a `call` claim on `room_load` with 10-frame windows around the load | "0 calls seen" | a load runs for about 9 frames (87,000-150,000 instructions) and a call counts only when it begins and ends inside the window; windows of 40 frames and more (in the card) |
| Round 12: "only attr_set, attr_put and 3D:A3FC write nt_attr" (read off the first lines of a long `kd xref`) | `xref`: 13:ADCB and 3D:A42B write it too | the claim lists them; they are not in the unit |
| Round 12: "screen_row_ptr, tiles_col and 13:AD5A are the only readers of screen_lo" | `xref`: the set was {13:AD5A, 38:A000, screen_row_ptr}; tiles_col, a reader by its own listing, was missing | the evidence keeps two readers per byte, so "only" cannot be claimed for a table with three; the claim says what was recorded (open item 6) |
| Round 12: "frame_wait returns with frame_flag = 1" | the `call` claim failed on the first call | a call's log holds what the routine did, not what the interrupt wrote meanwhile; the claim is the clear, plus a `frames` claim that it never starts twice in a frame |
| Round 12: a model function named `p` | TypeError: `p` is the status register in a `call` claim | renamed; in the card |
| Round 12: round 11's text for room_draw said it draws "24 columns of 8 pixels" | no gate; documenting the routine it calls (12:8170 draws rows) | text corrected |
| Round 12: a case claim asked for a row drawn with the display on that starts in the middle of a cell | 0 calls: no movie scrolls vertically away from a cell's left edge | a coverage task (open item 4); the case is shown on room draws |
| Round 13: "an answer of $30 means the point is below the room" | the case claim failed: $30 is also a block property inside the room | cases are picked by what the path wrote, not by its result |
| Round 13: windows chosen by sampling held none of the lookup's three rare paths (0 of 8,000 calls) | `min_calls` | `kd when` on an instruction inside the routine gives the first frame of each path; in the card |
| Round 14: "block_break_at leaves the block's index in $00" (the store at 3F:EF05) | the `call` claim failed on the first replaced block | block_draw, called through block_redraw, uses $00 again; the claim names the byte of room_map instead |
| Round 14: windows of 300 frames after the first call held 3 calls of block_break_at (2,048 in the corpus) | `min_calls` | the calls come in a few dense stretches; counting calls per 200 frames over the movie finds them |
| Round 14: `kd selftest` had run for 45 minutes and was at case 13 of 32 | no gate; looking at the process list | `kd check --unit U` ran every claim of every unit for its status block, and a planted error changes the cache key of all of them; the selftest now passes `--no-status` |
| Round 15: windows of 20 to 300 frames at the first call held 17 calls of the rectangle sweep and 18 of its wrapper (19,076 and 2,060 in the corpus) | `min_calls` | the calls come in bursts of about 6 frames, one per attack; windows of 3,000 frames in a movie that attacks often |
| Round 15: "the windows hold calls of down_bit5_test that return carry set" | 2 matching calls in 152; a search of five movies found two such calls in all (main@17449, main@57986) | the case claim is about the two-point path, and a second claim names the two frames |
| Round 15: `kd try` with entry 0 of the current tables zeroed at main@67640 | nothing differed: that shaft uses another entry | the experiment zeroes all 30 bytes |
| Round 12's claim on attr_set passed with a model that puts the field in the same vertical half in both copies | `kd selftest` (planted error not caught) | its four windows of 2-3 frames held calls for block rows 0-2 only, where both models agree; the windows now hold whole columns, and a case claim requires 100 calls for rows 3-11 |

## Selftest

40 planted errors, all caught (first run of the first 17: 15, and of the four for the tiles: 3; the misses are in the table above):
wrong routine model, wrong table formula, an omitted writer, a live variable declared scratch, an inverted
per-frame relation, a name on an operand byte, a name in the wrong bank window, a data region over executed
code, a duplicate name, an undefined `about` name, a script opcode with an extra operand, one a byte short,
one missing from the table, a wrong opcode meaning, an inverted jump condition, a corpus movie with changed
input, a changed line of rendered source; from round 8 on also the data formats (sprites, packed streams)
and, for the rooms, a screen of the wrong size, a door record of the wrong size, the entry row taken from the
wrong nibble, and the first reading of the object-list head; for the tiles, the lower tiles of a block taken from
the wrong tables, the second copy of a row a whole name table down, an attribute field with the same vertical half
in both copies, and a queue record with the address bytes swapped; for the lookups of rounds 13 and 14, a block
index with column and row exchanged, a door's cell read from the wrong nibble, a replaced block 8 after instead
of 8 before, and the two numbers of prop_extra exchanged; for round 15, a current's direction and strength exchanged,
water_left with the sense of the water bit inverted, a rectangle sweep one column and row short, and the objects of
the two kinds of broken block exchanged.

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

0. Collision proper, continued. Round 15 has the bank 21 layer (water = bit 7, currents = the pair, breaking =
   shapes 9, $A, $B). Still without a meaning: shape numbers 1-8, $C-$F and bits 5 and 6. They are in the other
   callers of `prop_shape_at` (21:8C7D, 22:8A6C, 22:8AC6, 25:ACD4 with four calls, 2D:B6D4, 14:AD96), in Kirby's
   move routine 21:95DE (limits at $05C8-$05CD, the camera) with 21:87AD before it, in 21:80C0 (shape $E) and in
   16:B149 / 2C:BD51 (the other callers of `block_break_at`). Coverage tasks from the round: `break_test_2` and the
   sweep of kind 2 (21:941C), the shape $A branch of `break_test_0`, the velocity limits of `current_push`.
   Around the room: 38:A000 (648 bytes, once per frame from
   obj_run_all; it reads the door tables and writes room_map), the hub rooms' map changes (13:ABD2, 13:ACD5,
   13:AD5A), the callers of `block_draw` (13:A804, 13:A93D, 38:A309, 38:AAF8, 3F:EF50), 3F:EA9B (asked by
   objs_spawn whether an object may be created; it keeps lists at $6621 / $667B / $66DD), the door kinds that
   never ran (8, 9, $D, $E, $20, $70). An `objlist` format in the style of `sprites.py` would render each list as
   cells, positions and kinds instead of rows of bytes.
   Then sound: 1D:84E0 is the stream reader of an engine whose data is 17,303 bytes read in the corpus (banks
   1D-20), a third format for the recipe of rounds 9 and 10; `kd next` has it at the top by use.
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
    other writers of `chr_bank`: a unit `video`. Round 12 has its queue (`ppu_write`, `ppu_flush`, `palette_send`);
    still to do are 3E:C0BE / 3E:C0DA (records of seven bytes that turn into `ppu_write` calls, 12 callers) and
    3E:C3A4 (the scroll registers from `scroll_x` / `scroll_y`). What the CHR registers select needs a claim that can see the
    PPU (the CHR fetch evidence is per tile, not per frame).
11. Other structured data by the same recipe (a format defined by the instructions that read each kind of
    byte, discovery, one `format` claim with completeness): `kd next --kind data` lists the candidates by use.
12. A `call` claim cannot see the PPU or what an interrupt did during the call: "this many bytes reach $2007"
    and "returns after the interrupt" are not checkable (round 12). An event log that marks interrupt entries
    would allow both.
13. `kd check` re-runs every claim when a checker module changes (about 135 s with 226 claims) and `kd selftest`
    takes over 10 minutes; the cache key could depend on the claim's kind.
