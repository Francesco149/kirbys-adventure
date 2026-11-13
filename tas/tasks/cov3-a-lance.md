---
name: cov3-a-lance
start: main@55718
reference: forbidden
steps:
  - the flying lance knight (type $34, variant 1, slot 13) is in the room: room == 8 and ram[0x6128+13] == 52
  - it hit the screen edges four times and changed height (variable 9 flips to 0): room == 8 and ram[0x6128+13] == 52 and ram[0x626C+13] == 0
  - it flips back (variable 9 = 1 again after four more walls): room == 8 and ram[0x6128+13] == 52 and ram[0x626C+13] == 1
  - and once more to 0: room == 8 and ram[0x6128+13] == 52 and ram[0x626C+13] == 0
forbid:
  - Kirby hit: hp < 31
---
Coverage movie (cov3, unit en27): the Meta-Knights' ambush of 4-5 (room $108). From main@55718, where the flying
lance knight (type $34, variant 1) has just come in, Kirby only dodges and never attacks, so the knight keeps
flying from edge to edge (e34_wall) and its wall count runs out, flipping its rise/sink (variable 9).
