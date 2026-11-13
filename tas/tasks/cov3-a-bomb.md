---
name: cov3-a-bomb
start: main:1-2-poppy
reference: forbidden
steps:
  - a bomb of Poppy Bros. Sr. (type $22 in slot 12) lands and bounces up: room == 49 and ram[0x6128+12] == 34 and ram[0x61CA+12] == 1 and s16(ram[0x6116+12]*256 + ram[0x6104+12]) < -200 and ram[0x6098+12] > 140
  - a bomb thrown to the left lands and bounces left: room == 49 and ((ram[0x6128+12] == 34 and ram[0x61CA+12] == 1 and s16(ram[0x6116+12]*256 + ram[0x6104+12]) < -200 and ram[0x6098+12] > 140 and s16(ram[0x60F2+12]*256 + ram[0x60E0+12]) < 0) or (ram[0x6128+13] == 34 and ram[0x61CA+13] == 1 and s16(ram[0x6116+13]*256 + ram[0x6104+13]) < -200 and ram[0x6098+13] > 140 and s16(ram[0x60F2+13]*256 + ram[0x60E0+13]) < 0) or (ram[0x6128+14] == 34 and ram[0x61CA+14] == 1 and s16(ram[0x6116+14]*256 + ram[0x6104+14]) < -200 and ram[0x6098+14] > 140 and s16(ram[0x60F2+14]*256 + ram[0x60E0+14]) < 0))
forbid:
  - Kirby hit: hp < 39
---
Coverage movie (cov3, unit en27): the bombs of Poppy Bros. Sr. (1-2 mid-boss) landing. In every corpus movie
each bomb hit Kirby in the air. Here Kirby dodges, so a bomb thrown right lands and bounces, and a later one
thrown left (Kirby on the boss's left) lands and bounces left.
