---
name: 1-1-speed
start: power-on
reference: forbidden
steps:
  - 1-1 entered: world == 0 and room == 43
  - 1-1 goal game: world == 0 and room == 42
  - back in the W1 hub: world == 0 and room == 0
---
A speed task: make the trace from power-on to the World 1 hub after clearing 1-1 **as short as you can**.
Points of comparison:
- the w12-opus validation run did this in 3,713 frames with the routine;
- the published human-made TAS takes 2,625 (it uses the UFO glitch in 1-1; the speedrun notes describe it).

Produce every input yourself; reference inputs are hidden.

This tests the recipe's priority 3, "speed where it demonstrates the method". What does it take to approach
TAS quality? Consider:
- frame-exact menu inputs (scan press frames in the lab);
- route choices (the speedrun notes);
- tight search per room: small actions, wide beams, goals at the exact door frame;
- per-segment re-optimisation.

Keep a table of each improvement against frames and dollars, and call `finish` when further gains cost more
than they're worth. Report the frames-per-dollar curve and which technique bought which frames. Expected
budget: ~$6-8.
