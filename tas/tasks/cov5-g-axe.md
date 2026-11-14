---
name: cov5-g-axe
start: main@18030
reference: forbidden
steps:
  - in the knights' ambush room 180 the upper knight of type $33 (slot 15) swings (state 1) at the left edge of its platform, Kirby floating beside it: room == 180 and ram[0x6128+15] == 0x33 and ram[0x6200+15] == 1 and ram[0x6086+15]*256 + ram[0x6074+15] < 152
  - Kirby slides (kirby_rect kind 1) into a knight of type $33 whose variable 5 is 0: room == 180 and ram[0x501] == 1 and ((ram[0x6128+10] == 0x33 and ram[0x6224+10] == 0 and abs(ram[0x502]+ram[0x503]*256 - (ram[0x6086+10]*256+ram[0x6074+10])) < 12 and abs(ram[0x504]+ram[0x505]*256 - (ram[0x60AA+10]*256+ram[0x6098+10])) < 12) or (ram[0x6128+15] == 0x33 and ram[0x6224+15] == 0 and abs(ram[0x502]+ram[0x503]*256 - (ram[0x6086+15]*256+ram[0x6074+15])) < 12 and abs(ram[0x504]+ram[0x505]*256 - (ram[0x60AA+15]*256+ram[0x6098+15])) < 12))
  - Kirby is thrown back (kirby_knock_back) without damage: room == 180 and ram[0x501] == 255 and vy < -300 and hp == 47
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 47
---
Coverage movie (cov5, unit en27). From main's World 2 knights' ambush (room 180) with the normal-form Kirby:
Kirby floats left of the upper platform (its left end at X 144), so the axe knight of type $33 there swings at
him right at the end of the floor: e33_st_swing's edge path (27:AD4E-AD7F: the frame's X step taken back, the X
velocity 0) runs. Then Kirby slides into a knight: its record answers kind 1 with variable 5 = $80 and e3x_hit's
path for that (27:BB08-BB16: variable 5 = 0, variable 0 put back, kirby_knock_back) throws him back. No movie had
slid into a knight.
