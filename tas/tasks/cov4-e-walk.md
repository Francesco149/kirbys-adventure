---
name: cov4-e-walk
start: main@73040
reference: forbidden
steps:
  - in the waterfall room 37 the walker (type $1D, variant 0, slot 14) jumps from its block (tick e1d_tick_jump 26.A10B): room == 37 and ram[0x6128+14] == 0x1D and ram[0x6290+14]*256 + ram[0x627E+14] == 0xA10B
  - Kirby (the UFO) stays where he is, does not shoot, and it lands on the next block to the left and walks again (tick e1d_tick_walk 26.A0BD, its jump count variable 3 back near 100): room == 37 and ram[0x6128+14] == 0x1D and ram[0x6290+14]*256 + ram[0x627E+14] == 0xA0BD and ram[0x6200+14] > 90 and ram[0x60AA+14]*256 + ram[0x6098+14] == 137
  - Kirby flies up out of its way: room == 37 and y < 100 and ram[0x6128+14] == 0x1D
forbid:
  - lost a life: lives < 6
  - Kirby hit: hp < 31
---
Coverage movie (cov4, unit en26b). The walker of type $1D jumps now and then (e1d_walk_jump). In the corpus every
jump was ended by Kirby's shots or by the fall into the waterfall. Here main's Kirby hovers at X 643 and
lets the walker of the block to the right jump: it lands on the next block to the left (by the hovering Kirby), so e1d_tick_jump takes its landing path
(26:A118 taken, 26:A128-A12D: sound $0E and entry 3 of e1d_scripts) and walks again. Kirby then flies up.
