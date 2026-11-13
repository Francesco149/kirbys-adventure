---
name: cov3-a-lance2
start: main@55260
reference: forbidden
steps:
  - the leaping lance knight (type $34, variant 0) is in slot 10: room == 8 and ram[0x6128+10] == 52
  - it lands and goes into one of its state routines 1-5 (variable 3 between 1 and 5): room == 8 and ram[0x6128+10] == 52 and ram[0x6200+10] >= 1 and ram[0x6200+10] <= 5
  - it is still leaping about 700 frames later: room == 8 and ram[0x6128+10] == 52 and frame >= 56390
forbid:
  - Kirby hit: hp < 31
---
Coverage movie (cov3, unit en27): the Meta-Knights' ambush of 4-5 (room $108), entered at main@55260. Kirby never
attacks and only dodges from the start of the ambush, so the knights live: the leaping lance knight (type $34,
variant 0) lands again and again and runs its state routines, and the axe knights finish their swings.
