---
name: cov5-i-mane
start: main@112740
reference: forbidden
steps:
  - in 7-2's room 139 Select drops main's UFO, the maned mid-boss (type $4D) in slot 11: room == 139 and ram[0x5E0] == 0 and ram[0x6128+11] == 0x4D
  - Kirby slides (kirby_rect kind 1) into it as it walks at him: room == 139 and ram[0x501] == 1 and abs(ram[0x502]+ram[0x503]*256 - (ram[0x6086+11]*256+ram[0x6074+11])) < 16 and abs(ram[0x504]+ram[0x505]*256 - (ram[0x60AA+11]*256+ram[0x6098+11])) < 14 and hp == 31
  - Kirby is thrown back and up from the slide (kirby_knock_back: Kirby's script 14:A1BB, Y velocity -$0240) without damage: room == 139 and ram[0x501] == 255 and vx < -300 and vy <= -500 and vy >= -560 and hp == 31
  - Kirby jumps into its leap (tick e4d_tick_air, variable 2 = 1) and it catches him in the air: room == 139 and ram[0x50C] == 1 and ram[0x7AA] == 11 and ram[0x60AA+11]*256 + ram[0x6098+11] < 140 and hp == 31
forbid:
  - lost a life: lives < 6
  - dying: hp > 47
---
Coverage movie (cov5, unit en2a). From main in 7-2's room 139 (the maned mid-boss, type $4D) Select drops the UFO.
The normal-form Kirby slides into it: its record 39:91AC answers kind 1 with variable 8 = $FF and e4d_hit's path for
that (2A:A1E9-A1EE: variable 8 = 0, kirby_knock_back) throws him back; no movie had slid into it. Then it pounces and
leaps (e4d_leap: variable 2 = 1, tick routine e4d_tick_air) and Kirby jumps into it: the catch in e4d_hit answers
carry set inside e4d_tick_air (2A:A085). In the corpus its only catch was on the ground.
