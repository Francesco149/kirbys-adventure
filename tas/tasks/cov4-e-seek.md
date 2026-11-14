---
name: cov4-e-seek
start: main@20380
reference: forbidden
steps:
  - in room 184 a Bronto Burt of pattern 1 (type $38, tick e38_tick_seek 26.AC81, slot 15) is in an upward half wave (variable 6 = 1) while Kirby flies up above it: room == 184 and ram[0x6128+15] == 0x38 and ram[0x6290+15]*256 + ram[0x627E+15] == 0xAC81 and ram[0x6236+15] == 1 and ram[0x60AA+15]*256 + ram[0x6098+15] > y + 32
  - at the middle of that half wave it is 32 pixels or more below Kirby with a downward acceleration, and gets $FFF3 (obj_var8 $F3, obj_var9 $FF), 26.ACB8: room == 184 and ram[0x6128+15] == 0x38 and ram[0x6290+15]*256 + ram[0x627E+15] == 0xAC81 and ram[0x625A+15] == 0xF3 and ram[0x626C+15] == 0xFF
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 47
---
Coverage movie (cov4, unit en26a). Pattern 1 of the winged flier checks Kirby's height at the middle of each half
wave. In the corpus it was 32 pixels or more below Kirby only in its downward half waves. Here Kirby flies up to the
top of room 184 while a flier in the lower part is in an upward half wave, so e38_tick_seek takes 26:ACA9 and
stores the acceleration $FFF3 (26:ACB8-ACC2).
