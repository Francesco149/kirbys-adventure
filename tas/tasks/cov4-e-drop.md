---
name: cov4-e-drop
start: main@12900
reference: forbidden
steps:
  - Kirby flies up to the top of room 172 (less than 32 pixels below the top edge of the screen) before the Bronto Burt of pattern 2 appears: room == 172 and y - (ram[0xE0] + 256*ram[0xE1]) < 32 and x > 560
  - e38_drop_place puts the new flier (type $38, slot 11) at the top edge right at Kirby's X instead of a random place (26.AC2D): room == 172 and ram[0x6128+11] == 0x38 and abs(ram[0x6086+11]*256 + ram[0x6074+11] - x) <= 3 and ram[0x60AA+11]*256 + ram[0x6098+11] == ram[0xE0] + 256*ram[0xE1]
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 47
---
Coverage movie (cov4, unit en26a). Pattern 2 of the winged flier appears at the top edge of the screen. In the corpus
Kirby was always lower than 32 pixels below that edge, and e38_drop_place took one of the four places of
e38_drop_xs. Here main's Kirby flies up to the top of room 172 before the flier appears, so e38_drop_place takes
Kirby's X (26:AC2D-AC43).
