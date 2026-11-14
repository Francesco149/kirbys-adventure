---
name: cov4-e-fish
start: main@4212
reference: forbidden
steps:
  - in room 50 the chasing fish (type $18, slot 10, tick e18_tick_chase 24.AF9F) is under Kirby, who stays on the ledge above the water: room == 50 and ram[0x6128+10] == 0x18 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xAF9F
  - its count of chase frames (variables 2 and 3) goes on while Kirby waits: room == 50 and ram[0x6128+10] == 0x18 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xAF9F and ram[0x6200+10] == 4
  - with variable 3 at 7 the script 24.AF89 starts (tick 24.B043): room == 50 and ram[0x6128+10] == 0x18 and ram[0x6200+10] == 7 and ram[0x6290+10]*256 + ram[0x627E+10] == 0xB043
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 39
---
Coverage movie (cov4, unit en24c). A chasing fish counts its frames of chase in variables 2 and 3. In the corpus Kirby
always left it (or beat it) long before the high byte reached 7. Here main's Kirby waits on the ledge at the left
of room 50 for about 2,400 frames: e18_tick_chase takes 24:AFB2 and the script 24:AF89 gives it the tick routine
24:B043 (with 24:B087-B0B1 of e18_chase_step's family); it then sinks and rises in place.
