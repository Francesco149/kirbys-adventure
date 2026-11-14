---
name: cov5-g-poppy
start: main:1-2-poppy
reference: forbidden
steps:
  - in 1-2's mid-boss room 49 Kirby slides (kirby_rect kind 1) into Poppy Bros. Sr. (type $22, slot 11), its blink count variable 5 at 0: room == 49 and ram[0x501] == 1 and ram[0x6128+11] == 0x22 and ram[0x622F] == 0 and abs(ram[0x502]+ram[0x503]*256 - (ram[0x6086+11]*256+ram[0x6074+11])) < 10
  - Kirby is thrown back and up from the slide (kirby_knock_back) without damage: room == 49 and ram[0x501] == 255 and vx > 200 and vy < -400 and hp == 39
forbid:
  - lost a life: lives < 4
  - Kirby hit: hp < 39
---
Coverage movie (cov5, unit en27). Poppy Bros. Sr.'s record 39:9794 answers kind 1 of kirby_rect (Kirby's slide)
with variable 5 = $FF; no movie had slid into it. Here main's normal-form Kirby in 1-2 slides into it while it lands:
e22_hit's negative path (27:A193-A19A: variable 5 counted back to 0, kirby_knock_back) throws Kirby back.
